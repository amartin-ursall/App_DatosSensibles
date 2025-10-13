Pipeline recomendado (robusto y eficaz)

A. Si el PDF es digital (no escaneado):

Normaliza el PDF al leer: ignora ligaduras, quita guiones de fin de línea, unifica espacios.

Detecta con reglas/regex (DNI/NIE/CIF, IBAN, tarjeta con Luhn, email, teléfono) + palabras clave de salud.

Subraya/Redacta en el PDF usando las coordenadas nativas:

Busca cada hallazgo en su misma página con un buscador tolerante a espacios y guiones.

Aplica highlight o, si es necesario, redacción real (el texto desaparece del contenido).

B. Si el PDF es escaneado (imagen):

Pasa OCR local (p. ej., ocrmypdf) para añadir capa de texto alineada.

Repite los pasos de A) detección + subrayado/redacción sobre esa capa.

Notas técnicas clave (para que te funcione a la primera)

Normalización idéntica en detección y búsqueda:

Sustituye ligaduras (ﬀ, ﬁ, ﬂ → ff, fi, fl).

Une cortes de línea con guion (-\n → ``), y colapsa espacios múltiples.

Quita separadores en números (IBAN con espacios → solo alfanumérico) para la verificación (módulo 97/Luhn).

Búsqueda por página: evita buscar en todo el documento plano; trabaja página a página para mantener contexto y coordenadas.

Coincidencias “elásticas”: crea variantes del patrón para tolerar espacios y saltos (p. ej., ES\d{2}\s?[\d\s]{20} para IBAN).

Destacar vs Redactar: subrayar es visual; redactar debe eliminar el texto del contenido (cumplimiento). Úsalo si el PDF va a salir fuera.