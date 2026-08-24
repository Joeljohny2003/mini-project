@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Creating the Python virtual environment...
    py -m venv "%PROJECT_DIR%venv"
    if errorlevel 1 (
        echo Could not create the virtual environment. Install Python and try again.
        exit /b 1
    )
)

echo Installing or updating project dependencies...
"%PYTHON%" -m pip install -r "%PROJECT_DIR%requirements.txt"
if errorlevel 1 exit /b 1

cd /d "%PROJECT_DIR%"
"%PYTHON%" manage.py migrate
if errorlevel 1 exit /b 1

echo Starting Thrift Store at http://127.0.0.1:8000/
"%PYTHON%" manage.py runserver %*