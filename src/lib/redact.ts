
import { RedactionRules, RedactionStrategy } from "./types";
import { PDFDocument, rgb, StandardFonts } from "pdf-lib";

// Basic Luhn algorithm implementation
const applyLuhn = (cc: string): boolean => {
  if (/[^0-9-\s]+/.test(cc)) return false;

  let nCheck = 0;
  let bEven = false;
  const val = cc.replace(/\D/g, "");

  for (var n = val.length - 1; n >= 0; n--) {
    var cDigit = val.charAt(n),
      nDigit = parseInt(cDigit, 10);

    if (bEven && (nDigit *= 2) > 9) nDigit -= 9;

    nCheck += nDigit;
    bEven = !bEven;
  }

  return nCheck % 10 === 0;
};

const mask = (match: string, strategy: RedactionStrategy, token: string) => {
  return strategy === "redact" ? `[${token}]` : "x".repeat(match.length);
};

const getRegex = (rules: RedactionRules): [RegExp, string][] => {
  const regexes: [RegExp, string][] = [];
  if (rules.email) {
    regexes.push([/[\w\.-]+@[\w\.-]+\.\w+/g, "EMAIL"]);
  }
  if (rules.phone) {
    regexes.push([
      /(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/g,
      "PHONE",
    ]);
  }
  if (rules.creditCard) {
    // This will match potential credit card numbers, which we then validate with Luhn
    regexes.push([/\b(?:\d[ -]*?){13,16}\b/g, "CREDIT_CARD"]);
  }
  if (rules.name) {
    // This is a simple example; a real implementation would be more robust
    regexes.push([/\b(John|Jane)\s(Doe|Smith)\b/gi, "NAME"]);
  }
  if (rules.ipAddress) {
    const ipv4Regex = /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/;
    const ipv6Regex =
      /(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))/;
    regexes.push([new RegExp(`${ipv4Regex.source}|${ipv6Regex.source}`, "g"), "IP_ADDRESS"]);
  }
  return regexes;
};


export const redactText = (
  text: string,
  rules: RedactionRules,
  strategy: RedactionStrategy
): string => {
  let redactedText = text;
  const regexes = getRegex(rules);
  
  for (const [regex, token] of regexes) {
    redactedText = redactedText.replace(regex, (match) => {
      if (token === "CREDIT_CARD" && !applyLuhn(match)) {
        return match;
      }
      return mask(match, strategy, token);
    });
  }

  return redactedText;
};

export const redactPdf = async (
  file: File,
  rules: RedactionRules
): Promise<Blob> => {
  const fileBuffer = await file.arrayBuffer();
  const pdfDoc = await PDFDocument.load(fileBuffer, {
    ignoreEncryption: true,
  });
  const regexes = getRegex(rules);
  const pages = pdfDoc.getPages();
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const { width, height } = page.getSize();
    
    // This is a workaround as pdf-lib doesn't have direct text extraction.
    // We get the drawing instructions.
    const contentStream = page.getContentStream();
    let textToRedact = '';

    // A simple parser for PDF text drawing commands (Tj, TJ).
    // This is not a full PDF content stream parser but works for many simple PDFs.
    for (const op of contentStream.operators) {
        if (op.name === 'Tj' || op.name === 'TJ') {
            const arg = op.args[0];
            if (typeof arg === 'string') {
                textToRedact += arg;
            } else if (Array.isArray(arg)) {
                arg.forEach(sub => {
                    if (typeof sub === 'string') {
                        textToRedact += sub;
                    }
                });
            }
        }
        if (op.name === 'BT') textToRedact += '\n'; // Reset for each text block
    }
    
    if (!textToRedact) continue;

    for (const [regex, token] of regexes) {
      let match;
      const pageRegex = new RegExp(regex.source, 'g' + (regex.ignoreCase ? 'i' : ''));
      while ((match = pageRegex.exec(textToRedact)) !== null) {
        const matchedText = match[0];
        if (token === "CREDIT_CARD" && !applyLuhn(matchedText)) {
          continue;
        }

        // Since we can't get coordinates, we have to cover the whole page.
        // This is a significant limitation. A better solution would involve
        // a more advanced PDF library that can provide coordinates for text.
        // For this app, we'll draw a placeholder redaction box and a warning.
      }
    }
  }

  // Since we can't reliably find text coordinates, we will add a warning to the PDF
  // and redact a small area as a demonstration.
  const firstPage = pages[0];
  if(firstPage) {
    const {width, height} = firstPage.getSize();
    firstPage.drawRectangle({
        x: 50,
        y: height - 100,
        width: 300,
        height: 20,
        color: rgb(0,0,0)
    });
    firstPage.drawText("NOTE: This is a sample redaction.", {
        x: 50,
        y: height - 120,
        size: 12,
        font,
        color: rgb(1,0,0)
    })
    firstPage.drawText("pdf-lib cannot accurately locate text for redaction.", {
        x: 50,
        y: height - 135,
        size: 10,
        font,
        color: rgb(0,0,0)
    })
  }


  const pdfBytes = await pdfDoc.save();
  return new Blob([pdfBytes], { type: "application/pdf" });
};
