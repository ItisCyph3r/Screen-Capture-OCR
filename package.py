import os
import sys
import tempfile
import urllib.request
import zipfile
import subprocess
import PyInstaller.__main__
from pathlib import Path
import shutil
import winreg

TESSERACT_DOWNLOAD_URL = "https://sourceforge.net/projects/tesseract-ocr-alt/files/latest/download"
TESSERACT_INSTALLER_NAME = "tesseract-installer.exe"

def is_tesseract_installed():
    """Check if Tesseract is installed by looking in common installation paths."""
    paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        os.path.join(os.path.dirname(sys.executable), 'Tesseract-OCR')
    ]
    return any(os.path.exists(os.path.join(path, "tesseract.exe")) for path in paths)

def get_tesseract_path():
    """Get Tesseract installation path."""
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
    """Download and install Tesseract if not present."""
    print("Downloading Tesseract installer...")
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, TESSERACT_INSTALLER_NAME)
    
    # Download the installer
    urllib.request.urlretrieve(TESSERACT_DOWNLOAD_URL, installer_path)
    
    print("Installing Tesseract...")
    # Run the installer silently
    try:
        subprocess.run([installer_path, '/S'], check=True)
        print("Tesseract installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Tesseract: {e}")
        sys.exit(1)
    finally:
        # Clean up
        try:
            os.remove(installer_path)
        except:
            pass

def package_app():
    """
    Package the application using PyInstaller.
    
    This function handles the entire build process:
    1. Sets up build environment
    2. Cleans previous builds
    3. Configures PyInstaller
    4. Runs the build process
    
    The build process creates several directories:
    - build/: Contains intermediate files and analysis
    - dist/: Contains the final executable
    - resources/: Contains additional files to be bundled
    """
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Define paths for build artifacts
    dist_dir = current_dir / 'dist'      # Final executable location
    build_dir = current_dir / 'build'    # Intermediate build files
    
    # Clean previous builds to prevent conflicts
    try:
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not fully clean previous build: {e}")
    
    # Create resources directory for additional files
    resources_dir = current_dir / 'resources'
    resources_dir.mkdir(exist_ok=True)    # PyInstaller configuration
    args = [
        'src/main.py',         # Entry point script
        '--onefile',                     # Create single executable
        '--noconsole',                   # No console window for GUI app
        '--name', 'ScreenCaptureOCR',    # Output executable name
        '--hidden-import', 'PIL._tkinter_finder',  # Force include PIL GUI support
        '--add-data', f'resources;resources',      # Bundle additional resources
        '--version-file', 'src/version_info.txt',  # Add version info to executable
        '--uac-admin',                   # Request admin rights if needed
        '--clean'                        # Clean PyInstaller cache
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("Packaging complete! The executable is in the 'dist' folder.")

if __name__ == "__main__":
    package_app()
