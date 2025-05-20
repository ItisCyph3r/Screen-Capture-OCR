import pyautogui
import cv2
import numpy as np
from PIL import Image
from tkinter import Tk, Canvas, messagebox
import win32clipboard
import pytesseract
import threading
import concurrent.futures
import queue
import time
from config import COLORS
from ocr_utils import setup_tesseract

class ScreenCaptureApp:
    def __init__(self, dashboard=None):
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.dashboard = dashboard
        self.result_queue = queue.Queue()
        self.processing_thread = None
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        setup_tesseract()
        self.initialize_ui()

    def initialize_ui(self):
        try:
            self.root = Tk()
            self.root.title("Screen Capture OCR")
            self.root.attributes('-alpha', 0.005)
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.canvas = Canvas(self.root)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.bind("<Button-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)
            self.root.bind("<Escape>", lambda e: self.quit())
        except Exception as e:
            print(f"Failed to initialize UI: {e}")
            if self.root:
                self.root.destroy()
            raise

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='', width=0
        )

    def on_release(self, event):
        if not self.start_x or not self.start_y:
            return
        try:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            if x2 - x1 < 5 or y2 - y1 < 5:
                messagebox.showinfo("Info", "Selection too small. Please try again.")
                return
            self.root.withdraw()
            
            # Capture screenshot with proper error handling
            try:
                # Start a loading indicator or message
                self.processing_thread = threading.Thread(
                    target=self.process_image_async,
                    args=(x1, y1, x2 - x1, y2 - y1)
                )
                self.processing_thread.daemon = True
                self.processing_thread.start()
                
                # Check for results every 50ms
                self.root.after(50, self.check_processing_results)
            except Exception as inner_e:
                print(f"Error starting processing thread: {inner_e}")
                messagebox.showerror("Error", f"Failed to start processing: {str(inner_e)}")
                self.quit()
        except Exception as e:
            print(f"Error in screen capture: {e}")
            messagebox.showerror("Error", f"Failed to capture screen: {str(e)}")
            self.quit()

    def copy_to_clipboard(self, text):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            # Make sure clipboard is closed even if there's an error
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            raise

    def quit(self):
        if self.root:
            try:
                # Clean up resources before quitting
                if self.current_rect:
                    self.canvas.delete(self.current_rect)
                    self.current_rect = None
                
                # Shut down the thread pool
                self.thread_pool.shutdown(wait=False)
                
                # Force garbage collection to free memory
                import gc
                gc.collect()
                
                # Destroy the root window properly
                self.root.destroy()
            except Exception as e:
                print(f"Error during cleanup: {e}")
                # Make sure we still try to quit even if cleanup fails
                try:
                    self.thread_pool.shutdown(wait=False)
                    self.root.quit()
                except:
                    pass

    def process_image_async(self, x, y, width, height):
        """Process the image in a separate thread to keep UI responsive"""
        try:
            # Capture screenshot
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert to OpenCV format
            image_array = np.array(screenshot)
            del screenshot  # Free memory
            
            # Convert to OpenCV format using CPU - safer across all systems
            image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Only attempt GPU acceleration if the image is large enough to benefit
            if width * height > 250000:  # Only for larger images
                try:
                    # Safely check for CUDA without importing cuda module directly
                    has_cuda = hasattr(cv2, 'cuda') and hasattr(cv2.cuda, 'getCudaEnabledDeviceCount')
                    if has_cuda and cv2.cuda.getCudaEnabledDeviceCount() > 0:
                        # Use GPU acceleration
                        try:
                            gpu_image = cv2.cuda_GpuMat()
                            gpu_image.upload(image)
                            gpu_gray = cv2.cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
                            gray = gpu_gray.download()
                            # If we got here, GPU processing worked
                            print("Using GPU acceleration for image processing")
                            del gpu_image, gpu_gray  # Free GPU memory
                        except Exception as gpu_err:
                            print(f"GPU acceleration failed, falling back to CPU: {gpu_err}")
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                except Exception:
                    # Any CUDA-related error, fall back to CPU
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                # For smaller images, just use CPU
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance image for better OCR results
            image = self.enhance_image(image)
            
            # Process with OCR
            text = pytesseract.image_to_string(image)
            del image  # Free memory
            
            # Put result in queue
            self.result_queue.put((True, text.strip()))
        except Exception as e:
            print(f"Error in image processing thread: {e}")
            self.result_queue.put((False, str(e)))
    
    def enhance_image(self, image):
        """Enhance image for better OCR results with cross-system compatibility"""
        # If grayscale conversion already happened in process_image_async
        if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
            gray = image
        else:
            # Convert to grayscale if needed
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding with safe parameters
        try:
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        except Exception as e:
            print(f"Adaptive threshold failed, using simple threshold: {e}")
            # Fall back to simple thresholding if adaptive fails
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Try to apply noise reduction, but fall back if it fails
        try:
            # Use a faster denoising method with reasonable parameters
            denoise = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            return denoise
        except Exception as e:
            print(f"Denoising failed, using threshold image: {e}")
            return thresh
    
    def check_processing_results(self):
        """Check if the image processing is complete"""
        try:
            # Non-blocking check for results
            success, result = self.result_queue.get_nowait()
            
            if success:
                if not result:
                    # No text found
                    if self.dashboard and hasattr(self.dashboard, 'error_var') and self.dashboard.error_var.get():
                        messagebox.showinfo("Info", "No text was found in the selected area.")
                    self.root.deiconify()
                    return
                
                # Copy text to clipboard
                self.copy_to_clipboard(result)
                
                # Show success notification if enabled
                if self.dashboard and hasattr(self.dashboard, 'notif_var') and self.dashboard.notif_var.get():
                    messagebox.showinfo("Success", "Text copied to clipboard!")
                self.quit()
            else:
                # Error occurred
                messagebox.showerror("Error", f"Failed to process image: {result}")
                self.quit()
        except queue.Empty:
            # Not ready yet, check again in 50ms
            self.root.after(50, self.check_processing_results)
    
    def run(self):
        if self.root:
            self.root.mainloop()