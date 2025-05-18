# Screen Capture OCR Tool

A powerful and easy-to-use tool that lets you extract text from any part of your screen with a simple keyboard shortcut. Just press the hotkey, select an area, and the text will be automatically copied to your clipboard.

## Features

- 🎯 Simple selection interface with semi-transparent overlay
- ⌨️ Quick access with hotkey (Ctrl+Shift+X)
- 📋 Automatic text copying to clipboard
- 🚀 High-performance OCR using Tesseract
- 🔄 Automatic Tesseract installation if needed
- ❌ Press Esc to cancel a capture

## Installation

### Option 1: Using the Executable (Recommended)

1. Download the latest release (`ScreenCaptureOCR.exe`)
2. Double-click to run the application
3. If Tesseract OCR is not installed, the application will offer to download and install it automatically

### Option 2: From Source

1. Clone this repository
2. Install Python 3.8 or higher
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

1. Start the application
2. Press `Ctrl+Shift+X` to activate screen capture mode
3. Click and drag to select the area containing text
4. The text will be automatically copied to your clipboard
5. A notification will confirm when text has been copied

## Code Structure

The codebase is modular and organized as follows:

- `src/main.py` — Entry point, launches the dashboard
- `src/dashboard.py` — Dashboard UI, hotkey logic, launches the overlay
- `src/capture_overlay.py` — Overlay, selection, OCR, and clipboard logic
- `src/ocr_utils.py` — Tesseract detection, installation, and pytesseract setup
- `src/config.py` — Color schemes, hotkey, and other constants

## Building from Source

To create your own executable:

1. Install requirements:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. Run the packaging script:
   ```bash
   python package.py
   ```

3. Find the executable in the `dist` folder

## Troubleshooting

- If the application doesn't start, try running it as administrator
- If text recognition seems inaccurate:
  - Make sure the text is clear and well-lit
  - Try selecting a slightly larger area around the text
  - Check if your screen scaling is set to 100%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
