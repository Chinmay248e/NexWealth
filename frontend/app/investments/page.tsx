"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { Investment } from "@/types/contract";
import { INVESTMENT_TYPES, InvestmentCreateInput, InvestmentUpdateInput } from "@/types/investment";
import {
  getInvestments,
  createInvestment,
  updateInvestment,
  deleteInvestment,
} from "@/lib/api/investment";
import {
  Plus,
  Pencil,
  Trash2,
  X,
  AlertCircle,
  RefreshCw,
  LineChart,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  Clock,
  Layers,
} from "lucide-react";

export default function InvestmentsPage() {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form / Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingInvestment, setEditingInvestment] = useState<Investment | null>(null);
  const [formData, setFormData] = useState<{
    name: string;
    type: string;
    investedAmount: string;
    currentValue: string;
    date: string;
  }>({
    name: "",
    type: "Mutual Fund",
    investedAmount: "",
    currentValue: "",
    date: new Date().toISOString().split("T")[0],
  });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Delete State
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Success Notification State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchInvestmentList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getInvestments();
      setInvestments(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load investment records";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInvestmentList();
  }, [fetchInvestmentList]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setEditingInvestment(null);
    setFormData({
      name: "",
      type: "Mutual Fund",
      investedAmount: "",
      currentValue: "",
      date: new Date().toISOString().split("T")[0],
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEditModal = (inv: Investment) => {
    setEditingInvestment(inv);
    setFormData({
      name: inv.name,
      type: inv.type,
      investedAmount: inv.investedAmount.toString(),
      currentValue: inv.currentValue.toString(),
      date: inv.date,
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Close Modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingInvestment(null);
    setFormErrors({});
  };

  // Validate Form
  const validateForm = () => {
    const errors: { [key: string]: string } = {};

    if (!formData.name.trim()) {
      errors.name = "Investment asset name is required.";
    }

    if (!formData.type.trim()) {
      errors.type = "Investment type is required.";
    }

    const invested = parseFloat(formData.investedAmount);
    if (!formData.investedAmount || isNaN(invested) || invested <= 0) {
      errors.investedAmount = "Invested amount must be greater than 0.";
    }

    const current = parseFloat(formData.currentValue);
    if (formData.currentValue === "" || isNaN(current) || current < 0) {
      errors.currentValue = "Current value must be 0 or greater.";
    }

    if (!formData.date) {
      errors.date = "Investment date is required.";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle Submit (Create or Update)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    setError(null);

    const payload: InvestmentCreateInput = {
      name: formData.name.trim(),
      type: formData.type.trim(),
      investedAmount: parseFloat(formData.investedAmount),
      currentValue: parseFloat(formData.currentValue),
      date: formData.date,
    };

    try {
      if (editingInvestment) {
        await updateInvestment(editingInvestment.id, payload as InvestmentUpdateInput);
        setSuccessMessage("Investment record updated successfully.");
      } else {
        await createInvestment(payload);
        setSuccessMessage("Investment record added successfully.");
      }
      handleCloseModal();
      await fetchInvestmentList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "An error occurred while saving the investment.";
      setFormErrors({ submit: msg });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    setIsDeleting(true);
    try {
      await deleteInvestment(id);
      setDeletingId(null);
      setSuccessMessage("Investment record deleted successfully.");
      await fetchInvestmentList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to delete investment.";
      setError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Portfolio Summary Calculations
  const summary = useMemo(() => {
    const totalInvested = investments.reduce(
      (sum, item) => sum + (Number(item.investedAmount) || 0),
      0
    );
    const totalCurrentValue = investments.reduce(
      (sum, item) => sum + (Number(item.currentValue) || 0),
      0
    );
    const gainLoss = totalCurrentValue - totalInvested;
    const returnPercent = totalInvested > 0 ? (gainLoss / totalInvested) * 100 : 0;

    return {
      totalInvested,
      totalCurrentValue,
      gainLoss,
      returnPercent,
    };
  }, [investments]);

  return (
    <AppShell>
      {/* Notifications / Alerts */}
      {successMessage && (
        <div className="mb-6 p-4 rounded-md bg-mint-500/10 border border-border-mint flex items-center gap-3 text-mint-300 text-sm animate-fade-in shadow-sm">
          <CheckCircle2 className="w-5 h-5 shrink-0 text-mint-400" />
          <span>{successMessage}</span>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-md bg-red-500/10 border border-red-500/25 flex items-center justify-between text-red-300 text-sm shadow-sm">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
          <Button
            variant="ghost"
            onClick={fetchInvestmentList}
            className="text-xs text-red-400 hover:text-white"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">Investments</h2>
            <Badge variant="cyan">Person 3 Portfolio</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Real-time portfolio management, asset valuation, and growth performance in INR (₹).
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={fetchInvestmentList}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
          <Button variant="primary" onClick={handleOpenAddModal}>
            <Plus className="w-4 h-4 mr-2" />
            Add Investment
          </Button>
        </div>
      </div>

      {/* Portfolio Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Invested */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Invested
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-white">
            {formatINR(summary.totalInvested)}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">Principal capital deployed</div>
        </Card>

        {/* Current Value */}
        <Card highlight className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              Current Valuation
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <LineChart className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-cyan-400">
            {formatINR(summary.totalCurrentValue)}
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Live market portfolio value</div>
        </Card>

        {/* Overall Gain / Loss */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Net Gain / Loss
            </span>
            <div
              className={`w-8 h-8 rounded-sm flex items-center justify-center border ${
                summary.gainLoss >= 0
                  ? "bg-mint-500/10 border-border-mint text-mint-400"
                  : "bg-red-500/10 border-red-500/30 text-red-400"
              }`}
            >
              {summary.gainLoss >= 0 ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
            </div>
          </div>
          <div
            className={`font-display font-black text-2xl ${
              summary.gainLoss >= 0 ? "text-mint-400" : "text-red-400"
            }`}
          >
            {summary.gainLoss >= 0 ? "+" : ""}
            {formatINR(summary.gainLoss)}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">
            Absolute portfolio profit/loss
          </div>
        </Card>

        {/* Return % */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Overall Return %
            </span>
            <div
              className={`w-8 h-8 rounded-sm flex items-center justify-center border ${
                summary.returnPercent >= 0
                  ? "bg-mint-500/10 border-border-mint text-mint-400"
                  : "bg-red-500/10 border-red-500/30 text-red-400"
              }`}
            >
              <span className="text-xs font-bold">%</span>
            </div>
          </div>
          <div
            className={`font-display font-black text-2xl ${
              summary.returnPercent >= 0 ? "text-mint-400" : "text-red-400"
            }`}
          >
            {summary.returnPercent >= 0 ? "+" : ""}
            {summary.returnPercent.toFixed(2)}%
          </div>
          <div className="text-[11px] text-slate-500 mt-2">Total ROI on deployed capital</div>
        </Card>
      </div>

      {/* Investment Listings */}
      <Card className="p-0 overflow-hidden">
        <div className="p-5 border-b border-border-subtle flex items-center justify-between">
          <h3 className="font-display font-bold text-base text-white">
            Holdings & Asset Ledger ({investments.length})
          </h3>
          <div className="text-xs text-slate-400">
            Sorted by Date (Desc)
          </div>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
            <span className="text-sm">Loading portfolio holdings...</span>
          </div>
        ) : investments.length === 0 ? (
          <div className="p-12 text-center flex flex-col items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <LineChart className="w-6 h-6" />
            </div>
            <div className="text-sm font-semibold text-white">No investments found</div>
            <p className="text-xs text-slate-400 max-w-sm">
              You haven&apos;t added any investment assets yet. Click below to start building your portfolio.
            </p>
            <Button variant="primary" onClick={handleOpenAddModal} className="mt-2">
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Investment
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-background-elevated/60 text-slate-400 uppercase text-[11px] font-bold tracking-wider border-b border-border-subtle">
                <tr>
                  <th className="py-3 px-5">Asset Name & Class</th>
                  <th className="py-3 px-5">Invested Amount</th>
                  <th className="py-3 px-5">Current Value</th>
                  <th className="py-3 px-5">Gain / Loss</th>
                  <th className="py-3 px-5">Purchase Date</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle/50">
                {investments.map((inv) => {
                  const gain = inv.currentValue - inv.investedAmount;
                  const ret = inv.investedAmount > 0 ? (gain / inv.investedAmount) * 100 : 0;
                  const isPositive = gain >= 0;

                  return (
                    <tr
                      key={inv.id}
                      className="hover:bg-background-elevated/40 transition-colors"
                    >
                      <td className="py-4 px-5">
                        <div className="font-bold text-white mb-0.5">{inv.name}</div>
                        <Badge variant="cyan">{inv.type}</Badge>
                      </td>
                      <td className="py-4 px-5 font-mono font-medium text-slate-300">
                        {formatINR(inv.investedAmount)}
                      </td>
                      <td className="py-4 px-5 font-mono font-bold text-cyan-300">
                        {formatINR(inv.currentValue)}
                      </td>
                      <td className="py-4 px-5 font-mono text-xs">
                        <div
                          className={`font-bold flex items-center gap-1 ${
                            isPositive ? "text-mint-400" : "text-red-400"
                          }`}
                        >
                          {isPositive ? "+" : ""}
                          {formatINR(gain)}
                          <span className="text-[10px] font-normal">
                            ({isPositive ? "+" : ""}
                            {ret.toFixed(1)}%)
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-5 text-xs text-slate-400">
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-500" />
                          <span>{formatDate(inv.date)}</span>
                        </div>
                      </td>
                      <td className="py-4 px-5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenEditModal(inv)}
                            className="p-1.5 rounded-sm hover:bg-background-elevated text-slate-400 hover:text-cyan-400 transition-colors"
                            title="Edit Investment"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeletingId(inv.id)}
                            className="p-1.5 rounded-sm hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors"
                            title="Delete Investment"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Add / Edit Investment Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-lg bg-background-surface border-border-accent shadow-2xl relative p-6">
            <div className="flex items-center justify-between pb-4 border-b border-border-subtle mb-6">
              <h3 className="font-display font-bold text-lg text-white">
                {editingInvestment ? "Edit Investment" : "Add New Investment"}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {formErrors.submit && (
                <div className="p-3 rounded-sm bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{formErrors.submit}</span>
                </div>
              )}

              {/* Asset Name */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Asset / Holding Name *
                </label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="e.g., Nifty 50 Index Fund, HDFC Bank, Sovereign Gold"
                />
                {formErrors.name && (
                  <div className="text-xs text-red-400 mt-1">{formErrors.name}</div>
                )}
              </div>

              {/* Asset Class / Type */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Asset Class / Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) =>
                    setFormData({ ...formData, type: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-background border border-border-subtle rounded-md text-sm text-white focus:outline-none focus:border-border-accent"
                >
                  {INVESTMENT_TYPES.map((type) => (
                    <option key={type} value={type} className="bg-background-surface text-white">
                      {type}
                    </option>
                  ))}
                </select>
                {formErrors.type && (
                  <div className="text-xs text-red-400 mt-1">{formErrors.type}</div>
                )}
              </div>

              {/* Amounts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Invested Principal */}
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Invested Principal (₹) *
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={formData.investedAmount}
                    onChange={(e) =>
                      setFormData({ ...formData, investedAmount: e.target.value })
                    }
                    placeholder="e.g., 50000"
                  />
                  {formErrors.investedAmount && (
                    <div className="text-xs text-red-400 mt-1">
                      {formErrors.investedAmount}
                    </div>
                  )}
                </div>

                {/* Current Valuation */}
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Current Valuation (₹) *
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.currentValue}
                    onChange={(e) =>
                      setFormData({ ...formData, currentValue: e.target.value })
                    }
                    placeholder="e.g., 62500"
                  />
                  {formErrors.currentValue && (
                    <div className="text-xs text-red-400 mt-1">
                      {formErrors.currentValue}
                    </div>
                  )}
                </div>
              </div>

              {/* Investment Date */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Investment Date *
                </label>
                <Input
                  type="date"
                  value={formData.date}
                  onChange={(e) =>
                    setFormData({ ...formData, date: e.target.value })
                  }
                />
                {formErrors.date && (
                  <div className="text-xs text-red-400 mt-1">{formErrors.date}</div>
                )}
              </div>

              {/* Form Buttons */}
              <div className="pt-4 border-t border-border-subtle flex justify-end gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleCloseModal}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  ) : null}
                  {editingInvestment ? "Save Changes" : "Create Investment"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-md bg-background-surface border-red-500/30 shadow-2xl p-6">
            <div className="flex items-center gap-3 text-red-400 mb-4">
              <AlertCircle className="w-6 h-6 shrink-0" />
              <h3 className="font-display font-bold text-lg text-white">
                Confirm Deletion
              </h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-6">
              Are you sure you want to delete this investment record? This action is permanent and will remove the holding from your portfolio metrics.
            </p>
            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                onClick={() => setDeletingId(null)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => handleDelete(deletingId)}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Trash2 className="w-4 h-4 mr-2" />
                )}
                Delete Investment
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
