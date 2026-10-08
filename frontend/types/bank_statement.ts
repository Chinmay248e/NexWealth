/**
 * Bank Statement type definitions matching NEXWEALTH_DATA_CONTRACT.md
 */

export interface BankStatementCreateInput {
  fileName: string;
  accountName: string;
  status?: string;
}

export interface BankStatementUpdateInput {
  fileName?: string;
  accountName?: string;
  status?: string;
}

export interface ParsedTransaction {
  date: string;
  description: string;
  amount: number;
  type: "income" | "expense";
  category: string;
  source: string;
}

export interface BankStatementParseResult {
  statementId: string;
  fileName: string;
  accountName: string;
  status: string;
  transactionCount: number;
  totalCredits: number;
  totalDebits: number;
  transactions: ParsedTransaction[];
}

export interface ImportTransactionsResponse {
  message: string;
  importedCount: number;
  statementId: string;
}
