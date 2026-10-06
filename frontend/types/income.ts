/**
 * Income API Request & Input Types
 */
export interface IncomeCreateInput {
  source: string;
  amount: number;
  date: string;
}

export interface IncomeUpdateInput {
  source?: string;
  amount?: number;
  date?: string;
}
