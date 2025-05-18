# Build Process Documentation

## Overview
The build process for ScreenCaptureOCR uses PyInstaller to create a standalone executable. This document explains the build process and the generated artifacts.

## Build Directory Structure
```
build/
└── ScreenCaptureOCR/
    ├── Analysis-00.toc      # Contains information about all analyzed modules
    ├── base_library.zip     # Basic Python libraries needed for the executable
    ├── EXE-00.toc          # Specifications for the final executable
    ├── PKG-00.toc          # Package configuration information
    ├── PYZ-00.pyz          # Compressed Python modules
    ├── PYZ-00.toc          # Table of contents for PYZ archive
    ├── ScreenCaptureOCR.pkg # The packaged application
    ├── warn-ScreenCaptureOCR.txt  # Build warnings if any
    ├── xref-ScreenCaptureOCR.html # Cross-reference of modules
    └── localpycs/          # Compiled Python files
        ├── pyimod01_archive.pyc   # PyInstaller bootstrap modules
        ├── pyimod02_importers.pyc
        ├── pyimod03_ctypes.pyc
        ├── pyimod04_pywin32.pyc
        └── struct.pyc
```

## Build Process Steps

1. **Cleanup**
   - Removes previous build and dist directories
   - Ensures a clean build environment

2. **Analysis Phase**
   - PyInstaller analyzes the application (`Analysis-00.toc`)
   - Determines all dependencies and required modules
   - Creates a dependency graph

3. **Collection Phase**
   - Gathers all required files (`PKG-00.toc`)
   - Copies necessary DLLs and binaries
   - Bundles Python standard library modules

4. **Python Archive Creation**
   - Creates `PYZ-00.pyz` containing compressed Python modules
   - Optimizes for size and load time

5. **Executable Creation**
   - Generates the final executable (`EXE-00.toc`)
   - Bundles everything into a single file

## Key Files Explained

### Analysis-00.toc
- Contains the complete dependency analysis
- Lists all Python modules needed
- Maps import statements to file locations

### base_library.zip
- Contains essential Python standard library modules
- Minimized to include only necessary components
- Optimized for size and performance

### PYZ-00.pyz
- Compressed archive of Python modules
- Contains all your application code
- Includes third-party dependencies

### localpycs/
- Contains compiled PyInstaller bootstrap code
- Handles unpacking and running the application
- Manages module imports at runtime

### warn-ScreenCaptureOCR.txt
- Lists any warnings encountered during build
- Important for debugging missing imports
- Shows compatibility issues if any

### xref-ScreenCaptureOCR.html
- Cross-reference documentation
- Shows module dependencies
- Useful for debugging import issues

## Building the Application

The build process is automated through `package.py` and can be run using:

```bash
python package.py
```

Or using the build script:

```bash
./build.sh
```

## Build Configuration

The build is configured in `package.py` with these key options:

- `--onefile`: Creates a single executable
- `--noconsole`: Hides the console window for GUI app
- `--name ScreenCaptureOCR`: Sets the output executable name
- `--clean`: Ensures a clean build environment
- `--uac-admin`: Requests admin rights if needed
- `--version-file`: Adds version information to the executable

## User Interface

The application features a modern, dark-themed interface with:

### Main Dashboard
- Professional dark theme (#1e1e1e background)
- Modern typography using Segoe UI font
- Clear visual hierarchy with title and subtitle
- Elegant button styling with hover effects
- Status indicators with color coding

### Components
- Instructions panel with dark background
- Custom-styled notification toggle
- Start/Stop buttons with visual feedback
- Status indicator showing current state
- Professional spacing and padding throughout

### Capture Interface
- Semi-transparent fullscreen overlay
- Real-time selection rectangle
- Cross cursor for precise selection
- Escape key to cancel operation

## Project Structure

```
src/
├── screen_capture.py    # Main application code
└── version_info.txt     # Version information for executable

resources/              # Additional resources
├── icons/             # Application icons
└── docs/              # Additional documentation

build/                 # Build artifacts
└── ScreenCaptureOCR/  # PyInstaller output

dist/                  # Final executable
```
- `--noconsole`: Hides the console window
- `--hidden-import`: Ensures all dependencies are included
- `--add-data`: Bundles additional resources

## Troubleshooting

1. **Missing Modules**
   - Check `warn-ScreenCaptureOCR.txt` for import errors
   - Add missing imports to `--hidden-import`

2. **DLL Issues**
   - Look for DLL warnings in build output
   - Ensure all required DLLs are in PATH

3. **Size Issues**
   - Review `Analysis-00.toc` for unnecessary imports
   - Use `--exclude-module` to remove unused modules

## Best Practices

1. Always clean build directories before rebuilding
2. Review warning files for potential issues
3. Test the executable in a clean environment
4. Keep track of dependencies in requirements.txt

## Notes

- The build process is deterministic - same input produces same output
- Build artifacts are platform-specific
- The build directory can be safely deleted after distribution
