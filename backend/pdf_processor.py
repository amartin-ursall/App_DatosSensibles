"""
Procesador de PDFs con PyMuPDF
Implementa el pipeline del blueprint:
- Extrae texto con coordenadas
- Busca matches por página
- Subraya o redacta en coordenadas nativas
"""
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from rapidfuzz import fuzz
from normalizer import normalizer
from detector import detector
from validators import validator


class PDFProcessor:
    """Procesa PDFs para detectar y marcar datos sensibles"""

    def __init__(self):
        self.min_fuzzy_score = 80  # Score mínimo para fuzzy matching

    def process_pdf(
        self,
        input_path: str,
        output_path: str,
        enabled_rules: Dict[str, bool],
        sensitivity_level: str = 'normal',
        action: str = 'highlight'  # 'highlight' o 'redact'
    ) -> Dict:
        """
        Procesa un PDF completo

        Args:
            input_path: Ruta al PDF de entrada
            output_path: Ruta para guardar PDF procesado
            enabled_rules: Reglas habilitadas {rule_id: bool}
            sensitivity_level: 'strict', 'normal', 'relaxed'
            action: 'highlight' (subrayar) o 'redact' (eliminar texto)

        Returns:
            Dict con estadísticas:
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

        # Abrir PDF con PyMuPDF
        doc = fitz.open(input_path)

        try:
            # Procesar cada página
            for page_num in range(len(doc)):
                page = doc[page_num]

                # Extraer texto de la página
                page_text = page.get_text()

                # Detectar datos sensibles
                matches = detector.detect(
                    page_text,
                    enabled_rules,
                    sensitivity_level
                )

                if matches:
                    print(f"[PAGE {page_num + 1}] {len(matches)} deteccion(es)")

                    # Buscar y marcar cada match en el PDF
                    for match in matches:
                        self._mark_match_on_page(
                            page,
                            match,
                            page_text,
                            action
                        )

                        # Actualizar estadísticas
                        stats['total_matches'] += 1
                        stats['by_type'][match['type']] = stats['by_type'].get(match['type'], 0) + 1

                    stats['by_page'][page_num + 1] = len(matches)

                stats['pages_processed'] += 1

            # Guardar PDF modificado
            doc.save(output_path, garbage=4, deflate=True)
            print(f"[OK] PDF guardado en: {output_path}")

        finally:
            doc.close()

        return stats

    def _mark_match_on_page(
        self,
        page: fitz.Page,
        match: Dict,
        page_text: str,
        action: str
    ):
        """
        Busca y marca un match en una página del PDF

        Args:
            page: Página de PyMuPDF
            match: Detección con 'value', 'start', 'end', 'type'
            page_text: Texto completo de la página
            action: 'highlight' o 'redact'
        """
        value = match['value']
        normalized_value = normalizer.normalize_for_search(value)

        # PASO 1: Intentar búsqueda exacta con PyMuPDF
        rects = page.search_for(value, quads=False)

        # PASO 2: Si no hay coincidencias exactas, intentar con texto normalizado
        if not rects:
            rects = page.search_for(normalized_value, quads=False)

        # PASO 3: Si aún no hay coincidencias, usar fuzzy matching
        if not rects:
            rects = self._fuzzy_search_on_page(page, normalized_value)

        # PASO 4: Aplicar acción (highlight o redact) en cada rectángulo
        for rect in rects:
            if action == 'highlight':
                # Redactar con rectángulo negro (oculta completamente el texto)
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Negro sólido
            elif action == 'redact':
                # Redactar (eliminar texto)
                page.add_redact_annot(rect, fill=(0, 0, 0))

        # Aplicar redacciones (negro sólido que oculta el texto)
        if rects:
            page.apply_redactions()

    def _fuzzy_search_on_page(
        self,
        page: fitz.Page,
        search_text: str
    ) -> List[fitz.Rect]:
        """
        Búsqueda fuzzy cuando la búsqueda exacta falla
        Útil para texto con espacios/saltos inconsistentes
        """
        rects = []

        # Extraer palabras con coordenadas
        words = page.get_text("words")  # [(x0, y0, x1, y1, "word", block_no, line_no, word_no)]

        # Normalizar texto de búsqueda
        search_normalized = normalizer.normalize_for_search(search_text).lower()
        search_words = search_normalized.split()

        # Buscar secuencias de palabras que coincidan fuzzy
        for i in range(len(words)):
            # Intentar emparejar desde esta posición
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
                            # Crear rectángulo que englobe todas las palabras
                            rect = self._create_rect_from_words(matched_words)
                            rects.append(rect)
                            break

        return rects

    def _create_rect_from_words(self, words: List[Tuple]) -> fitz.Rect:
        """Crea un rectángulo que engloba múltiples palabras"""
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
        Útil para análisis detallado

        Returns:
            Lista de páginas con palabras y coordenadas
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
        Detecta si un PDF es escaneado (sin texto extraíble)

        Returns:
            True si es escaneado, False si tiene texto
        """
        doc = fitz.open(pdf_path)
        try:
            # Verificar primeras 3 páginas
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
