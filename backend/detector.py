"""
Detector de datos sensibles
Implementa el pipeline del blueprint: regex + validaciones + contexto
"""
import regex as re
from typing import List, Dict, Tuple, Optional
from normalizer import normalizer
from validators import validator


class SensitiveDataDetector:
    """Detecta datos sensibles en texto usando regex y validaciones"""

    def __init__(self):
        # Patrones elásticos (tolerantes a espacios/saltos)
        self.patterns = {
            # IBAN (incluyendo con puntos y espacios)
            'iban': {
                'regex': re.compile(r'ES[\s\.\-]?\d{2}(?:[\s\.\-]?\d){20}', re.IGNORECASE),
                'context_keywords': ['iban', 'cuenta', 'bancaria', 'banco', 'transferencia', 'swift', 'bic'],
                'validator': True,
            },

            # Tarjetas de crédito
            'creditCard': {
                'regex': re.compile(r'\d{4}(?:[\s\-\.]?\d{4}){3}', re.IGNORECASE),
                'context_keywords': ['tarjeta', 'card', 'crédito', 'credito', 'visa', 'mastercard', 'pago', 'débito', 'debito'],
                'validator': True,
            },

            # DNI español
            'dni': {
                'regex': re.compile(r'\b\d{8}[\s\-]?[A-Z]\b', re.IGNORECASE),
                'context_keywords': ['dni', 'documento', 'identidad', 'identificación', 'nif'],
                'validator': True,
            },

            # NIE español
            'nie': {
                'regex': re.compile(r'\b[XYZ][\s\-]?\d{7}[\s\-]?[A-Z]\b', re.IGNORECASE),
                'context_keywords': ['nie', 'extranjero', 'extranjería'],
                'validator': True,
            },

            # CIF español
            'cif': {
                'regex': re.compile(r'\b[ABCDEFGHJNPQRSUVW][\s\-]?\d{7}[\s\-]?[0-9A-J]\b', re.IGNORECASE),
                'context_keywords': ['cif', 'empresa', 'sociedad', 'fiscal'],
                'validator': True,
            },

            # Email
            'email': {
                'regex': re.compile(
                    r'\b[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+\b',
                    re.IGNORECASE
                ),
                'context_keywords': ['email', 'correo', 'e-mail', 'mail', 'contacto', '@', 'correo electrónico'],
                'validator': True,
            },

            # Teléfonos (españoles e internacionales)
            'phone': {
                'regex': re.compile(
                    r'(?:\+?\d{1,3}[\s\-\.]?)?(?:\(?\d{2,4}\)?[\s\-\.]?)?(?:\d{2,4}[\s\-\.]?){2,3}\d{2,4}',
                    re.IGNORECASE
                ),
                'context_keywords': ['teléfono', 'telefono', 'tel', 'phone', 'móvil', 'movil', 'celular', 'contacto', 'llamar', 'fijo'],
                'validator': True,
            },

            # Fechas de nacimiento (múltiples formatos)
            'dateOfBirth': {
                'regex': re.compile(
                    r'(?:'
                    r'\b\d{1,2}[\s\-\/\.]\d{1,2}[\s\-\/\.]\d{2,4}\b|'  # 01/12/1990, 1-12-90
                    r'\b\d{2,4}[\s\-\/\.]\d{1,2}[\s\-\/\.]\d{1,2}\b|'  # 1990/12/01
                    r'\b\d{1,2}[\s](?:de[\s])?(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)[\s](?:de[\s])?\d{2,4}\b|'  # 1 de enero de 1990
                    r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)[\s]\d{1,2}[\s,]+\d{2,4}\b'  # January 1, 1990
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['nacimiento', 'fecha de nacimiento', 'nació', 'nacio', 'birth', 'dob', 'birthday', 'cumpleaños', 'edad', 'años', 'born'],
                'validator': True,
            },

            # Direcciones postales (formato español y genérico)
            'address': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:calle|c\/|avenida|av\.|avda\.|plaza|pza\.|paseo|p\.|camino|carretera|c\.)\s+[A-ZÁÉÍÓÚÑa-záéíóúñ\s]+,?\s+(?:n[úuº]?\.?|número|num\.?)?\s*\d{1,4}(?:\s*[a-z])?(?:\s*[,\-]\s*(?:piso|p\.?|pta\.?|puerta|portal|escalera|esc\.?|bloque|bl\.?)\s*[A-Z0-9\-]+)?(?:\s*[,\-]\s*\d{5}(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)?)?|'  # Calle Mayor, 25, 3º A, 28013 Madrid
                    r'\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)(?:\s*,\s*(?:Apt|Apartment|Suite|Ste|Unit|#)\s*[A-Z0-9\-]+)?(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,?\s*[A-Z]{2}\s+\d{5})?'  # 123 Main Street, Apt 4B, New York, NY 10001
                    r')',
                    re.IGNORECASE | re.MULTILINE
                ),
                'context_keywords': ['dirección', 'direccion', 'domicilio', 'address', 'residencia', 'vive en', 'calle', 'avenida', 'ubicación', 'localidad'],
                'validator': False,
            },

            # Nombres de usuario y alias
            'username': {
                'regex': re.compile(
                    r'(?:'
                    r'@[a-zA-Z0-9_]{3,30}|'  # @username (redes sociales)
                    r'(?:usuario|user|username|login|alias|nick|nickname)[\s:=]+[a-zA-Z0-9_\-\.]{3,30}'  # usuario: john_doe
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['usuario', 'user', 'username', 'login', 'alias', 'nick', 'nickname', 'cuenta', 'perfil', 'handle'],
                'validator': False,
            },

            # Nombres completos (mejorado)
            'fullName': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Sr\.|Sra\.|Dr\.|Dra\.|Don|Doña|Mr\.|Mrs\.|Ms\.)?\s*'  # Prefijo opcional
                    r'[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}(?:[\s\-][A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}){1,4}'  # 2-5 palabras capitalizadas
                    r')',
                    re.MULTILINE
                ),
                'context_keywords': ['nombre', 'apellido', 'titular', 'cliente', 'paciente', 'beneficiario', 'solicitante', 'asegurado', 'persona', 'señor', 'señora', 'firmante'],
                'validator': False,
            },

            # Titulares (contexto específico)
            'accountHolder': {
                'regex': re.compile(
                    r'(?:titular|titulares|account\s+holder|beneficiario|propietario)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}',
                    re.IGNORECASE
                ),
                'context_keywords': ['titular', 'titulares', 'beneficiario', 'propietario', 'account holder', 'nombre del titular', 'a nombre de'],
                'validator': False,
            },

            # Pasaportes (formato internacional mejorado)
            'passport': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Passport|Pasaporte|Pass|PPT)[\s:#\-]+[A-Z0-9]{6,12}|'  # Passport: AA1234567
                    r'(?:Passport[\s]?No|Passport[\s]?Number|No[\s]?Pasaporte|Núm[\s]?Pasaporte)[\s:#\-\.]*[A-Z0-9]{6,12}|'  # Passport No: ABC123456
                    r'\b[A-Z]{1,2}[\s\-]?\d{6,9}\b(?=.*(?:passport|pasaporte|travel|viaje))|'  # AA-1234567 (con contexto)
                    r'\b\d{9}\b(?=.*(?:passport|pasaporte|travel))|'  # 123456789 (con contexto passport)
                    r'\b[A-Z]\d{8}\b(?=.*(?:passport|pasaporte))'  # A12345678 (con contexto)
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['pasaporte', 'passport', 'travel document', 'documento de viaje', 'pass no', 'passport number', 'passport no', 'ppno', 'pp no', 'ppt', 'número de pasaporte'],
                'validator': False,
            },

            # Matrículas de vehículos (España y otros formatos)
            'licensePlate': {
                'regex': re.compile(
                    r'\b(?:'
                    r'\d{4}[\s\-]?[BCDFGHJKLMNPRSTVWXYZ]{3}|'  # España moderna: 1234 ABC
                    r'[A-Z]{1,2}[\s\-]?\d{4}[\s\-]?[A-Z]{1,2}|'  # España antigua: M-1234-AB
                    r'[A-Z]{3}[\s\-]?\d{3,4}|'  # Genérico: ABC-1234
                    r'\d{1,3}[\s\-]?[A-Z]{3}[\s\-]?\d{1,3}'  # Otro formato: 12-ABC-34
                    r')\b',
                    re.IGNORECASE
                ),
                'context_keywords': ['matrícula', 'matricula', 'license plate', 'placa', 'vehículo', 'vehiculo', 'coche', 'carro', 'auto', 'registration'],
                'validator': False,
            },

            # Número de Seguridad Social (SSN USA, NSS España, y otros)
            'ssn': {
                'regex': re.compile(
                    r'(?:'
                    r'\b\d{3}[\s\-]?\d{2}[\s\-]?\d{4}\b|'  # SSN USA: 123-45-6789
                    r'\b\d{2}[\s\/\-]?\d{10}[\s\/\-]?\d{2}\b|'  # NSS España: 12/1234567890/12
                    r'(?:SSN|NSS|SS|N\.?S\.?S\.?)[\s:#\-]+\d{2,3}[\s\-\/]?\d{2,10}[\s\-\/]?\d{2,4}'  # Con prefijo
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['ssn', 'nss', 'social security', 'seguro social', 'security number', 'ss no', 'ss#', 'seguridad social', 'número de seguridad', 'numero ss'],
                'validator': True,
            },

            # Employee ID / ID de Empleado (múltiples formatos)
            'employeeId': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:EMP|EMPL|Employee|Empleado|ID|Staff|Worker)[\s:#\-]+[A-Z0-9]{3,12}|'  # EMP-1234, Employee ID: ABC123
                    r'(?:ID[\s:]?Empleado|ID[\s:]?Employee|Employee[\s:]?ID|ID[\s:]?de[\s:]?Empleado)[\s:#\-]+[A-Z0-9]{3,12}|'  # ID Empleado: 1234
                    r'\b[A-Z]{2,4}[\-]?\d{4,8}\b(?=.*(?:empleado|employee|personal|staff|worker|id))|'  # ABC-12345 (con contexto)
                    r'(?:Legajo|File|Personal[\s]?No|Staff[\s]?No|Worker[\s]?No)[\s:#\-]+\d{3,8}'  # Legajo: 12345
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['empleado', 'employee', 'emp', 'id', 'staff', 'worker', 'legajo', 'personal', 'número de empleado', 'employee number', 'employee id', 'id empleado'],
                'validator': False,
            },

            # Cookies (sesiones web)
            'cookie': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:cookie|session|token|auth|jwt)[\s:=]+[A-Za-z0-9\+\/=\-_\.]{20,}|'  # cookie=xyz123...
                    r'Set-Cookie:\s*[^\n]+|'  # Header Set-Cookie
                    r'[A-Za-z0-9_\-]+=[A-Za-z0-9\+\/=\-_\.]{32,}(?:;|\s|$)'  # formato key=value
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['cookie', 'session', 'sesion', 'token', 'jwt', 'auth', 'authorization', 'set-cookie', 'sessionid'],
                'validator': False,
            },

            # Credenciales
            'credentials': {
                'regex': re.compile(
                    r'(?:password|contraseña|clave|pwd|pass|api[_\s]?key|token|bearer|secret)[\s:=]+[^\s]{6,}',
                    re.IGNORECASE
                ),
                'context_keywords': validator.credential_keywords,
                'validator': False,
            },

            # Datos de salud
            'healthData': {
                'regex': re.compile(
                    r'(?:diagnóstico|diagnostico|diagnosis|medicación|medicacion|medication|receta|enfermedad|tratamiento)[\s:]+[^\n]{10,100}',
                    re.IGNORECASE
                ),
                'context_keywords': validator.health_keywords,
                'validator': False,
            },
        }

    def detect(
        self,
        text: str,
        enabled_rules: Dict[str, bool],
        sensitivity_level: str = 'normal',
        context_length: int = 50
    ) -> List[Dict]:
        """
        Detecta datos sensibles en texto

        Args:
            text: Texto a analizar
            enabled_rules: Dict con reglas habilitadas {rule_id: bool}
            sensitivity_level: 'strict', 'normal', 'relaxed'
            context_length: Caracteres de contexto alrededor del match

        Returns:
            Lista de detecciones con formato:
            {
                'type': str,
                'value': str,
                'start': int,
                'end': int,
                'confidence': float,
                'context': str,
                'normalized_value': str
            }
        """
        matches = []

        # Normalizar texto completo
        normalized_text = normalizer.normalize_full(text)

        # Umbral de confianza según sensibilidad
        threshold = self._get_confidence_threshold(sensitivity_level)

        # Procesar cada patrón habilitado
        for data_type, pattern_info in self.patterns.items():
            if not enabled_rules.get(data_type, False):
                continue

            regex_pattern = pattern_info['regex']

            # Buscar matches en texto normalizado
            for match in regex_pattern.finditer(normalized_text):
                value = match.group(0)
                start = match.start()
                end = match.end()

                # Obtener contexto
                context = self._get_context(normalized_text, start, end, context_length)

                # Verificar si hay palabras clave en contexto
                has_context_keywords = self._has_context_keywords(
                    context, pattern_info['context_keywords']
                )

                # Normalizar valor para validación
                normalized_value = normalizer.normalize_for_validation(value, data_type)

                # Calcular confianza
                confidence = validator.calculate_confidence(
                    normalized_value,
                    data_type,
                    context,
                    has_context_keywords,
                    sensitivity_level
                )

                # Solo agregar si supera el umbral
                if confidence >= threshold:
                    matches.append({
                        'type': data_type,
                        'value': value,
                        'start': start,
                        'end': end,
                        'confidence': confidence,
                        'context': context,
                        'normalized_value': normalized_value,
                    })

        # Eliminar duplicados y resolver solapamientos
        matches = self._remove_overlaps(matches)

        return matches

    def _get_context(self, text: str, start: int, end: int, length: int) -> str:
        """Extrae contexto alrededor de un match"""
        context_start = max(0, start - length)
        context_end = min(len(text), end + length)
        return text[context_start:context_end]

    def _has_context_keywords(self, context: str, keywords: List[str]) -> bool:
        """Verifica si hay palabras clave en el contexto"""
        context_lower = context.lower()
        return any(keyword.lower() in context_lower for keyword in keywords)

    def _get_confidence_threshold(self, sensitivity_level: str) -> float:
        """Obtiene umbral de confianza según sensibilidad"""
        thresholds = {
            'strict': 0.5,
            'normal': 0.65,
            'relaxed': 0.8,
        }
        return thresholds.get(sensitivity_level, 0.65)

    def _remove_overlaps(self, matches: List[Dict]) -> List[Dict]:
        """Elimina solapamientos, manteniendo el de mayor confianza"""
        if not matches:
            return []

        # Ordenar por posición y confianza
        sorted_matches = sorted(matches, key=lambda m: (m['start'], -m['confidence']))

        result = []
        last_end = -1

        for match in sorted_matches:
            # Si no se solapa con el anterior
            if match['start'] >= last_end:
                result.append(match)
                last_end = match['end']
            else:
                # Hay solapamiento, mantener el de mayor confianza
                if result and match['confidence'] > result[-1]['confidence']:
                    result[-1] = match
                    last_end = match['end']

        return result


# Instancia global
detector = SensitiveDataDetector()
