"""
Script de prueba para OCR con Microsoft TrOCR
Procesa el PDF de Canarias usando OCR local
"""
import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_ocr():
    """Prueba el OCR con el PDF de Canarias"""
    from ocr_processor import ocr_processor

    pdf_path = r"incidencias\Canarias_scan_20250603_075732.pdf"

    if not os.path.exists(pdf_path):
        print(f"ERROR: No se encuentra el archivo {pdf_path}")
        return False

    print(f"\n{'='*80}")
    print(f"TEST OCR: Canarias_scan_20250603_075732.pdf")
    print(f"{'='*80}\n")

    # Verificar dependencias
    if not ocr_processor.can_use_ocr():
        print("[ERROR] Dependencias OCR no instaladas")
        print("[INFO] Instala con: pip install transformers torch pillow")
        return False

    print("[OK] Dependencias OCR disponibles\n")

    try:
        # Extraer texto con OCR
        print("[PASO 1] Extrayendo texto con OCR...")
        parsed_data = ocr_processor.extract_text_from_pdf(pdf_path)

        print(f"\n[PASO 2] Analizando resultados...")
        if 'pages' in parsed_data:
            num_pages = len(parsed_data['pages'])
            print(f"  Paginas extraidas: {num_pages}")

            total_chars = 0
            for i, page in enumerate(parsed_data['pages'], 1):
                if isinstance(page, dict):
                    text = page.get('text', '')
                else:
                    text = page

                chars = len(text)
                total_chars += chars
                print(f"  Pagina {i}: {chars} caracteres")

                if i == 1 and chars > 0:
                    print(f"\n  Preview pagina 1:")
                    print(f"  {'-'*80}")
                    print(f"  {text[:500]}")
                    print(f"  {'-'*80}")

            print(f"\n[RESULTADO]")
            print(f"  Total caracteres extraidos: {total_chars}")

            if total_chars > 100:
                print(f"  [OK] OCR extrajo texto correctamente")
                return True
            else:
                print(f"  [ERROR] OCR extrajo muy poco texto")
                return False
        else:
            print(f"[ERROR] Formato de respuesta invalido")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error ejecutando OCR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    success = test_ocr()
    sys.exit(0 if success else 1)
