# ==============================================================================
# One-Click Launch Script: AI-Based Smart Allocation Engine for PM Internship Scheme
# Windows 11 PowerShell Automation
# ==============================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  AI-Based Smart Allocation Engine for PM Internship Scheme" -ForegroundColor Yellow
Write-Host "  Academic Prototype Launcher (B.Tech Final Year Evaluation)" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_DIR = Join-Path $ROOT_DIR "backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "frontend"

# Check Python virtual environment
$VENV_PYTHON = Join-Path $BACKEND_DIR "venv\Scripts\python.exe"
if (-Not (Test-Path $VENV_PYTHON)) {
    Write-Host "[1/3] Creating Python virtual environment in backend/venv..." -ForegroundColor Yellow
    python -m venv (Join-Path $BACKEND_DIR "venv")
    & $VENV_PYTHON -m pip install --upgrade pip
    & $VENV_PYTHON -m pip install -r (Join-Path $BACKEND_DIR "requirements.txt")
} else {
    Write-Host "[1/3] Backend virtual environment verified." -ForegroundColor Green
}

# Ensure database tables and demo seed data exist
Write-Host "[2/3] Verifying database schema and seeding demo scenario..." -ForegroundColor Yellow
Set-Location $BACKEND_DIR
& $VENV_PYTHON seed_demo_data.py

# Launch Backend in new window
Write-Host "[3/3] Launching FastAPI Backend (Port 8000)..." -ForegroundColor Green
$BACKEND_PY = if (Test-Path $VENV_PYTHON) { $VENV_PYTHON } else { (Get-Command python).Source }
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "cd '$BACKEND_DIR'; & '$BACKEND_PY' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

# Launch Frontend in new window
Write-Host "Launching Vite React Frontend (Port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "cd '$FRONTEND_DIR'; cmd.exe /c 'npm.cmd run dev'"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  PLATFORM IS READY FOR DEMONSTRATION!" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Frontend URL:     http://localhost:5173" -ForegroundColor White
Write-Host "  Backend Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Pre-Seeded Demo Credentials:" -ForegroundColor Yellow
Write-Host "    Admin:   admin@pm-internship.edu.in   / AdminSecurePass@2026" -ForegroundColor Cyan
Write-Host "    Student: rahul.sharma@pm-internship.edu.in / StudentPass@2026" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
