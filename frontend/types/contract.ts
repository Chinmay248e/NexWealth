/**
 * ==========================================================================
 * NEXWEALTH TYPESCRIPT DATA CONTRACT
 * Single Source of Truth matching NEXWEALTH_DATA_CONTRACT.md
 * Strict CamelCase, Unique IDs, and INR Currency Standard
 * ==========================================================================
 */

// Person 1: User & Authentication
export interface User {
  id: string;
  name: string;
  email: string;
  passwordHash?: string;
  createdAt: string;
}

// Person 1: Income
export interface Income {
  id: string;
  userId: string;
  source: string;
  amount: number; // Stored as raw number in INR
  date: string; // YYYY-MM-DD
  createdAt: string;
}

// Person 1: Expense Categories (Strict Enum)
export type ExpenseCategory =
  | "Food"
  | "Shopping"
  | "Transport"
  | "Bills"
  | "Entertainment"
  | "Education"
  | "Medical"
  | "Travel"
  | "Other";

// Person 1: Expense
export interface Expense {
  id: string;
  userId: string;
  description: string;
  amount: number;
  category: ExpenseCategory;
  date: string;
  createdAt: string;
}

// Person 1: Transaction (Unified Ledger)
export type TransactionType = "income" | "expense";

export interface Transaction {
  id: string;
  userId: string;
  type: TransactionType;
  description: string;
  amount: number;
  category: string;
  date: string;
  source: string;
  createdAt: string;
}

// Person 2: Goal
export interface Goal {
  id: string;
  userId: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  targetDate: string;
  monthlyContribution: number;
  createdAt: string;
}

// Person 2: Document
export interface Document {
  id: string;
  userId: string;
  fileName: string;
  documentType: string;
  status: string;
  uploadedAt: string;
  createdAt: string;
}

// Person 2: Bank Statement
export interface BankStatement {
  id: string;
  userId: string;
  fileName: string;
  accountName: string;
  status: string;
  uploadedAt: string;
  createdAt: string;
}

// Person 3: Investment
export interface Investment {
  id: string;
  userId: string;
  name: string;
  type: string;
  investedAmount: number;
  currentValue: number;
  date: string;
  createdAt: string;
}

// Person 3: Budget
export interface Budget {
  id: string;
  userId: string;
  category: ExpenseCategory;
  limitAmount: number;
  month: string; // YYYY-MM
  createdAt: string;
}

// Person 3: Notification
export interface Notification {
  id: string;
  userId: string;
  type: string;
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
}

// Core Financial Calculations Response / State
export interface FinancialMetrics {
  totalIncome: number;
  totalExpenses: number;
  availableSavings: number;
  savingsRate: number; // (Available Savings / Total Income) * 100
  goalProgressMap: Record<string, number>; // (currentAmount / targetAmount) * 100
}
