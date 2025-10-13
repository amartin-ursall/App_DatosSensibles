# Backend Python - Detector de Datos Sensibles

Backend en Python para la detección y redacción de datos sensibles en PDFs y texto.

## Arquitectura

Implementa el pipeline robusto definido en `docs/blueprint.md`:

1. **Normalización** (`normalizer.py`): Maneja ligaduras, guiones, espacios
2. **Detección** (`detector.py`): Regex + validaciones + contexto
3. **Validación** (`validators.py`): IBAN (mod-97), Luhn, NIF/NIE/CIF
4. **Procesamiento PDF** (`pdf_processor.py`): PyMuPDF para coordenadas + subrayado
5. **API** (`app.py`): Flask con endpoints para el frontend

## Tecnologías

- **PyMuPDF (fitz)**: Lectura, búsqueda con coordenadas, subrayado/redacción nativa
- **pdfplumber**: Extracción de palabras con cajas (coordenadas)
- **python-stdnum**: Validaciones robustas (IBAN, Luhn, NIF, NIE, CIF)
- **regex**: Patrones tolerantes a espacios/saltos
- **ftfy**: Arregla ligaduras y encoding
- **rapidfuzz**: Fuzzy matching para búsqueda elástica
- **Flask**: API REST

## Instalación

```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Iniciar servidor

```bash
python app.py
```

El servidor escuchará en `http://localhost:5000`

### Endpoints

#### 1. Procesar PDF

```bash
POST /api/process-pdf

Form Data:
- file: PDF file
- rules: JSON string con reglas {"email": true, "dni": true, ...}
- sensitivityLevel: "strict" | "normal" | "relaxed"
- action: "highlight" (subrayar) | "redact" (eliminar)

Response:
- PDF procesado con datos sensibles marcados
- Headers:
  - X-Total-Matches: número total
  - X-Matches-By-Type: JSON por tipo
  - X-Pages-Processed: páginas procesadas
```

#### 2. Detectar en texto

```bash
POST /api/detect-text

Body:
{
  "text": "Juan Perez, DNI: 12345678A, Email: juan@example.com",
  "rules": {"email": true, "dni": true},
  "sensitivityLevel": "normal"
}

Response:
{
  "matches": [
    {
      "type": "dni",
      "value": "12345678A",
      "start": 18,
      "end": 27,
      "confidence": 0.95,
      "context": "...Juan Perez, DNI: 12345678A, Email..."
    }
  ],
  "stats": {
    "total": 2,
    "by_type": {"dni": 1, "email": 1}
  }
}
```

#### 3. Validar dato

```bash
POST /api/validate

Body:
{
  "value": "12345678Z",
  "type": "dni"
}

Response:
{
  "valid": true,
  "normalized": "12345678Z"
}
```

#### 4. Health check

```bash
GET /health

Response:
{
  "status": "ok",
  "service": "sensitive-data-detector",
  "version": "1.0.0"
}
```

## Tipos de datos detectados

- **IBAN**: Validación con módulo 97
- **Tarjeta de crédito**: Algoritmo de Luhn
- **DNI español**: Validación de letra de control
- **NIE español**: Validación de letra de control
- **CIF español**: Validación de dígito de control
- **Email**: Formato RFC compliant
- **Teléfono**: Formatos españoles (9 dígitos)
- **Credenciales**: Contraseñas, API keys, tokens
- **Datos de salud**: Diagnósticos, medicación, historias clínicas

## Características

### Normalización robusta
- Sustituye ligaduras (ﬀ, ﬁ, ﬂ → ff, fi, fl)
- Une cortes de línea con guion (-\n → '')
- Colapsa espacios múltiples
- Arregla encoding con ftfy

### Búsqueda inteligente
- Búsqueda exacta con PyMuPDF
- Búsqueda normalizada si falla la exacta
- Fuzzy matching con rapidfuzz como fallback
- Tolerante a espacios y saltos de línea

### Validaciones robustas
- IBAN: módulo 97
- Tarjetas: Luhn
- DNI/NIE/CIF: letra/dígito de control
- Contexto: palabras clave cercanas

### Niveles de sensibilidad
- **Strict** (0.5): Detecta más, acepta menor confianza
- **Normal** (0.65): Balance recomendado
- **Relaxed** (0.8): Solo alta confianza

## Testing

```bash
# Probar con curl
curl -X POST http://localhost:5000/api/detect-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Juan Perez, DNI: 12345678A",
    "rules": {"dni": true},
    "sensitivityLevel": "normal"
  }'
```

## Desarrollo

```bash
# Activar entorno virtual
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar en modo desarrollo
pip install -r requirements.txt

# Ejecutar con auto-reload
python app.py
```

## Notas técnicas

### PyMuPDF vs otras librerías
- **PyMuPDF**: AGPL license, muy preciso para coordenadas
- Si necesitas Apache/MIT, usa: pypdf/pikepdf + borb

### OCR para PDFs escaneados
- Usar `ocrmypdf` antes de procesar
- Añade capa de texto alineada
- Luego aplicar detección normal

```python
import ocrmypdf
ocrmypdf.ocr("scan.pdf", "scan_ocr.pdf", language="spa", deskew=True)
```

## Troubleshooting

### Error: "No module named 'fitz'"
```bash
pip install pymupdf
```

### Error: "IBAN validation failed"
Asegúrate de que el IBAN esté en formato correcto (ES + 22 dígitos)

### PDF no se procesa
Verifica que:
1. El PDF no esté encriptado
2. Tenga texto extraíble (no sea solo imagen)
3. El tamaño sea < 50MB
