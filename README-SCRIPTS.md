# Scripts de Gestión - App Datos Sensibles

Conjunto de scripts para gestionar fácilmente la aplicación de detección de datos sensibles.

## 📋 Scripts Disponibles

### `start.bat` - Iniciar la Aplicación
Inicia tanto el backend Python como el frontend Next.js.

**Uso:**
```cmd
start.bat
```

**Funcionalidades:**
- ✅ Verifica que Node.js y Python están instalados
- ✅ Instala dependencias automáticamente si no existen
- ✅ Crea el entorno virtual de Python si no existe
- ✅ Inicia el backend Flask en puerto 5000
- ✅ Inicia el frontend Next.js en puerto 3030
- ✅ Abre ventanas separadas para cada servicio

**URLs de Acceso:**
- Frontend: http://localhost:3030
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/health

---

### `stop.bat` - Detener la Aplicación
Detiene todos los servicios en ejecución.

**Uso:**
```cmd
stop.bat
```

**Funcionalidades:**
- 🛑 Detiene el proceso del frontend (puerto 3030)
- 🛑 Detiene el proceso del backend (puerto 5000)
- 🛑 Cierra las ventanas de comando asociadas

---

### `status.bat` - Ver Estado de la Aplicación
Muestra el estado actual de todos los servicios.

**Uso:**
```cmd
status.bat
```

**Información Mostrada:**
- ✔️ Estado de cada servicio (ACTIVO/INACTIVO)
- ✔️ PID del proceso si está activo
- ✔️ URLs de acceso local y en red
- ✔️ Direcciones IP para acceso desde otros dispositivos
- ✔️ Health check del backend

---

### `firewall-config.bat` - Configurar Firewall
Configura el firewall de Windows para permitir acceso desde la red local.

**Uso:**
```cmd
Click derecho -> Ejecutar como administrador
```

**⚠️ REQUIERE PERMISOS DE ADMINISTRADOR**

**Funcionalidades:**
- 🔓 Crea reglas para puerto 3030 (Frontend)
- 🔓 Crea reglas para puerto 5000 (Backend)
- 🔓 Permite acceso desde redes Privadas y de Dominio
- 🔒 Bloquea acceso desde redes Públicas (seguridad)

**Después de ejecutar:**
La aplicación será accesible desde otros dispositivos en tu red local usando tu IP:
- http://TU_IP:3030 (Frontend)
- http://TU_IP:5000 (Backend)

Para encontrar tu IP ejecuta: `ipconfig`

---

### `firewall-remove.bat` - Eliminar Reglas de Firewall
Elimina las reglas de firewall creadas.

**Uso:**
```cmd
Click derecho -> Ejecutar como administrador
```

**⚠️ REQUIERE PERMISOS DE ADMINISTRADOR**

---

## 🚀 Tarea Programada (RECOMENDADO - Sin Ventanas)

**¿Quieres que la app se ejecute completamente en segundo plano SIN ventanas visibles?**

Consulta la **[Guía de Tarea Programada](scripts/README-SCHEDULED-TASK.md)** para la configuración completa.

### Instalación Rápida (2 pasos):

1. **Instalar PM2** (solo primera vez):
   ```cmd
   Click derecho en scripts\install-service.bat -> Ejecutar como administrador
   ```

2. **Instalar Tarea Programada**:
   ```cmd
   Click derecho en scripts\install-scheduled-task.bat -> Ejecutar como administrador
   ```

¡Listo! La app se iniciará automáticamente sin ventanas cada vez que inicies sesión en Windows.

---

## 🔄 Scripts de Servicio del Sistema (Ejecución Permanente)

Para ejecutar la aplicación como un servicio del sistema que inicia automáticamente con Windows, consulta la **[Guía completa de servicios](scripts/README-SERVICE.md)**.

### Scripts de Servicio (en carpeta `scripts/`)

#### `install-service.bat` - Instalar como Servicio
Configura la aplicación como servicio de Windows usando PM2.

**⚠️ REQUIERE PERMISOS DE ADMINISTRADOR**

**Uso:**
```cmd
Click derecho en scripts\install-service.bat -> Ejecutar como administrador
```

**Instala:**
- PM2 (gestor de procesos)
- pm2-windows-service (servicio de Windows)
- Configura inicio automático con Windows

---

#### `service-start.bat` - Iniciar Servicio
Inicia la aplicación como servicio en segundo plano.

**Uso:**
```cmd
scripts\service-start.bat
```

**Ventajas sobre start.bat:**
- ✅ Se ejecuta en segundo plano (sin ventanas)
- ✅ Reinicio automático si falla
- ✅ Gestión centralizada de logs
- ✅ Monitoreo de recursos

---

#### `service-stop.bat` - Detener Servicio
Detiene el servicio sin desinstalarlo.

**Uso:**
```cmd
scripts\service-stop.bat
```

---

#### `service-restart.bat` - Reiniciar Servicio
Reinicia ambos servicios (útil después de actualizaciones).

**Uso:**
```cmd
scripts\service-restart.bat
```

---

#### `service-status.bat` - Estado del Servicio
Muestra el estado detallado del servicio con información útil.

**Uso:**
```cmd
scripts\service-status.bat
```

**Muestra:**
- Estado de cada proceso (backend/frontend)
- Uso de CPU y memoria
- Tiempo de ejecución
- Número de reinicios
- URLs de acceso
- Comandos útiles de PM2

---

#### `service-uninstall.bat` - Desinstalar Servicio
Elimina el servicio del sistema completamente.

**⚠️ REQUIERE PERMISOS DE ADMINISTRADOR**

**Uso:**
```cmd
Click derecho en scripts\service-uninstall.bat -> Ejecutar como administrador
```

---

### ¿Cuándo usar cada modo?

| Característica | start.bat | Servicio PM2 | Tarea Programada |
|---------------|-----------|--------------|------------------|
| **Mejor para** | Desarrollo y pruebas | Uso continuo | **Producción invisible** |
| **Ventanas visibles** | ✅ Sí (2 ventanas) | ❌ No | **❌ No (completamente invisible)** |
| **Inicio automático** | ❌ No | ❌ Manual | **✅ Sí al iniciar sesión** |
| **Reinicio si falla** | ❌ No | ✅ Sí automático | **✅ Sí automático** |
| **Logs centralizados** | ❌ No | ✅ Sí | **✅ Sí en carpeta logs/** |
| **Monitoreo** | ❌ Manual | ✅ Con pm2 monit | **✅ Con pm2 monit** |
| **Complejidad** | Simple | Moderada | **Moderada** |

**Recomendación:**
- Usa `start.bat` cuando estés **desarrollando o probando**
- Usa **servicio PM2** cuando quieras **gestión manual con PM2**
- Usa **Tarea Programada** para **ejecución invisible y automática** (RECOMENDADO)

---

## 🚀 Guía Rápida de Inicio

### Opción A: Tarea Programada - Sin Ventanas (RECOMENDADO)

**Primera vez:**

1. **Instalar PM2:**
   ```cmd
   Click derecho en scripts\install-service.bat -> Ejecutar como administrador
   ```
   Sigue las instrucciones (usa el nombre: PM2-DatosSensibles)

2. **Instalar Tarea Programada:**
   ```cmd
   Click derecho en scripts\install-scheduled-task.bat -> Ejecutar como administrador
   ```

3. **¡Listo!** La aplicación se iniciará automáticamente sin ventanas.

4. **Acceder:**
   - Abre tu navegador en: http://localhost:3030

**Gestión diaria:**
```cmd
pm2 status              # Ver estado
pm2 logs                # Ver logs
pm2 restart all         # Reiniciar
scripts\start-silent.vbs # Iniciar manualmente (doble click)
```

**Desinstalar:**
```cmd
Click derecho en scripts\uninstall-scheduled-task.bat -> Ejecutar como administrador
```

---

### Opción B: Modo Normal (Desarrollo/Pruebas)

**Primera vez:**

1. **Configurar el firewall** (opcional, solo si necesitas acceso desde red):
   ```cmd
   Click derecho en firewall-config.bat -> Ejecutar como administrador
   ```

2. **Iniciar la aplicación:**
   ```cmd
   start.bat
   ```

3. **Verificar que todo funciona:**
   ```cmd
   status.bat
   ```

4. **Acceder a la aplicación:**
   - Abre tu navegador en: http://localhost:3030

**Uso diario:**
```cmd
start.bat   # Iniciar
status.bat  # Ver estado
stop.bat    # Detener
```

---

### Opción C: Modo Servicio (Gestión Manual con PM2)

**Primera vez:**

1. **Instalar el servicio:**
   ```cmd
   Click derecho en scripts\install-service.bat -> Ejecutar como administrador
   ```

2. **Iniciar el servicio:**
   ```cmd
   scripts\service-start.bat
   ```

3. **Configurar firewall** (opcional):
   ```cmd
   Click derecho en firewall-config.bat -> Ejecutar como administrador
   ```

4. **Acceder a la aplicación:**
   - Abre tu navegador en: http://localhost:3030

**Uso diario:**
```cmd
scripts\service-start.bat    # Iniciar
scripts\service-status.bat   # Ver estado
scripts\service-stop.bat     # Detener
scripts\service-restart.bat  # Reiniciar
```

**Ventajas del modo servicio:**
- ✅ Se inicia automáticamente con Windows
- ✅ Se ejecuta en segundo plano (sin ventanas)
- ✅ Se reinicia automáticamente si falla
- ✅ Logs centralizados en carpeta `logs/`

---

## 🌐 Acceso desde Red Local

Para acceder desde otros dispositivos en tu red:

1. **Ejecutar firewall-config.bat como administrador** (una sola vez)

2. **Encontrar tu IP:**
   ```cmd
   ipconfig
   ```
   Busca "Dirección IPv4" (ejemplo: 192.168.1.100)

3. **Acceder desde otro dispositivo:**
   ```
   http://192.168.1.100:3030
   ```

---

## 📱 Acceso desde Móvil/Tablet

Asegúrate de que:
- ✅ El firewall está configurado (firewall-config.bat)
- ✅ Tu móvil/tablet está en la misma red WiFi
- ✅ La aplicación está iniciada (start.bat)

Luego abre en el navegador del móvil:
```
http://TU_IP:3030
```

---

## ⚙️ Requisitos del Sistema

- **Node.js** (v18 o superior)
- **Python** (v3.8 o superior)
- **Windows** con PowerShell/CMD
- **Permisos de administrador** (solo para configurar firewall)

---

## 🔧 Solución de Problemas

### "Node.js no está instalado"
Instala Node.js desde: https://nodejs.org/

### "Python no está instalado"
Instala Python desde: https://www.python.org/

### "Puerto ya en uso"
Ejecuta `stop.bat` para detener servicios anteriores

### No puedo acceder desde otro dispositivo
1. Verifica que ejecutaste `firewall-config.bat` como administrador
2. Verifica que ambos dispositivos están en la misma red
3. Ejecuta `status.bat` para ver tu IP correcta

### El backend no inicia
1. Verifica que existe `backend/requirements.txt`
2. Elimina `backend/venv` y ejecuta `start.bat` de nuevo

---

## 📝 Notas de Seguridad

- Las reglas de firewall **solo permiten** acceso desde redes **Privadas y de Dominio**
- El acceso desde redes **Públicas está bloqueado** por defecto
- Para desactivar el acceso desde red, ejecuta `firewall-remove.bat`
- Nunca expongas estos puertos a Internet sin medidas de seguridad adicionales

---

## 📞 Soporte

Si encuentras problemas:
1. Ejecuta `status.bat` para ver el estado
2. Verifica los logs en las ventanas de comando
3. Revisa que los puertos 3030 y 5000 estén libres

---

## 📂 Estructura de Archivos

```
App_DatosSensibles/
├── start.bat                        # Inicio modo normal
├── stop.bat                         # Detener modo normal
├── status.bat                       # Estado modo normal
├── firewall-config.bat              # Configurar firewall
├── firewall-remove.bat              # Eliminar reglas firewall
├── ecosystem.config.js              # Configuración PM2
├── logs/                            # Logs del servicio PM2
│   ├── backend-error.log
│   ├── backend-out.log
│   ├── frontend-error.log
│   └── frontend-out.log
└── scripts/
    ├── README-SERVICE.md            # Documentación servicios PM2
    ├── README-SCHEDULED-TASK.md     # Documentación tarea programada (SIN VENTANAS)
    ├── install-service.bat          # Instalar PM2 (admin)
    ├── service-start.bat            # Iniciar servicio PM2
    ├── service-stop.bat             # Detener servicio PM2
    ├── service-restart.bat          # Reiniciar servicio PM2
    ├── service-status.bat           # Estado del servicio PM2
    ├── service-uninstall.bat        # Desinstalar servicio PM2 (admin)
    ├── start-silent.vbs             # Iniciar sin ventanas (doble click)
    ├── install-scheduled-task.bat   # Instalar tarea programada (admin)
    └── uninstall-scheduled-task.bat # Desinstalar tarea programada (admin)
```

---

**Versión:** 3.0
**Última actualización:** 2025-10-28
**Novedades v3.0:**
- ✨ **Tarea Programada de Windows - Ejecución completamente invisible (SIN VENTANAS)**
- ✨ Script VBS para inicio silencioso sin terminales
- ✨ Instalación y desinstalación automática de tarea programada
- ✨ Documentación completa de configuración sin ventanas

**Novedades v2.0:**
- ✨ Scripts de servicio del sistema con PM2
- ✨ Inicio automático con Windows
- ✨ Gestión centralizada de logs
- ✨ Reinicio automático ante fallos
- ✨ Monitoreo de recursos integrado
