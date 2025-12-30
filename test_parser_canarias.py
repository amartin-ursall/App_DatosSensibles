"""
Test del parser externo con Canarias_scan_20250603_075732.pdf
"""
import sys
import os
import requests
import json

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_parser_on_canarias():
    """Prueba el parser externo con el PDF de Canarias"""
    pdf_path = r"incidencias\Canarias_scan_20250603_075732.pdf"

    if not os.path.exists(pdf_path):
        print(f"ERROR: No se encuentra el archivo {pdf_path}")
        return

    print(f"\n{'='*80}")
    print(f"TEST PARSER EXTERNO: Canarias_scan_20250603_075732.pdf")
    print(f"{'='*80}\n")

    # Calcular tamaño
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"[INFO] Tamano del archivo: {file_size_mb:.2f} MB")

    # Calcular timeout
    if file_size_mb <= 5:
        timeout = 120
    else:
        timeout = 120 + int((file_size_mb - 5) * 30)
    timeout = min(timeout, 600)

    print(f"[INFO] Timeout configurado: {timeout}s")

    parser_url = os.getenv("PARSER_SERVICE_URL", "http://127.0.0.1:1000")

    try:
        print(f"\n[PASO 1] Enviando PDF al parser externo...")
        print(f"  URL: {parser_url}/parse")

        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            print(f"  Esperando respuesta (puede tardar varios minutos)...")

            response = requests.post(
                f"{parser_url}/parse",
                files=files,
                timeout=timeout
            )

        print(f"\n[PASO 2] Analizando respuesta...")
        print(f"  Status code: {response.status_code}")

        if response.status_code == 200:
            print(f"  OK Respuesta recibida")

            try:
                parsed_data = response.json()

                print(f"\n[PASO 3] Estructura del JSON recibido")
                print(f"  Claves principales: {list(parsed_data.keys())}")

                if 'pages' in parsed_data:
                    num_pages = len(parsed_data['pages'])
                    print(f"  OK Numero de paginas: {num_pages}")

                    # Analizar primera página
                    if num_pages > 0:
                        print(f"\n[PASO 4] Analizando primera pagina...")
                        first_page = parsed_data['pages'][0]
                        print(f"  Tipo: {type(first_page)}")

                        if isinstance(first_page, dict):
                            print(f"  Claves: {list(first_page.keys())}")

                            # Buscar campo de texto
                            text = first_page.get('text') or first_page.get('content') or first_page.get('extracted_text')

                            if text:
                                print(f"\n[RESULTADO] Texto extraido correctamente")
                                print(f"  Longitud: {len(text)} caracteres")
                                print(f"  Preview (primeros 500 caracteres):")
                                print(f"  {'-'*80}")
                                print(f"  {text[:500]}")
                                print(f"  {'-'*80}")

                                # Buscar datos sensibles comunes
                                print(f"\n[BUSQUEDA RAPIDA]")
                                import re
                                phones = re.findall(r'\d{3}\s?\d{3}\s?\d{3}', text)
                                emails = re.findall(r'\S+@\S+\.\S+', text)
                                dnis = re.findall(r'\d{8}[A-Z]', text)

                                print(f"  Telefonos encontrados: {len(phones)}")
                                if phones:
                                    for p in phones[:3]:
                                        print(f"    - {p}")

                                print(f"  Emails encontrados: {len(emails)}")
                                if emails:
                                    for e in emails[:3]:
                                        print(f"    - {e}")

                                print(f"  DNIs encontrados: {len(dnis)}")
                                if dnis:
                                    for d in dnis[:3]:
                                        print(f"    - {d}")

                                return True
                            else:
                                print(f"\n[ERROR] No se encontro campo de texto en la pagina")
                                print(f"  Contenido de la pagina:")
                                print(f"  {str(first_page)[:500]}")
                                return False
                        elif isinstance(first_page, str):
                            print(f"\n[RESULTADO] Pagina es string directo")
                            print(f"  Longitud: {len(first_page)} caracteres")
                            print(f"  Preview: {first_page[:500]}")
                            return True
                        else:
                            print(f"\n[ERROR] Tipo de pagina no reconocido: {type(first_page)}")
                            return False
                else:
                    print(f"\n[ERROR] No se encontro campo 'pages' en la respuesta")
                    print(f"  Estructura: {str(parsed_data)[:500]}")
                    return False

            except ValueError as e:
                print(f"\n[ERROR] No se pudo decodificar JSON: {e}")
                print(f"  Respuesta raw: {response.text[:500]}")
                return False
        else:
            print(f"\n[ERROR] HTTP {response.status_code}")
            print(f"  Respuesta: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Timeout despues de {timeout}s")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"\n[ERROR] No se pudo conectar al servicio")
        print(f"  Error: {e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    success = test_parser_on_canarias()
    if success:
        print("OK El parser externo puede extraer texto del PDF")
    else:
        print("ERROR El parser externo no pudo extraer texto correctamente")
