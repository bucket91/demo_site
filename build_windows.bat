@echo off
REM Build Site Tools for Windows
python build.py
if %ERRORLEVEL% neq 0 (
    echo Build failed. Make sure Python 3 is installed and on PATH.
    pause
)
