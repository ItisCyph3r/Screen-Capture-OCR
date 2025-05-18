import pyautogui
import cv2
import numpy as np
from PIL import Image
from tkinter import Tk, Canvas, messagebox
import win32clipboard
import pytesseract
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
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            text = pytesseract.image_to_string(image)
            if not text.strip():
                if self.dashboard and hasattr(self.dashboard, 'error_var') and self.dashboard.error_var.get():
                    messagebox.showinfo("Info", "No text was found in the selected area.")
                self.root.deiconify()
                return
            self.copy_to_clipboard(text.strip())
            if self.dashboard and hasattr(self.dashboard, 'notif_var') and self.dashboard.notif_var.get():
                messagebox.showinfo("Success", "Text copied to clipboard!")
            self.quit()
        except Exception as e:
            print(f"Error processing screenshot: {e}")
            messagebox.showerror("Error", f"Failed to process screenshot: {str(e)}")
            self.quit()

    def copy_to_clipboard(self, text):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            raise

    def quit(self):
        if self.root:
            self.root.quit()

    def run(self):
        if self.root:
            self.root.mainloop() 