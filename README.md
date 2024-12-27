# screenshot-renamer
# Screenshot Auto Rename Tool
This is a tool that automatically monitors, renames and organizes screenshots. It automatically recognizes text in screenshots and uses AI to generate appropriate file names.

## Features
1. Automatically monitor desktop for new screenshots
2. Recognize image text using OCR
3. Call AI to generate smart file names
4. Automatically move files to specified folders
5. Support Chinese and English recognition
6. Automatically handle file name conflicts

## Install dependencies
```bash
pip install -r requirements.txt
``

## How to use it
1. Make sure all dependencies are installed
2. Run the program:
   ```bash
   python screenshot_renamer.py
   ```
3. The program will automatically monitor the desktop for new screenshots.
4. Take a screenshot using the system's own screenshot tool.
5. The program will automatically process the new screenshot file.
6. The processed files are moved to the desktop's “Screenshots” folder.

## 1. You need to set a valid API Key.

1. You need to set a valid API Key.
2. Make sure the desktop path is correct.
3. Please keep the internet connection while the program is running. 4.
4. Press Ctrl+C to stop the program.

## Dependencies

- openai: AI interface call
- Pillow: image processing
- watchdog: File system monitoring
- easyocr: OCR Text Recognition 
