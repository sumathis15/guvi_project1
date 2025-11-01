@echo off
echo 🏏 Cricbuzz LiveStats - Windows Startup Script
echo ================================================

echo.
echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo.
echo 🔍 Checking dependencies...
pip install -r requirements.txt

echo.
echo 🔍 Testing MySQL connection...
python -c "from config import DB_CONFIG; import mysql.connector; conn = mysql.connector.connect(**DB_CONFIG); print('MySQL connected!'); conn.close()" 2>nul
if %errorlevel% neq 0 (
    echo ❌ MySQL connection failed!
    echo Please:
    echo 1. Install MySQL Server
    echo 2. Update credentials in config.py
    echo 3. Ensure MySQL service is running
    pause
    exit /b 1
)

echo.
echo 🚀 Starting FastAPI backend...
start "FastAPI Backend" cmd /k "python main.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo 🎨 Starting Streamlit frontend...
start "Streamlit Frontend" cmd /k "streamlit run app.py"

echo.
echo ✅ Application started!
echo.
echo 📱 Access the application at:
echo    Frontend: http://localhost:8501
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
