# Tarea Programada de Windows - App Datos Sensibles

Esta guía explica cómo configurar la aplicación para que se ejecute automáticamente en segundo plano usando el Programador de Tareas de Windows, **completamente sin ventanas visibles**.

## ¿Qué hace esto?

Configura tu aplicación para que:
- Se inicia automáticamente al iniciar sesión en Windows
- Se ejecuta **completamente en segundo plano** (sin ventanas ni terminales visibles)
- Se gestiona automáticamente con PM2 (reinicio automático si falla)
- Mantiene logs de todas las actividades
- Es completamente invisible (no interrumpe tu trabajo)

## Requisitos Previos

Antes de instalar la tarea programada, **DEBES** instalar PM2:

```cmd
scripts\install-service.bat
```

Este paso es **obligatorio** y solo se hace una vez. Instala PM2 y sus dependencias.

## Instalación Rápida (3 pasos)

### Paso 1: Instalar PM2 (solo la primera vez)

1. Ve a la carpeta `scripts`
2. Click derecho en `install-service.bat`
3. Selecciona "Ejecutar como administrador"
4. Espera a que termine la instalación

### Paso 2: Instalar Tarea Programada

1. Click derecho en `install-scheduled-task.bat`
2. Selecciona "Ejecutar como administrador"
3. Sigue las instrucciones en pantalla

### Paso 3: ¡Listo!

Tu aplicación ahora se iniciará automáticamente cada vez que inicies sesión en Windows, completamente en segundo plano.

## Verificación

Para verificar que está funcionando:

1. Abre tu navegador
2. Ve a `http://localhost:3030` (Frontend)
3. Ve a `http://localhost:5000/health` (Backend)

## Gestión de la Tarea

### Ver estado de los servicios

```cmd
pm2 status
```

o

```cmd
pm2 list
```

### Ver logs en tiempo real

```cmd
pm2 logs
```

### Ver solo logs del backend

```cmd
pm2 logs datossensibles-backend
```

### Ver solo logs del frontend

```cmd
pm2 logs datossensibles-frontend
```

### Reiniciar los servicios

```cmd
pm2 restart all
```

### Detener los servicios temporalmente

```cmd
pm2 stop all
```

### Iniciar los servicios manualmente

```cmd
pm2 start all
```

o ejecuta:

```cmd
scripts\start-silent.vbs
```

(doble click en el archivo, sin necesidad de permisos de administrador)

## Gestión de la Tarea Programada

### Ver información de la tarea

Abre el Programador de Tareas de Windows:

1. Presiona `Win + R`
2. Escribe: `taskschd.msc`
3. Presiona Enter
4. Busca la tarea: `App_DatosSensibles`

### Ejecutar la tarea manualmente ahora

```cmd
schtasks /Run /TN "App_DatosSensibles"
```

### Ver estado de la tarea

```cmd
schtasks /Query /TN "App_DatosSensibles" /FO LIST /V
```

### Deshabilitar (temporalmente) la tarea

```cmd
schtasks /Change /TN "App_DatosSensibles" /DISABLE
```

### Habilitar la tarea

```cmd
schtasks /Change /TN "App_DatosSensibles" /ENABLE
```

### Desinstalar la tarea completamente

1. Click derecho en `uninstall-scheduled-task.bat`
2. Selecciona "Ejecutar como administrador"

## Ubicación de Logs

Los logs se guardan automáticamente en:

```
App_DatosSensibles/logs/
├── backend-error.log    (errores del backend)
├── backend-out.log      (salida del backend)
├── frontend-error.log   (errores del frontend)
└── frontend-out.log     (salida del frontend)
```

## Diferencias entre Métodos de Inicio

| Característica | start.bat | service-start.bat | Tarea Programada |
|---------------|-----------|-------------------|------------------|
| Ventanas visibles | Sí (2 ventanas) | Sí (1 ventana) | **No (invisible)** |
| Inicio automático | No | No | **Sí** |
| Requiere PM2 | No | Sí | **Sí** |
| Reinicio automático | No | Sí | **Sí** |
| Complejidad | Baja | Media | **Media** |
| Ideal para | Desarrollo | Pruebas | **Producción** |

## Recomendaciones de Uso

- **Desarrollo:** Usa `start.bat` (para ver logs en consola)
- **Pruebas:** Usa `service-start.bat` (gestión con PM2)
- **Producción/Uso diario:** Usa **Tarea Programada** (completamente invisible)

## Solución de Problemas

### La aplicación no inicia al iniciar sesión

1. Verifica que la tarea está instalada:
   ```cmd
   schtasks /Query /TN "App_DatosSensibles"
   ```

2. Si no está, ejecuta `install-scheduled-task.bat` de nuevo

3. Verifica que PM2 está instalado:
   ```cmd
   pm2 --version
   ```

### No puedo acceder a la aplicación

1. Verifica que los servicios están corriendo:
   ```cmd
   pm2 status
   ```

2. Si no están corriendo, inícialo manualmente:
   ```cmd
   scripts\start-silent.vbs
   ```
   (doble click en el archivo)

3. Revisa los logs:
   ```cmd
   pm2 logs
   ```

### Error "PM2 no está instalado"

Debes instalar PM2 primero:

```cmd
scripts\install-service.bat
```

(ejecutar como administrador)

### Puerto ya en uso

Si los puertos 3030 o 5000 están ocupados:

1. Detén los servicios:
   ```cmd
   pm2 stop all
   ```

2. Encuentra qué está usando el puerto:
   ```cmd
   netstat -ano | findstr :3030
   netstat -ano | findstr :5000
   ```

3. Detén el proceso o cambia los puertos en `ecosystem.config.js`

### Los servicios se reinician constantemente

1. Revisa los logs para ver el error:
   ```cmd
   pm2 logs
   ```

2. Verifica que las dependencias están instaladas:
   ```cmd
   cd backend
   venv\Scripts\pip install -r requirements.txt
   cd ..
   npm install
   ```

3. Reinicia los servicios:
   ```cmd
   pm2 restart all
   ```

## Cómo Funciona

1. **Tarea Programada** se ejecuta al iniciar sesión
2. **start-silent.vbs** se ejecuta sin mostrar ventanas
3. **PM2** inicia y gestiona los servicios (backend y frontend)
4. **Logs** se guardan automáticamente en la carpeta `logs/`

Todo el proceso es completamente invisible y automático.

## Comandos PM2 Útiles

```cmd
# Ver dashboard con métricas en tiempo real
pm2 monit

# Ver información detallada de un proceso
pm2 info datossensibles-backend
pm2 info datossensibles-frontend

# Limpiar todos los logs
pm2 flush

# Reiniciar un proceso específico
pm2 restart datossensibles-backend
pm2 restart datossensibles-frontend

# Ver logs con filtro
pm2 logs --lines 100

# Ver logs solo de errores
pm2 logs --err
```

## Desinstalación Completa

Si quieres eliminar todo:

### 1. Eliminar Tarea Programada

```cmd
scripts\uninstall-scheduled-task.bat
```

(ejecutar como administrador)

### 2. Detener Servicios PM2

```cmd
pm2 delete all
pm2 save --force
```

### 3. (Opcional) Desinstalar PM2

```cmd
npm uninstall -g pm2 pm2-windows-service
```

## Consejos y Mejores Prácticas

1. **Revisa logs regularmente:** Los logs están en `logs/` y te ayudarán a detectar problemas

2. **Monitoreo:** Usa `pm2 monit` para ver el uso de CPU y memoria en tiempo real

3. **Después de actualizar código:** Ejecuta `pm2 restart all` para aplicar cambios

4. **Backup:** Guarda una copia de `ecosystem.config.js` si lo personalizas

5. **Desactivar temporalmente:** Si no quieres que inicie automáticamente por un tiempo, deshabilita la tarea en lugar de desinstalarla

6. **Notificaciones:** Puedes comentar la línea del `MsgBox` en `start-silent.vbs` si no quieres ver la notificación de inicio

## Personalización

### Cambiar puertos

Edita `ecosystem.config.js`:

```javascript
env: {
  PORT: 3030  // Cambiar puerto del frontend
}
```

y

```javascript
env: {
  PORT: 5000  // Cambiar puerto del backend
}
```

Luego reinicia:

```cmd
pm2 restart all
```

### Cambiar límites de memoria

Edita `ecosystem.config.js`:

```javascript
max_memory_restart: '1G'  // Cambia el límite
```

### Deshabilitar notificación de inicio

Edita `start-silent.vbs` y comenta (añade ' al inicio) la sección del `MsgBox` final.

## Recursos

- [Documentación PM2](https://pm2.keymetrics.io/)
- [Programador de Tareas de Windows](https://docs.microsoft.com/es-es/windows/win32/taskschd/task-scheduler-start-page)
- [VBScript Reference](https://docs.microsoft.com/es-es/previous-versions/windows/internet-explorer/ie-developer/scripting-articles/d1wf56tt%28v=vs.84%29)

---

**Versión:** 1.0
**Última actualización:** 2025-10-28
