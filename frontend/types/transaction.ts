import { TransactionType } from "./contract";

export interface TransactionFilterParams {
  type?: TransactionType;
  category?: string;
  date_from?: string;
  date_to?: string;
}

export const TRANSACTION_CATEGORIES = [
  "Food",
  "Shopping",
  "Transport",
  "Bills",
  "Entertainment",
  "Education",
  "Medical",
  "Travel",
  "Other",
] as const;
