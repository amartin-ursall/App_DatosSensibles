@echo off
echo =========================================
echo  Instalacion de Servicio del Sistema
echo  App Datos Sensibles
echo =========================================
echo.

REM Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este script requiere permisos de administrador
    echo Por favor, ejecuta como administrador: Click derecho -> Ejecutar como administrador
    pause
    exit /b 1
)

echo [1/5] Verificando Node.js...
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Descarga e instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo OK - Node.js encontrado
echo.

echo [2/5] Instalando PM2 globalmente...
call npm install -g pm2
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo instalar PM2
    pause
    exit /b 1
)
echo OK - PM2 instalado
echo.

echo [3/5] Instalando pm2-windows-service...
call npm install -g pm2-windows-service
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo instalar pm2-windows-service
    pause
    exit /b 1
)
echo OK - pm2-windows-service instalado
echo.

echo [4/5] Configurando PM2 como servicio de Windows...
echo Se abrira un asistente interactivo. Usa los siguientes valores:
echo - Service name: PM2-DatosSensibles
echo - PM2 runtime: %APPDATA%\npm\node_modules\pm2\index.js
echo.
pause
call pm2-service-install
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo configurar el servicio
    pause
    exit /b 1
)
echo OK - Servicio configurado
echo.

echo [5/5] Verificando instalacion...
sc query PM2 >nul 2>&1
if %errorLevel% equ 0 (
    echo OK - Servicio PM2 instalado correctamente
) else (
    echo [ADVERTENCIA] No se pudo verificar el servicio
    echo Revisa la configuracion manualmente
)
echo.

echo =========================================
echo  Instalacion Completada
echo =========================================
echo.
echo Proximo paso: Ejecuta 'service-start.bat' para iniciar los servicios
echo.
pause
