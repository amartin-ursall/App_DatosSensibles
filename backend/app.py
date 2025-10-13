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

app = Flask(__name__)
# Permitir CORS para Next.js y exponer headers personalizados
CORS(app, expose_headers=['X-Total-Matches', 'X-Matches-By-Type', 'X-Pages-Processed'])

# Configuración
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        # Parsear reglas
        try:
            rules = json.loads(rules_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid rules JSON'}), 400

        # Guardar archivo temporal
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'input_{filename}')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'output_{filename}')

        file.save(input_path)

        try:
            # Procesar PDF
            print(f"[PDF] Procesando: {filename}")
            print(f"      Reglas: {sum(rules.values())} habilitadas")
            print(f"      Sensibilidad: {sensitivity_level}")
            print(f"      Accion: {action}")

            stats = pdf_processor.process_pdf(
                input_path,
                output_path,
                rules,
                sensitivity_level,
                action
            )

            print(f"[OK] Procesado: {stats['total_matches']} deteccion(es)")
            print(f"[STATS] Por tipo: {stats['by_type']}")

            # Retornar PDF procesado
            response = send_file(
                output_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'redacted_{filename}'
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
            if os.path.exists(input_path):
                os.remove(input_path)
            # No eliminar output_path aún, send_file lo necesita

    except Exception as e:
        print(f"[ERROR] Error procesando PDF: {str(e)}")
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
