@echo off
echo ========================================
echo   GREEN VISION - Quick Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo   SETUP COMPLETED!
echo ========================================
echo.
echo Next steps:
echo 1. Create admin user: python manage.py createsuperuser
echo 2. Run server: run_server.bat
echo.
pause
