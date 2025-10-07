import { RedactionRules, RedactionStrategy } from "./types";
import { PDFDocument, rgb, StandardFonts } from "pdf-lib";

const LOREM_IPSUM_PDF =
  "This is a simulated redacted PDF file. In a real application, the sensitive content would be covered by black boxes. This file is a placeholder to demonstrate the download functionality. Redacted content based on rules:\n";

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
    // Some PDFs have issues with text extraction, this can help
    ignoreEncryption: true 
  });
  const regexes = getRegex(rules);
  const pages = pdfDoc.getPages();
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const { width, height } = page.getSize();
    const textContent = await page.getTextContent();

    if (textContent.items.length === 0) continue;

    let fullText = "";
    textContent.items.forEach(item => {
        if ('str' in item) {
            fullText += item.str;
        }
    });

    for (const [regex, token] of regexes) {
        let match;
        // Reset regex state for each page
        const pageRegex = new RegExp(regex); 
        while ((match = pageRegex.exec(fullText)) !== null) {
          const matchedText = match[0];
          
          if (token === "CREDIT_CARD" && !applyLuhn(matchedText)) {
            continue;
          }

          // This is a simplified approach to finding the position.
          // A more robust solution would map characters to their exact coordinates.
          // For now, we'll find the text block and redact the whole thing.
          for (const item of textContent.items) {
            if ('str' in item && item.str.includes(matchedText)) {
                const { transform, width: itemWidth, height: itemHeight } = item;
                const x = transform[4];
                const y = height - transform[5] - itemHeight; // pdf-lib y-axis is bottom-up

                page.drawRectangle({
                    x: x - 1,
                    y: height - transform[5] - (itemHeight / 4), // Adjust y position
                    width: itemWidth + 2,
                    height: itemHeight,
                    color: rgb(0, 0, 0),
                });
            }
          }
        }
    }
  }

  const pdfBytes = await pdfDoc.save();
  return new Blob([pdfBytes], { type: "application/pdf" });
};
