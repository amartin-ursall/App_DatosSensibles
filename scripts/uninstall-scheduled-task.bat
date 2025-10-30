@echo off
REM =========================================
REM Desinstalar Tarea Programada de Windows
REM App Datos Sensibles
REM =========================================

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Este script requiere permisos de administrador
    echo.
    echo Por favor:
    echo   1. Click derecho en este archivo
    echo   2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo =========================================
echo  Desinstalando Tarea Programada
echo  App Datos Sensibles
echo =========================================
echo.

set TASK_NAME=App_DatosSensibles

echo Eliminando tarea programada: %TASK_NAME%...
schtasks /Delete /TN "%TASK_NAME%" /F

if %errorLevel% equ 0 (
    echo.
    echo =========================================
    echo  Tarea Programada Desinstalada
    echo =========================================
    echo.
    echo La aplicacion ya NO se iniciara automaticamente con Windows.
    echo.
    echo Nota: PM2 sigue instalado. Para iniciar manualmente usa:
    echo   - scripts\start-silent.vbs (sin ventanas)
    echo   - scripts\service-start.bat (con ventanas)
    echo.
) else (
    echo.
    echo [ADVERTENCIA] No se encontro la tarea o ya estaba desinstalada.
    echo.
)

pause
