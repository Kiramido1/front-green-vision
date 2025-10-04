@echo off
echo ========================================
echo   GREEN VISION - Starting Server
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo Please create one with: python -m venv venv
    pause
    exit /b 1
)

echo.
echo Starting Django development server...
echo.
echo Visit: http://127.0.0.1:8000/
echo Admin: http://127.0.0.1:8000/admin/
echo.
echo Press CTRL+C to stop the server
echo.

python manage.py runserver

pause
