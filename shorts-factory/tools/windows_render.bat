@echo off
rem Render every script in scripts\ straight into your Downloads folder.
cd /d "%~dp0\.."
python make_short.py scripts\*.json --out "%USERPROFILE%\Downloads"
pause
