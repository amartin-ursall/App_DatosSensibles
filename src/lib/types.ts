export type RedactionRuleInfo = {
  id: "creditCard" | "email" | "phone" | "name" | "ipAddress";
  name: string;
  description: string;
};

export type RedactionRules = Record<RedactionRuleInfo["id"], boolean>;

export type RedactionStrategy = "mask" | "redact";

export const supportedMimeTypes = [
  "text/plain",
  "text/csv",
  "text/markdown",
  "application/json",
  "application/pdf",
];

// Combine mimetypes and extensions for broader support
export const supportedFileTypes = [
  ...supportedMimeTypes,
  ".txt",
  ".csv",
  ".md",
  ".json",
  ".pdf",
  ".log",
];

export const fileTypeExtensions: { [key: string]: string } = {
  "text/plain": "txt",
  "text/csv": "csv",
  "text/markdown": "md",
  "application/json": "json",
  "application/pdf": "pdf",
  "application/log": "log", // Custom for .log
};
