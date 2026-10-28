@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat

echo =========================================================
echo  Chay bo kiem thu hoi quy 24 Tests bang Pytest (trong venv)
echo =========================================================

python -m pytest tests -v
pause
