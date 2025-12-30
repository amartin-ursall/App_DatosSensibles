# Backend - Python Flask con OCR
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para PyMuPDF, pdfplumber y PyTorch
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descargar el modelo OCR para evitar latencia al iniciar
RUN python - <<'PY'
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

model_name = "microsoft/trocr-base-printed"
print(f"Descargando modelo {model_name} para cache local...")
TrOCRProcessor.from_pretrained(model_name)
VisionEncoderDecoderModel.from_pretrained(model_name)
print("Descarga completada.")
PY
# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 5000

# Variable de entorno para Python
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
