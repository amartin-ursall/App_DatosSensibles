# Servicio del Sistema - App Datos Sensibles

Esta guía explica cómo configurar la aplicación como un servicio del sistema Windows que se ejecuta automáticamente en segundo plano.

## 🎯 ¿Qué hace esto?

Convierte tu aplicación en un **servicio de Windows** que:
- ✅ Se inicia automáticamente con Windows
- ✅ Se ejecuta en segundo plano (sin ventanas)
- ✅ Se reinicia automáticamente si falla
- ✅ Gestiona logs de forma automática
- ✅ Permite control fácil (iniciar/detener/reiniciar)

## 📋 Requisitos

- **Windows** (cualquier versión moderna)
- **Node.js** instalado
- **Python** instalado
- **Permisos de administrador** (solo para instalación)

## 🚀 Instalación (Solo una vez)

### Paso 1: Instalar el servicio

1. Ve a la carpeta `scripts`
2. Click derecho en `install-service.bat`
3. Selecciona "Ejecutar como administrador"
4. Sigue las instrucciones en pantalla

Durante la instalación se te pedirá:
- **Service name:** Usa `PM2-DatosSensibles` o el nombre que prefieras
- **PM2 runtime:** Deja el valor por defecto que se sugiere

### Paso 2: Iniciar los servicios

Después de instalar, ejecuta:
```cmd
service-start.bat
```

Este script:
1. Verifica e instala dependencias
2. Crea el entorno virtual de Python si no existe
3. Inicia el backend y frontend con PM2
4. Guarda la configuración

## 🎮 Uso Diario

### Iniciar servicios
```cmd
scripts\service-start.bat
```

### Detener servicios
```cmd
scripts\service-stop.bat
```

### Reiniciar servicios
```cmd
scripts\service-restart.bat
```

### Ver estado
```cmd
scripts\service-status.bat
```

## 📊 Monitoreo y Logs

### Ver logs en tiempo real
```cmd
pm2 logs
```

### Ver logs solo del backend
```cmd
pm2 logs datossensibles-backend
```

### Ver logs solo del frontend
```cmd
pm2 logs datossensibles-frontend
```

### Ver uso de recursos (CPU, memoria)
```cmd
pm2 monit
```

### Ver información detallada
```cmd
pm2 info datossensibles-backend
pm2 info datossensibles-frontend
```

## 📁 Ubicación de Logs

Los logs se guardan automáticamente en:
```
App_DatosSensibles/logs/
├── backend-error.log    (errores del backend)
├── backend-out.log      (salida del backend)
├── frontend-error.log   (errores del frontend)
└── frontend-out.log     (salida del frontend)
```

## 🔧 Comandos PM2 Útiles

```cmd
# Ver todos los procesos
pm2 list

# Reiniciar un proceso específico
pm2 restart datossensibles-backend
pm2 restart datossensibles-frontend

# Detener un proceso específico
pm2 stop datossensibles-backend
pm2 stop datossensibles-frontend

# Ver detalles de un proceso
pm2 show datossensibles-backend

# Limpiar logs
pm2 flush

# Ver dashboard con métricas
pm2 monit
```

## ⚙️ Configuración

La configuración de PM2 está en el archivo `ecosystem.config.js` en la raíz del proyecto.

Puedes modificar:
- Puertos
- Variables de entorno
- Límites de memoria
- Comportamiento de reinicio
- Ubicación de logs

## 🔄 Reinicio Automático

El servicio está configurado para:
- ✅ Reiniciarse si falla
- ✅ Esperar 10 segundos antes de considerar que inició correctamente
- ✅ Máximo 10 reintentos si falla repetidamente
- ✅ Esperar 4 segundos entre reinicios

## 🌐 Acceso desde la Red

Los servicios están configurados para aceptar conexiones desde la red local:
- Frontend: `http://localhost:3030` o `http://TU_IP:3030`
- Backend: `http://localhost:5000` o `http://TU_IP:5000`

Si necesitas acceso desde otros dispositivos, asegúrate de:
1. Configurar el firewall (ver `README-SCRIPTS.md`)
2. Verificar que ambos dispositivos están en la misma red

## ❌ Desinstalar el Servicio

Si deseas eliminar el servicio del sistema:

1. Ve a la carpeta `scripts`
2. Click derecho en `service-uninstall.bat`
3. Selecciona "Ejecutar como administrador"
4. Confirma la desinstalación

Esto:
- Detendrá todos los procesos
- Eliminará el servicio de Windows
- Limpiará la configuración de PM2
- Mantendrá PM2 instalado (por si lo necesitas para otros proyectos)

Si quieres eliminar PM2 completamente:
```cmd
npm uninstall -g pm2 pm2-windows-service
```

## 🔍 Solución de Problemas

### Los servicios no inician

1. Verifica que Node.js y Python están instalados:
   ```cmd
   node --version
   py --version
   ```

2. Verifica que PM2 está instalado:
   ```cmd
   pm2 --version
   ```

3. Revisa los logs:
   ```cmd
   pm2 logs
   ```

### El servicio no se inicia con Windows

1. Verifica que el servicio está instalado:
   ```cmd
   sc query PM2
   ```

2. Si no está, ejecuta `install-service.bat` de nuevo como administrador

### Puerto ya en uso

Si los puertos 3030 o 5000 están ocupados:

1. Detén otros servicios que usen esos puertos
2. O modifica los puertos en `ecosystem.config.js`
3. Reinicia los servicios:
   ```cmd
   service-restart.bat
   ```

### Error "EACCES" o permisos denegados

1. Ejecuta el script como administrador
2. O verifica que no hay antivirus bloqueando PM2

### Backend no encuentra el entorno virtual

1. Asegúrate de que existe `backend/venv`
2. Si no existe, ejecuta:
   ```cmd
   cd backend
   py -m venv venv
   venv\Scripts\pip install -r requirements.txt
   ```

## 📝 Diferencias con start.bat

| Característica | start.bat | Servicio PM2 |
|---------------|-----------|--------------|
| Ventanas visibles | ✅ Sí | ❌ No (segundo plano) |
| Inicio automático con Windows | ❌ No | ✅ Sí |
| Reinicio automático si falla | ❌ No | ✅ Sí |
| Gestión de logs | ❌ Manual | ✅ Automática |
| Control centralizado | ❌ No | ✅ Sí (PM2) |
| Uso de recursos | Similar | Similar |
| Complejidad | Simple | Moderada |

**Recomendación:**
- Usa `start.bat` para **desarrollo y pruebas**
- Usa **Servicio PM2** para **producción y uso continuo**

## 🎓 Recursos Adicionales

- [Documentación oficial de PM2](https://pm2.keymetrics.io/)
- [PM2 en Windows](https://pm2.keymetrics.io/docs/usage/pm2-windows/)
- [Ecosystem File](https://pm2.keymetrics.io/docs/usage/application-declaration/)

## 💡 Consejos

1. **Logs:** Revisa los logs regularmente en `logs/`
2. **Memoria:** Si la app usa mucha memoria, ajusta `max_memory_restart` en `ecosystem.config.js`
3. **Actualizaciones:** Después de actualizar el código, ejecuta `service-restart.bat`
4. **Monitoreo:** Usa `pm2 monit` para ver el uso de recursos en tiempo real
5. **Backup:** Guarda una copia de `ecosystem.config.js` si lo personalizas

---

**Versión:** 1.0
**Última actualización:** 2025-10-27
