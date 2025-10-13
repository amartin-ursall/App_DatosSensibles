"""
Validadores para diferentes tipos de datos sensibles
Usa python-stdnum para validaciones robustas (IBAN, Luhn, NIF, NIE, CIF)
"""
import re
from typing import Optional
from stdnum import iban, luhn
from stdnum.es import nif, nie, cif


class DataValidator:
    """Validador centralizado para todos los tipos de datos"""

    def __init__(self):
        # Palabras clave para detección contextual
        self.credential_keywords = [
            'password', 'contraseña', 'clave', 'pwd', 'pass',
            'api_key', 'apikey', 'api key', 'token', 'bearer',
            'authorization', 'auth', 'secret', 'secreto',
            'cookie', 'session', 'sesion', 'credential', 'credencial',
            'ssh-rsa', 'private key', 'clave privada',
            'BEGIN PRIVATE KEY', 'BEGIN RSA PRIVATE KEY',
            'access_token', 'refresh_token'
        ]

        self.health_keywords = [
            'diagnóstico', 'diagnostico', 'diagnosis',
            'medicación', 'medicacion', 'medication', 'medicina',
            'receta', 'prescription',
            'enfermedad', 'disease', 'illness',
            'tratamiento', 'treatment',
            'historia clínica', 'historia clinica', 'medical history',
            'carencia', 'preexistencia', 'preexisting',
            'copago', 'coinsurance',
            'reembolso', 'reimbursement',
            'sintoma', 'síntoma', 'symptom',
            'alergia', 'allergy',
            'cirugía', 'cirugia', 'surgery',
            'hospitalización', 'hospitalizacion', 'hospitalization',
            'paciente', 'patient'
        ]

    def validate(self, value: str, data_type: str) -> bool:
        """Valida un valor según su tipo"""
        validators = {
            'iban': self.validate_iban,
            'creditCard': self.validate_credit_card,
            'dni': self.validate_dni,
            'nie': self.validate_nie,
            'cif': self.validate_cif,
            'email': self.validate_email,
            'phone': self.validate_phone,
        }

        validator = validators.get(data_type)
        if validator:
            return validator(value)

        return True  # Si no hay validador específico, aceptar

    def validate_iban(self, value: str) -> bool:
        """Valida IBAN usando módulo 97"""
        try:
            # Normalizar: quitar espacios
            clean = value.replace(' ', '').replace('\t', '').upper()
            return iban.is_valid(clean)
        except Exception:
            return False

    def validate_credit_card(self, value: str) -> bool:
        """Valida tarjeta de crédito con algoritmo de Luhn"""
        try:
            # Normalizar: quitar espacios y guiones
            clean = re.sub(r'[\s\-]', '', value)
            return luhn.is_valid(clean)
        except Exception:
            return False

    def validate_dni(self, value: str) -> bool:
        """Valida DNI español con letra de control"""
        try:
            # Normalizar
            clean = value.replace(' ', '').replace('-', '').upper()
            return nif.is_valid(clean)
        except Exception:
            return False

    def validate_nie(self, value: str) -> bool:
        """Valida NIE español con letra de control"""
        try:
            clean = value.replace(' ', '').replace('-', '').upper()
            return nie.is_valid(clean)
        except Exception:
            return False

    def validate_cif(self, value: str) -> bool:
        """Valida CIF español con dígito de control"""
        try:
            clean = value.replace(' ', '').replace('-', '').upper()
            return cif.is_valid(clean)
        except Exception:
            return False

    def validate_email(self, value: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$'
        return bool(re.match(pattern, value))

    def validate_phone(self, value: str) -> bool:
        """Valida teléfono español"""
        clean = re.sub(r'[\s\-\(\)]', '', value)
        # Quitar prefijo +34 si existe
        if clean.startswith('+34'):
            clean = clean[3:]
        elif clean.startswith('34') and len(clean) == 11:
            clean = clean[2:]

        # Debe tener 9 dígitos y empezar por 6, 7, 8 o 9
        return len(clean) == 9 and clean[0] in '6789' and clean.isdigit()

    def has_credential_keywords(self, context: str) -> bool:
        """Verifica si el contexto contiene palabras clave de credenciales"""
        context_lower = context.lower()
        return any(keyword in context_lower for keyword in self.credential_keywords)

    def has_health_keywords(self, context: str) -> bool:
        """Verifica si el contexto contiene palabras clave de salud"""
        context_lower = context.lower()
        return any(keyword in context_lower for keyword in self.health_keywords)

    def calculate_confidence(
        self,
        value: str,
        data_type: str,
        context: str,
        has_context_keywords: bool,
        sensitivity_level: str = 'normal'
    ) -> float:
        """
        Calcula confianza de una detección
        Implementa Steps 2-4 del blueprint
        """
        # Confianza base según tipo
        base_confidence = {
            'iban': 0.8,
            'creditCard': 0.5,
            'dni': 0.7,
            'nie': 0.75,
            'cif': 0.75,
            'email': 0.8,
            'phone': 0.7,
            'credentials': 0.85,
            'healthData': 0.8,
            'name': 0.5,
        }.get(data_type, 0.6)

        confidence = base_confidence

        # PASO 1: Aplicar validador
        is_valid = self.validate(value, data_type)
        if is_valid:
            confidence = max(confidence, 0.9)
        else:
            # Si falla validación, penalizar
            confidence *= 0.5

        # PASO 2: Verificar contexto
        if has_context_keywords:
            confidence = max(confidence, 0.95)

        # PASO 3: Bonus si tiene validación + contexto
        if is_valid and has_context_keywords:
            confidence = min(1.0, confidence * 1.05)

        # PASO 4: Verificaciones especiales
        if data_type == 'credentials' and self.has_credential_keywords(context):
            confidence = max(confidence, 0.95)

        if data_type == 'healthData' and self.has_health_keywords(context):
            confidence = max(confidence, 0.95)

        # PASO 5: Ajustar según sensibilidad
        if sensitivity_level == 'strict':
            confidence *= 1.15
        elif sensitivity_level == 'relaxed':
            confidence *= 0.85

        return min(1.0, max(0.0, confidence))


# Instancia global
validator = DataValidator()
