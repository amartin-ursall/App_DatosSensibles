@echo off
echo =========================================
echo  Estado del Servicio - App Datos Sensibles
echo =========================================
echo.

echo Estado de PM2:
call pm2 status
echo.

echo =========================================
echo  Informacion Detallada
echo =========================================
echo.

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP:~1%

echo URLs de acceso local:
echo  - Frontend: http://localhost:3030
echo  - Backend:  http://localhost:5000
echo  - Health:   http://localhost:5000/health
echo.
echo URLs de acceso desde red local:
echo  - Frontend: http://%IP%:3030
echo  - Backend:  http://%IP%:5000
echo  - Health:   http://%IP%:5000/health
echo.

echo =========================================
echo  Comandos Utiles
echo =========================================
echo.
echo Ver logs en tiempo real:
echo   pm2 logs
echo.
echo Ver logs de backend:
echo   pm2 logs datossensibles-backend
echo.
echo Ver logs de frontend:
echo   pm2 logs datossensibles-frontend
echo.
echo Reiniciar backend:
echo   pm2 restart datossensibles-backend
echo.
echo Reiniciar frontend:
echo   pm2 restart datossensibles-frontend
echo.
echo Reiniciar todo:
echo   pm2 restart all
echo.
echo Ver informacion detallada:
echo   pm2 info datossensibles-backend
echo   pm2 info datossensibles-frontend
echo.
echo Ver uso de recursos:
echo   pm2 monit
echo.
pause
