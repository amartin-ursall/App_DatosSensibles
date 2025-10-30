@echo off
echo =========================================
echo  Desinstalacion de Servicio del Sistema
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

echo [ADVERTENCIA] Esta operacion eliminara el servicio del sistema
echo Presiona Ctrl+C para cancelar o
pause

echo.
echo [1/4] Deteniendo aplicaciones PM2...
call pm2 stop all
call pm2 delete all
call pm2 kill
echo OK - Aplicaciones detenidas
echo.

echo [2/4] Desinstalando servicio de Windows...
call pm2-service-uninstall
echo OK - Servicio desinstalado
echo.

echo [3/4] Limpiando configuracion PM2...
rmdir /s /q "%APPDATA%\.pm2" 2>nul
echo OK - Configuracion limpiada
echo.

echo [4/4] Verificando desinstalacion...
sc query PM2 >nul 2>&1
if %errorLevel% equ 0 (
    echo [ADVERTENCIA] El servicio PM2 aun existe
    echo Puede ser necesario reiniciar el sistema
) else (
    echo OK - Servicio completamente desinstalado
)
echo.

echo =========================================
echo  Desinstalacion Completada
echo =========================================
echo.
echo NOTA: PM2 y pm2-windows-service siguen instalados globalmente
echo Si deseas eliminarlos completamente, ejecuta:
echo   npm uninstall -g pm2 pm2-windows-service
echo.
pause
