@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  set "OCR_PYTHON=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python is required. Install Python 3.12 or newer, then run this file again.
    pause
    exit /b 1
  )
  set "OCR_PYTHON=python"
)
echo Starting the local OCR viewer. Keep this window open.
start "" "http://127.0.0.1:8000/LOCAL_HOME.html"
%OCR_PYTHON% -m http.server 8000 --bind 127.0.0.1
pause
