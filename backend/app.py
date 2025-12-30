"""
API Flask para procesamiento de PDFs
Expone endpoints para el frontend Next.js
"""
import os
import tempfile
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf_processor import pdf_processor
from detector import detector
import fitz  # PyMuPDF para conversin de imgenes
import time
from threading import Lock
from typing import Any, Dict, Optional

app = Flask(__name__)
# Permitir CORS para Next.js y exponer headers personalizados
CORS(app, expose_headers=['X-Total-Matches', 'X-Matches-By-Type', 'X-Pages-Processed'])

# Configuración
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

progress_lock = Lock()
progress_state: Dict[str, Dict[str, Any]] = {}

def _update_progress(progress_id: Optional[str], **updates):
    """Actualiza el estado de progreso para un identificador dado."""
    if not progress_id:
        return
    updates.setdefault('updatedAt', time.time())
    with progress_lock:
        state = progress_state.get(progress_id, {})
        state.update(updates)
        state['progressId'] = progress_id
        progress_state[progress_id] = state

def _get_progress(progress_id: str) -> Optional[Dict[str, Any]]:
    with progress_lock:
        state = progress_state.get(progress_id)
        return dict(state) if state else None

def _clear_progress(progress_id: Optional[str]) -> None:
    if not progress_id:
        return
    with progress_lock:
        progress_state.pop(progress_id, None)



def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image(filename):
    """Verifica si el archivo es una imagen"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'jpg', 'jpeg', 'png'}


def convert_image_to_pdf(image_path, output_pdf_path):
    """
    Convierte una imagen a PDF

    Args:
        image_path: Ruta a la imagen
        output_pdf_path: Ruta donde guardar el PDF

    Returns:
        True si la conversión fue exitosa, False en caso contrario
    """
    try:
        print(f"[IMG→PDF] Convirtiendo imagen a PDF: {image_path}")

        # Crear un nuevo documento PDF
        doc = fitz.open()

        # Abrir la imagen
        img = fitz.open(image_path)

        # Obtener el primer (y único) pixmap de la imagen
        pix = fitz.Pixmap(image_path)

        # Crear una página con el tamaño de la imagen
        # Usar A4 como máximo, escalando si es necesario
        img_width = pix.width
        img_height = pix.height

        # A4 size in points (595 x 842)
        a4_width = 595
        a4_height = 842

        # Calcular escala para que quepa en A4 si es más grande
        scale = min(a4_width / img_width, a4_height / img_height, 1.0)

        page_width = img_width * scale
        page_height = img_height * scale

        # Crear página
        page = doc.new_page(width=page_width, height=page_height)

        # Insertar la imagen
        rect = fitz.Rect(0, 0, page_width, page_height)
        page.insert_image(rect, filename=image_path)

        # Guardar el PDF
        doc.save(output_pdf_path)
        doc.close()
        pix = None

        print(f"[IMG→PDF] ✓ Conversión exitosa: {output_pdf_path}")
        return True

    except Exception as e:
        print(f"[IMG→PDF] ✗ Error al convertir imagen: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.route('/api/progress/<progress_id>', methods=['GET'])
def get_progress_status(progress_id: str):
    """Devuelve el estado de progreso asociado a un identificador."""
    data = _get_progress(progress_id)
    if not data:
        return jsonify({'message': 'Progress not found'}), 404
    return jsonify(data)


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({
        'status': 'ok',
        'service': 'sensitive-data-detector',
        'version': '1.0.0'
    })


@app.route('/api/process-pdf', methods=['POST'])
def process_pdf():
    """
    Procesa un PDF para detectar y subrayar datos sensibles

    Request:
        - file: PDF file
        - rules: JSON string con reglas habilitadas
        - sensitivityLevel: 'strict', 'normal', 'relaxed'
        - action: 'highlight' (default) o 'redact'
        - extractionMode: 'auto', 'parser' o 'ocr'

    Response:
        - PDF procesado como archivo
        - Headers con estadísticas:
            - X-Total-Matches: número total de detecciones
            - X-Matches-By-Type: JSON con detecciones por tipo
            - X-Pages-Processed: número de páginas procesadas
    """
    try:
        # Validar que hay archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Obtener parámetros
        rules_json = request.form.get('rules', '{}')
        sensitivity_level = request.form.get('sensitivityLevel', 'normal')
        action = request.form.get('action', 'highlight')
        extraction_mode = (request.form.get('extractionMode', 'auto') or 'auto').lower()
        if extraction_mode not in {'parser', 'ocr', 'auto'}:
            extraction_mode = 'auto'

        progress_id = request.form.get('progressId')
        progress_callback = None
        if progress_id:
            _update_progress(
                progress_id,
                stage='queued',
                percent=0,
                currentPage=0,
                totalPages=0,
                extractionMethod=extraction_mode,
                done=False,
            )

            def _progress_callback(update: Dict[str, Any]):
                data = dict(update) if update else {}
                percent = data.get('percent')
                if percent is not None:
                    try:
                        data['percent'] = max(0, min(99, int(percent)))
                    except (ValueError, TypeError):
                        data.pop('percent', None)
                _update_progress(progress_id, **data)

            progress_callback = _progress_callback

        # Parsear reglas
        try:
            rules = json.loads(rules_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid rules JSON'}), 400

        # Guardar archivo temporal
        filename = secure_filename(file.filename)
        original_input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'input_{filename}')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'output_{filename}')

        file.save(original_input_path)

        if progress_id:
            _update_progress(progress_id, stage='saved-input', percent=5, currentPage=0)

        # Si es una imagen, convertirla a PDF primero
        input_path = original_input_path
        pdf_filename = filename

        if is_image(filename):
            print(f"[IMAGEN] Detectada imagen: {filename}")
            pdf_filename = filename.rsplit('.', 1)[0] + '.pdf'
            pdf_input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'converted_{pdf_filename}')

            if not convert_image_to_pdf(original_input_path, pdf_input_path):
                return jsonify({'error': 'Error converting image to PDF'}), 500

            input_path = pdf_input_path
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'output_{pdf_filename}')
            print(f"[IMAGEN] ✓ Imagen convertida a PDF para procesamiento")

            if progress_id:
                _update_progress(progress_id, stage='image-converted', percent=8, currentPage=0)

        try:
            # Procesar PDF (original o convertido desde imagen)
            print(f"[PROCESO] Procesando: {pdf_filename}")
            print(f"          Reglas: {sum(rules.values())} habilitadas")
            print(f"          Sensibilidad: {sensitivity_level}")
            print(f"          Accion: {action}")
            print(f"          Modo extraccion: {extraction_mode}")

            if progress_id:
                _update_progress(progress_id, stage='starting-processing', percent=10, currentPage=0, extractionMethod=extraction_mode)

            stats = pdf_processor.process_pdf(
                input_path,
                output_path,
                rules,
                sensitivity_level,
                action,
                extraction_mode,
                progress_callback=progress_callback
            )

            print(f"[OK] Procesado: {stats['total_matches']} deteccion(es)")
            print(f"[STATS] Por tipo: {stats['by_type']}")

            if progress_id:
                _update_progress(
                    progress_id,
                    stage='completed',
                    percent=100,
                    done=True,
                    currentPage=stats.get('pages_processed'),
                    totalPages=stats.get('pages_processed'),
                )

            # Retornar PDF procesado
            response = send_file(
                output_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'redacted_{pdf_filename}'
            )

            # Añadir headers con estadísticas
            response.headers['X-Total-Matches'] = str(stats['total_matches'])
            response.headers['X-Matches-By-Type'] = json.dumps(stats['by_type'])
            response.headers['X-Pages-Processed'] = str(stats['pages_processed'])

            print(f"[HEADERS] X-Total-Matches: {response.headers.get('X-Total-Matches')}")
            print(f"[HEADERS] X-Matches-By-Type: {response.headers.get('X-Matches-By-Type')}")

            return response

        finally:
            # Limpiar archivos temporales
            if os.path.exists(original_input_path):
                os.remove(original_input_path)

            # Si convertimos una imagen a PDF, limpiar el PDF temporal también
            if is_image(filename) and input_path != original_input_path and os.path.exists(input_path):
                os.remove(input_path)

            # No eliminar output_path aún, send_file lo necesita

    except Exception as e:
        print(f"[ERROR] Error procesando PDF: {str(e)}")
        if progress_id:
            _update_progress(progress_id, stage='error', percent=100, done=True, message=str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error processing PDF',
            'details': str(e)
        }), 500


@app.route('/api/detect-text', methods=['POST'])
def detect_text():
    """
    Detecta datos sensibles en texto plano

    Request:
        {
            "text": "texto a analizar",
            "rules": {"email": true, "phone": true, ...},
            "sensitivityLevel": "normal"
        }

    Response:
        {
            "matches": [
                {
                    "type": "email",
                    "value": "test@example.com",
                    "start": 10,
                    "end": 27,
                    "confidence": 0.95,
                    "context": "...contexto..."
                }
            ],
            "stats": {
                "total": 1,
                "by_type": {"email": 1}
            }
        }
    """
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        rules = data.get('rules', {})
        sensitivity_level = data.get('sensitivityLevel', 'normal')

        # Detectar datos sensibles
        matches = detector.detect(text, rules, sensitivity_level)

        # Calcular estadísticas
        stats = {
            'total': len(matches),
            'by_type': {}
        }

        for match in matches:
            match_type = match['type']
            stats['by_type'][match_type] = stats['by_type'].get(match_type, 0) + 1

        return jsonify({
            'matches': matches,
            'stats': stats
        })

    except Exception as e:
        print(f"[ERROR] Error detectando texto: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error detecting sensitive data',
            'details': str(e)
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_data():
    """
    Valida un dato específico

    Request:
        {
            "value": "12345678Z",
            "type": "dni"
        }

    Response:
        {
            "valid": true,
            "normalized": "12345678Z"
        }
    """
    try:
        data = request.get_json()

        if not data or 'value' not in data or 'type' not in data:
            return jsonify({'error': 'Missing value or type'}), 400

        from validators import validator
        from normalizer import normalizer

        value = data['value']
        data_type = data['type']

        normalized = normalizer.normalize_for_validation(value, data_type)
        is_valid = validator.validate(normalized, data_type)

        return jsonify({
            'valid': is_valid,
            'normalized': normalized
        })

    except Exception as e:
        print(f"[ERROR] Error validando: {str(e)}")
        return jsonify({
            'error': 'Error validating data',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("  INICIANDO SERVIDOR FLASK")
    print("=" * 60)
    print(f"  Directorio temporal: {UPLOAD_FOLDER}")
    print(f"  Puerto: 5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
