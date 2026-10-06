@echo off
cd /d "%~dp0"

start "FastAPI Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn api:app --reload"

cd /d "%~dp0frontend"
start "React Frontend" cmd /k "npm run dev"

timeout /t 8 /nobreak >nul
start http://localhost:5173

exit