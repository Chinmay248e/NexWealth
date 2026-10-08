/**
 * Goal type definitions matching NEXWEALTH_DATA_CONTRACT.md
 */

export interface GoalCreateInput {
  name: string;
  targetAmount: number;
  currentAmount?: number;
  targetDate: string; // YYYY-MM-DD
  monthlyContribution?: number;
}

export interface GoalUpdateInput {
  name?: string;
  targetAmount?: number;
  currentAmount?: number;
  targetDate?: string;
  monthlyContribution?: number;
}

export interface GoalAddFundsInput {
  amount: number;
}
