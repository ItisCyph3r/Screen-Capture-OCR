#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/Scripts/activate
fi

# Install requirements
echo "Installing requirements..."
python -m pip install -r requirements.txt

# Run the packaging script
echo "Packaging the application..."
python package.py

# Check if packaging was successful
if [ -f "dist/ScreenCaptureOCR.exe" ]; then
    echo "Build successful! The executable is in the dist folder."
    echo "You can now distribute ScreenCaptureOCR.exe"
else
    echo "Build failed! Check the error messages above."
fi
