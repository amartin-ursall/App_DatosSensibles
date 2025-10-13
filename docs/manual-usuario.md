# Manual de uso básico

Este documento explica cómo usar la aplicación, sus funcionalidades básicas y el significado de cada botón. Incluye instrucciones paso a paso y un lugar indicado para insertar una captura de pantalla.

## 1) Acceso a la aplicación
- Opción rápida: ejecuta `start.bat` en la carpeta raíz del proyecto (inicia backend en `http://localhost:5000` y frontend en `http://localhost:9002`).
- Opción manual:
  - Backend (Python): `cd backend` y `python app.py` (requiere dependencias de `backend/requirements.txt`).
  - Frontend (Next.js): `npm install` en la raíz y luego `npm run dev` (abre `http://localhost:9002`).
- Abre `http://localhost:9002` en tu navegador.

## 2) Vista general de la interfaz
- Cabecera: título “Aplicación de Privacidad”.
- Sidebar izquierda “Ajustes”: contiene las reglas de redacción y el nivel de sensibilidad.
- Área principal:
  - “Buscar Archivos” para seleccionar el archivo.
  - Tras analizar, muestra estadísticas y el contenido original / subrayado (texto) o una vista previa (PDF).

> Inserte aquí una captura de la pantalla principal
> Ruta sugerida: `docs/img/pantalla-principal.png`
> Cómo agregarla: crea la carpeta `docs/img/` y guarda la imagen como `pantalla-principal.png`. Luego reemplaza este bloque por `![Pantalla principal](./img/pantalla-principal.png)`.

## 3) Tipos de archivo soportados
- Texto: `.txt`, `.csv`, `.md`, `.json`, `.log`
- PDF: `.pdf`
- Si intentas subir un tipo no soportado, verás un aviso en la parte inferior derecha.

## 4) Paso a paso para analizar un archivo
1. Abre la app en `http://localhost:9002`.
2. Pulsa “Buscar Archivos” y selecciona tu documento.
3. El análisis comienza automáticamente:
   - Si es texto: se detectan datos sensibles y se subrayan en el resultado.
   - Si es PDF: se genera un PDF con subrayado, mostrado en una vista previa.
4. Revisa las “Estadísticas de Detección” (total y tipos detectados).
5. Usa “Descargar” para guardar el resultado.
6. Usa “Procesar Otro Archivo” para reiniciar y cargar otro documento.

## 5) Ajustes de redacción (Sidebar)
- Reglas de Redacción:
  - Lista de reglas con interruptores (Switch) individuales para activar/desactivar cada una.
  - Botones “Activar todas” y “Desactivar todas” ubicados justo debajo del título “Reglas de Redacción”.
- Nivel de Sensibilidad:
  - “Estricto”: mayor umbral de confianza (80%).
  - “Normal”: equilibrio recomendado (65%).
  - “Relajado”: detecta solo coincidencias de alta confianza.

## 6) Qué hace cada botón y control
- “Buscar Archivos”: abre el selector de archivos del sistema.
- “Activar todas” / “Desactivar todas”: en Ajustes, activan o desactivan todas las reglas a la vez.
- Interruptor (Switch) por cada regla: activa/desactiva una regla individual.
- Radio “Nivel de Sensibilidad”: selecciona el umbral de detección.
- “Descargar”: guarda el contenido procesado:
  - Texto: genera un archivo con el texto subrayado.
  - PDF: descarga el PDF con subrayado.
- “Procesar Otro Archivo”: vuelve a la pantalla de subida.

## 7) Resultados y visualización
- Texto:
  - Panel “Original”: muestra el archivo tal cual.
  - Panel “Con Subrayado”: muestra el texto con marcas `__texto__` que se visualizan subrayadas.
- PDF:
  - Vista previa embebida del PDF con subrayado en rojo.
  - Si la vista tarda, aparecerá un estado de carga.

## 8) Consejos y solución de problemas
- Asegura que el backend Python esté corriendo en `http://localhost:5000`.
- Si ves errores de tipo de archivo, verifica que sea uno de los soportados.
- Si el frontend no carga, confirma que `npm run dev` está en ejecución y que el puerto `9002` está libre.
- Si el PDF no se ve, intenta descargarlo y abrirlo localmente; puede estar encriptado o mal formado.

## 9) Seguridad
- El análisis ocurre de forma local (backend Python). Los datos sensibles se subrayan para que puedas identificarlos fácilmente sin exponerlos a servicios externos.

## 10) Dónde ubicar más imágenes en el manual
- Crea `docs/img/` y añade más capturas:
  - `docs/img/ajustes.png`: captura mostrando la sidebar con reglas y sensibilidad.
  - `docs/img/resultado-texto.png`: captura con el texto original y el subrayado.
  - `docs/img/resultado-pdf.png`: captura con la vista previa del PDF.
- Inserta las imágenes en este archivo con `![Título](./img/nombre.png)`.