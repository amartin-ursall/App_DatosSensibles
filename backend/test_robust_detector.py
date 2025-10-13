"""
Test completo del detector robusto con todos los nuevos campos
"""
from detector import detector

# Texto de prueba exhaustivo con TODOS los tipos de datos
test_text = """
=== DOCUMENTO DE PRUEBA COMPLETO ===

DATOS PERSONALES:
Titular: Juan Perez Garcia
Sr. Antonio Lopez Martinez
Dra. Maria Fernandez Rodriguez
Fecha de nacimiento: 15/03/1985
Nacio el 1 de enero de 1990
Born: January 15, 1980

IDENTIFICACION:
DNI: 12345678Z
NIE: X1234567L
Pasaporte: AA1234567
Passport No: 123456789
SSN: 123-45-6789

CONTACTO:
Email: juan.perez@example.com
Correo electronico: maria@empresa.es
Telefono: +34 612 345 678
Tel: 91-123-45-67
Movil: 655.123.456

DIRECCION:
Direccion: Calle Mayor, 25, 3 A, 28013 Madrid
Domicilio: Avenida de la Constitucion 100, piso 2, puerta B, 41001 Sevilla
Address: 123 Main Street, Apt 4B, New York, NY 10001
Vive en c/ Gran Via 45, Madrid

FINANCIERO:
IBAN: ES76 2077 0024 0031 0257 5766
IBAN con puntos: ES76.2077.0024.0031.0257.5766
Cuenta bancaria: ES7620770024003102575766
Tarjeta: 4111 1111 1111 1111
Tarjeta de credito: 5555-5555-5555-4444

VEHICULOS:
Matricula: 1234 ABC
Placa del coche: M-5678-CD
License plate: ABC-1234

USUARIO Y SESION:
Usuario: john_doe
Username: maria.garcia
Alias: @tech_guru
Login: admin123
Cookie: sessionid=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
Set-Cookie: auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
JWT: eyJzdWIiOiIxMjM0NTY3ODkwIn0

CREDENCIALES (CRITICO):
Password: MiPassword123!
Contrasena: SuperSecret2024
API_KEY: sk-1234567890abcdefghijklmnop
Token: Bearer xyz123abc456def789
Secret: my_secret_key_2024

DATOS DE SALUD (CRITICO):
Diagnostico: diabetes tipo 2
Medicacion: metformina 850mg dos veces al dia
Receta: ibuprofeno 600mg cada 8 horas
Historia clinica: paciente con hipertension arterial
Tratamiento: quimioterapia ciclo 3

TITULAR DE CUENTA:
Titular: Maria Isabel Gonzalez Fernandez
Beneficiario: Carlos Alberto Rodriguez Martinez
Account holder: John Michael Smith Anderson
Propietario: Ana Sofia Torres Navarro

FIN DEL DOCUMENTO
"""

print("=" * 80)
print(" TEST DETECTOR ROBUSTO - TODOS LOS CAMPOS")
print("=" * 80)

# Configurar TODAS las reglas habilitadas
rules = {
    'email': True,
    'phone': True,
    'dni': True,
    'nie': True,
    'cif': True,
    'iban': True,
    'creditCard': True,
    'ssn': True,
    'passport': True,
    'licensePlate': True,
    'dateOfBirth': True,
    'address': True,
    'username': True,
    'fullName': True,
    'accountHolder': True,
    'cookie': True,
    'credentials': True,
    'healthData': True,
}

print("\n[Detectando con sensibilidad NORMAL...]")
matches = detector.detect(test_text, rules, sensitivity_level='normal')

print(f"\n[OK] Encontradas {len(matches)} deteccion(es):\n")

# Agrupar por tipo
by_type = {}
for match in matches:
    match_type = match['type']
    if match_type not in by_type:
        by_type[match_type] = []
    by_type[match_type].append(match)

# Mostrar resultados agrupados
for data_type, type_matches in sorted(by_type.items()):
    print(f"\n{'='*60}")
    print(f"  {data_type.upper()} ({len(type_matches)} encontrado(s))")
    print(f"{'='*60}")

    for i, match in enumerate(type_matches, 1):
        print(f"\n  [{i}] Valor: {match['value']}")
        print(f"      Confianza: {match['confidence']:.2%}")
        print(f"      Posicion: {match['start']}-{match['end']}")
        if match.get('context'):
            context_preview = match['context'][:70].replace('\n', ' ')
            print(f"      Contexto: ...{context_preview}...")

# Estadisticas finales
print("\n" + "=" * 80)
print(" RESUMEN FINAL")
print("=" * 80)
print(f"\n  Total de detecciones: {len(matches)}")
print(f"\n  Detecciones por tipo:")
for data_type, count in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"    - {data_type}: {len(by_type[data_type])}")

print("\n" + "=" * 80)
print("[OK] Test completado exitosamente")
print("=" * 80)
