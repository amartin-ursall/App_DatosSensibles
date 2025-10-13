"""
Script de prueba simple para el detector
"""
from detector import detector
from validators import validator
from normalizer import normalizer

# Texto de prueba con datos sensibles
test_text = """
Juan Perez García
DNI: 12345678Z
Email: juan.perez@example.com
Teléfono: 612 345 678
IBAN: ES76 2077 0024 0031 0257 5766
Tarjeta: 4111 1111 1111 1111

Diagnóstico: diabetes tipo 2
Medicación: metformina 850mg

Password: MiContraseña123!
API_KEY: sk-1234567890abcdef
"""

print("=" * 60)
print("TEST DEL DETECTOR DE DATOS SENSIBLES")
print("=" * 60)

# Configurar reglas (todas habilitadas)
rules = {
    'email': True,
    'phone': True,
    'dni': True,
    'nie': False,
    'cif': False,
    'iban': True,
    'creditCard': True,
    'credentials': True,
    'healthData': True,
}

print("\n[Texto de prueba]")
print("-" * 60)
print(test_text)
print("-" * 60)

print("\n[Detectando con sensibilidad NORMAL...]")
matches = detector.detect(test_text, rules, sensitivity_level='normal')

print(f"\n[OK] Encontradas {len(matches)} deteccion(es):\n")

for i, match in enumerate(matches, 1):
    print(f"{i}. {match['type'].upper()}")
    print(f"   Valor: {match['value']}")
    print(f"   Confianza: {match['confidence']:.2%}")
    print(f"   Posición: {match['start']}-{match['end']}")
    print(f"   Contexto: ...{match['context'][:50]}...")
    print()

# Estadísticas
stats = {}
for match in matches:
    match_type = match['type']
    stats[match_type] = stats.get(match_type, 0) + 1

print("\n[Estadisticas por tipo]")
for data_type, count in stats.items():
    print(f"   {data_type}: {count}")

print("\n" + "=" * 60)

# Test de validaciones individuales
print("\n[TESTS DE VALIDACION]")
print("-" * 60)

test_cases = [
    ('12345678Z', 'dni', 'DNI valido'),
    ('12345678A', 'dni', 'DNI invalido (letra incorrecta)'),
    ('ES7620770024003102575766', 'iban', 'IBAN valido'),
    ('ES7620770024003102575767', 'iban', 'IBAN invalido (checksum)'),
    ('4111111111111111', 'creditCard', 'Tarjeta valida (Luhn)'),
    ('4111111111111112', 'creditCard', 'Tarjeta invalida (Luhn)'),
    ('juan@example.com', 'email', 'Email valido'),
    ('juan@', 'email', 'Email invalido'),
]

for value, data_type, description in test_cases:
    is_valid = validator.validate(value, data_type)
    status = "[OK]" if is_valid else "[FAIL]"
    print(f"{status} {description}: {value}")

print("\n" + "=" * 60)
print("[OK] Test completado")
print("=" * 60)
