# Guía de Despliegue con Docker

Esta aplicación está completamente dockerizada y lista para ejecutarse con Docker Compose.

## Prerrequisitos

- Docker Engine 20.10 o superior
- Docker Compose 2.0 o superior

## Arquitectura

La aplicación se compone de dos servicios:

1. **Backend** (Flask/Python) - Puerto 5000
   - Procesamiento de PDFs
   - Detección de datos sensibles
   - API REST

2. **Frontend** (Next.js) - Puerto 3030
   - Interfaz de usuario
   - Carga de archivos
   - Visualización de resultados

## Inicio Rápido

### 1. Construir y levantar los servicios

```bash
docker-compose up -d --build
```

Este comando:
- Construye las imágenes de Docker
- Crea los contenedores
- Inicia los servicios en background

### 2. Verificar el estado

```bash
docker-compose ps
```

Deberías ver ambos servicios como "running".

### 3. Ver los logs

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs solo del backend
docker-compose logs -f backend

# Logs solo del frontend
docker-compose logs -f frontend
```

### 4. Acceder a la aplicación

- **Frontend**: http://localhost:3030
- **Backend API**: http://localhost:5000
- **Health check**: http://localhost:5000/health

## Comandos Útiles

### Detener los servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes

```bash
docker-compose down -v
```

### Reconstruir solo un servicio

```bash
# Reconstruir backend
docker-compose up -d --build backend

# Reconstruir frontend
docker-compose up -d --build frontend
```

### Reiniciar un servicio

```bash
docker-compose restart backend
docker-compose restart frontend
```

### Ejecutar comandos dentro de un contenedor

```bash
# Acceder al shell del backend
docker-compose exec backend /bin/bash

# Acceder al shell del frontend
docker-compose exec frontend /bin/sh
```

### Ver uso de recursos

```bash
docker stats
```

## Configuración

### Variables de Entorno

El archivo `docker-compose.yml` incluye las siguientes variables de entorno:

**Backend:**
- `PYTHONUNBUFFERED=1`: Output inmediato de Python
- `FLASK_ENV=production`: Modo producción
- `PARSER_SERVICE_URL`: URL del parser externo (por defecto `http://host.docker.internal:1000`)
- `PARSER_ENABLE_TIMEOUTS`: Activa timeouts en la llamada al parser cuando se establece en `1`, `true`, `yes` o `on`.  
  Si no se define (valor por defecto), el backend esperará indefinidamente a que el parser responda.
- `PARSER_CONNECT_TIMEOUT`, `PARSER_MIN_TIMEOUT`, `PARSER_TIMEOUT_PER_MB`, `PARSER_TIMEOUT_MAX`: Parámetros opcionales que solo se aplican cuando `PARSER_ENABLE_TIMEOUTS` está activo.

**Frontend:**
- `NODE_ENV=production`: Modo producción
- `NEXT_TELEMETRY_DISABLED=1`: Desactiva telemetría de Next.js
- `NEXT_PUBLIC_API_URL=http://backend:5000`: URL del backend

### Puertos

Si necesitas cambiar los puertos, edita el `docker-compose.yml`:

```yaml
ports:
  - "TU_PUERTO:3030"  # Frontend
  - "TU_PUERTO:5000"  # Backend
```

## Volúmenes

La aplicación utiliza un volumen para archivos temporales:

- `pdf-temp`: Almacena PDFs procesados temporalmente

## Red

Los servicios se comunican a través de una red Docker Bridge llamada `app-network`.

Cuando el parser externo corre en tu máquina anfitriona (fuera de Docker), se expone mediante `host.docker.internal`.  
Este hostname funciona en Windows/Mac automáticamente y en Linux se habilita gracias a `extra_hosts` dentro del `docker-compose.yml`.  
Si necesitas usar otra dirección (por ejemplo un parser remoto), puedes sobreescribir `PARSER_SERVICE_URL` al levantar los servicios:

```bash
PARSER_SERVICE_URL=http://192.168.0.98:1000 docker-compose up -d
```

También puedes definir `PARSER_SERVICE_URL_FALLBACKS` con una lista separada por comas para que el backend pruebe URLs alternativas antes de rendirse.

## Health Checks

El backend incluye un health check que verifica que el servicio está respondiendo:

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### El frontend no se conecta al backend

1. Verifica que el backend esté running:
   ```bash
   docker-compose ps backend
   ```

2. Verifica los logs del backend:
   ```bash
   docker-compose logs backend
   ```

3. Verifica el health check:
   ```bash
   curl http://localhost:5000/health
   ```

### Error de memoria

Si encuentras errores de memoria durante el build, aumenta la memoria de Docker:

- **Docker Desktop**: Settings > Resources > Memory

### Reconstrucción completa

Si tienes problemas, intenta una reconstrucción desde cero:

```bash
# Detener y eliminar todo
docker-compose down -v

# Eliminar imágenes
docker-compose rm -f

# Reconstruir desde cero
docker-compose up -d --build --force-recreate
```

## Producción

Para despliegue en producción, considera:

1. **Variables de entorno**: Usa archivos `.env` para configuración sensible
2. **HTTPS**: Configura un reverse proxy (nginx, traefik)
3. **Límites de recursos**: Añade límites de memoria y CPU en docker-compose
4. **Logs**: Configura un sistema de logging centralizado
5. **Backups**: Implementa backups de los volúmenes
6. **Monitoreo**: Añade herramientas de monitoreo (Prometheus, Grafana)

### Ejemplo de límites de recursos:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Desarrollo

Para desarrollo local con hot-reload, puedes montar los directorios:

```yaml
services:
  backend:
    volumes:
      - ./backend:/app
  frontend:
    volumes:
      - ./src:/app/src
      - ./public:/app/public
```

Y cambiar los comandos a modo desarrollo.
