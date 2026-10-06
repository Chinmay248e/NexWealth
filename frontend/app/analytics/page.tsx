"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatINR } from "@/lib/utils/currency";
import { getAnalyticsSummary } from "@/lib/api/analytics";
import { AnalyticsSummary } from "@/types/analytics";
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  Percent,
  RefreshCw,
  AlertCircle,
  PieChart as PieIcon,
  LineChart as ChartIcon,
  Layers,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const CATEGORY_COLORS = [
  "#00f2fe", // Cyan
  "#00f5a0", // Mint
  "#38bdf8", // Sky
  "#fbbf24", // Amber
  "#a855f7", // Purple
  "#f87171", // Rose
  "#ec4899", // Pink
  "#6366f1", // Indigo
  "#64748b", // Slate
];

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAnalyticsSummary();
      setAnalytics(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load financial analytics.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const overview = analytics?.overview || {
    totalIncome: 0,
    totalExpenses: 0,
    availableSavings: 0,
    savingsRate: 0,
  };

  const investment = analytics?.investmentOverview || {
    totalInvested: 0,
    currentValue: 0,
    gainLoss: 0,
    returnPercent: 0,
  };

  const categories = analytics?.categoryBreakdown || [];
  const monthlyData = analytics?.monthlyCashflow || [];

  const pieData = categories.map((c) => ({
    name: c.category,
    value: c.amount,
    percentage: c.percentage,
  }));

  const isNetSavingsPositive = overview.availableSavings >= 0;
  const isInvestmentPositive = investment.gainLoss >= 0;

  return (
    <AppShell>
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">
              Wealth Analytics & Intelligence
            </h2>
            <Badge variant="cyan">Person 3 Analytics</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Real-time financial cashflow modeling, category distributions, and portfolio growth metrics in INR (₹).
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={fetchAnalytics}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Analytics"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 p-4 rounded-md bg-red-500/10 border border-red-500/25 flex items-center justify-between text-red-300 text-sm shadow-sm">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
          <Button
            variant="ghost"
            onClick={fetchAnalytics}
            className="text-xs text-red-400 hover:text-white"
          >
            Retry
          </Button>
        </div>
      )}

      {/* 1. Core Financial Overview KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        {/* Total Income */}
        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Inflows
            </span>
            <div className="w-9 h-9 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-32 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div className="font-display font-black text-2xl text-white">
                {formatINR(overview.totalIncome)}
              </div>
            )}
            <div className="text-[11px] text-slate-500 mt-2">Cumulative verified income</div>
          </div>
        </Card>

        {/* Total Expenses */}
        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Outflows
            </span>
            <div className="w-9 h-9 rounded-sm bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-32 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div className="font-display font-black text-2xl text-white">
                {formatINR(overview.totalExpenses)}
              </div>
            )}
            <div className="text-[11px] text-slate-500 mt-2">All categorized expenditures</div>
          </div>
        </Card>

        {/* Net Savings */}
        <Card highlight className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              Net Savings
            </span>
            <div className="w-9 h-9 rounded-sm bg-mint-500/10 border border-border-mint flex items-center justify-center text-mint-400">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-32 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div
                className={`font-display font-black text-2xl ${
                  isNetSavingsPositive ? "text-mint-400" : "text-red-400"
                }`}
              >
                {isNetSavingsPositive ? "+" : ""}
                {formatINR(overview.availableSavings)}
              </div>
            )}
            <div className="text-[11px] text-slate-400 mt-2">Income minus expenses</div>
          </div>
        </Card>

        {/* Savings Rate */}
        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Savings Rate
            </span>
            <div className="w-9 h-9 rounded-sm bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Percent className="w-4 h-4" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-24 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div
                className={`font-display font-black text-2xl ${
                  overview.savingsRate >= 0 ? "text-mint-400" : "text-red-400"
                }`}
              >
                {overview.savingsRate.toFixed(1)}%
              </div>
            )}
            <div className="text-[11px] text-slate-500 mt-2">Efficiency ratio</div>
          </div>
        </Card>
      </div>

      {/* 2. Visual Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Income vs Expenses Cashflow Trend (2 cols) */}
        <Card className="lg:col-span-2 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-border-subtle">
            <div className="flex items-center gap-2">
              <ChartIcon className="w-4 h-4 text-cyan-400" />
              <h3 className="font-display font-bold text-base text-white">
                Monthly Income vs Expenses Trend
              </h3>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                <span className="text-slate-300">Income</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-mint-400" />
                <span className="text-slate-300">Expense</span>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="h-64 flex items-center justify-center text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
            </div>
          ) : monthlyData.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs">
              <Layers className="w-8 h-8 text-slate-600 mb-2" />
              <span>No monthly transaction data available for charting yet.</span>
            </div>
          ) : (
            <div className="w-full h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthlyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="incomeGlow" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00f2fe" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#00f2fe" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="expenseGlow" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00f5a0" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#00f5a0" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#64748b"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(val) => `₹${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0c1824",
                      borderColor: "rgba(0,242,254,0.3)",
                      borderRadius: "8px",
                      color: "#fff",
                      fontSize: "12px",
                    }}
                    formatter={(value: any) => [formatINR(Number(value)), ""]}
                  />
                  <Area
                    type="monotone"
                    dataKey="income"
                    name="Income"
                    stroke="#00f2fe"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#incomeGlow)"
                  />
                  <Area
                    type="monotone"
                    dataKey="expenses"
                    name="Expenses"
                    stroke="#00f5a0"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#expenseGlow)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        {/* Expense Category Donut Breakdown (1 col) */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-border-subtle">
            <div className="flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-mint-400" />
              <h3 className="font-display font-bold text-base text-white">
                Category Distribution
              </h3>
            </div>
            <Badge variant="mint">Outflows</Badge>
          </div>

          {isLoading ? (
            <div className="h-64 flex items-center justify-center text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin text-mint-400" />
            </div>
          ) : pieData.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs">
              <PieIcon className="w-8 h-8 text-slate-600 mb-2" />
              <span>No expense records recorded yet.</span>
            </div>
          ) : (
            <div className="w-full h-64 flex flex-col items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="48%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0c1824",
                      borderColor: "rgba(0,242,254,0.3)",
                      borderRadius: "8px",
                      color: "#fff",
                      fontSize: "12px",
                    }}
                    formatter={(val: any) => [formatINR(Number(val)), ""]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="text-[11px] text-slate-400 text-center -mt-2">
                {categories.length} active spending categories
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* 3. Investment Portfolio Intelligence Banner & Cards */}
      <Card highlight className="mb-8 p-6 bg-gradient-to-r from-slate-900 via-background to-cyan-950/30 border-border-accent">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6 pb-4 border-b border-border-subtle">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-display font-bold text-lg text-white">
                Investment Portfolio Performance
              </h3>
              <p className="text-xs text-slate-400">
                Asset allocation, capital appreciation, and compound return velocity.
              </p>
            </div>
          </div>
          <Badge variant="cyan">Asset Tracking</Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-md bg-background-elevated/40 border border-border-subtle">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Capital Deployed
            </div>
            <div className="font-display font-bold text-xl text-white">
              {formatINR(investment.totalInvested)}
            </div>
          </div>

          <div className="p-4 rounded-md bg-background-elevated/40 border border-border-subtle">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Current Valuation
            </div>
            <div className="font-display font-bold text-xl text-cyan-400">
              {formatINR(investment.currentValue)}
            </div>
          </div>

          <div className="p-4 rounded-md bg-background-elevated/40 border border-border-subtle">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Net Capital Growth
            </div>
            <div
              className={`font-display font-bold text-xl ${
                isInvestmentPositive ? "text-mint-400" : "text-red-400"
              }`}
            >
              {isInvestmentPositive ? "+" : ""}
              {formatINR(investment.gainLoss)}
            </div>
          </div>

          <div className="p-4 rounded-md bg-background-elevated/40 border border-border-subtle">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              All-Time ROI
            </div>
            <div
              className={`font-display font-bold text-xl flex items-center gap-1 ${
                investment.returnPercent >= 0 ? "text-mint-400" : "text-red-400"
              }`}
            >
              {investment.returnPercent >= 0 ? (
                <ArrowUpRight className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span>{investment.returnPercent >= 0 ? "+" : ""}{investment.returnPercent.toFixed(2)}%</span>
            </div>
          </div>
        </div>
      </Card>

      {/* 4. Category Breakdown & Monthly Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Share List */}
        <Card className="p-0 overflow-hidden">
          <div className="p-5 border-b border-border-subtle flex items-center justify-between">
            <h4 className="font-display font-bold text-sm text-white">
              Expenditure by Category ({categories.length})
            </h4>
            <span className="text-xs text-slate-400">Share of Total</span>
          </div>

          {categories.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No categorized expenses recorded yet.
            </div>
          ) : (
            <div className="p-5 space-y-4">
              {categories.map((cat, idx) => (
                <div key={cat.category} className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{
                          backgroundColor:
                            CATEGORY_COLORS[idx % CATEGORY_COLORS.length],
                        }}
                      />
                      <span className="font-semibold text-white">
                        {cat.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-300 font-mono">
                        {formatINR(cat.amount)}
                      </span>
                      <span className="text-slate-400 font-bold min-w-12 text-right">
                        {cat.percentage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-background-elevated h-1.5 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(cat.percentage, 100)}%`,
                        backgroundColor:
                          CATEGORY_COLORS[idx % CATEGORY_COLORS.length],
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Monthly Ledger Table */}
        <Card className="p-0 overflow-hidden">
          <div className="p-5 border-b border-border-subtle flex items-center justify-between">
            <h4 className="font-display font-bold text-sm text-white">
              Chronological Monthly Cashflow
            </h4>
            <span className="text-xs text-slate-400">Net Retained</span>
          </div>

          {monthlyData.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No monthly activity logged yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-background-elevated/60 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-border-subtle">
                  <tr>
                    <th className="py-2.5 px-4">Month</th>
                    <th className="py-2.5 px-4 text-right">Inflows</th>
                    <th className="py-2.5 px-4 text-right">Outflows</th>
                    <th className="py-2.5 px-4 text-right">Net Savings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle/50 text-slate-300">
                  {monthlyData.map((m) => {
                    const isPositive = m.savings >= 0;
                    return (
                      <tr key={m.month} className="hover:bg-background-elevated/40">
                        <td className="py-3 px-4 font-mono font-bold text-white">
                          {m.month}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-cyan-300">
                          {formatINR(m.income)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-slate-300">
                          {formatINR(m.expenses)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-bold">
                          <span className={isPositive ? "text-mint-400" : "text-red-400"}>
                            {isPositive ? "+" : ""}
                            {formatINR(m.savings)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </AppShell>
  );
}
