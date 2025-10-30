@echo off
REM ========================================
REM Script de configuración de Firewall
REM App Datos Sensibles
REM ========================================
REM
REM IMPORTANTE: Este script debe ejecutarse como ADMINISTRADOR
REM Click derecho -> Ejecutar como administrador
REM

echo.
echo ========================================
echo  Configuracion de Firewall
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

echo [INFO] Permisos de administrador detectados
echo.

REM Eliminar reglas existentes si ya existen
echo [1/5] Limpiando reglas anteriores...
netsh advfirewall firewall delete rule name="App Datos Sensibles - Frontend" >nul 2>&1
netsh advfirewall firewall delete rule name="App Datos Sensibles - Backend" >nul 2>&1
netsh advfirewall firewall delete rule name="App Datos Sensibles - Node.js" >nul 2>&1
netsh advfirewall firewall delete rule name="App Datos Sensibles - Python" >nul 2>&1
echo [OK] Reglas antiguas eliminadas

REM Crear regla para el Frontend (puerto 3030)
echo.
echo [2/5] Creando regla para Frontend Next.js (puerto 3030)...
netsh advfirewall firewall add rule name="App Datos Sensibles - Frontend" dir=in action=allow protocol=TCP localport=3030 enable=yes profile=private,domain
if %ERRORLEVEL% equ 0 (
    echo [OK] Regla de entrada para puerto 3030 creada
) else (
    echo [ERROR] Fallo al crear regla para puerto 3030
)

REM Crear regla para el Backend (puerto 5000)
echo.
echo [3/5] Creando regla para Backend Python (puerto 5000)...
netsh advfirewall firewall add rule name="App Datos Sensibles - Backend" dir=in action=allow protocol=TCP localport=5000 enable=yes profile=private,domain
if %ERRORLEVEL% equ 0 (
    echo [OK] Regla de entrada para puerto 5000 creada
) else (
    echo [ERROR] Fallo al crear regla para puerto 5000
)

REM Crear regla para Node.js (alternativa por ejecutable)
echo.
echo [4/5] Creando regla para Node.js...
where node >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%a in ('where node') do (
        netsh advfirewall firewall add rule name="App Datos Sensibles - Node.js" dir=in action=allow program="%%a" enable=yes profile=private,domain >nul 2>&1
        echo [OK] Regla para Node.js creada: %%a
    )
) else (
    echo [ADVERTENCIA] Node.js no encontrado en PATH
)

REM Crear regla para Python (alternativa por ejecutable)
echo.
echo [5/5] Creando regla para Python...
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%a in ('where python') do (
        netsh advfirewall firewall add rule name="App Datos Sensibles - Python" dir=in action=allow program="%%a" enable=yes profile=private,domain >nul 2>&1
        echo [OK] Regla para Python creada: %%a
    )
) else (
    echo [ADVERTENCIA] Python no encontrado en PATH
)

echo.
echo ========================================
echo  Configuracion Completada
echo ========================================
echo.
echo Reglas de firewall creadas:
echo  - Puerto 3030 (Frontend Next.js)
echo  - Puerto 5000 (Backend Python)
echo.
echo La aplicacion ahora es accesible desde:
echo  - Red local (LAN)
echo  - Otros dispositivos en la misma red
echo.
echo Para encontrar tu IP local ejecuta: ipconfig
echo Busca "Direccion IPv4" en tu adaptador de red
echo.
echo Ejemplo de acceso desde otro equipo:
echo  http://192.168.1.XXX:3030
echo.
echo ========================================
echo.
echo NOTA DE SEGURIDAD:
echo - Estas reglas solo permiten acceso en redes Privadas y de Dominio
echo - NO se permite acceso desde redes Publicas
echo - Para desactivar, ejecuta: firewall-remove.bat
echo.
pause
