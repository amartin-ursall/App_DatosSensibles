"""
Test completo del procesamiento del PDF Canarias
"""
import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pdf_processor import pdf_processor

def test_process_canarias():
    """Procesa el PDF de Canarias para diagnosticar el problema"""
    input_pdf = r"incidencias\Canarias_scan_20250603_075732.pdf"
    output_pdf = r"incidencias\Canarias_scan_20250603_075732_processed.pdf"

    if not os.path.exists(input_pdf):
        print(f"ERROR: No se encuentra {input_pdf}")
        return

    print(f"\n{'='*80}")
    print(f"PROCESANDO: Canarias_scan_20250603_075732.pdf")
    print(f"{'='*80}\n")

    # Habilitar todas las reglas
    enabled_rules = {
        'dni': True,
        'nie': True,
        'cif': True,
        'email': True,
        'phone': True,
        'iban': True,
        'creditCard': True,
        'dateOfBirth': True,
        'address': True,
        'fullName': True,
        'username': True,
        'accountHolder': True,
        'passport': True,
        'licensePlate': True,
        'ssn': True,
        'employeeId': True,
        'cookie': True,
        'credentials': True,
        'healthData': True,
        'numeroFactura': True,
        'tomador': True,
        'numeroPoliza': True,
        'domicilio': True,
        'codigoPostal': True,
        'asegurado': True,
        'fechaEfecto': True,
        'primaSeguro': True,
        'mediador': True,
        'siniestro': True,
        'nifAseguradora': True,
        'cuentaDomiciliacion': True,
        'matriculaAsegurada': True,
    }

    try:
        stats = pdf_processor.process_pdf(
            input_path=input_pdf,
            output_path=output_pdf,
            enabled_rules=enabled_rules,
            sensitivity_level='normal',
            action='redact'  # Usar redact para ver si se subraya
        )

        print(f"\n{'='*80}")
        print(f"RESULTADO:")
        print(f"  Total matches: {stats['total_matches']}")
        print(f"  Por tipo: {stats['by_type']}")
        print(f"  Por pagina: {stats['by_page']}")
        print(f"  Paginas procesadas: {stats['pages_processed']}")
        print(f"{'='*80}\n")

        if os.path.exists(output_pdf):
            print(f"OK PDF procesado guardado en: {output_pdf}")
        else:
            print(f"ERROR: No se genero el PDF de salida")

    except Exception as e:
        print(f"\nERROR durante el procesamiento:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_process_canarias()
