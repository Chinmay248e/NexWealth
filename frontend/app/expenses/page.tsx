"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { Expense, ExpenseCategory } from "@/types/contract";
import { EXPENSE_CATEGORIES } from "@/types/expense";
import {
  getExpenses,
  createExpense,
  updateExpense,
  deleteExpense,
} from "@/lib/api/expense";
import {
  Plus,
  Pencil,
  Trash2,
  X,
  AlertCircle,
  RefreshCw,
  TrendingDown,
  CheckCircle2,
} from "lucide-react";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form / Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [formData, setFormData] = useState<{
    description: string;
    amount: string;
    category: ExpenseCategory;
    date: string;
  }>({
    description: "",
    amount: "",
    category: "Food",
    date: new Date().toISOString().split("T")[0],
  });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Delete State
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Success Notification State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchExpenseList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getExpenses();
      setExpenses(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load expense records";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExpenseList();
  }, [fetchExpenseList]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setEditingExpense(null);
    setFormData({
      description: "",
      amount: "",
      category: "Food",
      date: new Date().toISOString().split("T")[0],
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEditModal = (expense: Expense) => {
    setEditingExpense(expense);
    setFormData({
      description: expense.description,
      amount: expense.amount.toString(),
      category: expense.category,
      date: expense.date,
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Close Modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingExpense(null);
    setFormErrors({});
  };

  // Validation
  const validateForm = () => {
    const errors: { [key: string]: string } = {};
    if (!formData.description.trim()) {
      errors.description = "Description is required.";
    }

    const numAmount = parseFloat(formData.amount);
    if (!formData.amount || isNaN(numAmount) || numAmount <= 0) {
      errors.amount = "Amount must be a positive number greater than 0.";
    }

    if (!formData.category || !EXPENSE_CATEGORIES.includes(formData.category)) {
      errors.category = "Please select a valid expense category.";
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
      description: formData.description.trim(),
      amount: parseFloat(formData.amount),
      category: formData.category,
      date: formData.date,
    };

    try {
      if (editingExpense) {
        await updateExpense(editingExpense.id, payload);
        showSuccess("Expense record updated successfully.");
      } else {
        await createExpense(payload);
        showSuccess("New expense recorded successfully.");
      }
      handleCloseModal();
      await fetchExpenseList();
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
      await deleteExpense(id);
      showSuccess("Expense record deleted successfully.");
      setDeletingId(null);
      await fetchExpenseList();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to delete expense record.";
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

  const totalExpenseAmount = expenses.reduce((acc, curr) => acc + curr.amount, 0);

  const getCategoryBadgeVariant = (category: ExpenseCategory) => {
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
          <h2 className="font-display font-bold text-2xl text-white">Expense Outflows</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time expense categorization with synchronized transaction ledger
          </p>
        </div>
        <Button variant="mint" onClick={handleOpenAddModal} className="gap-2">
          <Plus className="w-4 h-4" />
          Record Expense
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
                ? "Please sign in to view and manage your expense outflows."
                : error}
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => fetchExpenseList()} className="gap-2">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </Button>
        </div>
      )}

      {/* Expense Table Card */}
      <Card className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-display font-bold text-base text-white">Expense Register</h3>
            <p className="text-xs text-slate-400">All registered outflows across 9 categories</p>
          </div>
          <Badge variant="warning">
            Total: {formatINR(totalExpenseAmount)}
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
        ) : expenses.length === 0 ? (
          /* Empty State */
          <div className="text-center py-12 px-4 border border-dashed border-border-subtle rounded-lg my-4">
            <div className="w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/25 text-amber-400 flex items-center justify-center mx-auto mb-3">
              <TrendingDown className="w-6 h-6" />
            </div>
            <h4 className="font-display font-bold text-base text-white">No Expense Records Found</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
              Track your financial outflow and optimize savings by logging expenses.
            </p>
            <Button variant="mint" size="sm" onClick={handleOpenAddModal} className="gap-2">
              <Plus className="w-4 h-4" />
              Record Your First Expense
            </Button>
          </div>
        ) : (
          /* Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-background-elevated text-slate-400 uppercase text-[11px] tracking-wider border-b border-border-subtle">
                <tr>
                  <th className="py-3 px-4">Expense ID</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4 text-right">Amount (INR)</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle text-slate-200">
                {expenses.map((exp) => (
                  <tr key={exp.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-mono text-cyan-400 text-xs">{exp.id}</td>
                    <td className="py-3.5 px-4 font-semibold text-white">{exp.description}</td>
                    <td className="py-3.5 px-4">
                      <Badge variant={getCategoryBadgeVariant(exp.category)}>
                        {exp.category}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-xs">{formatDate(exp.date)}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-amber-400">
                      - {formatINR(exp.amount)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => handleOpenEditModal(exp)}
                          title="Edit Expense"
                          className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10 rounded transition-colors"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeletingId(exp.id)}
                          title="Delete Expense"
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
                {editingExpense ? "Edit Expense Record" : "Record New Expense"}
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
                  Description <span className="text-cyan-400">*</span>
                </label>
                <Input
                  type="text"
                  placeholder="e.g. Grocery shopping, Electricity bill"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  required
                />
                {formErrors.description && (
                  <p className="text-xs text-red-400 mt-1">{formErrors.description}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Category <span className="text-cyan-400">*</span>
                </label>
                <select
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      category: e.target.value as ExpenseCategory,
                    })
                  }
                  className="w-full bg-background-elevated border border-border-light rounded-sm text-sm text-white py-2.5 px-3.5 outline-none transition-all duration-150 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-subtle"
                >
                  {EXPENSE_CATEGORIES.map((cat) => (
                    <option key={cat} value={cat} className="bg-card text-white">
                      {cat}
                    </option>
                  ))}
                </select>
                {formErrors.category && (
                  <p className="text-xs text-red-400 mt-1">{formErrors.category}</p>
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
                  placeholder="2500"
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
                  Date <span className="text-cyan-400">*</span>
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
                  variant="mint"
                  disabled={isSubmitting}
                >
                  {isSubmitting
                    ? "Saving..."
                    : editingExpense
                    ? "Update Expense"
                    : "Record Expense"}
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
              Delete Expense Record?
            </h4>
            <p className="text-xs text-slate-400 mb-5">
              Are you sure you want to delete this expense entry? Its synchronized transaction ledger record will also be removed.
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
