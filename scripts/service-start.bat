@echo off
echo =========================================
echo  Iniciando Servicio - App Datos Sensibles
echo =========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0\.."

echo [1/4] Verificando entorno virtual de Python...
if not exist "backend\venv" (
    echo [INFO] Creando entorno virtual de Python...
    py -m venv backend\venv
    if %errorLevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)
echo OK - Entorno virtual verificado
echo.

echo [2/4] Instalando dependencias de Python...
call backend\venv\Scripts\pip install -r backend\requirements.txt >nul 2>&1
echo OK - Dependencias de Python instaladas
echo.

echo [3/4] Instalando dependencias de Node.js...
if not exist "node_modules" (
    echo Instalando paquetes de Node.js (esto puede tardar)...
    call npm install
    if %errorLevel% neq 0 (
        echo [ERROR] No se pudieron instalar las dependencias de Node.js
        pause
        exit /b 1
    )
) else (
    echo OK - Dependencias ya instaladas
)
echo.

echo [4/4] Creando directorio de logs...
if not exist "logs" mkdir logs
echo OK - Directorio de logs creado
echo.

echo Iniciando aplicaciones con PM2...
call pm2 delete all >nul 2>&1
call pm2 start ecosystem.config.js
if %errorLevel% neq 0 (
    echo [ERROR] No se pudieron iniciar las aplicaciones
    pause
    exit /b 1
)
echo.

echo Guardando configuracion de PM2...
call pm2 save
echo.

echo =========================================
echo  Servicio Iniciado Correctamente
echo =========================================
echo.
echo Estado de los servicios:
call pm2 status
echo.
echo URLs de acceso:
echo  - Frontend: http://localhost:3030
echo  - Backend:  http://localhost:5000
echo  - Health:   http://localhost:5000/health
echo.
echo Para ver logs en tiempo real: pm2 logs
echo Para ver el estado: service-status.bat
echo Para detener: service-stop.bat
echo.
pause
