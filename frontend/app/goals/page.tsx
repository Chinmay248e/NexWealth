"use client";

import React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { calculateGoalProgress } from "@/lib/calculations/financial";
import { Goal } from "@/types/contract";

const sampleGoals: Goal[] = [
  { id: "gol_001", userId: "usr_9f8b2c1a", name: "Emergency Liquidity Reserve", targetAmount: 1200000, currentAmount: 940000, targetDate: "2027-03-31", monthlyContribution: 50000, createdAt: "2026-01-20T10:00:00.000Z" },
  { id: "gol_002", userId: "usr_9f8b2c1a", name: "Next-Gen Electric Vehicle Fund", targetAmount: 2400000, currentAmount: 1480000, targetDate: "2027-12-31", monthlyContribution: 65000, createdAt: "2026-02-10T12:00:00.000Z" },
  { id: "gol_003", userId: "usr_9f8b2c1a", name: "Global Wealth Diversification", targetAmount: 3500000, currentAmount: 1120000, targetDate: "2028-06-30", monthlyContribution: 75000, createdAt: "2026-03-01T15:00:00.000Z" },
];

export default function GoalsPage() {
  return (
    <AppShell>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl text-white">Target Savings Goals</h2>
          <p className="text-xs text-slate-400 mt-0.5">Person 2 Domain: Goal Progress Calculation</p>
        </div>
        <Button variant="mint">+ Create Goal</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sampleGoals.map((goal) => {
          const progress = calculateGoalProgress(goal);
          return (
            <Card key={goal.id} className="flex flex-col justify-between hover:border-border-accent">
              <div>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-display font-bold text-base text-white">{goal.name}</h3>
                  <Badge variant="mint">{progress}%</Badge>
                </div>
                <div className="text-xs text-slate-400 mb-4">
                  Target Date: {formatDate(goal.targetDate)}
                </div>

                <div className="flex justify-between items-baseline mb-2">
                  <span className="font-display font-bold text-xl text-cyan-400">
                    {formatINR(goal.currentAmount)}
                  </span>
                  <span className="text-xs text-slate-400">of {formatINR(goal.targetAmount)}</span>
                </div>

                <div className="w-full bg-background-elevated h-2 rounded-full overflow-hidden mb-4">
                  <div
                    className="bg-cyan-400 h-full rounded-full transition-all duration-500 shadow-cyan-glow"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-border-subtle flex justify-between items-center text-xs">
                <span className="text-slate-400">
                  Monthly: <strong className="text-white">{formatINR(goal.monthlyContribution)}</strong>
                </span>
                <Button variant="outline" size="sm">
                  + Add Funds
                </Button>
              </div>
            </Card>
          );
        })}
      </div>
    </AppShell>
  );
}
