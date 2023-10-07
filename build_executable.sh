#!/bin/bash

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
  echo "PyInstaller is not installed. You can install it using 'pip install pyinstaller'."
  exit 1
fi

# Source file / directory
SOURCE="./main.py"

# Output directory
OUTPUT_DIR="./dist"

# Output program name
OUTPUT_NAME="DiscordChatExporter-MediaDownloader"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Use PyInstaller to build the executable
pyinstaller \
  --onefile \
  --name "$OUTPUT_NAME" \
  --distpath "$OUTPUT_DIR" \
  --workpath "$OUTPUT_DIR/tmp" \
  --specpath "$OUTPUT_DIR/tmp" \
  --clean \
  "$SOURCE"

# Check if PyInstaller successfully created the executable
if [ $? -eq 0 ]; then
  echo "Build successful. Your executable file is located in $OUTPUT_DIR."
else
  echo "Build failed."
fi
