"""
Procesador de PDFs con PyMuPDF
Implementa el pipeline del blueprint:
- Extrae texto con coordenadas
- Busca matches por pÃ¡gina
- Subraya o redacta en coordenadas nativas
"""
import fitz  # PyMuPDF
import pdfplumber
import requests
import os
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple, Callable, Any
from pathlib import Path
from rapidfuzz import fuzz
from normalizer import normalizer
from detector import detector
from validators import validator
from ocr_processor import ocr_processor


class PDFProcessor:
    """Procesa PDFs para detectar y marcar datos sensibles"""

    def __init__(self):
        self.min_fuzzy_score = 80  # Score mÃ­nimo para fuzzy matching
        base_parser_url = os.getenv('PARSER_SERVICE_URL', 'http://127.0.0.1:1000').rstrip('/')
        self.parser_url = base_parser_url or 'http://127.0.0.1:1000'
        self.parser_url_candidates = self._build_parser_url_candidates(self.parser_url)
        self._current_page_ocr_lines: List[Dict] = []
        # Por defecto no aplicamos timeouts para esperar la respuesta todo el tiempo necesario.
        self.use_parser_timeouts = os.getenv('PARSER_ENABLE_TIMEOUTS', '').strip().lower() in {'1', 'true', 'yes', 'on'}
        self.parser_connect_timeout = float(os.getenv('PARSER_CONNECT_TIMEOUT', '15'))
        self.parser_min_timeout = float(os.getenv('PARSER_MIN_TIMEOUT', '120'))
        self.parser_timeout_per_mb = float(os.getenv('PARSER_TIMEOUT_PER_MB', '30'))
        self.parser_timeout_max = float(os.getenv('PARSER_TIMEOUT_MAX', '600'))

    def _build_parser_url_candidates(self, base_url: str) -> List[str]:
        """
        Genera una lista de URLs candidatas para el parser externo.
        Incluye fallback automÃ¡tico a host.docker.internal cuando se usa localhost/127.0.0.1.
        """
        raw_candidates: List[str] = []

        normalized_base = (base_url or '').strip().rstrip('/')
        if normalized_base:
            raw_candidates.append(normalized_base)

        fallback_env = os.getenv('PARSER_SERVICE_URL_FALLBACKS', '')
        if fallback_env:
            for candidate in fallback_env.split(','):
                cleaned = candidate.strip().rstrip('/')
                if cleaned:
                    raw_candidates.append(cleaned)

        try:
            parsed = urlparse(normalized_base) if normalized_base else None
        except Exception:
            parsed = None

        if parsed and parsed.hostname in {'127.0.0.1', 'localhost'}:
            alias_url = normalized_base.replace(parsed.hostname, 'host.docker.internal', 1)
            raw_candidates.append(alias_url)

        seen = set()
        ordered_candidates: List[str] = []
        for candidate in raw_candidates:
            if candidate and candidate not in seen:
                seen.add(candidate)
                ordered_candidates.append(candidate)

        return ordered_candidates or ['http://127.0.0.1:1000']

    def _get_file_size_mb(self, file_path: str) -> float:
        """Devuelve el tamaño del archivo en MB. Retorna 0.0 si no se puede leer."""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except OSError:
            return 0.0

    def _validate_parsed_data(self, parsed_data: Dict) -> bool:
        """
        Valida que los datos parseados son Ãºtiles

        Args:
            parsed_data: Datos del parser o OCR

        Returns:
            True si los datos son vÃ¡lidos y contienen texto, False si no
        """
        if not isinstance(parsed_data, dict):
            return False

        if 'pages' not in parsed_data:
            return False

        pages = parsed_data['pages']
        if not isinstance(pages, list) or len(pages) == 0:
            return False

        # Verificar que al menos una pÃ¡gina tiene texto
        total_chars = 0
        for page in pages:
            if isinstance(page, dict):
                text = page.get('text') or page.get('content') or page.get('extracted_text') or ''
            elif isinstance(page, str):
                text = page
            else:
                continue

            total_chars += len(text.strip())

        # Considerar vÃ¡lido si hay al menos 10 caracteres en total
        return total_chars >= 10

    def _calculate_timeout(self, file_size_mb: float) -> Tuple[float, float]:
        """
        Calcula timeouts dinámicos en función del tamaño del archivo.

        Args:
            file_size_mb: Tamaño del archivo en MB

        Returns:
            Tuple(connect_timeout, read_timeout) en segundos
        """
        read_timeout = self.parser_min_timeout
        if file_size_mb > 5:
            read_timeout += (file_size_mb - 5) * self.parser_timeout_per_mb
        read_timeout = min(read_timeout, self.parser_timeout_max)
        return self.parser_connect_timeout, max(read_timeout, self.parser_min_timeout)

    def _parse_with_external_service(self, file_path: str) -> Optional[Dict]:
        """
        Envía el archivo al servicio externo de parseo y retorna el JSON estructurado.
        IMPORTANTE: Este método espera la respuesta del parser, puede tardar según el tamaño del archivo.
        """
        file_size_mb = self._get_file_size_mb(file_path)
        connect_timeout = read_timeout = None
        if self.use_parser_timeouts:
            connect_timeout, read_timeout = self._calculate_timeout(file_size_mb)
        parser_urls = self.parser_url_candidates or [self.parser_url]
        total_attempts = len(parser_urls)
        last_error: Optional[str] = None

        print("[PARSER] Enviando archivo al servicio externo...")
        print(f"[PARSER] Tamaño: {file_size_mb:.2f} MB")
        if self.use_parser_timeouts and connect_timeout is not None and read_timeout is not None:
            print(f"[PARSER] Timeout conexión: {connect_timeout}s | lectura: {read_timeout}s (máximo)")
        else:
            print("[PARSER] Sin timeout - esperará todo el tiempo necesario")

        for attempt, candidate_url in enumerate(parser_urls, start=1):
            print(f"[PARSER] Intento {attempt}/{total_attempts}: {candidate_url}/parse")
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    print("[PARSER] Esperando respuesta del servicio (puede tardar varios minutos para PDFs escaneados)...")
                    post_kwargs = {}
                    if self.use_parser_timeouts and connect_timeout is not None and read_timeout is not None:
                        post_kwargs['timeout'] = (connect_timeout, read_timeout)

                    response = requests.post(
                        f"{candidate_url}/parse",
                        files=files,
                        **post_kwargs
                    )

                if response.status_code != 200:
                    print(f"[PARSER] ? Error HTTP {response.status_code}")
                    print(f"[PARSER] Respuesta: {response.text[:500]}")
                    last_error = f"HTTP {response.status_code}"
                    continue

                print("[PARSER] ? Respuesta recibida con éxito (status 200)")

                try:
                    parsed_data = response.json()
                except ValueError as e:
                    print(f"[PARSER] ? Error al decodificar JSON: {e}")
                    print(f"[PARSER] Respuesta raw: {response.text[:500]}")
                    last_error = str(e)
                    continue

                if not isinstance(parsed_data, dict):
                    print("[PARSER] ? Respuesta no es un diccionario válido")
                    last_error = "Respuesta JSON inválida"
                    continue

                print(f"[PARSER] [DEBUG] Claves principales del JSON: {list(parsed_data.keys())}")

                if 'pages' in parsed_data:
                    num_pages = len(parsed_data['pages'])
                    print(f"[PARSER] ? Documento parseado: {num_pages} página(s)")

                    if num_pages > 0:
                        first_page = parsed_data['pages'][0]
                        print(f"[PARSER] [DEBUG] Tipo de primera página: {type(first_page)}")
                        if isinstance(first_page, dict):
                            print(f"[PARSER] [DEBUG] Claves en primera página: {list(first_page.keys())}")
                            text = first_page.get('text') or first_page.get('content') or first_page.get('extracted_text')
                            if text:
                                print(f"[PARSER] [DEBUG] Preview texto página 1: {text[:100]}...")
                            else:
                                print("[PARSER] [DEBUG] NO se encontró campo de texto en primera página")
                                print(f"[PARSER] [DEBUG] Contenido completo: {str(first_page)[:300]}")
                        elif isinstance(first_page, str):
                            print(f"[PARSER] [DEBUG] Primera página es string: {first_page[:100]}...")
                else:
                    print("[PARSER] ? Respuesta no contiene 'pages'")
                    print(f"[PARSER] [DEBUG] Estructura completa: {str(parsed_data)[:500]}")
                    last_error = "Respuesta sin 'pages'"
                    continue

                print("[PARSER] ? Parseo externo completado exitosamente")
                self.parser_url = candidate_url
                return parsed_data

            except requests.exceptions.Timeout:
                print(f"[PARSER] ? Timeout al conectar con {candidate_url}")
                last_error = "timeout"
                continue

            except requests.exceptions.ConnectionError as e:
                print(f"[PARSER] ? No se pudo conectar al servicio en {candidate_url}")
                print(f"[PARSER] Error: {e}")
                last_error = str(e)
                continue

            except requests.exceptions.RequestException as e:
                print(f"[PARSER] ? Error en la petición hacia {candidate_url}: {e}")
                last_error = str(e)
                continue

            except Exception as e:
                print(f"[PARSER] ? Error inesperado al invocar {candidate_url}: {e}")
                last_error = str(e)
                continue

        print(f"[PARSER] ? No se pudo obtener respuesta del parser externo tras {total_attempts} intento(s)")
        if last_error:
            print(f"[PARSER] [DEBUG] Último error registrado: {last_error}")
        print("[PARSER] ? Usando fallback a extracción local con PyMuPDF/OCR")
        return None

    def process_pdf(
        self,
        input_path: str,
        output_path: str,
        enabled_rules: Dict[str, bool],
        sensitivity_level: str = 'normal',
        action: str = 'highlight',  # 'highlight' o 'redact'
        extraction_mode: str = 'auto',
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict:
        """
        Procesa un PDF completo

        Args:
            input_path: Ruta al PDF de entrada
            output_path: Ruta para guardar PDF procesado
            enabled_rules: Reglas habilitadas {rule_id: bool}
            sensitivity_level: 'strict', 'normal', 'relaxed'
            action: 'highlight' (subrayar) o 'redact' (eliminar texto)
            extraction_mode: 'auto', 'parser' o 'ocr' segun el metodo deseado

        Returns:
            Dict con estadÃ­sticas:
            {
                'total_matches': int,
                'by_type': {type: count},
                'by_page': {page_num: count},
                'pages_processed': int
            }
        """
        stats = {
            'total_matches': 0,
            'by_type': {},
            'by_page': {},
            'pages_processed': 0
        }

        def report_progress(update: Dict[str, Any]) -> None:
            if progress_callback:
                try:
                    progress_callback(update)
                except Exception as progress_error:  # pragma: no cover
                    print(f'[WARN] Error reportando progreso: {progress_error}')

        print(f"\n{'='*60}")
        print(f"[INICIO] Procesando documento: {input_path}")
        print(f"{'='*60}\n")

        report_progress({'stage': 'preparing', 'percent': 12, 'currentPage': 0, 'totalPages': 0, 'extractionMethod': extraction_mode})

        normalized_mode = (extraction_mode or "auto").lower()
        if normalized_mode not in {"auto", "parser", "ocr"}:
            normalized_mode = "auto"
        print(f"[MODO] Estrategia de extraccion seleccionada: {normalized_mode}")

        parsed_data = None
        extraction_method = None

        if normalized_mode != "ocr":
            print("[PASO 1/4] Parseo del documento con servicio externo")
            parsed_data = self._parse_with_external_service(input_path)

            if parsed_data is not None:
                if self._validate_parsed_data(parsed_data):
                    extraction_method = "PARSER_EXTERNO"
                    print("\n[V] Usando datos del PARSER EXTERNO\n")
                    report_progress({
                        'stage': 'parsing-external',
                        'percent': 18,
                        'currentPage': 0,
                        'totalPages': 0,
                        'extractionMethod': extraction_method,
                    })
                else:
                    print("\n[?] Parser externo devolvio datos vacios o invalidos\n")
                    parsed_data = None

            if parsed_data is None and normalized_mode == "parser":
                raise Exception(
                    "No se pudo extraer texto con el parser externo. "
                    "Marca el documento como escaneado para ejecutar OCR."
                )
        else:
            print("[PASO 1/4] Se omite parser externo al forzar OCR")

        if parsed_data is None and normalized_mode != "parser":
            if ocr_processor.can_use_ocr():
                print("\n[>] Intentando extraccion con OCR (Microsoft TrOCR)\n")
                try:
                    parsed_data = ocr_processor.extract_text_from_pdf(input_path)
                    if self._validate_parsed_data(parsed_data):
                        extraction_method = "OCR"
                        print("\n[V] Usando datos extraidos con OCR\n")
                        report_progress({
                            'stage': 'ocr-initializing',
                            'percent': 18,
                            'currentPage': 0,
                            'totalPages': 0,
                            'extractionMethod': extraction_method,
                        })
                    else:
                        print("\n[?] OCR no pudo extraer texto util\n")
                        parsed_data = None
                        if normalized_mode == "ocr":
                            raise Exception(
                                "OCR no pudo extraer texto util del documento. "
                                "Verifica la calidad del escaneo."
                            )
                except Exception as e:
                    print(f"\n[?] Error en OCR: {e}\n")
                    parsed_data = None
                    if normalized_mode == "ocr":
                        raise
            else:
                print("\n[?] OCR no disponible (dependencias no instaladas)\n")
                if normalized_mode == "ocr":
                    raise Exception(
                        "OCR no esta disponible. Instala las dependencias necesarias o usa el parser externo."
                    )

        if parsed_data is None:
            raise Exception(
                "No se pudo extraer texto del documento con los metodos disponibles. "
                f"Modo solicitado: {normalized_mode}. "
                "Verifica el parser externo y el OCR antes de reintentar."
            )
        # Abrir PDF con PyMuPDF
        print(f"[PASO 2/4] Abriendo documento PDF con PyMuPDF")
        doc = fitz.open(input_path)
        total_pages = len(doc)
        print(f"[INFO] Total de pÃ¡ginas: {total_pages}\n")
        total_for_progress = total_pages if total_pages > 0 else 1
        report_progress({
            'stage': 'opening-document',
            'percent': 20,
            'currentPage': 0,
            'totalPages': total_pages,
            'extractionMethod': extraction_method or normalized_mode.upper(),
        })


        try:
            print(f"[PASO 3/4] Procesando pÃ¡ginas y detectando datos sensibles")
            print(f"{'-'*60}")

            # Procesar cada pÃ¡gina
            for page_num in range(total_pages):
                page = doc[page_num]
                print(f"\n[PAGINA {page_num + 1}/{total_pages}]")

                # PASO 2: Obtener texto de la pÃ¡gina
                page_text = None

                # Obtener texto del mÃ©todo de extracciÃ³n disponible (parser o OCR)
                ocr_lines = []

                if page_num >= len(parsed_data['pages']):
                    print(f'  [WARN] Pagina {page_num + 1} no encontrada en datos parseados')
                    page_text = ''
                else:
                    page_data = parsed_data['pages'][page_num]

                    if isinstance(page_data, dict):
                        page_text = page_data.get('text') or page_data.get('content') or page_data.get('extracted_text') or ''
                        lines_candidate = page_data.get('lines')
                        if isinstance(lines_candidate, list):
                            ocr_lines = lines_candidate
                    elif isinstance(page_data, str):
                        page_text = page_data
                    else:
                        print(f'  [WARN] Estructura de pagina no reconocida: {type(page_data)}')
                        page_text = ''

                    if not page_text or len(page_text.strip()) == 0:
                        print('  [WARN] No se obtuvo texto para esta pagina')
                        page_text = ''
                    else:
                        print(f'  [INFO] Fuente de texto: {extraction_method}')
                        print(f'  [INFO] Caracteres extraidos: {len(page_text)}')
                        print(f'  [INFO] Preview: {page_text[:100]}...')

                self._current_page_ocr_lines = ocr_lines

                page_stage = 'ocr-page' if (extraction_method == 'OCR') else 'parser-page'
                percent_start = 20 + int((page_num / total_for_progress) * 75) if total_for_progress else 20
                report_progress({
                    'stage': page_stage,
                    'percent': min(95, percent_start),
                    'currentPage': page_num + 1,
                    'totalPages': total_pages,
                })

                # Detectar datos sensibles
                print(f"  â”œâ”€ Detectando datos sensibles...")
                matches = detector.detect(
                    page_text,
                    enabled_rules,
                    sensitivity_level
                )

                if matches:
                    print(f"  â”œâ”€ âœ“ {len(matches)} dato(s) sensible(s) detectado(s)")

                    # Buscar y marcar cada match en el PDF
                    for idx, match in enumerate(matches, 1):
                        print(f"  â”‚  â””â”€ [{idx}] {match['type']}: {match['value'][:30]}...")
                        self._mark_match_on_page(
                            page,
                            match,
                            page_text,
                            action,
                            self._current_page_ocr_lines
                        )

                        # Actualizar estadÃ­sticas
                        stats['total_matches'] += 1
                        stats['by_type'][match['type']] = stats['by_type'].get(match['type'], 0) + 1

                    stats['by_page'][page_num + 1] = len(matches)
                    print(f"  â””â”€ âœ“ Datos marcados en el PDF")
                else:
                    print(f"  â””â”€ No se detectaron datos sensibles")

                percent_end = 20 + int(((page_num + 1) / total_for_progress) * 75) if total_for_progress else 95
                report_progress({
                    'stage': page_stage,
                    'percent': min(95, percent_end),
                    'currentPage': page_num + 1,
                    'totalPages': total_pages,
                })

                stats['pages_processed'] += 1

            # Guardar PDF modificado
            print(f"\n{'-'*60}")
            print(f"[PASO 4/4] Guardando PDF procesado")
            report_progress({'stage': 'finalizing', 'percent': 97, 'currentPage': total_pages, 'totalPages': total_pages})
            doc.save(output_path, garbage=4, deflate=True)
            print(f"[âœ“] PDF guardado exitosamente: {output_path}")

            # Resumen final
            print(f"\n{'='*60}")
            print(f"[RESUMEN]")
            print(f"  Paginas procesadas: {stats['pages_processed']}")
            print(f"  Total datos sensibles encontrados: {stats['total_matches']}")
            if stats['by_type']:
                print(f"  Desglose por tipo:")
                for data_type, count in stats['by_type'].items():
                    print(f"    - {data_type}: {count}")
            print(f"{'='*60}\n")

        finally:
            doc.close()

        return stats

    # MÃ‰TODO ELIMINADO: _extract_text_with_layout
    # Ya no se usa PyMuPDF para extracciÃ³n de texto
    # TODO texto viene del parser externo en 127.0.0.1:1000

    def _mark_match_on_page(
        self,
        page: fitz.Page,
        match: Dict,
        page_text: str,
        action: str,
        ocr_lines: Optional[List[Dict]] = None,
    ):
        """Locate a match on a PDF page and apply highlight or redaction with pixel-perfect precision."""
        value = match["value"]
        normalized_value = normalizer.normalize_for_search(value)

        # Nueva estrategia: búsqueda carácter por carácter para máxima precisión
        rects = self._get_precise_char_rects(page, value)

        if not rects:
            rects = self._get_precise_char_rects(page, normalized_value)

        # Fallback a métodos anteriores si la búsqueda carácter por carácter falla
        if not rects:
            rects = page.search_for(value, quads=False)
        if not rects:
            rects = page.search_for(normalized_value, quads=False)
        if not rects:
            rects = self._search_by_words(page, value)
        if not rects:
            rects = self._fuzzy_search_on_page(page, normalized_value)
        if not rects and ocr_lines:
            rects = self._rects_from_ocr_lines(match, ocr_lines)

        if not rects:
            print("    [WARN] No se encontraron coordenadas para el dato sensible")
            return

        # SIN PADDING - precisión exacta
        precise_rects = rects

        if action == "highlight":
            highlight_shape = page.new_shape()
            for precise_rect in precise_rects:
                highlight_shape.draw_rect(precise_rect)
            highlight_shape.finish(color=(1, 0, 0), fill=None, width=1.2)
            highlight_shape.commit()
            return

        # Para redacción: aplicar directamente sin padding
        for precise_rect in precise_rects:
            page.add_redact_annot(precise_rect, fill=(0, 0, 0), text="")

        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    def _get_precise_char_rects(self, page: fitz.Page, search_text: str) -> List[fitz.Rect]:
        """
        Obtiene rectángulos precisos buscando carácter por carácter.
        Método de máxima precisión para censurar solo el texto exacto.

        Args:
            page: Página del PDF
            search_text: Texto a buscar

        Returns:
            Lista de rectángulos que cubren exactamente el texto
        """
        if not search_text or len(search_text.strip()) == 0:
            return []

        # Obtener todas las instancias de texto con sus caracteres y posiciones
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])

        all_chars = []  # Lista de todos los caracteres con sus coordenadas

        # Extraer todos los caracteres con coordenadas
        for block in blocks:
            if block.get("type") != 0:  # Solo bloques de texto
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    chars = span.get("chars", [])
                    for char_info in chars:
                        char = char_info.get("c", "")
                        bbox = char_info.get("bbox")
                        if char and bbox:
                            all_chars.append({
                                "char": char,
                                "bbox": bbox,
                                "char_lower": char.lower()
                            })

        if not all_chars:
            return []

        # Normalizar texto de búsqueda
        search_lower = search_text.lower()
        search_len = len(search_text)

        found_rects = []

        # Buscar el patrón carácter por carácter
        for i in range(len(all_chars)):
            # Intentar match desde esta posición
            match_chars = []
            search_idx = 0

            for j in range(i, min(i + search_len * 2, len(all_chars))):
                if search_idx >= search_len:
                    break

                current_char = all_chars[j]["char_lower"]
                target_char = search_lower[search_idx].lower()

                # Comparar caracteres (ignorando espacios extra)
                if current_char == target_char:
                    match_chars.append(all_chars[j])
                    search_idx += 1
                elif current_char in [' ', '\n', '\t'] and target_char not in [' ', '\n', '\t']:
                    # Saltar espacios en el PDF si no están en el patrón
                    continue
                elif current_char not in [' ', '\n', '\t'] and target_char in [' ', '\n', '\t']:
                    # Espacio en el patrón, avanzar en el patrón
                    search_idx += 1
                    if search_idx < search_len and search_lower[search_idx].lower() == current_char:
                        match_chars.append(all_chars[j])
                        search_idx += 1
                else:
                    # No coincide, romper
                    break

            # Si encontramos todos los caracteres
            if search_idx >= search_len and len(match_chars) > 0:
                # En lugar de un solo rectángulo grande, dividir en rectángulos más pequeños
                # agrupando caracteres que estén en la misma línea (misma Y)
                line_groups = self._group_chars_by_line(match_chars)

                for line_chars in line_groups:
                    # Dividir aún más por palabras (detectar gaps horizontales grandes)
                    word_groups = self._split_into_words(line_chars)

                    for word_chars in word_groups:
                        x0 = min(c["bbox"][0] for c in word_chars)
                        y0 = min(c["bbox"][1] for c in word_chars)
                        x1 = max(c["bbox"][2] for c in word_chars)
                        y1 = max(c["bbox"][3] for c in word_chars)

                        found_rects.append(fitz.Rect(x0, y0, x1, y1))

        return found_rects

    def _group_chars_by_line(self, chars: List[Dict]) -> List[List[Dict]]:
        """Agrupa caracteres por línea (misma coordenada Y aproximada)"""
        if not chars:
            return []

        # Ordenar por Y
        sorted_chars = sorted(chars, key=lambda c: c["bbox"][1])

        lines = []
        current_line = [sorted_chars[0]]
        current_y = sorted_chars[0]["bbox"][1]

        for char in sorted_chars[1:]:
            char_y = char["bbox"][1]
            # Si la diferencia de Y es pequeña (< 5 pixels), es la misma línea
            if abs(char_y - current_y) < 5:
                current_line.append(char)
            else:
                lines.append(current_line)
                current_line = [char]
                current_y = char_y

        if current_line:
            lines.append(current_line)

        return lines

    def _split_into_words(self, chars: List[Dict]) -> List[List[Dict]]:
        """Divide caracteres en palabras detectando gaps horizontales"""
        if not chars:
            return []

        # Ordenar por X
        sorted_chars = sorted(chars, key=lambda c: c["bbox"][0])

        # Calcular el ancho promedio de caracteres para detectar espacios
        avg_char_width = sum(c["bbox"][2] - c["bbox"][0] for c in sorted_chars) / len(sorted_chars)
        space_threshold = avg_char_width * 1.5  # Un espacio es > 1.5x el ancho promedio

        words = []
        current_word = [sorted_chars[0]]
        last_x1 = sorted_chars[0]["bbox"][2]

        for char in sorted_chars[1:]:
            char_x0 = char["bbox"][0]
            gap = char_x0 - last_x1

            # Si el gap es pequeño, es la misma palabra
            if gap < space_threshold:
                current_word.append(char)
            else:
                # Nuevo palabra
                words.append(current_word)
                current_word = [char]

            last_x1 = char["bbox"][2]

        if current_word:
            words.append(current_word)

        return words

    def _rects_from_ocr_lines(self, match: Dict, ocr_lines: List[Dict]) -> List[fitz.Rect]:
        """Build refined rectangles from OCR stripe metadata for a match."""
        rects: List[fitz.Rect] = []
        value = match["value"].strip()
        if not value:
            return rects

        normalized_value = normalizer.normalize_for_search(value)
        value_lower = value.lower()

        for line in ocr_lines or []:
            line_text_original = str(line.get("text") or "")
            if not line_text_original:
                continue

            line_text_lower = line_text_original.lower()
            match_start = line_text_lower.find(value_lower)
            match_end = match_start + len(value_lower) if match_start != -1 else -1

            mapping: Optional[List[int]] = None
            normalized_line: Optional[str] = None

            if match_start == -1:
                normalized_line, mapping = self._normalized_with_mapping(line_text_original)
                if normalized_value and normalized_line:
                    idx = normalized_line.find(normalized_value)
                    if idx != -1 and mapping:
                        match_start = mapping[idx]
                        mapping_end_idx = mapping[min(idx + len(normalized_value) - 1, len(mapping) - 1)]
                        match_end = mapping_end_idx + 1

            if match_start == -1 and normalized_value and normalized_value.strip():
                if normalized_line is None or mapping is None:
                    normalized_line, mapping = self._normalized_with_mapping(line_text_original)
                if normalized_line and mapping:
                    idx = normalized_line.find(normalized_value)
                    if idx != -1:
                        match_start = mapping[idx]
                        mapping_end_idx = mapping[min(idx + len(normalized_value) - 1, len(mapping) - 1)]
                        match_end = mapping_end_idx + 1
                    else:
                        score = fuzz.partial_ratio(normalized_value, normalized_line)
                        if score >= self.min_fuzzy_score:
                            match_start = mapping[0]
                            match_end = mapping[-1] + 1

            if match_start == -1 or match_end == -1:
                continue

            bbox = line.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            x0_line, y0_line, x1_line, y1_line = bbox

            text_length = max(len(line_text_original), 1)
            ratio_start = max(0.0, match_start / text_length)
            ratio_end = min(1.0, match_end / text_length)
            if ratio_end <= ratio_start:
                ratio_end = min(1.0, ratio_start + (len(value) / text_length))

            width_span = x1_line - x0_line
            x0 = x0_line + ratio_start * width_span
            x1 = x0_line + ratio_end * width_span

            # SIN padding - precisión exacta para OCR también
            # Las coordenadas ya son las correctas del OCR
            y0 = y0_line
            y1 = y1_line

            try:
                rects.append(fitz.Rect(x0, y0, x1, y1))
            except Exception:
                continue

        return rects

    def _normalized_with_mapping(self, text: str) -> Tuple[str, List[int]]:
        normalized_parts: List[str] = []
        mapping: List[int] = []
        for idx, char in enumerate(text):
            fragment = normalizer.normalize_for_search(char)
            if not fragment:
                continue
            normalized_parts.append(fragment)
            mapping.extend([idx] * len(fragment))
        return ''.join(normalized_parts), mapping

    def _search_by_words(
        self,
        page: fitz.Page,
        search_text: str
    ) -> List[fitz.Rect]:
        """
        Busca texto palabra por palabra en el PDF, ignorando espacios extras
        Ãštil cuando el parser externo devuelve texto sin espacios correctos

        Por ejemplo, si buscamos "932 052 213", busca "932", "052", "213"
        consecutivamente y devuelve un rectÃ¡ngulo que los engloba todos
        """
        rects = []

        # Dividir en palabras (tokens)
        words = search_text.split()
        if len(words) < 2:
            # Si es una sola palabra, no tiene sentido este mÃ©todo
            return rects

        # Extraer todas las palabras del PDF con sus posiciones
        page_words = page.get_text("words")  # [(x0, y0, x1, y1, "word", block_no, line_no, word_no)]

        # Buscar secuencias de palabras que coincidan
        for i in range(len(page_words)):
            matched_words = []
            word_idx = 0

            # Intentar emparejar desde esta posiciÃ³n
            for j in range(i, min(i + len(words) * 2, len(page_words))):
                page_word = page_words[j][4].strip()
                search_word = words[word_idx].strip()

                # Comparar palabras (exacta o normalizada)
                if page_word.lower() == search_word.lower():
                    matched_words.append(page_words[j])
                    word_idx += 1

                    # Si hemos encontrado todas las palabras
                    if word_idx == len(words):
                        # Crear rectÃ¡ngulo que englobe todas las palabras encontradas
                        rect = self._create_rect_from_words(matched_words)
                        rects.append(rect)
                        break
                elif word_idx > 0:
                    # Ya habÃ­amos empezado a emparejar pero fallÃ³, reiniciar
                    break

        return rects

    def _fuzzy_search_on_page(
        self,
        page: fitz.Page,
        search_text: str
    ) -> List[fitz.Rect]:
        """
        BÃºsqueda fuzzy cuando la bÃºsqueda exacta falla
        Ãštil para texto con espacios/saltos inconsistentes
        """
        rects = []

        # Extraer palabras con coordenadas
        words = page.get_text("words")  # [(x0, y0, x1, y1, "word", block_no, line_no, word_no)]

        # Normalizar texto de bÃºsqueda
        search_normalized = normalizer.normalize_for_search(search_text).lower()
        search_words = search_normalized.split()

        # Buscar secuencias de palabras que coincidan fuzzy
        for i in range(len(words)):
            # Intentar emparejar desde esta posiciÃ³n
            matched_words = []
            current_search_idx = 0

            for j in range(i, min(i + len(search_words) + 5, len(words))):
                word_text = words[j][4].lower()
                word_normalized = normalizer.normalize_for_search(word_text)

                if current_search_idx < len(search_words):
                    target_word = search_words[current_search_idx]

                    # Calcular similitud
                    score = fuzz.ratio(word_normalized, target_word)

                    if score >= self.min_fuzzy_score:
                        matched_words.append(words[j])
                        current_search_idx += 1

                        # Si hemos encontrado todas las palabras
                        if current_search_idx == len(search_words):
                            # Crear rectÃ¡ngulo que englobe todas las palabras
                            rect = self._create_rect_from_words(matched_words)
                            rects.append(rect)
                            break

        return rects

    def _create_rect_from_words(self, words: List[Tuple]) -> fitz.Rect:
        """Crea un rectÃ¡ngulo que engloba mÃºltiples palabras"""
        if not words:
            return fitz.Rect()

        x0 = min(w[0] for w in words)
        y0 = min(w[1] for w in words)
        x1 = max(w[2] for w in words)
        y1 = max(w[3] for w in words)

        return fitz.Rect(x0, y0, x1, y1)

    def extract_text_with_coords(self, pdf_path: str) -> List[Dict]:
        """
        Extrae texto con coordenadas usando pdfplumber
        Ãštil para anÃ¡lisis detallado

        Returns:
            Lista de pÃ¡ginas con palabras y coordenadas
        """
        pages_data = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                words = page.extract_words()
                pages_data.append({
                    'page_num': page_num + 1,
                    'words': words,
                    'full_text': page.extract_text() or ''
                })

        return pages_data

    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Detecta si un PDF es escaneado (sin texto extraÃ­ble)

        Returns:
            True si es escaneado, False si tiene texto
        """
        doc = fitz.open(pdf_path)
        try:
            # Verificar primeras 3 pÃ¡ginas
            for page_num in range(min(3, len(doc))):
                page = doc[page_num]
                text = page.get_text().strip()

                # Si tiene texto significativo, no es escaneado
                if len(text) > 50:
                    return False

            # Si no encontramos texto, es escaneado
            return True

        finally:
            doc.close()


# Instancia global
pdf_processor = PDFProcessor()
