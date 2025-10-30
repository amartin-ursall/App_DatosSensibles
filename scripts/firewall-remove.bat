@echo off
REM ========================================
REM Script para eliminar reglas de Firewall
REM App Datos Sensibles
REM ========================================
REM
REM IMPORTANTE: Este script debe ejecutarse como ADMINISTRADOR
REM

echo.
echo ========================================
echo  Eliminando Reglas de Firewall
echo  App Datos Sensibles
echo ========================================
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Este script requiere permisos de administrador
    echo.
    echo Por favor:
    echo 1. Click derecho en este archivo
    echo 2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo [INFO] Eliminando todas las reglas de firewall...
echo.

netsh advfirewall firewall delete rule name="App Datos Sensibles - Frontend"
netsh advfirewall firewall delete rule name="App Datos Sensibles - Backend"
netsh advfirewall firewall delete rule name="App Datos Sensibles - Node.js"
netsh advfirewall firewall delete rule name="App Datos Sensibles - Python"

echo.
echo ========================================
echo  Reglas de Firewall Eliminadas
echo ========================================
echo.
echo La aplicacion ya no es accesible desde la red local
echo Para volver a habilitar, ejecuta: firewall-config.bat
echo.
pause
