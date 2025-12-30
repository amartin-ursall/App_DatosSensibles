"""
Script de diagnóstico para Canarias_scan_20250603_075732.pdf
Investiga por qué no se subraya el contenido sensible
"""
import fitz  # PyMuPDF
import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from detector import detector
from normalizer import normalizer

def diagnose_canarias_pdf():
    """Analiza por qué no se detecta o marca contenido sensible"""
    pdf_path = r"incidencias\Canarias_scan_20250603_075732.pdf"

    if not os.path.exists(pdf_path):
        print(f"ERROR: No se encuentra el archivo {pdf_path}")
        return

    print(f"\n{'='*80}")
    print(f"DIAGNÓSTICO: Canarias_scan_20250603_075732.pdf")
    print(f"{'='*80}\n")

    doc = fitz.open(pdf_path)
    print(f"[INFO] Total páginas: {len(doc)}")

    # Analizar primera página
    page = doc[0]
    print(f"\n[PÁGINA 1]")
    print(f"  Tamaño: {page.rect}")
    print(f"  Rotación: {page.rotation}")

    # Extraer texto con PyMuPDF (método local)
    text_pymupdf = page.get_text()
    print(f"\n[TEXTO EXTRAÍDO - PyMuPDF LOCAL]")
    print(f"  Longitud: {len(text_pymupdf)} caracteres")
    print(f"  Preview (primeros 500 caracteres):")
    print(f"  {'-'*80}")
    print(f"  {text_pymupdf[:500]}")
    print(f"  {'-'*80}")

    # Detectar datos sensibles con todas las reglas habilitadas
    print(f"\n[DETECCIÓN DE DATOS SENSIBLES]")
    enabled_rules = {
        'dni': True,
        'nie': True,
        'cif': True,
        'email': True,
        'phone': True,
        'iban': True,
        'creditCard': True,
        'dateOfBirth': True,
        'address': True,
        'fullName': True,
        'numeroFactura': True,
        'numeroPoliza': True,
        'domicilio': True,
        'codigoPostal': True,
        'asegurado': True,
    }

    matches = detector.detect(
        text_pymupdf,
        enabled_rules,
        sensitivity_level='normal'
    )

    print(f"  Total detectados: {len(matches)}")

    if matches:
        print(f"\n[DATOS SENSIBLES DETECTADOS]")
        for i, match in enumerate(matches, 1):
            print(f"\n  [{i}] Tipo: {match['type']}")
            print(f"      Valor: {match['value']}")
            print(f"      Confianza: {match['confidence']:.2f}")
            print(f"      Posición: {match['start']}-{match['end']}")
            print(f"      Contexto: ...{match['context']}...")

            # Intentar buscar en el PDF
            print(f"      Búsqueda en PDF:")

            # Búsqueda exacta
            rects = page.search_for(match['value'], quads=False)
            print(f"        - Exacta: {len(rects)} coincidencias")

            # Búsqueda normalizada
            normalized = normalizer.normalize_for_search(match['value'])
            rects_norm = page.search_for(normalized, quads=False)
            print(f"        - Normalizada '{normalized}': {len(rects_norm)} coincidencias")

            # Búsqueda por palabras
            words = match['value'].split()
            if len(words) > 1:
                print(f"        - Por palabras: {words}")
                for word in words:
                    word_rects = page.search_for(word, quads=False)
                    print(f"          '{word}': {len(word_rects)} coincidencias")

            if rects:
                print(f"        ✓ SE PUEDE LOCALIZAR en el PDF")
                for rect in rects[:2]:
                    print(f"          Rect: {rect}")
            else:
                print(f"        ✗ NO SE PUEDE LOCALIZAR en el PDF")
                print(f"        RAZÓN: El texto extraído por PyMuPDF no coincide con el texto visual")
    else:
        print(f"  ⚠ NO SE DETECTARON DATOS SENSIBLES")
        print(f"  Esto puede deberse a:")
        print(f"    1. El PDF es escaneado y PyMuPDF no extrae texto correctamente")
        print(f"    2. El texto tiene formato especial que no detectan los regex")
        print(f"    3. La sensibilidad está muy alta")

    # Verificar si es PDF escaneado
    print(f"\n[VERIFICACIÓN DE PDF ESCANEADO]")
    images = page.get_images()
    print(f"  Imágenes en la página: {len(images)}")

    if len(images) > 0 and len(text_pymupdf) < 100:
        print(f"  ✓ Probablemente ES UN PDF ESCANEADO")
        print(f"  → Se requiere el parser externo (127.0.0.1:1000) con OCR")
    else:
        print(f"  ✓ Tiene texto extraíble con PyMuPDF")

    # Test de búsqueda manual de patrones comunes
    print(f"\n[TEST DE BÚSQUEDA MANUAL]")
    test_patterns = [
        ("Teléfono", r'\d{3}\s?\d{3}\s?\d{3}'),
        ("Email", r'\S+@\S+\.\S+'),
        ("DNI", r'\d{8}[A-Z]'),
        ("Dirección con número", r'[Cc]alle.*\d+'),
    ]

    import re
    for name, pattern in test_patterns:
        matches_manual = re.findall(pattern, text_pymupdf, re.IGNORECASE)
        if matches_manual:
            print(f"  {name}: {len(matches_manual)} encontrado(s)")
            for m in matches_manual[:3]:
                print(f"    - {m}")
        else:
            print(f"  {name}: No encontrado")

    doc.close()
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    diagnose_canarias_pdf()
