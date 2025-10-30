@echo off
REM =========================================
REM Instalar Tarea Programada de Windows
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
echo  Instalando Tarea Programada
echo  App Datos Sensibles
echo =========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0\.."

REM Variables
set TASK_NAME=App_DatosSensibles
set SCRIPT_PATH=%CD%\scripts\start-silent.vbs

echo [1/3] Verificando que el script exista...
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] No se encuentra el archivo: start-silent.vbs
    echo Por favor verifica que el archivo exista en la carpeta scripts
    pause
    exit /b 1
)
echo OK - Script encontrado: %SCRIPT_PATH%
echo.

echo [2/3] Eliminando tarea anterior si existe...
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
echo OK - Tarea anterior eliminada (si existia)
echo.

echo [3/3] Creando nueva tarea programada...
schtasks /Create /TN "%TASK_NAME%" ^
    /TR "wscript.exe \"%SCRIPT_PATH%\"" ^
    /SC ONLOGON ^
    /RL HIGHEST ^
    /F

if %errorLevel% neq 0 (
    echo [ERROR] No se pudo crear la tarea programada
    pause
    exit /b 1
)

echo.
echo =========================================
echo  Tarea Programada Instalada Correctamente
echo =========================================
echo.
echo Nombre de la tarea: %TASK_NAME%
echo Script: %SCRIPT_PATH%
echo.
echo La aplicacion se iniciara automaticamente:
echo   - Al iniciar sesion en Windows
echo   - Sin abrir ventanas (completamente en segundo plano)
echo.
echo Opciones disponibles:
echo.
echo   [1] Ejecutar la tarea ahora (probar)
echo   [2] Ver estado de la tarea
echo   [3] Abrir Programador de Tareas de Windows
echo   [4] Salir
echo.

choice /C 1234 /N /M "Selecciona una opcion (1-4): "

if errorlevel 4 goto :end
if errorlevel 3 goto :open_scheduler
if errorlevel 2 goto :view_status
if errorlevel 1 goto :run_now

:run_now
echo.
echo Ejecutando la tarea ahora...
schtasks /Run /TN "%TASK_NAME%"
echo.
echo La aplicacion se esta iniciando en segundo plano...
echo Espera unos segundos y abre: http://localhost:3030
echo.
pause
goto :end

:view_status
echo.
echo Estado de la tarea:
echo.
schtasks /Query /TN "%TASK_NAME%" /FO LIST /V
echo.
pause
goto :end

:open_scheduler
echo.
echo Abriendo Programador de Tareas de Windows...
start taskschd.msc
echo.
echo Busca la tarea: %TASK_NAME%
echo.
pause
goto :end

:end
echo.
echo Para gestionar manualmente la tarea:
echo   - Presiona Win + R
echo   - Escribe: taskschd.msc
echo   - Busca: %TASK_NAME%
echo.
echo Para desinstalar la tarea: uninstall-scheduled-task.bat
echo.
pause
