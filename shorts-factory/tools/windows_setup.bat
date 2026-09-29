@echo off
rem One-time setup on Windows: Python, ffmpeg, Python packages, models/fonts/SFX.
cd /d "%~dp0\.."
where python >nul 2>nul || winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
where ffmpeg >nul 2>nul || winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
echo.
echo If Python or ffmpeg was just installed, close this window and run windows_setup.bat again (PATH refresh).
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install num2words
python tools\fetch_assets.py
echo.
echo Setup finished. Put your profile picture at assets\branding\avatar.png
pause
