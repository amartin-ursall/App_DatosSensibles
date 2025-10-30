@echo off
REM ========================================
REM Script de detención - App Datos Sensibles
REM ========================================

echo.
echo ========================================
echo  Deteniendo Aplicacion de Privacidad
echo ========================================
echo.

REM Matar procesos de Node.js en puerto 3030
echo [1/3] Deteniendo Frontend Next.js (puerto 3030)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3030 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [OK] Frontend detenido (PID: %%a^)
    )
)

REM Matar procesos de Python en puerto 5000
echo [2/3] Deteniendo Backend Python (puerto 5000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [OK] Backend detenido (PID: %%a^)
    )
)

REM Cerrar ventanas de comando con títulos específicos
echo [3/3] Cerrando ventanas de comando...
taskkill /FI "WINDOWTITLE eq Backend Python - App Datos Sensibles*" >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend Next.js - App Datos Sensibles*" >nul 2>&1

echo.
echo ========================================
echo  Servidores detenidos correctamente
echo ========================================
echo.
pause
