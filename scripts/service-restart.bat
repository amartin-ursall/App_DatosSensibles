@echo off
echo =========================================
echo  Reiniciando Servicio - App Datos Sensibles
echo =========================================
echo.

echo Reiniciando todas las aplicaciones con PM2...
call pm2 restart all
if %errorLevel% neq 0 (
    echo [ERROR] No se pudieron reiniciar las aplicaciones
    pause
    exit /b 1
)
echo.

echo =========================================
echo  Servicio Reiniciado
echo =========================================
echo.
echo Estado de los servicios:
call pm2 status
echo.
echo Para ver logs: pm2 logs
echo Para ver estado: service-status.bat
echo.
pause
