/**
 * Analytics Data Types (Person 3)
 */
export interface FinancialOverview {
  totalIncome: number;
  totalExpenses: number;
  availableSavings: number;
  savingsRate: number;
}

export interface CategoryBreakdownItem {
  category: string;
  amount: number;
  percentage: number;
}

export interface MonthlyCashflowItem {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

export interface InvestmentOverview {
  totalInvested: number;
  currentValue: number;
  gainLoss: number;
  returnPercent: number;
}

export interface AnalyticsSummary {
  overview: FinancialOverview;
  categoryBreakdown: CategoryBreakdownItem[];
  monthlyCashflow: MonthlyCashflowItem[];
  investmentOverview: InvestmentOverview;
}
