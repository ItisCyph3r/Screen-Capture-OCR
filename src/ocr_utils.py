import sys
import os
import tempfile
import urllib.request
import subprocess
import pytesseract
import winreg
from tkinter import messagebox
from config import TESSERACT_DOWNLOAD_URL, TESSERACT_INSTALLER_NAME

def is_tesseract_installed():
    paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        os.path.join(os.path.dirname(sys.executable), 'Tesseract-OCR')
    ]
    return any(os.path.exists(os.path.join(path, "tesseract.exe")) for path in paths)

def get_tesseract_path():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tesseract-OCR") as key:
            return winreg.QueryValueEx(key, "Path")[0]
    except:
        if is_tesseract_installed():
            for path in [r"C:\Program Files\Tesseract-OCR", r"C:\Program Files (x86)\Tesseract-OCR"]:
                if os.path.exists(os.path.join(path, "tesseract.exe")):
                    return path
    return None

def download_and_install_tesseract():
    try:
        result = messagebox.askyesno(
            "Tesseract OCR Required",
            "Tesseract OCR is required but not installed. Would you like to download and install it now?"
        )
        if not result:
            messagebox.showinfo("Info", "Application cannot run without Tesseract OCR.")
            sys.exit(0)
        print("Downloading Tesseract installer...")
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, TESSERACT_INSTALLER_NAME)
        urllib.request.urlretrieve(TESSERACT_DOWNLOAD_URL, installer_path)
        print("Installing Tesseract...")
        subprocess.run([installer_path, '/S'], check=True)
        messagebox.showinfo("Success", "Tesseract OCR has been installed successfully!")
        try:
            os.remove(installer_path)
        except:
            pass
        return get_tesseract_path()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install Tesseract: {str(e)}")
        sys.exit(1)

def setup_tesseract():
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        tesseract_path = download_and_install_tesseract()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = os.path.join(tesseract_path, "tesseract.exe")
        return True
    else:
        messagebox.showerror("Error", "Failed to initialize Tesseract OCR")
        sys.exit(1) 