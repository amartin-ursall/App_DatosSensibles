@echo off
echo ========================================
echo Añadiendo Python al PATH del sistema
echo ========================================
echo.

REM Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Este script debe ejecutarse como Administrador
    echo.
    echo Haz clic derecho en el archivo y selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

REM Obtener la ruta de Python
set PYTHON_PATH=C:\Users\amartin\AppData\Local\Microsoft\WindowsApps

echo Ruta de Python detectada: %PYTHON_PATH%
echo.

REM Agregar Python al PATH del sistema
echo Agregando Python al PATH del sistema...
setx /M PATH "%PATH%;%PYTHON_PATH%" >nul 2>&1

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo Python se ha añadido correctamente al PATH
    echo ========================================
    echo.
    echo IMPORTANTE: Debes cerrar y volver a abrir tu terminal
    echo para que los cambios surtan efecto.
    echo.
) else (
    echo.
    echo ERROR: No se pudo agregar Python al PATH
    echo Verifica que tienes permisos de administrador
    echo.
)

pause
