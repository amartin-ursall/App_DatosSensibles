# ⚡ Configuración SIN VENTANAS - Pasos Rápidos

## 🎯 Objetivo
Configurar la aplicación para que se ejecute **completamente en segundo plano SIN abrir ninguna ventana** y que se inicie automáticamente al iniciar sesión en Windows.

---

## 📋 Pasos a Seguir (Solo 2 pasos)

### PASO 1️⃣: Instalar PM2

1. Ve a la carpeta `scripts` de tu proyecto
2. Busca el archivo: **`install-service.bat`**
3. **Click derecho** sobre el archivo
4. Selecciona: **"Ejecutar como administrador"**
5. Sigue las instrucciones en pantalla:
   - Cuando pregunte "Service name", escribe: **PM2-DatosSensibles**
   - Cuando pregunte "PM2 runtime", presiona **Enter** (deja el valor por defecto)
6. Espera a que termine la instalación
7. Verás el mensaje: **"Instalacion Completada"**

✅ **PM2 instalado correctamente**

---

### PASO 2️⃣: Instalar la Tarea Programada

1. En la misma carpeta `scripts`
2. Busca el archivo: **`install-scheduled-task.bat`**
3. **Click derecho** sobre el archivo
4. Selecciona: **"Ejecutar como administrador"**
5. Espera a que se instale (toma unos segundos)
6. Aparecerá un menú con opciones:
   - Opción **1**: Ejecutar la tarea ahora (para probar)
   - Opción **2**: Ver estado de la tarea
   - Opción **3**: Abrir Programador de Tareas
   - Opción **4**: Salir

7. **Selecciona opción 1** para iniciar la aplicación ahora

✅ **Tarea programada instalada correctamente**

---

## 🎉 ¡LISTO!

La aplicación ahora:
- ✅ Se ejecuta completamente **en segundo plano** (sin ventanas)
- ✅ Se inicia **automáticamente** al iniciar sesión en Windows
- ✅ Se **reinicia automáticamente** si hay algún error
- ✅ Guarda **logs** de todo en la carpeta `logs/`

---

## 🌐 Acceder a la Aplicación

Abre tu navegador y ve a:

**Frontend:** http://localhost:3030

**Backend (API):** http://localhost:5000

**Health Check:** http://localhost:5000/health

---

## 🔍 Ver Estado y Logs

Para verificar que todo está funcionando:

### Ver si está corriendo:
```cmd
pm2 status
```

### Ver logs en tiempo real:
```cmd
pm2 logs
```

### Ver solo logs del backend:
```cmd
pm2 logs datossensibles-backend
```

### Ver solo logs del frontend:
```cmd
pm2 logs datossensibles-frontend
```

---

## 🔄 Gestión Diaria

### Reiniciar la aplicación:
```cmd
pm2 restart all
```

### Detener temporalmente:
```cmd
pm2 stop all
```

### Iniciar de nuevo:
```cmd
pm2 start all
```

O también puedes hacer **doble click** en:
```
scripts\start-silent.vbs
```
(Este archivo inicia todo sin ventanas)

---

## ❌ Desinstalar (si ya no lo quieres)

Si en algún momento quieres eliminar la tarea programada:

1. Ve a la carpeta `scripts`
2. Busca: **`uninstall-scheduled-task.bat`**
3. **Click derecho** → **"Ejecutar como administrador"**

Esto eliminará la tarea programada, pero PM2 seguirá instalado por si lo necesitas para otros proyectos.

---

## 🔧 Solución de Problemas

### "PM2 no está instalado"
- Asegúrate de haber completado el **PASO 1** correctamente
- Ejecuta de nuevo `install-service.bat` como administrador

### "No puedo acceder a localhost:3030"
1. Verifica que los servicios están corriendo:
   ```cmd
   pm2 status
   ```
2. Si no están corriendo, inícialo manualmente:
   - Doble click en: `scripts\start-silent.vbs`
   - O ejecuta: `pm2 start all`

### "Puerto ya en uso"
1. Detén los servicios:
   ```cmd
   pm2 stop all
   pm2 delete all
   ```
2. Inicia de nuevo:
   - Doble click en: `scripts\start-silent.vbs`

### Ver qué está usando el puerto:
```cmd
netstat -ano | findstr :3030
netstat -ano | findstr :5000
```

---

## 📞 Comandos Útiles de PM2

```cmd
# Ver dashboard interactivo con métricas
pm2 monit

# Ver información detallada
pm2 info datossensibles-backend
pm2 info datossensibles-frontend

# Limpiar todos los logs
pm2 flush

# Ver últimas 50 líneas de logs
pm2 logs --lines 50

# Ver solo errores
pm2 logs --err
```

---

## 📚 Documentación Completa

Para más información detallada:

- **Tarea Programada:** [scripts/README-SCHEDULED-TASK.md](scripts/README-SCHEDULED-TASK.md)
- **Gestión de Scripts:** [README-SCRIPTS.md](README-SCRIPTS.md)
- **PM2 Servicios:** [scripts/README-SERVICE.md](scripts/README-SERVICE.md)

---

## ✨ Ventajas de Este Método

| Característica | Estado |
|---------------|--------|
| Sin ventanas visibles | ✅ Sí |
| Inicio automático con Windows | ✅ Sí |
| Reinicio automático si falla | ✅ Sí |
| Logs centralizados | ✅ Sí |
| Fácil de gestionar | ✅ Sí |
| Sin interrupciones | ✅ Sí |

---

**¿Tienes problemas?**

Revisa los logs en:
```
App_DatosSensibles/logs/
```

O consulta la documentación completa en los archivos mencionados arriba.

---

**Versión:** 1.0
**Fecha:** 2025-10-28
