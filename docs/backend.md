Núcleo PDF (lectura, coordenadas, edición)

PyMuPDF (fitz) → leer texto por página, buscar con coordenadas y subrayar/redactar nativo. Muy precisa.
pip install pymupdf

import fitz
doc = fitz.open("in.pdf")
for i, page in enumerate(doc):
    for rect in page.search_for("ES76 2077"):  # ejemplo IBAN parcial
        page.add_highlight_annot(rect)
doc.save("out.pdf")


Nota: revisar su licencia (AGPL/comercial) con Jurídico si tu app es cerrada.

pdfplumber → extracción de palabras con cajas (coordenadas) basada en pdfminer; ideal para casar regex con posiciones.
pip install pdfplumber

import pdfplumber
with pdfplumber.open("in.pdf") as pdf:
    words = pdf.pages[0].extract_words()  # [{'text': 'ES76', 'x0':..., 'top':...}, ...]


pypdf o pikepdf → manipulación estructural del PDF (Apache/MPL). Útiles si quieres evitar AGPL.
pip install pypdf / pip install pikepdf

borb → edición avanzada (dibujar rectángulos, redactar) con Apache-2.0.
pip install borb

OCR (cuando el PDF es escaneado/imagen)

ocrmypdf → añade capa de texto alineada (usa Tesseract por debajo). Resulta perfecto para luego buscar y subrayar.
pip install ocrmypdf

import ocrmypdf
ocrmypdf.ocr("scan.pdf", "scan_ocr.pdf", language="spa", deskew=True)

Detección (reglas + validaciones)

regex (módulo regex) → expresiones tolerantes a espacios/saltos de línea.
pip install regex

import regex as re
IBAN_ES = re.compile(r'ES\d{2}(?:[ \t]?\d){20}', re.I)


python-stdnum → validaciones reales: IBAN (mód.97), Luhn para tarjeta, NIF/NIE/CIF (España).
pip install python-stdnum

from stdnum import iban, luhn
from stdnum.es import nif, nie, cif
iban.is_valid("ES7620770024003102575766"); luhn.is_valid("4111111111111111")
nif.is_valid("12345678Z"); nie.is_valid("X1234567L"); cif.is_valid("A12345678")

NLP (opcional, para contexto en Salud/PII)

spaCy + modelo español (es_core_news_md) para NER básica (PERSON, ORG, LOC).
pip install spacy && python -m spacy download es_core_news_md

Microsoft Presidio (si quieres un detector PII configurable on-prem).
pip install presidio-analyzer presidio-anonymizer

Utilidades de calidad de texto

ftfy → arregla ligaduras/encoding raros (e.g., “ﬁ”→“fi”).
pip install ftfy

rapidfuzz → ayuda a casar detecciones entre texto normalizado y texto original (fuzzy match página a página).
pip install rapidfuzz

Pilas recomendadas (elige según tus restricciones)

Pila A – Precisión y rapidez (revisar licencia):
PyMuPDF + pdfplumber + ocrmypdf + regex + python-stdnum (+ ftfy/rapidfuzz opcional)

Pila B – 100% licencias permisivas (Apache/MPL):
pypdf/pikepdf + pdfplumber + ocrmypdf + regex + python-stdnum (+ borb para redacción/overlay)

Patrón de uso (resumen de flujo)

Si es escaneado: ocrmypdf → PDF con texto.

Extrae texto y palabras: pdfplumber (palabras+cajas) o PyMuPDF (get_text("words")).

Normaliza y detecta: ftfy + regex + stdnum (valida IBAN/Luhn/NIF…).

Localiza coordenadas: busca por página con patrones tolerantes (o fuzzy con rapidfuzz).

Marca en PDF: highlight o redact con PyMuPDF (o borb/pypdf si evitas AGPL).

Guardar auditoría: JSON con tipo de dato, página, bbox y acción (subrayado/redactado).