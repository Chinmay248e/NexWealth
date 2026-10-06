import { ExpenseCategory } from "./contract";

export const EXPENSE_CATEGORIES: ExpenseCategory[] = [
  "Food",
  "Shopping",
  "Transport",
  "Bills",
  "Entertainment",
  "Education",
  "Medical",
  "Travel",
  "Other",
];

/**
 * Expense API Request & Input Types
 */
export interface ExpenseCreateInput {
  description: string;
  amount: number;
  category: ExpenseCategory;
  date: string;
}

export interface ExpenseUpdateInput {
  description?: string;
  amount?: number;
  category?: ExpenseCategory;
  date?: string;
}
