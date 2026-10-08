/**
 * AI Advisor type definitions matching NEXWEALTH_DATA_CONTRACT.md
 */

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface AdvisorInsightCard {
  id: string;
  type: "optimization" | "strategy" | "warning" | "achievement";
  title: string;
  description: string;
  tag: string;
  impact?: string;
}

export interface FinancialContextSummary {
  totalIncome: number;
  totalExpenses: number;
  availableSavings: number;
  savingsRate: number;
  totalInvestments: number;
  totalGoalsTarget: number;
  totalGoalsSaved: number;
  topExpenseCategory?: string;
}

export interface AdvisorQueryRequest {
  message: string;
  history?: ChatMessage[];
}

export interface AdvisorQueryResponse {
  reply: string;
  insights: AdvisorInsightCard[];
  contextSummary: FinancialContextSummary;
  model: string;
}

export interface AdvisorInsightsResponse {
  insights: AdvisorInsightCard[];
  summary: FinancialContextSummary;
}
