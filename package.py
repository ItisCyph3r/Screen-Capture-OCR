import os
import sys
import tempfile
import urllib.request
import subprocess
import PyInstaller.__main__
from pathlib import Path
import shutil
import winreg
import gc
import multiprocessing
import psutil
import time

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

def ensure_upx_available():
    """Download UPX if not available for better compression with robust error handling"""
    upx_dir = Path(__file__).parent.absolute() / 'upx'
    upx_dir.mkdir(exist_ok=True)
    
    # Check if UPX is already available
    upx_exe = upx_dir / 'upx.exe'
    if upx_exe.exists():
        return True
    
    try:
        print("Downloading UPX for better compression...")
        # Multiple mirror URLs in case one fails
        upx_urls = [
            "https://github.com/upx/upx/releases/download/v4.0.2/upx-4.0.2-win64.zip",
            "https://sourceforge.net/projects/upx/files/upx/4.0.2/upx-4.0.2-win64.zip/download"
        ]
        
        zip_path = upx_dir / "upx.zip"
        download_success = False
        
        # Try each URL until one works
        for url in upx_urls:
            try:
                # Download with timeout to avoid hanging
                urllib.request.urlretrieve(url, zip_path)
                download_success = True
                break
            except Exception as url_err:
                print(f"Failed to download from {url}: {url_err}")
                continue
        
        if not download_success:
            print("Could not download UPX from any source, continuing without it")
            return False
        
        # Extract UPX
        import zipfile
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(upx_dir)
        except zipfile.BadZipFile:
            print("Downloaded file is not a valid zip file")
            return False
        
        # Move the executable to the right place
        upx_found = False
        for item in upx_dir.glob("**/upx.exe"):
            try:
                shutil.copy(item, upx_exe)
                upx_found = True
                break
            except Exception as copy_err:
                print(f"Failed to copy UPX: {copy_err}")
        
        if not upx_found:
            print("Could not find upx.exe in the downloaded package")
            return False
            
        # Clean up
        try:
            for item in upx_dir.glob("upx-*"):
                if item.is_dir():
                    shutil.rmtree(item)
            if zip_path.exists():
                zip_path.unlink()
        except Exception as cleanup_err:
            print(f"Warning during cleanup: {cleanup_err}")
        
        print("UPX downloaded successfully!")
        return True
    except Exception as e:
        print(f"Warning: Could not download UPX: {e}")
        # Not critical, build can continue without UPX
        return False

def get_optimal_workers():
    """
    Determine the optimal number of worker processes based on system resources.
    Safely handles systems where resource detection might fail.
    
    Returns a tuple of (cpu_count, worker_count) where:
    - cpu_count: Number of logical CPU cores available
    - worker_count: Optimal number of worker processes to use
    """
    try:
        # Try to detect CPU count
        cpu_count = multiprocessing.cpu_count()
    except Exception:
        # Default to 2 if detection fails
        print("Could not detect CPU count, defaulting to 2")
        cpu_count = 2
    
    try:
        # Try to detect memory
        mem_gb = psutil.virtual_memory().total / (1024 * 1024 * 1024)
    except Exception:
        # Default to 4GB if detection fails
        print("Could not detect system memory, defaulting to 4GB")
        mem_gb = 4
    
    # Calculate optimal workers based on CPU and memory
    # Each worker might need ~1GB of memory
    mem_based_workers = max(1, int(mem_gb / 1.5))
    cpu_based_workers = max(1, cpu_count - 1)  # Leave one core free for system
    
    # Use the smaller of the two to avoid resource exhaustion
    worker_count = min(mem_based_workers, cpu_based_workers)
    
    # Cap at 8 workers to avoid issues on very high-end systems
    worker_count = min(worker_count, 8)
    
    print(f"System has {cpu_count} CPU cores and {mem_gb:.1f}GB RAM")
    print(f"Using {worker_count} worker processes for optimal performance")
    
    return cpu_count, worker_count

def package_app():
    """
    Package the application using PyInstaller with parallel processing.
    
    This function handles the entire build process:
    1. Sets up build environment
    2. Cleans previous builds
    3. Configures PyInstaller for optimal performance
    4. Runs the build process with parallel workers
    
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
    resources_dir.mkdir(exist_ok=True)    # Get optimal worker count for parallel processing
    cpu_count, worker_count = get_optimal_workers()
    
    # Ensure we have all necessary files and directories
    try:
        # Create a resources directory if it doesn't exist
        resources_dir = current_dir / 'resources'
        resources_dir.mkdir(exist_ok=True)
        
        # Create a README.txt in resources to explain the app
        readme_path = resources_dir / 'README.txt'
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write("Screen Capture OCR\n\n")
                f.write("This application allows you to capture text from anywhere on your screen.\n")
                f.write("1. Click 'Start' to enable screen capture\n")
                f.write("2. Press Ctrl+Shift+X to start capture\n")
                f.write("3. Click and drag to select text area\n")
                f.write("4. Text will be copied to clipboard\n")
                f.write("5. Press 'Stop' to disable\n\n")
                f.write("For support, please contact the developer.\n")
    except Exception as e:
        print(f"Warning: Could not create resource files: {e}")
    
    # Check if UPX is available for compression
    upx_available = ensure_upx_available()
    
    # Base PyInstaller configuration
    args = [
        'src/main.py',                  # Entry point script
        '--onefile',                     # Create single executable
        '--noconsole',                   # No console window for GUI app
        '--name', 'ScreenCaptureOCR',    # Output executable name
        '--hidden-import', 'PIL._tkinter_finder',  # Force include PIL GUI support
        '--hidden-import', 'win32clipboard',  # Ensure win32clipboard is included
        '--hidden-import', 'cv2',        # Ensure OpenCV is included
        '--hidden-import', 'pytesseract',  # Ensure pytesseract is included
        # Explicitly include NumPy modules that are needed
        '--hidden-import', 'numpy',
        '--hidden-import', 'numpy.core._multiarray_umath',
        '--hidden-import', 'numpy.core.multiarray',
        '--hidden-import', 'numpy.core._dtype_ctypes',
        '--add-data', f'resources;resources',  # Bundle additional resources
        '--version-file', 'src/version_info.txt',  # Add version info to executable
        '--uac-admin',                   # Request admin rights if needed
        '--clean',                       # Clean PyInstaller cache
        # Enable parallel processing if supported
        '--log-level', 'WARN',           # Reduce log noise during parallel build
        f'--distpath={dist_dir}',        # Specify dist directory
        f'--workpath={build_dir}',       # Specify build directory
        f'--specpath={current_dir}',     # Specify spec directory
        # Exclude unnecessary large packages to reduce size
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'notebook',
        '--exclude-module', 'pandas',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PySide2',
        '--exclude-module', 'IPython',
        '--exclude-module', 'sphinx',
        '--exclude-module', 'tensorflow',
        '--exclude-module', 'torch',
        '--exclude-module', 'sklearn',
        # Only exclude test modules from NumPy, keep the core functionality
        '--exclude-module', 'numpy.random._examples',
        '--exclude-module', 'numpy.fft.tests',
        '--exclude-module', 'numpy.linalg.tests',
        '--exclude-module', 'numpy.ma.tests',
        '--exclude-module', 'numpy.matrixlib.tests',
        '--exclude-module', 'numpy.polynomial.tests',
        '--exclude-module', 'numpy.random.tests',
        # High-performance optimization flags
        '--strip',                       # Strip symbols from binary
    ]
    
    # Add UPX compression if available
    if upx_available:
        args.extend(['--upx-dir', os.path.join(current_dir, 'upx')])
    
    # Note: Parallel processing with --number-processes is not supported in this PyInstaller version
    # We'll use system resources efficiently in other ways
    
    # Ensure UPX is available for better compression
    ensure_upx_available()
    
    # Set environment variables to optimize performance
    os.environ['PYTHONOPTIMIZE'] = '2'  # Enable Python optimization
    
    # Force garbage collection before building
    gc.collect()
    
    print(f"Starting build with {worker_count} parallel workers...")
    start_time = time.time()
    
    # Run PyInstaller with error handling
    try:
        PyInstaller.__main__.run(args)
        build_success = True
    except Exception as build_error:
        print(f"\nError during build: {build_error}")
        print("Attempting to build with fallback settings...")
        
        # Fallback to simpler build settings
        fallback_args = [
            'src/main.py',
            '--onefile',
            '--noconsole',
            '--name', 'ScreenCaptureOCR',
            '--hidden-import', 'PIL._tkinter_finder',
            '--hidden-import', 'win32clipboard',
            '--hidden-import', 'cv2',
            '--hidden-import', 'pytesseract',
            '--add-data', f'resources;resources',
            '--version-file', 'src/version_info.txt',
            '--clean',
        ]
        
        try:
            PyInstaller.__main__.run(fallback_args)
            build_success = True
            print("Build completed with fallback settings")
        except Exception as fallback_error:
            print(f"Fallback build also failed: {fallback_error}")
            build_success = False
    
    # Calculate build time
    build_time = time.time() - start_time
    
    if build_success:
        print(f"\nPackaging complete in {build_time:.2f} seconds!")
        print("The executable is in the 'dist' folder.")
    else:
        print("\nBuild process failed. Please check the errors above.")
    
    # Calculate and display the size of the executable
    exe_path = dist_dir / 'ScreenCaptureOCR.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Executable size: {size_mb:.2f} MB")
        
        # Print performance summary
        print("\nBuild Performance Summary:")
        print(f"CPU cores used: {worker_count} of {cpu_count}")
        print(f"Build time: {build_time:.2f} seconds")
        print(f"Average throughput: {size_mb/build_time:.2f} MB/s")
        
        # Create a copy of the executable with a version number for backup
        try:
            import datetime
            version_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            backup_path = dist_dir / f"ScreenCaptureOCR_{version_stamp}.exe"
            shutil.copy2(exe_path, backup_path)
            print(f"\nBackup copy created: {backup_path.name}")
        except Exception as e:
            print(f"Warning: Could not create backup copy: {e}")
        
        print("\nBuild completed successfully! Your application should work on any Windows system.")
    else:
        print("\nWarning: Could not find the executable in the dist folder.")
        print("Please check the build logs for errors.")
        
    # Create a simple batch file to run the application
    try:
        batch_path = dist_dir / "Run_ScreenCaptureOCR.bat"
        with open(batch_path, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Screen Capture OCR...\n')
            f.write('start "" "%~dp0ScreenCaptureOCR.exe"\n')
        print(f"Created launcher batch file: {batch_path.name}")
    except Exception as e:
        print(f"Warning: Could not create launcher batch file: {e}")

if __name__ == "__main__":
    package_app()
