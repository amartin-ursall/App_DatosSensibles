# Iniciar la Aplicación

## Requisitos previos

### Backend Python
1. Python 3.8 o superior instalado
2. pip actualizado

### Frontend Next.js
1. Node.js 18 o superior instalado
2. npm instalado

## Instalación

### 1. Backend Python

```bash
# Ir al directorio backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Frontend Next.js

```bash
# Ir al directorio raíz
cd ..

# Instalar dependencias (si no lo has hecho)
npm install
```

## Iniciar la aplicación

### Opción 1: Dos terminales (recomendado)

**Terminal 1 - Backend Python:**
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
python app.py
```

Debería ver:
```
🚀 Iniciando servidor Flask...
📁 Directorio temporal: /tmp
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Frontend Next.js:**
```bash
npm run dev
```

Debería ver:
```
▲ Next.js 15.3.3
- Local:        http://localhost:9002
```

### Opción 2: Script automatizado (Windows)

Crear archivo `start.bat` en la raíz:
```batch
@echo off
echo Iniciando Backend Python...
start cmd /k "cd backend && venv\Scripts\activate && python app.py"

timeout /t 3 /nobreak

echo Iniciando Frontend Next.js...
start cmd /k "npm run dev"

echo.
echo Servidores iniciados:
echo - Backend Python: http://localhost:5000
echo - Frontend Next.js: http://localhost:9002
```

Ejecutar: `start.bat`

### Opción 3: Script automatizado (Linux/Mac)

Crear archivo `start.sh` en la raíz:
```bash
#!/bin/bash

echo "Iniciando Backend Python..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

sleep 3

echo "Iniciando Frontend Next.js..."
cd ..
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Servidores iniciados:"
echo "- Backend Python: http://localhost:5000 (PID: $BACKEND_PID)"
echo "- Frontend Next.js: http://localhost:9002 (PID: $FRONTEND_PID)"
echo ""
echo "Presiona Ctrl+C para detener ambos servidores"

# Esperar a que se presione Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

Dar permisos y ejecutar:
```bash
chmod +x start.sh
./start.sh
```

## Verificar que funciona

1. **Backend Python**: Abrir http://localhost:5000/health
   - Debería ver: `{"status": "ok", "service": "sensitive-data-detector", "version": "1.0.0"}`

2. **Frontend Next.js**: Abrir http://localhost:9002
   - Debería ver la interfaz de la aplicación

3. **Prueba completa**:
   - Subir un PDF de prueba
   - Activar algunas reglas (DNI, Email, Teléfono)
   - Click en "Procesar"
   - Debería detectar y subrayar los datos sensibles

## Troubleshooting

### Backend no inicia

**Error: "No module named 'fitz'"**
```bash
pip install pymupdf
```

**Error: "Port 5000 already in use"**
- Cambiar puerto en `backend/app.py`:
  ```python
  app.run(host='0.0.0.0', port=5001, debug=True)
  ```
- Y actualizar en `src/app/page.tsx`:
  ```typescript
  const response = await fetch('http://localhost:5001/api/process-pdf', {
  ```

### Frontend no conecta con backend

**Error: "CORS error"**
- Verificar que Flask-CORS esté instalado:
  ```bash
  pip install flask-cors
  ```

**Error: "Connection refused"**
- Verificar que el backend esté corriendo en http://localhost:5000
- Probar: `curl http://localhost:5000/health`

### PDF no se procesa

**Error: "Invalid file type"**
- Solo se aceptan archivos .pdf

**Error: "Error processing PDF"**
- Ver logs del backend Python
- Verificar que el PDF no esté encriptado
- Verificar que tenga texto extraíble (no solo imagen)

## Detener la aplicación

### Opción 1: Ctrl+C en cada terminal

### Opción 2: Windows Task Manager
- Buscar procesos: `python.exe` y `node.exe`
- Terminar procesos

### Opción 3: Linux/Mac
```bash
# Encontrar PIDs
ps aux | grep python
ps aux | grep node

# Matar procesos
kill <PID>
```

## Testing

### Test del backend Python
```bash
cd backend
python test_detector.py
```

### Test manual con curl
```bash
# Detectar texto
curl -X POST http://localhost:5000/api/detect-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Juan Perez, DNI: 12345678Z, Email: juan@example.com",
    "rules": {"dni": true, "email": true},
    "sensitivityLevel": "normal"
  }'

# Validar dato
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "value": "12345678Z",
    "type": "dni"
  }'
```

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│          Frontend Next.js (port 9002)           │
│  - UI/UX                                        │
│  - File upload                                  │
│  - Results display                              │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   │
┌──────────────────▼──────────────────────────────┐
│        Backend Python (port 5000)               │
│  - PDF processing (PyMuPDF)                     │
│  - Text detection (regex + validators)          │
│  - Coordinates search (fuzzy matching)          │
│  - Highlighting/Redaction                       │
└─────────────────────────────────────────────────┘
```

## Próximos pasos

- [ ] OCR para PDFs escaneados con `ocrmypdf`
- [ ] Batch processing de múltiples archivos
- [ ] Configuración de patrones personalizados
- [ ] Export de auditoría (JSON con detecciones)
- [ ] Integración con bases de datos
