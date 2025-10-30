@echo off
REM ========================================
REM Script de estado - App Datos Sensibles
REM ========================================

echo.
echo ========================================
echo  Estado de Aplicacion de Privacidad
echo ========================================
echo.

REM Verificar Frontend (puerto 3030)
echo [Frontend Next.js - Puerto 3030]
netstat -ano | findstr :3030 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Estado: [ACTIVO]
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3030 ^| findstr LISTENING') do (
        echo PID: %%a
        for /f "tokens=1" %%b in ('tasklist /FI "PID eq %%a" /FO LIST ^| findstr /B "Image"') do (
            echo Proceso: %%b
        )
    )
    echo URL Local: http://localhost:3030
    echo URL Red: http://%COMPUTERNAME%:3030
) else (
    echo Estado: [INACTIVO]
)

echo.
echo [Backend Python - Puerto 5000]
netstat -ano | findstr :5000 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Estado: [ACTIVO]
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
        echo PID: %%a
        for /f "tokens=1" %%b in ('tasklist /FI "PID eq %%a" /FO LIST ^| findstr /B "Image"') do (
            echo Proceso: %%b
        )
    )
    echo URL Local: http://localhost:5000
    echo URL Red: http://%COMPUTERNAME%:5000
    echo.
    echo [Verificando salud del backend...]
    curl -s http://localhost:5000/health >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Health Check: [OK]
        curl -s http://localhost:5000/health
    ) else (
        echo Health Check: [ERROR]
    )
) else (
    echo Estado: [INACTIVO]
)

echo.
echo ========================================
echo  Informacion del Sistema
echo ========================================
echo.
echo IP del equipo:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do echo  - http://%%a:3030 (Frontend)

echo.
echo ========================================
echo.
pause
