"""
Normalización de texto para detección robusta
Basado en blueprint.md - Normalización idéntica en detección y búsqueda
"""
import re
import ftfy


class TextNormalizer:
    """Normaliza texto de PDFs para detección consistente"""

    # Mapa de ligaduras comunes
    LIGATURES = {
        'ﬀ': 'ff',
        'ﬁ': 'fi',
        'ﬂ': 'fl',
        'ﬃ': 'ffi',
        'ﬄ': 'ffl',
        'ﬅ': 'ft',
        'ﬆ': 'st',
    }

    def __init__(self):
        # Compilar patrones para mejor performance
        self.hyphen_newline_pattern = re.compile(r'-\n')
        self.multiple_spaces_pattern = re.compile(r'\s+')
        self.separator_pattern = re.compile(r'[\s\-]+')

    def normalize_full(self, text: str) -> str:
        """
        Normalización completa para detección
        Sigue el blueprint: ligaduras, guiones, espacios
        """
        if not text:
            return ""

        # 1. Arreglar encoding raro con ftfy
        text = ftfy.fix_text(text)

        # 2. Sustituir ligaduras
        text = self._replace_ligatures(text)

        # 3. Unir cortes de línea con guion
        text = self.hyphen_newline_pattern.sub('', text)

        # 4. Colapsar espacios múltiples
        text = self.multiple_spaces_pattern.sub(' ', text)

        # 5. Eliminar espacios al inicio y final
        text = text.strip()

        return text

    def normalize_for_validation(self, text: str, data_type: str) -> str:
        """
        Normalización específica para validación
        Elimina separadores en números (IBAN, tarjetas, etc.)
        """
        text = self.normalize_full(text)

        # Para datos numéricos, quitar todos los separadores
        if data_type in ['iban', 'creditCard', 'dni', 'nie', 'cif', 'phone']:
            text = self.separator_pattern.sub('', text)

        return text

    def normalize_for_search(self, text: str) -> str:
        """
        Normalización para búsqueda (igual que normalize_full)
        Mantiene espacios simples para matching elástico
        """
        return self.normalize_full(text)

    def _replace_ligatures(self, text: str) -> str:
        """Reemplaza ligaduras tipográficas"""
        for ligature, replacement in self.LIGATURES.items():
            text = text.replace(ligature, replacement)
        return text

    def create_elastic_pattern(self, pattern: str, data_type: str) -> str:
        """
        Crea patron regex tolerante a espacios y saltos
        Ejemplo: ES + 2 digitos con espacios opcionales
        """
        if data_type == 'iban':
            # IBAN: ES76 2077... → ES\d{2}\s?[\d\s]{20}
            return r'ES\d{2}(?:[\s\t]?\d){20}'
        elif data_type == 'creditCard':
            # Tarjeta: 1234 5678... → \d{4}(?:[\s\-]?\d{4}){3}
            return r'\d{4}(?:[\s\-]?\d{4}){3}'
        elif data_type == 'dni':
            # DNI: 12345678Z → \d{8}[\s\-]?[A-Z]
            return r'\d{8}[\s\-]?[A-Z]'
        elif data_type == 'nie':
            # NIE: X1234567L → [XYZ][\s\-]?\d{7}[\s\-]?[A-Z]
            return r'[XYZ][\s\-]?\d{7}[\s\-]?[A-Z]'
        elif data_type == 'cif':
            # CIF: A12345678 → [A-Z][\s\-]?\d{7}[\s\-]?[0-9A-J]
            return r'[ABCDEFGHJNPQRSUVW][\s\-]?\d{7}[\s\-]?[0-9A-J]'
        elif data_type == 'phone':
            # Teléfono español: 612345678
            return r'(?:\+?34[\s\-]?)?[6-9]\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}'
        else:
            return pattern


# Instancia global
normalizer = TextNormalizer()
