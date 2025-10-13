@echo off
echo ========================================
echo  Iniciando Aplicacion de Privacidad
echo ========================================
echo.

echo [1/2] Iniciando Backend Python (puerto 5000)...
start "Backend Python" cmd /k "cd backend && venv\Scripts\activate && python app.py"

echo [INFO] Esperando 5 segundos para que el backend inicie...
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Iniciando Frontend Next.js (puerto 9002)...
start "Frontend Next.js" cmd /k "npm run dev"

echo.
echo ========================================
echo  Servidores iniciados correctamente
echo ========================================
echo.
echo  Backend Python:  http://localhost:5000
echo  Frontend Next.js: http://localhost:9002
echo.
echo  Abre tu navegador en: http://localhost:9002
echo.
echo  Para detener los servidores:
echo  - Presiona Ctrl+C en cada ventana
echo  - O cierra las ventanas de comando
echo.
pause
