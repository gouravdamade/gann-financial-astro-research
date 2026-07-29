@echo off
setlocal
cd /d "%~dp0"
python jhora_kaala_capture_assistant.py --gui
if errorlevel 1 (
  echo.
  echo The capture assistant could not start.
  pause
)
endlocal
