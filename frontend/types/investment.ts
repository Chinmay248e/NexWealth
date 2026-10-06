/**
 * Investment API Request & Input Types (Person 3)
 */
export interface InvestmentCreateInput {
  name: string;
  type: string;
  investedAmount: number;
  currentValue: number;
  date: string;
}

export interface InvestmentUpdateInput {
  name?: string;
  type?: string;
  investedAmount?: number;
  currentValue?: number;
  date?: string;
}

export const INVESTMENT_TYPES = [
  "Mutual Fund",
  "Stock",
  "Fixed Deposit",
  "Gold / SGB",
  "PPF / EPF",
  "Bonds",
  "Real Estate",
  "Other",
] as const;

export type InvestmentType = typeof INVESTMENT_TYPES[number] | string;
