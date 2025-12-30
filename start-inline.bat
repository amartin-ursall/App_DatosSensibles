@echo off
REM ========================================
REM Script de inicio inline - App Datos Sensibles
REM ========================================

echo.
echo ========================================
echo  Iniciando Aplicacion de Privacidad
echo ========================================
echo.

REM Iniciar backend en background
echo [1/2] Iniciando Backend Python (puerto 5000)...
cd backend
start /B cmd /c "venv\Scripts\activate.bat && python app.py > ..\logs\backend.log 2>&1"
cd ..

echo [INFO] Esperando 8 segundos para que el backend inicie...
timeout /t 8 /nobreak > nul

REM Iniciar frontend
echo [2/2] Iniciando Frontend Next.js (puerto 3030)...
start /B cmd /c "npm run dev > logs\frontend.log 2>&1"

echo.
echo ========================================
echo  Servidores iniciados correctamente
echo ========================================
echo.
echo  Backend Python:   http://localhost:5000
echo  Frontend Next.js: http://localhost:3030
echo.
echo  Para ver los logs:
echo    - Backend:  type logs\backend.log
echo    - Frontend: type logs\frontend.log
echo.
echo  Para detener: ejecuta scripts\stop.bat
echo.
