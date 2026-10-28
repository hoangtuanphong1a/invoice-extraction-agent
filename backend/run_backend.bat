@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Chua tim thay venv. Dang tao venv moi...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo =========================================================
echo  Khoi chay Invoice Extraction Agent Backend (FastAPI)
echo  Moi truong: venv (Da duoc co lap sach se)
echo  Dia chi API: http://localhost:8000
echo  Swagger API Docs: http://localhost:8000/docs
echo =========================================================

python -m uvicorn app.main:app --reload --port 8000
pause
