@echo off
echo =========================================
echo  Deteniendo Servicio - App Datos Sensibles
echo =========================================
echo.

echo Deteniendo todas las aplicaciones con PM2...
call pm2 stop all
if %errorLevel% neq 0 (
    echo [ERROR] No se pudieron detener las aplicaciones
    pause
    exit /b 1
)
echo.

echo =========================================
echo  Servicio Detenido
echo =========================================
echo.
echo Estado de los servicios:
call pm2 status
echo.
echo Para reiniciar: service-start.bat
echo Para ver logs: pm2 logs
echo.
pause
