@echo off
REM ========================================
REM Script de inicio - App Datos Sensibles
REM ========================================

REM Cambiar al directorio del proyecto (directorio padre del script)
cd /d "%~dp0.."

echo.
echo ========================================
echo  Iniciando Aplicacion de Privacidad
echo ========================================
echo.
echo [INFO] Directorio de trabajo: %CD%
echo.

REM Verificar Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Por favor instala Node.js desde https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python no esta instalado
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

REM Verificar e instalar dependencias del frontend
if not exist "node_modules\" (
    echo [INFO] Instalando dependencias del frontend...
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Fallo la instalacion de dependencias del frontend
        pause
        exit /b 1
    )
)

REM Verificar e instalar dependencias del backend
if not exist "backend\venv\" (
    echo [INFO] Creando entorno virtual Python...
    cd backend
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Fallo la creacion del entorno virtual
        cd ..
        pause
        exit /b 1
    )

    echo [INFO] Instalando dependencias del backend...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Fallo la instalacion de dependencias del backend
        cd ..
        pause
        exit /b 1
    )
    call deactivate
    cd ..
)

echo.
echo [1/2] Iniciando Backend Python (puerto 5000)...
start "Backend Python - App Datos Sensibles" cmd /k "cd /d "%CD%\backend" && venv\Scripts\activate.bat && python app.py"

echo [INFO] Esperando 5 segundos para que el backend inicie...
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Iniciando Frontend Next.js (puerto 3030)...
start "Frontend Next.js - App Datos Sensibles" cmd /k "cd /d "%CD%" && npm run dev"

echo.
echo ========================================
echo  Servidores iniciados correctamente
echo ========================================
echo.
echo  Backend Python:   http://localhost:5000
echo  Frontend Next.js: http://localhost:3030
echo.
echo  Acceso desde red local:
echo  - Backend:  http://TU_IP:5000
echo  - Frontend: http://TU_IP:3030
echo.
echo  Para detener los servidores ejecuta: stop.bat
echo  Para ver el estado ejecuta: status.bat
echo.
pause
