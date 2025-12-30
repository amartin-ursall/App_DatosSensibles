"""
Script de diagnóstico para investigar el problema de superposición de texto
"""
import fitz  # PyMuPDF
import sys

def diagnose_pdf(pdf_path):
    """Analiza la estructura del PDF para entender el problema"""
    print(f"\n{'='*60}")
    print(f"DIAGNÓSTICO DE PDF: {pdf_path}")
    print(f"{'='*60}\n")

    doc = fitz.open(pdf_path)

    # Analizar primera página
    page = doc[0]

    print(f"[INFO] Página 1 de {len(doc)}")
    print(f"  Tamaño: {page.rect}")
    print(f"  Rotación: {page.rotation}")

    # Analizar texto
    text_dict = page.get_text("dict")
    print(f"\n[TEXTO]")
    print(f"  Bloques de texto: {len(text_dict['blocks'])}")

    # Analizar primer bloque
    if text_dict['blocks']:
        first_block = text_dict['blocks'][0]
        print(f"  Tipo de primer bloque: {first_block.get('type', 'unknown')}")
        if 'lines' in first_block:
            print(f"  Líneas en primer bloque: {len(first_block['lines'])}")
            if first_block['lines']:
                first_line = first_block['lines'][0]
                if 'spans' in first_line:
                    print(f"  Spans en primera línea: {len(first_line['spans'])}")
                    for i, span in enumerate(first_line['spans'][:3]):
                        print(f"    Span {i}: font='{span.get('font', 'N/A')}' size={span.get('size', 'N/A')}")
                        print(f"            text='{span.get('text', 'N/A')[:50]}'")

    # Buscar texto específico y ver sus rectángulos
    print(f"\n[BÚSQUEDA DE TEXTO]")
    test_searches = [
        "648",  # Dirección
        "Barcelona",
        "932 052 213"  # Teléfono
    ]

    for search_text in test_searches:
        rects = page.search_for(search_text, quads=False)
        print(f"  '{search_text}': {len(rects)} coincidencia(s)")
        for i, rect in enumerate(rects[:2]):  # Solo primeras 2
            print(f"    Rect {i}: {rect}")
            # Extraer texto en esa área
            extracted = page.get_textbox(rect)
            print(f"    Texto en rect: '{extracted.strip()}'")

    # Analizar fuentes
    print(f"\n[FUENTES]")
    fonts = set()
    for block in text_dict['blocks']:
        if block.get('type') == 0:  # Bloque de texto
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    fonts.add(span.get('font', 'unknown'))
    print(f"  Fuentes únicas: {len(fonts)}")
    for font in list(fonts)[:5]:
        print(f"    - {font}")

    # Test de dibujo
    print(f"\n[TEST DE DIBUJO]")
    print(f"  Probando dibujar rectángulo negro sobre 'Barcelona'...")
    rects = page.search_for("Barcelona", quads=False)
    if rects:
        rect = rects[0]
        expanded = fitz.Rect(rect.x0 - 2, rect.y0 - 2, rect.x1 + 2, rect.y1 + 2)

        # Probar con shape
        shape = page.new_shape()
        shape.draw_rect(expanded)
        shape.finish(fill=(0, 0, 0), color=(0, 0, 0), width=0)
        shape.commit()

        # Guardar para inspección
        test_output = pdf_path.replace('.pdf', '_test_draw.pdf')
        doc.save(test_output)
        print(f"  ✓ Guardado en: {test_output}")

        # Reabrir y verificar
        doc2 = fitz.open(test_output)
        page2 = doc2[0]
        text_after = page2.get_textbox(expanded)
        print(f"  Texto después de dibujar: '{text_after.strip()}'")
        doc2.close()

    doc.close()
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    pdf_path = r"incidencias\Original.pdf"
    diagnose_pdf(pdf_path)
