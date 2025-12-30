"""
Script de prueba para verificar la precisión del redactado
"""
import sys
sys.path.insert(0, 'backend')

from pdf_processor import pdf_processor
import os

# Configuración de prueba
INPUT_PDF = "test_parser.pdf"  # Ajusta este path
OUTPUT_PDF = "output_precision_test.pdf"

# Reglas de detección - todas activadas
rules = {
    "dni": True,
    "nie": True,
    "cif": True,
    "email": True,
    "phone": True,
    "iban": True,
    "creditCard": True,
    "dateOfBirth": True,
    "fullName": True,
    "address": True,
    "passport": True,
    "ssn": True,
    "username": True,
    "accountHolder": True,
    "licensePlate": True,
    "employeeId": True,
    "cookie": True,
    "credentials": True,
    "healthData": True,
    # Campos específicos de seguros
    "numeroFactura": True,
    "tomador": True,
    "numeroPoliza": True,
    "domicilio": True,
    "codigoPostal": True,
    "asegurado": True,
    "fechaEfecto": True,
    "primaSeguro": True,
    "mediador": True,
    "siniestro": True,
    "nifAseguradora": True,
    "cuentaDomiciliacion": True,
    "matriculaAsegurada": True,
}

if not os.path.exists(INPUT_PDF):
    print(f"❌ No se encontró el archivo: {INPUT_PDF}")
    print(f"Por favor, crea un PDF de prueba o ajusta la variable INPUT_PDF")
    sys.exit(1)

print("="*60)
print("PRUEBA DE PRECISIÓN DE REDACTADO")
print("="*60)
print(f"Archivo de entrada: {INPUT_PDF}")
print(f"Archivo de salida: {OUTPUT_PDF}")
print()

try:
    stats = pdf_processor.process_pdf(
        INPUT_PDF,
        OUTPUT_PDF,
        rules,
        sensitivity_level='strict',
        action='redact',  # Usar redact para ver bloques negros
        extraction_mode='auto'
    )

    print("\n" + "="*60)
    print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("="*60)
    print(f"Total de datos sensibles encontrados: {stats['total_matches']}")
    print(f"Páginas procesadas: {stats['pages_processed']}")

    if stats['by_type']:
        print("\nDesglose por tipo:")
        for data_type, count in stats['by_type'].items():
            print(f"  - {data_type}: {count}")

    print(f"\n📄 Abre el archivo '{OUTPUT_PDF}' para verificar la precisión del redactado")
    print("   Los bloques negros deberían cubrir SOLO el texto sensible, sin espacios extra")

except Exception as e:
    print("\n❌ ERROR:")
    print(str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
