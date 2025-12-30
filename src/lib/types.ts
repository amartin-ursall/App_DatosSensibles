export type RedactionRuleInfo = {
  id: "creditCard" | "email" | "phone" | "dni" | "nie" | "cif" | "ssn" | "iban" | "passport" | "licensePlate" | "address" | "dateOfBirth" | "username" | "fullName" | "accountHolder" | "cookie" | "credentials" | "healthData" | "employeeId";
  name: string;
  description: string;
};

export type RedactionRule = RedactionRuleInfo;

export type RedactionRules = Record<RedactionRuleInfo["id"], boolean>;

export type RedactionStrategy = "underline";

export type SensitivityLevel = "strict" | "normal" | "relaxed";

// Tipos de detección AI/TS eliminados del frontend

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

export interface ProcessingProgress {
  stage: string;
  percent: number;
  currentPage?: number;
  totalPages?: number;
  extractionMethod?: string;
  message?: string;
  done?: boolean;
  updatedAt?: number;
}
