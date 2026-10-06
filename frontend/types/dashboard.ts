/**
 * Dashboard Summary API Response Type
 * GET /api/v1/dashboard/summary
 */
export interface DashboardSummary {
  totalIncome: number;
  totalExpenses: number;
  availableSavings: number;
  savingsRate: number;
}
