"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CashflowChart } from "@/components/charts/cashflow-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  PieChart as PieIcon,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { formatINR } from "@/lib/utils/currency";
import { getDashboardSummary } from "@/lib/api/dashboard";
import { DashboardSummary } from "@/types/dashboard";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load dashboard summary";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  return (
    <AppShell>
      {/* Financial Welcome Banner */}
      <div className="relative overflow-hidden rounded-xl p-8 bg-gradient-to-r from-card to-background-elevated border border-border-accent shadow-cyan-glow mb-8">
        <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-display font-extrabold text-2xl text-white">
              Welcome to NexWealth 👋
            </h2>
            <p className="text-sm text-slate-300 mt-1">
              Real-time portfolio metrics operating at optimal efficiency. Single Source of Truth:{" "}
              <code className="text-cyan-400 font-mono">NEXWEALTH_DATA_CONTRACT.md</code>
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="primary">+ Record Income</Button>
            <Button variant="mint">+ Record Expense</Button>
          </div>
        </div>
      </div>

      {/* User-friendly Error Alert (Non-blocking) */}
      {error && (
        <div className="mb-6 rounded-lg p-4 bg-amber-500/10 border border-amber-500/25 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-amber-300 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 text-amber-400" />
            <span>
              {error.toLowerCase().includes("token") || error.includes("401")
                ? "Please sign in to view your real-time financial metrics."
                : "Unable to load real-time financial metrics."}
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => loadSummary()} className="gap-2">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </Button>
        </div>
      )}

      {/* Core Financial Stat Cards (Section 6 Calculation Engine) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Total Income
            </span>
            <div className="w-10 h-10 rounded-md bg-cyan-subtle text-cyan-400 border border-border-accent flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-32 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div className="font-display font-bold text-2xl text-white">
                {formatINR(summary?.totalIncome ?? 0)}
              </div>
            )}
            <div className="text-xs text-mint-400 font-semibold mt-1">SUM(Income.amount)</div>
          </div>
        </Card>

        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Total Expenses
            </span>
            <div className="w-10 h-10 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/25 flex items-center justify-center">
              <TrendingDown className="w-5 h-5" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-32 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div className="font-display font-bold text-2xl text-white">
                {formatINR(summary?.totalExpenses ?? 0)}
              </div>
            )}
            <div className="text-xs text-amber-400 font-semibold mt-1">SUM(Expense.amount)</div>
          </div>
        </Card>

        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Available Savings
            </span>
            <div className="w-10 h-10 rounded-md bg-mint-subtle text-mint-400 border border-border-mint flex items-center justify-center">
              <Wallet className="w-5 h-5" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-32 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div
                className={`font-display font-bold text-2xl ${
                  (summary?.availableSavings ?? 0) < 0 ? "text-amber-400" : "text-mint-400"
                }`}
              >
                {formatINR(summary?.availableSavings ?? 0)}
              </div>
            )}
            <div className="text-xs text-slate-400 font-semibold mt-1">Income - Expenses</div>
          </div>
        </Card>

        <Card className="flex flex-col justify-between hover:border-border-accent transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Savings Rate
            </span>
            <div className="w-10 h-10 rounded-md bg-cyan-subtle text-cyan-400 border border-border-accent flex items-center justify-center">
              <PieIcon className="w-5 h-5" />
            </div>
          </div>
          <div>
            {isLoading ? (
              <div className="h-8 w-24 bg-white/10 rounded animate-pulse my-0.5" />
            ) : (
              <div className="font-display font-bold text-2xl text-cyan-400">
                {`${(summary?.savingsRate ?? 0).toFixed(1)}%`}
              </div>
            )}
            <div className="text-xs text-cyan-300 font-semibold mt-1">
              (Available / Total) × 100
            </div>
          </div>
        </Card>
      </div>

      {/* Visual Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-display font-bold text-base text-white">Cashflow Dynamics</h3>
              <p className="text-xs text-slate-400">Income vs categorized outflow trends (INR)</p>
            </div>
            <Badge variant="cyan">Realtime</Badge>
          </div>
          <CashflowChart />
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-display font-bold text-base text-white">Category Allocation</h3>
              <p className="text-xs text-slate-400">Spending across 9 contract categories</p>
            </div>
          </div>
          <DonutChart />
        </Card>
      </div>
    </AppShell>
  );
}
