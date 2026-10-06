"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { Transaction, TransactionType } from "@/types/contract";
import { TRANSACTION_CATEGORIES } from "@/types/transaction";
import { getTransactions } from "@/lib/api/transaction";
import {
  RefreshCw,
  AlertCircle,
  RotateCcw,
  ArrowDownLeft,
  ArrowUpRight,
  SlidersHorizontal,
} from "lucide-react";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [typeFilter, setTypeFilter] = useState<"all" | TransactionType>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [dateValidationError, setDateValidationError] = useState<string | null>(null);

  const isFiltered = useMemo(() => {
    return (
      typeFilter !== "all" ||
      categoryFilter !== "all" ||
      dateFrom !== "" ||
      dateTo !== ""
    );
  }, [typeFilter, categoryFilter, dateFrom, dateTo]);

  const fetchTransactionList = useCallback(async () => {
    // Validate date range
    if (dateFrom && dateTo && dateFrom > dateTo) {
      setDateValidationError("Date From cannot be after Date To.");
      return;
    }
    setDateValidationError(null);

    setIsLoading(true);
    setError(null);

    try {
      const params = {
        type: typeFilter !== "all" ? typeFilter : undefined,
        category: categoryFilter !== "all" ? categoryFilter : undefined,
        date_from: dateFrom ? dateFrom : undefined,
        date_to: dateTo ? dateTo : undefined,
      };

      const data = await getTransactions(params);
      setTransactions(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load transactions";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [typeFilter, categoryFilter, dateFrom, dateTo]);

  useEffect(() => {
    fetchTransactionList();
  }, [fetchTransactionList]);

  const handleResetFilters = () => {
    setTypeFilter("all");
    setCategoryFilter("all");
    setDateFrom("");
    setDateTo("");
    setDateValidationError(null);
  };

  const getCategoryBadgeVariant = (category: string) => {
    switch (category) {
      case "Food":
        return "mint";
      case "Shopping":
      case "Transport":
      case "Travel":
        return "cyan";
      case "Bills":
      case "Medical":
        return "warning";
      case "Entertainment":
      case "Education":
      default:
        return "neutral";
    }
  };

  return (
    <AppShell>
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl text-white">Unified Ledger</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Read-only synchronized financial ledger automatically updated via Income &amp; Expense APIs
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => fetchTransactionList()}
            disabled={isLoading}
            className="gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Badge variant="cyan">Currency: INR (₹)</Badge>
        </div>
      </div>

      {/* Date Validation Error Banner */}
      {dateValidationError && (
        <div className="mb-6 rounded-lg p-3.5 bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{dateValidationError}</span>
        </div>
      )}

      {/* API Error Banner */}
      {error && (
        <div className="mb-6 rounded-lg p-4 bg-amber-500/10 border border-amber-500/25 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-amber-300 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 text-amber-400" />
            <span>
              {error.toLowerCase().includes("token") || error.includes("401")
                ? "Please sign in to view your transaction ledger."
                : error}
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => fetchTransactionList()} className="gap-2">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </Button>
        </div>
      )}

      {/* Filters Card */}
      <Card className="mb-6 p-4">
        <div className="flex items-center gap-2 mb-3 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          <SlidersHorizontal className="w-3.5 h-3.5 text-cyan-400" />
          Filter Transactions
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 items-end">
          {/* Type Filter */}
          <div>
            <label className="block text-xs text-slate-400 mb-1 font-medium">
              Transaction Type
            </label>
            <div className="flex rounded-sm bg-background-elevated p-0.5 border border-border-light">
              <button
                type="button"
                onClick={() => setTypeFilter("all")}
                className={`flex-1 py-1.5 text-xs font-semibold rounded-sm transition-all ${
                  typeFilter === "all"
                    ? "bg-cyan-500 text-background shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => setTypeFilter("income")}
                className={`flex-1 py-1.5 text-xs font-semibold rounded-sm transition-all ${
                  typeFilter === "income"
                    ? "bg-mint-500 text-background shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Income
              </button>
              <button
                type="button"
                onClick={() => setTypeFilter("expense")}
                className={`flex-1 py-1.5 text-xs font-semibold rounded-sm transition-all ${
                  typeFilter === "expense"
                    ? "bg-amber-500 text-background shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Expense
              </button>
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-xs text-slate-400 mb-1 font-medium">
              Category
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full bg-background-elevated border border-border-light rounded-sm text-xs text-white py-2 px-3 outline-none transition-all duration-150 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-subtle"
            >
              <option value="all" className="bg-card text-white">
                All Categories
              </option>
              {TRANSACTION_CATEGORIES.map((cat) => (
                <option key={cat} value={cat} className="bg-card text-white">
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Date From */}
          <div>
            <label className="block text-xs text-slate-400 mb-1 font-medium">
              Date From
            </label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="py-1.5 text-xs"
            />
          </div>

          {/* Date To + Reset */}
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1 font-medium">
                Date To
              </label>
              <Input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="py-1.5 text-xs"
              />
            </div>
            {isFiltered && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleResetFilters}
                title="Reset all filters"
                className="h-[34px] px-2.5 text-slate-400 hover:text-white"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Transactions Table Card */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-display font-bold text-base text-white">Ledger Records</h3>
            <p className="text-xs text-slate-400">Chronological transaction journal (Date DESC)</p>
          </div>
          <Badge variant="neutral">
            {transactions.length} {transactions.length === 1 ? "Record" : "Records"}
          </Badge>
        </div>

        {/* Loading Skeleton */}
        {isLoading ? (
          <div className="space-y-3 py-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-12 w-full bg-background-elevated/60 rounded animate-pulse"
              />
            ))}
          </div>
        ) : transactions.length === 0 ? (
          /* Empty State */
          <div className="text-center py-12 px-4 border border-dashed border-border-subtle rounded-lg my-4">
            <div className="w-12 h-12 rounded-full bg-cyan-subtle border border-border-accent text-cyan-400 flex items-center justify-center mx-auto mb-3">
              <SlidersHorizontal className="w-6 h-6" />
            </div>
            <h4 className="font-display font-bold text-base text-white">No Transactions Found</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
              {isFiltered
                ? "No ledger entries match your filter criteria. Try clearing or adjusting the filters."
                : "Your transaction ledger is currently empty. Transactions will appear here automatically when you record income or expenses."}
            </p>
            {isFiltered && (
              <Button variant="ghost" size="sm" onClick={handleResetFilters} className="gap-2">
                <RotateCcw className="w-3.5 h-3.5" />
                Clear Filters
              </Button>
            )}
          </div>
        ) : (
          /* Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-background-elevated text-slate-400 uppercase text-[11px] tracking-wider border-b border-border-subtle">
                <tr>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Description / Source</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4 text-right">Amount (INR)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle text-slate-200">
                {transactions.map((tx) => {
                  const isIncome = tx.type === "income";
                  return (
                    <tr key={tx.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3.5 px-4">
                        <Badge variant={isIncome ? "mint" : "warning"}>
                          <span className="flex items-center gap-1">
                            {isIncome ? (
                              <ArrowUpRight className="w-3 h-3" />
                            ) : (
                              <ArrowDownLeft className="w-3 h-3" />
                            )}
                            {tx.type.toUpperCase()}
                          </span>
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-white">{tx.description}</div>
                        {tx.source && (
                          <div className="text-xs text-slate-400 mt-0.5">{tx.source}</div>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge variant={getCategoryBadgeVariant(tx.category)}>
                          {tx.category || (isIncome ? "Income" : "Expense")}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 text-xs">{formatDate(tx.date)}</td>
                      <td
                        className={`py-3.5 px-4 text-right font-bold ${
                          isIncome ? "text-mint-400" : "text-amber-400"
                        }`}
                      >
                        {isIncome ? "+ " : "- "}
                        {formatINR(tx.amount)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
