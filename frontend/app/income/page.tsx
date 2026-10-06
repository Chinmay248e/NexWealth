"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { Income } from "@/types/contract";
import {
  getIncomes,
  createIncome,
  updateIncome,
  deleteIncome,
} from "@/lib/api/income";
import {
  Plus,
  Pencil,
  Trash2,
  X,
  AlertCircle,
  RefreshCw,
  TrendingUp,
  CheckCircle2,
} from "lucide-react";

export default function IncomePage() {
  const [incomes, setIncomes] = useState<Income[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form / Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingIncome, setEditingIncome] = useState<Income | null>(null);
  const [formData, setFormData] = useState({
    source: "",
    amount: "",
    date: new Date().toISOString().split("T")[0],
  });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Delete State
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Success Notification State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchIncomeList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getIncomes();
      setIncomes(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load income records";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncomeList();
  }, [fetchIncomeList]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setEditingIncome(null);
    setFormData({
      source: "",
      amount: "",
      date: new Date().toISOString().split("T")[0],
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEditModal = (income: Income) => {
    setEditingIncome(income);
    setFormData({
      source: income.source,
      amount: income.amount.toString(),
      date: income.date,
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Close Modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingIncome(null);
    setFormErrors({});
  };

  // Validation
  const validateForm = () => {
    const errors: { [key: string]: string } = {};
    if (!formData.source.trim()) {
      errors.source = "Source is required.";
    }

    const numAmount = parseFloat(formData.amount);
    if (!formData.amount || isNaN(numAmount) || numAmount <= 0) {
      errors.amount = "Amount must be a positive number greater than 0.";
    }

    if (!formData.date) {
      errors.date = "Date is required.";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle Form Submit (Add or Edit)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    setError(null);

    const payload = {
      source: formData.source.trim(),
      amount: parseFloat(formData.amount),
      date: formData.date,
    };

    try {
      if (editingIncome) {
        await updateIncome(editingIncome.id, payload);
        showSuccess("Income record updated successfully.");
      } else {
        await createIncome(payload);
        showSuccess("New income record recorded successfully.");
      }
      handleCloseModal();
      await fetchIncomeList();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Operation failed. Please try again.";
      setFormErrors({ submit: msg });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    setIsDeleting(true);
    setError(null);
    try {
      await deleteIncome(id);
      showSuccess("Income record deleted successfully.");
      setDeletingId(null);
      await fetchIncomeList();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to delete income record.";
      setError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  const showSuccess = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => {
      setSuccessMessage(null);
    }, 4000);
  };

  const totalIncomeAmount = incomes.reduce((acc, curr) => acc + curr.amount, 0);

  return (
    <AppShell>
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl text-white">Income Streams</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time income tracking with synchronized transaction ledger
          </p>
        </div>
        <Button variant="primary" onClick={handleOpenAddModal} className="gap-2">
          <Plus className="w-4 h-4" />
          Add New Income
        </Button>
      </div>

      {/* Success Banner */}
      {successMessage && (
        <div className="mb-6 rounded-lg p-3.5 bg-mint-500/10 border border-mint-500/30 flex items-center gap-3 text-mint-400 text-sm">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="mb-6 rounded-lg p-4 bg-amber-500/10 border border-amber-500/25 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-amber-300 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 text-amber-400" />
            <span>
              {error.toLowerCase().includes("token") || error.includes("401")
                ? "Please sign in to view and manage your income streams."
                : error}
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => fetchIncomeList()} className="gap-2">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </Button>
        </div>
      )}

      {/* Income Table Card */}
      <Card className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-display font-bold text-base text-white">Income Registry (INR)</h3>
            <p className="text-xs text-slate-400">All registered inflows for your account</p>
          </div>
          <Badge variant="cyan">
            Total: {formatINR(totalIncomeAmount)}
          </Badge>
        </div>

        {/* Loading Skeleton */}
        {isLoading ? (
          <div className="space-y-3 py-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-12 w-full bg-background-elevated/60 rounded animate-pulse"
              />
            ))}
          </div>
        ) : incomes.length === 0 ? (
          /* Empty State */
          <div className="text-center py-12 px-4 border border-dashed border-border-subtle rounded-lg my-4">
            <div className="w-12 h-12 rounded-full bg-cyan-subtle border border-border-accent text-cyan-400 flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h4 className="font-display font-bold text-base text-white">No Income Records Found</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
              Start building your financial overview by logging your first income stream.
            </p>
            <Button variant="primary" size="sm" onClick={handleOpenAddModal} className="gap-2">
              <Plus className="w-4 h-4" />
              Add Your First Income
            </Button>
          </div>
        ) : (
          /* Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-background-elevated text-slate-400 uppercase text-[11px] tracking-wider border-b border-border-subtle">
                <tr>
                  <th className="py-3 px-4">Income ID</th>
                  <th className="py-3 px-4">Source</th>
                  <th className="py-3 px-4">Date Received</th>
                  <th className="py-3 px-4 text-right">Amount (INR)</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle text-slate-200">
                {incomes.map((inc) => (
                  <tr key={inc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-mono text-cyan-400 text-xs">{inc.id}</td>
                    <td className="py-3.5 px-4 font-semibold text-white">{inc.source}</td>
                    <td className="py-3.5 px-4 text-slate-400 text-xs">{formatDate(inc.date)}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-mint-400">
                      + {formatINR(inc.amount)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => handleOpenEditModal(inc)}
                          title="Edit Income"
                          className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10 rounded transition-colors"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeletingId(inc.id)}
                          title="Delete Income"
                          className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Add / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-card border border-border-accent rounded-lg shadow-2xl p-6 relative">
            <div className="flex items-center justify-between mb-5 border-b border-border-subtle pb-3">
              <h3 className="font-display font-bold text-lg text-white">
                {editingIncome ? "Edit Income Record" : "Record New Income"}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-slate-400 hover:text-white p-1 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {formErrors.submit && (
              <div className="mb-4 p-3 rounded bg-red-500/10 border border-red-500/25 text-red-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formErrors.submit}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Income Source <span className="text-cyan-400">*</span>
                </label>
                <Input
                  type="text"
                  placeholder="e.g. Monthly Salary, Freelance, Dividend"
                  value={formData.source}
                  onChange={(e) =>
                    setFormData({ ...formData, source: e.target.value })
                  }
                  required
                />
                {formErrors.source && (
                  <p className="text-xs text-red-400 mt-1">{formErrors.source}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Amount in INR (₹) <span className="text-cyan-400">*</span>
                </label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  prefixSymbol="₹"
                  placeholder="75000"
                  value={formData.amount}
                  onChange={(e) =>
                    setFormData({ ...formData, amount: e.target.value })
                  }
                  required
                />
                {formErrors.amount && (
                  <p className="text-xs text-red-400 mt-1">{formErrors.amount}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Date Received <span className="text-cyan-400">*</span>
                </label>
                <Input
                  type="date"
                  value={formData.date}
                  onChange={(e) =>
                    setFormData({ ...formData, date: e.target.value })
                  }
                  required
                />
                {formErrors.date && (
                  <p className="text-xs text-red-400 mt-1">{formErrors.date}</p>
                )}
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleCloseModal}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting
                    ? "Saving..."
                    : editingIncome
                    ? "Update Income"
                    : "Save Income"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <div className="w-full max-w-sm bg-card border border-red-500/30 rounded-lg shadow-2xl p-6">
            <h4 className="font-display font-bold text-base text-white mb-2">
              Delete Income Record?
            </h4>
            <p className="text-xs text-slate-400 mb-5">
              Are you sure you want to delete this income entry? Its synchronized transaction ledger record will also be removed.
            </p>
            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDeletingId(null)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDelete(deletingId)}
                disabled={isDeleting}
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
