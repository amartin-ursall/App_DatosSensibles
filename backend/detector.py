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

            # DNI español (mejorado para detectar sin contexto fuerte)
            'dni': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:DNI|NIF)[\s:#\-]*\d{8}[\s\-]?[A-Z]|'  # DNI: 12345678A o NIF 12345678-A
                    r'\b\d{8}[\s\-]?[A-Z]\b'  # 12345678A (formato estándar)
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['dni', 'documento', 'identidad', 'identificación', 'nif', 'cliente', 'titular', 'beneficiario', 'paciente'],
                'validator': True,
            },

            # NIE español (mejorado)
            'nie': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:NIE)[\s:#\-]*[XYZ][\s\-]?\d{7}[\s\-]?[A-Z]|'  # NIE: X1234567A
                    r'\b[XYZ][\s\-]?\d{7}[\s\-]?[A-Z]\b'  # X1234567A
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['nie', 'extranjero', 'extranjería', 'identificación', 'documento'],
                'validator': True,
            },

            # CIF español (mejorado)
            'cif': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:CIF|NIF)[\s:#\-]*[ABCDEFGHJNPQRSUVW][\s\-]?\d{7}[\s\-]?[0-9A-J]|'  # CIF: A12345678
                    r'\b[ABCDEFGHJNPQRSUVW][\s\-]?\d{7,8}[\s\-]?[0-9A-J]?\b'  # B56818370 o A12345678
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['cif', 'empresa', 'sociedad', 'fiscal', 'nif', 'compañía', 'de:', 's.l.', 's.a.'],
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

            # Direcciones postales (formato español, alemán y genérico mejorado)
            'address': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:calle|c\/|avenida|av\.|avda\.|plaza|pza\.|paseo|p\.|camino|carretera|c\.|strasse|straße|str\.|rambergstr)\s+[A-ZÁÉÍÓÚÑa-záéíóúñß\s]+[,\.]?\s+(?:n[úuº]?\.?|número|num\.?|oficina)?\s*\d{1,4}(?:\s*[a-z])?(?:\s*[,\-]\s*(?:piso|p\.?|pta\.?|puerta|portal|escalera|esc\.?|bloque|bl\.?|oficina)\s*[A-Z0-9\-]+)?(?:\s*[,\-]\s*\d{5}(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)?)?|'  # Calle Mayor, 25, oficina 58, Barcelona | Rambergstr. 2
                    r'[A-ZÁÉÍÓÚÑa-záéíóúñß]+(?:strasse|straße|str\.)\s+\d{1,4}[a-z]?(?:\s*,\s*\d{5}\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]+)?|'  # Romanstrasse 62a, 80639 München
                    r'\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)(?:\s*,\s*(?:Apt|Apartment|Suite|Ste|Unit|#)\s*[A-Z0-9\-]+)?(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,?\s*[A-Z]{2}\s+\d{5})?'  # 123 Main Street, Apt 4B
                    r')',
                    re.IGNORECASE | re.MULTILINE
                ),
                'context_keywords': ['dirección', 'direccion', 'domicilio', 'address', 'residencia', 'vive en', 'calle', 'avenida', 'ubicación', 'localidad', 'de:', 'para:'],
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

            # Nombres completos (mejorado con mayúsculas y minúsculas mixtas)
            'fullName': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Sr\.|Sra\.|Dr\.|Dra\.|Don|Doña|Mr\.|Mrs\.|Ms\.|Frau|Herr)?\s*'  # Prefijo opcional
                    r'[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]{2,}(?:[\s\-][A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]{2,}){1,4}'  # 2-5 palabras con mayúsculas mixtas
                    r')',
                    re.MULTILINE
                ),
                'context_keywords': ['nombre', 'apellido', 'titular', 'cliente', 'paciente', 'beneficiario', 'solicitante', 'asegurado', 'persona', 'señor', 'señora', 'firmante', 'de:', 'para:', 'client'],
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

            # ===== CAMPOS ESPECÍFICOS DE SEGUROS Y JURÍDICO =====

            # Número de Factura
            'numeroFactura': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Factura|Invoice|Rechnung|Bill|Receipt)[\s]+(?:N[úuº]?\.?|Number|No|Nr)[\s:#\-\.]*[A-Z0-9\-\/\.]{3,20}|'  # Factura Nº: ORD./25/673, Invoice No: 12345
                    r'(?:N[úuº]?\.?|Num\.?)[\s]?(?:Factura|Invoice|Rechnung)[\s:#\-]*[A-Z0-9\-\/\.]{3,20}|'  # Nº Factura: ABC-123
                    r'(?:FACTURA|INVOICE|RECHNUNG)[\s:]+[A-Z0-9\-\/\.]{3,20}'  # FACTURA: ORD./25/673
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['factura', 'invoice', 'rechnung', 'bill', 'receipt', 'número', 'number', 'fecha', 'importe', 'total'],
                'validator': False,
            },

            # Tomador del seguro
            'tomador': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Tomador|Tomadora|Contratante)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}|'  # Tomador: Juan Pérez García
                    r'(?:Nombre[\s]+del[\s]+Tomador|Tomador[\s]+del[\s]+Seguro)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}'  # Nombre del Tomador: ...
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['tomador', 'tomadora', 'contratante', 'asegurado', 'póliza', 'poliza', 'seguro', 'titular del seguro'],
                'validator': False,
            },

            # Número de Póliza
            'numeroPoliza': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:N[úuº]?\.?[\s]?Póliza|N[úuº]?\.?[\s]?Poliza|Póliza[\s]+N[úuº]?\.?|Poliza[\s]+N[úuº]?\.?|Num[\s]?\.?[\s]?Póliza|Num[\s]?\.?[\s]?Poliza)[\s:#\-]+[A-Z0-9\-\/]{5,20}|'  # Nº Póliza: ABC-123456
                    r'(?:Policy[\s]+Number|Policy[\s]+No|Pol[\s]+No)[\s:#\-\.]+[A-Z0-9\-\/]{5,20}|'  # Policy No: 123456
                    r'[A-Z]{2,4}[\-\/]?\d{6,12}(?=.*(?:póliza|poliza|policy))'  # ABC-123456789 (con contexto)
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['póliza', 'poliza', 'policy', 'número de póliza', 'numero de poliza', 'policy number', 'contrato', 'seguro'],
                'validator': False,
            },

            # Domicilio
            'domicilio': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Domicilio|Domicilio[\s]+Social|Dirección|Direccion|Address|Residencia)[\s:]+(?:calle|c\/|avenida|av\.|plaza|pza\.|paseo|camino)?[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s,\.º\-]{10,100}|'  # Domicilio: Calle Mayor, 25
                    r'(?:Vive[\s]+en|Reside[\s]+en|Ubicado[\s]+en|Sito[\s]+en)[\s:]+[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s,\.º\-]{10,100}'  # Vive en: Madrid...
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['domicilio', 'dirección', 'direccion', 'address', 'residencia', 'vive en', 'ubicación', 'calle', 'avenida'],
                'validator': False,
            },

            # Código Postal
            'codigoPostal': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:C[\.]?P[\.]?|Código[\s]+Postal|Codigo[\s]+Postal|CP|Postal[\s]+Code|Zip[\s]+Code)[\s:#\-]*(\d{5})|'  # CP: 28013, Código Postal: 08001
                    r'(?<!\d)\d{5}(?!\d)(?=.*(?:madrid|barcelona|valencia|sevilla|bilbao|málaga|murcia|palma|las palmas|alicante|córdoba|valladolid|vigo|gijón|zaragoza|spain|españa))'  # 28013 (con contexto de ciudad)
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['código postal', 'codigo postal', 'cp', 'postal', 'zip', 'código', 'codigo', 'localidad'],
                'validator': False,
            },

            # Asegurado / Beneficiario
            'asegurado': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Asegurado|Asegurada|Beneficiario|Beneficiaria|Titular|Interesado)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}|'  # Asegurado: Juan García
                    r'(?:Nombre[\s]+del[\s]+Asegurado|Nombre[\s]+del[\s]+Beneficiario)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}'
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['asegurado', 'asegurada', 'beneficiario', 'beneficiaria', 'titular', 'interesado', 'póliza', 'poliza', 'seguro'],
                'validator': False,
            },

            # Fecha de Efecto / Vigencia
            'fechaEfecto': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Fecha[\s]+de[\s]+Efecto|Fecha[\s]+de[\s]+Inicio|Inicio[\s]+de[\s]+Vigencia|Vigencia|Effective[\s]+Date)[\s:]+\d{1,2}[\s\-\/\.]\d{1,2}[\s\-\/\.]\d{2,4}|'  # Fecha de Efecto: 01/01/2024
                    r'(?:Desde|From)[\s:]+\d{1,2}[\s\-\/\.]\d{1,2}[\s\-\/\.]\d{2,4}[\s]+(?:al|hasta|to|until)[\s]+\d{1,2}[\s\-\/\.]\d{1,2}[\s\-\/\.]\d{2,4}'  # Desde 01/01/2024 al 31/12/2024
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['fecha de efecto', 'vigencia', 'inicio', 'fecha inicio', 'effective date', 'póliza', 'poliza', 'contrato'],
                'validator': False,
            },

            # Prima / Importe del seguro
            'primaSeguro': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Prima|Importe|Cuota|Premium|Tarifa|Coste[\s]+Anual)[\s:]+\d{1,}[,\.]?\d{0,2}[\s]?(?:€|EUR|euros?|dollars?|\$)|'  # Prima: 500,50 €
                    r'(?:Pago|Payment)[\s:]+\d{1,}[,\.]?\d{0,2}[\s]?(?:€|EUR|euros?)'  # Pago: 150 €
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['prima', 'importe', 'cuota', 'premium', 'tarifa', 'coste', 'pago', 'precio', 'póliza', 'poliza'],
                'validator': False,
            },

            # Mediador / Corredor / Agente
            'mediador': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Mediador|Mediadora|Corredor|Corredora|Agente|Broker|Intermediario)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}|'  # Mediador: María López
                    r'(?:Nombre[\s]+del[\s]+Mediador|Nombre[\s]+del[\s]+Corredor)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{5,50}'
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['mediador', 'mediadora', 'corredor', 'corredora', 'agente', 'broker', 'intermediario', 'correduría', 'correduria'],
                'validator': False,
            },

            # Siniestro
            'siniestro': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Siniestro|Claim|Reclamación|Reclamacion|Parte|Incidente)[\s]+N[úuº]?\.?[\s:#\-]+[A-Z0-9\-\/]{5,20}|'  # Siniestro Nº: 2024/001234
                    r'(?:N[úuº]?\.?[\s]?Siniestro|Claim[\s]+Number)[\s:#\-]+[A-Z0-9\-\/]{5,20}'  # Nº Siniestro: ABC-123
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['siniestro', 'claim', 'reclamación', 'reclamacion', 'parte', 'incidente', 'daño', 'daños', 'accidente'],
                'validator': False,
            },

            # NIF/CIF empresa aseguradora
            'nifAseguradora': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Aseguradora|Compañía|Compania|Empresa)[\s:]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]{3,40}[\s,]+(?:NIF|CIF)[\s:#\-]+[A-Z0-9\-]{9,12}|'  # Aseguradora: MAPFRE, CIF: A12345678
                    r'(?:NIF|CIF)[\s]+(?:Aseguradora|Compañía|Empresa)[\s:#\-]+[A-Z0-9\-]{9,12}'  # CIF Aseguradora: A12345678
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['aseguradora', 'compañía', 'compania', 'empresa', 'nif', 'cif', 'fiscal', 'seguro'],
                'validator': False,
            },

            # Cuenta bancaria para pagos/domiciliación
            'cuentaDomiciliacion': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Cuenta[\s]+de[\s]+domiciliación|Cuenta[\s]+domiciliacion|Domiciliación[\s]+bancaria|IBAN[\s]+domiciliación)[\s:]+ES[\s\.\-]?\d{2}(?:[\s\.\-]?\d){20}|'  # Cuenta de domiciliación: ES12 1234...
                    r'(?:Pago[\s]+domiciliado[\s]+en|Domiciliado[\s]+en)[\s:]+ES[\s\.\-]?\d{2}(?:[\s\.\-]?\d){20}'  # Pago domiciliado en: ES12...
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['domiciliación', 'domiciliacion', 'cuenta', 'iban', 'pago', 'bancaria', 'recibo', 'domiciliado'],
                'validator': True,
            },

            # Matrícula del vehículo asegurado
            'matriculaAsegurada': {
                'regex': re.compile(
                    r'(?:'
                    r'(?:Matrícula|Matricula|Vehículo|Vehiculo|Automóvil|Automovil)[\s:]+\d{4}[\s\-]?[BCDFGHJKLMNPRSTVWXYZ]{3}|'  # Matrícula: 1234 ABC
                    r'(?:Placa|Registration)[\s:]+[A-Z0-9\-]{6,10}'  # Placa: ABC-1234
                    r')',
                    re.IGNORECASE
                ),
                'context_keywords': ['matrícula', 'matricula', 'vehículo', 'vehiculo', 'coche', 'auto', 'automóvil', 'seguro de coche', 'placa'],
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
