"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { calculateGoalProgress } from "@/lib/calculations/financial";
import { Goal } from "@/types/contract";
import { GoalCreateInput, GoalUpdateInput } from "@/types/goal";
import {
  getGoals,
  createGoal,
  updateGoal,
  addFundsToGoal,
  deleteGoal,
} from "@/lib/api/goal";
import {
  Plus,
  Pencil,
  Trash2,
  X,
  AlertCircle,
  RefreshCw,
  Target,
  TrendingUp,
  CheckCircle2,
  Calendar,
  DollarSign,
  Coins,
} from "lucide-react";

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form / Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [formData, setFormData] = useState<{
    name: string;
    targetAmount: string;
    currentAmount: string;
    targetDate: string;
    monthlyContribution: string;
  }>({
    name: "",
    targetAmount: "",
    currentAmount: "0",
    targetDate: "",
    monthlyContribution: "0",
  });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Add Funds Modal State
  const [fundingGoal, setFundingGoal] = useState<Goal | null>(null);
  const [fundAmount, setFundAmount] = useState<string>("");
  const [fundError, setFundError] = useState<string | null>(null);
  const [isFunding, setIsFunding] = useState<boolean>(false);

  // Delete State
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Success Notification State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchGoalList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getGoals();
      setGoals(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load savings goals";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGoalList();
  }, [fetchGoalList]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setEditingGoal(null);
    setFormData({
      name: "",
      targetAmount: "",
      currentAmount: "0",
      targetDate: "",
      monthlyContribution: "0",
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEditModal = (goal: Goal) => {
    setEditingGoal(goal);
    setFormData({
      name: goal.name,
      targetAmount: goal.targetAmount.toString(),
      currentAmount: goal.currentAmount.toString(),
      targetDate: goal.targetDate,
      monthlyContribution: goal.monthlyContribution.toString(),
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Close Modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingGoal(null);
    setFormErrors({});
  };

  // Validate Form
  const validateForm = () => {
    const errors: { [key: string]: string } = {};

    if (!formData.name.trim()) {
      errors.name = "Goal name is required.";
    }

    const target = parseFloat(formData.targetAmount);
    if (!formData.targetAmount || isNaN(target) || target <= 0) {
      errors.targetAmount = "Target amount must be greater than 0.";
    }

    const current = parseFloat(formData.currentAmount);
    if (formData.currentAmount !== "" && (isNaN(current) || current < 0)) {
      errors.currentAmount = "Current amount cannot be negative.";
    }

    if (!formData.targetDate) {
      errors.targetDate = "Target completion date is required.";
    }

    const monthly = parseFloat(formData.monthlyContribution);
    if (formData.monthlyContribution !== "" && (isNaN(monthly) || monthly < 0)) {
      errors.monthlyContribution = "Monthly contribution cannot be negative.";
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

    const payload: GoalCreateInput = {
      name: formData.name.trim(),
      targetAmount: parseFloat(formData.targetAmount),
      currentAmount: parseFloat(formData.currentAmount || "0"),
      targetDate: formData.targetDate,
      monthlyContribution: parseFloat(formData.monthlyContribution || "0"),
    };

    try {
      if (editingGoal) {
        await updateGoal(editingGoal.id, payload as GoalUpdateInput);
        setSuccessMessage("Savings goal updated successfully.");
      } else {
        await createGoal(payload);
        setSuccessMessage("Savings goal created successfully.");
      }
      handleCloseModal();
      await fetchGoalList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "An error occurred while saving the goal.";
      setFormErrors({ submit: msg });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Open Add Funds Modal
  const handleOpenAddFunds = (goal: Goal) => {
    setFundingGoal(goal);
    setFundAmount("");
    setFundError(null);
  };

  // Handle Add Funds Submit
  const handleAddFundsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fundingGoal) return;

    const amount = parseFloat(fundAmount);
    if (!fundAmount || isNaN(amount) || amount <= 0) {
      setFundError("Please enter a valid deposit amount greater than 0.");
      return;
    }

    setIsFunding(true);
    setFundError(null);
    try {
      await addFundsToGoal(fundingGoal.id, { amount });
      setSuccessMessage(`Successfully added ${formatINR(amount)} to "${fundingGoal.name}".`);
      setFundingGoal(null);
      await fetchGoalList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to add funds to goal.";
      setFundError(msg);
    } finally {
      setIsFunding(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    setIsDeleting(true);
    try {
      await deleteGoal(id);
      setDeletingId(null);
      setSuccessMessage("Goal deleted successfully.");
      await fetchGoalList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete goal.";
      setError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Goal Aggregate Metrics
  const metrics = useMemo(() => {
    const totalTarget = goals.reduce((sum, g) => sum + (Number(g.targetAmount) || 0), 0);
    const totalCurrent = goals.reduce((sum, g) => sum + (Number(g.currentAmount) || 0), 0);
    const totalMonthly = goals.reduce(
      (sum, g) => sum + (Number(g.monthlyContribution) || 0),
      0
    );
    const overallProgress =
      totalTarget > 0 ? Math.min((totalCurrent / totalTarget) * 100, 100) : 0;

    return {
      totalTarget,
      totalCurrent,
      totalMonthly,
      overallProgress,
    };
  }, [goals]);

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
            onClick={fetchGoalList}
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
            <h2 className="font-display font-bold text-2xl text-white">Target Savings Goals</h2>
            <Badge variant="cyan">Person 2 Domain</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Set, track, and deposit toward your strategic financial milestones in INR (₹).
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={fetchGoalList}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Goals"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
          <Button variant="mint" onClick={handleOpenAddModal}>
            <Plus className="w-4 h-4 mr-2" />
            Create Goal
          </Button>
        </div>
      </div>

      {/* Aggregate KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Target */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Target
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <Target className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-white">
            {formatINR(metrics.totalTarget)}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">Combined targeted savings</div>
        </Card>

        {/* Total Accumulated */}
        <Card highlight className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              Accumulated Capital
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <Coins className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-cyan-400">
            {formatINR(metrics.totalCurrent)}
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Saved across all active goals</div>
        </Card>

        {/* Overall Completion Rate */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Overall Progress
            </span>
            <div className="w-8 h-8 rounded-sm bg-mint-500/10 border border-border-mint flex items-center justify-center text-mint-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-mint-400">
            {metrics.overallProgress.toFixed(1)}%
          </div>
          <div className="w-full bg-background-elevated h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className="bg-mint-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${metrics.overallProgress}%` }}
            />
          </div>
        </Card>

        {/* Monthly Planned Savings */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Monthly Inflow
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-white">
            {formatINR(metrics.totalMonthly)}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">Planned monthly contributions</div>
        </Card>
      </div>

      {/* Goals Grid */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
          <span className="text-sm">Loading savings goals...</span>
        </div>
      ) : goals.length === 0 ? (
        <Card className="p-12 text-center flex flex-col items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
            <Target className="w-6 h-6" />
          </div>
          <div className="text-sm font-semibold text-white">No savings goals created yet</div>
          <p className="text-xs text-slate-400 max-w-sm">
            Set up targeted funds for emergency reserves, luxury purchases, vehicle funds, or home acquisitions.
          </p>
          <Button variant="mint" onClick={handleOpenAddModal} className="mt-2">
            <Plus className="w-4 h-4 mr-2" />
            Create Your First Goal
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {goals.map((goal) => {
            const progress = calculateGoalProgress(goal);
            const remaining = Math.max(goal.targetAmount - goal.currentAmount, 0);

            return (
              <Card
                key={goal.id}
                className="flex flex-col justify-between hover:border-border-accent transition-all relative group"
              >
                <div>
                  {/* Goal Header & Badge */}
                  <div className="flex justify-between items-start mb-3">
                    <div className="min-w-0 pr-2">
                      <h3 className="font-display font-bold text-base text-white truncate" title={goal.name}>
                        {goal.name}
                      </h3>
                      <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        <span>Target: {formatDate(goal.targetDate)}</span>
                      </div>
                    </div>
                    <Badge variant={progress >= 100 ? "mint" : "cyan"}>
                      {progress.toFixed(1)}%
                    </Badge>
                  </div>

                  {/* Amounts Display */}
                  <div className="flex justify-between items-baseline mb-2 mt-4">
                    <span className="font-display font-black text-xl text-cyan-300">
                      {formatINR(goal.currentAmount)}
                    </span>
                    <span className="text-xs text-slate-400">
                      of <strong className="text-white">{formatINR(goal.targetAmount)}</strong>
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-background-elevated h-2 rounded-full overflow-hidden mb-2">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        progress >= 100
                          ? "bg-mint-400 shadow-[0_0_10px_rgba(38,208,124,0.5)]"
                          : "bg-cyan-400 shadow-cyan-glow"
                      }`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>

                  <div className="flex justify-between text-[11px] text-slate-400 mb-4">
                    <span>{progress >= 100 ? "Goal Completed!" : `Remaining: ${formatINR(remaining)}`}</span>
                    <span>Monthly: {formatINR(goal.monthlyContribution)}</span>
                  </div>
                </div>

                {/* Actions Footer */}
                <div className="pt-4 border-t border-border-subtle flex justify-between items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleOpenAddFunds(goal)}
                    className="text-xs hover:border-mint-400 hover:text-mint-400"
                  >
                    + Add Funds
                  </Button>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleOpenEditModal(goal)}
                      className="p-1.5 rounded-sm hover:bg-background-elevated text-slate-400 hover:text-cyan-400 transition-colors"
                      title="Edit Goal"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeletingId(goal.id)}
                      className="p-1.5 rounded-sm hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors"
                      title="Delete Goal"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Add / Edit Goal Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-lg bg-background-surface border-border-accent shadow-2xl relative p-6">
            <div className="flex items-center justify-between pb-4 border-b border-border-subtle mb-6">
              <h3 className="font-display font-bold text-lg text-white">
                {editingGoal ? "Edit Savings Goal" : "Create New Savings Goal"}
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

              {/* Goal Name */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Goal Name / Objective *
                </label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Emergency Liquidity Reserve, Tesla Fund, Home Downpayment"
                />
                {formErrors.name && (
                  <div className="text-xs text-red-400 mt-1">{formErrors.name}</div>
                )}
              </div>

              {/* Target & Current Amounts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Target Amount (₹) *
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={formData.targetAmount}
                    onChange={(e) =>
                      setFormData({ ...formData, targetAmount: e.target.value })
                    }
                    placeholder="e.g., 500000"
                  />
                  {formErrors.targetAmount && (
                    <div className="text-xs text-red-400 mt-1">
                      {formErrors.targetAmount}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Current Saved (₹)
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.currentAmount}
                    onChange={(e) =>
                      setFormData({ ...formData, currentAmount: e.target.value })
                    }
                    placeholder="e.g., 50000"
                  />
                  {formErrors.currentAmount && (
                    <div className="text-xs text-red-400 mt-1">
                      {formErrors.currentAmount}
                    </div>
                  )}
                </div>
              </div>

              {/* Target Date & Monthly Contribution */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Target Completion Date *
                  </label>
                  <Input
                    type="date"
                    value={formData.targetDate}
                    onChange={(e) =>
                      setFormData({ ...formData, targetDate: e.target.value })
                    }
                  />
                  {formErrors.targetDate && (
                    <div className="text-xs text-red-400 mt-1">{formErrors.targetDate}</div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Monthly Contribution (₹)
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.monthlyContribution}
                    onChange={(e) =>
                      setFormData({ ...formData, monthlyContribution: e.target.value })
                    }
                    placeholder="e.g., 25000"
                  />
                  {formErrors.monthlyContribution && (
                    <div className="text-xs text-red-400 mt-1">
                      {formErrors.monthlyContribution}
                    </div>
                  )}
                </div>
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
                <Button type="submit" variant="mint" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  ) : null}
                  {editingGoal ? "Save Changes" : "Create Goal"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Add Funds Modal */}
      {fundingGoal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-md bg-background-surface border-border-mint shadow-2xl p-6">
            <div className="flex items-center justify-between pb-4 border-b border-border-subtle mb-4">
              <div className="flex items-center gap-2 text-mint-400">
                <Coins className="w-5 h-5" />
                <h3 className="font-display font-bold text-lg text-white">
                  Add Funds to Goal
                </h3>
              </div>
              <button
                onClick={() => setFundingGoal(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-300 mb-4">
              Deposit funds directly to <strong className="text-white">&quot;{fundingGoal.name}&quot;</strong>. Current balance: <span className="text-cyan-300 font-bold">{formatINR(fundingGoal.currentAmount)}</span>.
            </p>

            <form onSubmit={handleAddFundsSubmit} className="space-y-4">
              {fundError && (
                <div className="p-3 rounded-sm bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{fundError}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Deposit Amount (₹) *
                </label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={fundAmount}
                  onChange={(e) => setFundAmount(e.target.value)}
                  placeholder="e.g., 10000"
                  autoFocus
                />
              </div>

              <div className="pt-4 border-t border-border-subtle flex justify-end gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setFundingGoal(null)}
                  disabled={isFunding}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="mint" disabled={isFunding}>
                  {isFunding ? (
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Coins className="w-4 h-4 mr-2" />
                  )}
                  Deposit Funds
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
              Are you sure you want to delete this savings goal? This action is permanent and will remove the goal from your progress metrics.
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
                Delete Goal
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
