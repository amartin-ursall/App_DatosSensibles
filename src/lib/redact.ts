import { RedactionRules, RedactionStrategy } from "./types";

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

export const redactText = (
  text: string,
  rules: RedactionRules,
  strategy: RedactionStrategy
): string => {
  let redactedText = text;

  if (rules.email) {
    const emailRegex = /[\w\.-]+@[\w\.-]+\.\w+/g;
    redactedText = redactedText.replace(emailRegex, (match) =>
      mask(match, strategy, "EMAIL")
    );
  }
  if (rules.phone) {
    const phoneRegex = /(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/g;
    redactedText = redactedText.replace(phoneRegex, (match) =>
      mask(match, strategy, "PHONE")
    );
  }
  if (rules.creditCard) {
    const ccRegex = /\b(?:\d[ -]*?){13,16}\b/g;
    redactedText = redactedText.replace(ccRegex, (match) => {
      if (applyLuhn(match)) {
        return mask(match, strategy, "CREDIT_CARD");
      }
      return match;
    });
  }
  if (rules.name) {
    const nameRegex = /\b(John|Jane)\s(Doe|Smith)\b/gi; // Simple example
    redactedText = redactedText.replace(nameRegex, (match) =>
      mask(match, strategy, "NAME")
    );
  }
  if (rules.ipAddress) {
    const ipRegex =
      /(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))/g;
    redactedText = redactedText.replace(ipRegex, (match) =>
      mask(match, strategy, "IP_ADDRESS")
    );
  }

  return redactedText;
};

export const redactPdf = (file: File, rules: RedactionRules): Blob => {
  // Simulate PDF redaction. In a real app, this would involve a library
  // to process the PDF, find text, and draw rectangles.
  // Here, we'll just create a new text file blob as a placeholder.
  const activeRules = Object.entries(rules)
    .filter(([, isEnabled]) => isEnabled)
    .map(([ruleName]) => ruleName)
    .join(", ");

  const blob = new Blob(
    [
      `Redacted version of: ${file.name}\n`,
      `${LOREM_IPSUM_PDF}${activeRules || "None"}`,
    ],
    { type: "text/plain" }
  );
  return blob;
};
