# Cricbuzz LiveStats - PowerShell Startup Script
Write-Host "🏏 Cricbuzz LiveStats - PowerShell Startup" -ForegroundColor Green
Write-Host "=" * 50

# Check Python installation
Write-Host "`n🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Test MySQL connection
Write-Host "`n🔍 Testing MySQL connection..." -ForegroundColor Yellow
try {
    python -c "from config import DB_CONFIG; import mysql.connector; conn = mysql.connector.connect(**DB_CONFIG); print('MySQL connected!'); conn.close()"
    Write-Host "✅ MySQL connection successful!" -ForegroundColor Green
} catch {
    Write-Host "❌ MySQL connection failed!" -ForegroundColor Red
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Install MySQL Server" -ForegroundColor White
    Write-Host "2. Update credentials in config.py" -ForegroundColor White
    Write-Host "3. Ensure MySQL service is running" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}

# Start FastAPI backend
Write-Host "`n🚀 Starting FastAPI backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py"

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Streamlit frontend
Write-Host "`n🎨 Starting Streamlit frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run app.py"

# Open browser
Write-Host "`n🌐 Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:8501"

Write-Host "`n✅ Application started successfully!" -ForegroundColor Green
Write-Host "`n📱 Access the application at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
