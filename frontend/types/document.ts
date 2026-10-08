/**
 * Document type definitions matching NEXWEALTH_DATA_CONTRACT.md
 */

export const DOCUMENT_CATEGORIES = [
  "Tax Return",
  "Insurance",
  "Investment",
  "Invoice",
  "Salary Slip",
  "Other",
] as const;

export type DocumentCategory = (typeof DOCUMENT_CATEGORIES)[number];

export interface DocumentCreateInput {
  fileName: string;
  documentType: string;
  status?: string;
}

export interface DocumentUpdateInput {
  fileName?: string;
  documentType?: string;
  status?: string;
}
