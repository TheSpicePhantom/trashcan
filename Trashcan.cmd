@echo off
setlocal
cd /d "%~dp0"
pythonw "%~dp0trashcan.py" %*
if errorlevel 1 (
  python "%~dp0trashcan.py" %*
)
endlocal