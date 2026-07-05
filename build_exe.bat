@echo off
REM Builds a standalone FluidVoiceWin.exe using PyInstaller.
REM Run this from a Windows machine with Python 3.10+ installed.

pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onefile --noconsole --name FluidVoiceWin main.py

echo.
echo Build complete. Find FluidVoiceWin.exe in the dist\ folder.
pause
