# YouTube Video Downloader Setup Guide

## Option 1: Python Web Application (Recommended)

### Prerequisites
1. **Install Python 3.7 or higher:**
   - Go to https://python.org/downloads/
   - Download and install Python
   - **IMPORTANT**: During installation, check "Add Python to PATH"

2. **Verify Python Installation:**
   - Open Command Prompt or PowerShell
   - Type: `python --version`
   - You should see something like "Python 3.x.x"

### Installation Steps
1. **Easy Installation (Windows):**
   - Double-click `install.bat` to automatically install dependencies
   
2. **Manual Installation:**
   ```bash
   # Navigate to the project folder
   cd "c:\Users\hites\OneDrive\Desktop\tdownload"
   
   # Install dependencies
   python -m pip install -r requirements.txt
   ```

### Running the Application
1. **Easy Start (Windows):**
   - Double-click `start.bat`
   
2. **Manual Start:**
   ```bash
   python app.py
   ```

3. **Access the Application:**
   - Open your web browser
   - Go to: http://localhost:5000
   - Paste YouTube URLs and download!

---

## Option 2: Simple HTML Tool (No Installation Required)

If you don't want to install Python, I've also created a simple HTML file that you can use with online downloaders.

### Features of the Python Web App:
- ✅ Download videos in original quality
- ✅ Modern, beautiful web interface
- ✅ Progress tracking
- ✅ File management
- ✅ Works offline
- ✅ Privacy-focused (runs locally)

### Features of the HTML Tool:
- ✅ No installation required
- ✅ Works in any browser
- ✅ Links to reliable online downloaders
- ✅ Simple and fast

---

## Troubleshooting

### Python Not Found Error:
1. Install Python from https://python.org
2. Make sure to check "Add Python to PATH" during installation
3. Restart your computer after installation

### Permission Errors:
- Run Command Prompt as Administrator
- Try: `python -m pip install --user -r requirements.txt`

### Network Errors:
- Check your internet connection
- Some corporate networks block pip installs

### Video Download Fails:
- Ensure the YouTube URL is valid
- Some videos may be restricted
- Try a different video to test

---

## Legal Notice
Please respect YouTube's Terms of Service and copyright laws. Only download videos for personal use or when you have permission.
