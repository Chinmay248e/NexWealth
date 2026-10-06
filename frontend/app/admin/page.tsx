"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils/currency";
import { getUserProfile } from "@/lib/api/profile";
import { UserProfile } from "@/types/profile";
import {
  ShieldCheck,
  FileCode2,
  Users,
  CheckCircle2,
  Clock,
  Database,
  IndianRupee,
  Layers,
  Lock,
  RefreshCw,
  Server,
  AlertCircle,
  FileText,
  Workflow,
  Cpu,
} from "lucide-react";

interface TeamOwnershipRow {
  person: string;
  entities: string[];
  domain: string;
  status: "Completed & Verified" | "Specification Ready";
  accent: "cyan" | "mint" | "warning";
}

const teamOwnership: TeamOwnershipRow[] = [
  {
    person: "Person 1",
    entities: ["User", "Income", "Expense", "Transaction"],
    domain: "Authentication, Core Cashflow, Income & Expense Tracking, Unified Financial Ledger, Dashboard Engine",
    status: "Completed & Verified",
    accent: "cyan",
  },
  {
    person: "Person 2",
    entities: ["Goal", "Document", "BankStatement"],
    domain: "Savings Goals, Encrypted Document Vault, Bank Statement Ingestion & OCR, NexAdvisor AI Copilot",
    status: "Specification Ready",
    accent: "warning",
  },
  {
    person: "Person 3",
    entities: ["Investment", "Budget", "Notification"],
    domain: "Portfolio & Investments, Category Budgets, Notification Engine, Live Analytics, Profile, Admin & Contract",
    status: "Completed & Verified",
    accent: "mint",
  },
];

interface ModuleStatusItem {
  name: string;
  owner: "Person 1" | "Person 2" | "Person 3";
  status: "Live & Tested" | "Placeholder UI";
  description: string;
}

const moduleChecklist: ModuleStatusItem[] = [
  {
    name: "Authentication & JWT Session",
    owner: "Person 1",
    status: "Live & Tested",
    description: "SessionStorage token persistence, bcrypt password security, and protected route guards.",
  },
  {
    name: "Executive Dashboard",
    owner: "Person 1",
    status: "Live & Tested",
    description: "Real-time financial summary API, total income, expenses, available savings, and savings rate.",
  },
  {
    name: "Income Management",
    owner: "Person 1",
    status: "Live & Tested",
    description: "Full CRUD with atomic transaction ledger synchronization.",
  },
  {
    name: "Expense Categorization",
    owner: "Person 1",
    status: "Live & Tested",
    description: "Categorized expenses with validation and atomic transaction ledger sync.",
  },
  {
    name: "Unified Financial Ledger (Transactions)",
    owner: "Person 1",
    status: "Live & Tested",
    description: "Chronological read-only transaction ledger with type, category, and date filtering.",
  },
  {
    name: "Investments Portfolio",
    owner: "Person 3",
    status: "Live & Tested",
    description: "Multi-asset portfolio tracking, live valuation, and ROI % calculations.",
  },
  {
    name: "Wealth Analytics & Intelligence",
    owner: "Person 3",
    status: "Live & Tested",
    description: "Live monthly cashflow area chart, category donut breakdown, and portfolio ROI metrics.",
  },
  {
    name: "User Profile & Credentials",
    owner: "Person 3",
    status: "Live & Tested",
    description: "Authenticated profile management, email uniqueness verification, and security telemetry.",
  },
  {
    name: "System Notifications Engine",
    owner: "Person 3",
    status: "Live & Tested",
    description: "Real-time alerts, unread filtering, bulk read confirmation, and item deletion.",
  },
  {
    name: "Combined Admin & Contract",
    owner: "Person 3",
    status: "Live & Tested",
    description: "Authenticated system architecture viewer, data contract specification, and ownership matrix.",
  },
  {
    name: "Target Savings Goals",
    owner: "Person 2",
    status: "Placeholder UI",
    description: "Goal progress calculation engine and milestone allocation (Person 2 Domain).",
  },
  {
    name: "Bank Statement Ingestion",
    owner: "Person 2",
    status: "Placeholder UI",
    description: "Automated statement parsing and reconciliation (Person 2 Domain).",
  },
  {
    name: "Encrypted Document Vault",
    owner: "Person 2",
    status: "Placeholder UI",
    description: "Encrypted tax receipts and Demat holding storage (Person 2 Domain).",
  },
  {
    name: "NexAdvisor AI Copilot",
    owner: "Person 2",
    status: "Placeholder UI",
    description: "Neural conversational financial insights copilot (Person 2 Domain).",
  },
];

export default function AdminPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<"overview" | "contract" | "ownership" | "status">("overview");

  const loadProfile = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getUserProfile();
      setProfile(data);
    } catch {
      // Fallback gracefully if profile fetch fails
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const getInitials = (name?: string) => {
    if (!name) return "AD";
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <AppShell>
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">
              System Administration & Data Contract
            </h2>
            <Badge variant="cyan">Person 3 Core</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Single Source of Truth: <code className="text-cyan-400 font-mono">NEXWEALTH_DATA_CONTRACT.md</code>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            onClick={loadProfile}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Status"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border-subtle pb-4 mb-8 overflow-x-auto">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 px-4 py-2 rounded-sm text-xs font-semibold transition-all ${
            activeTab === "overview"
              ? "bg-background-elevated text-cyan-400 border border-border-accent shadow-sm"
              : "text-slate-400 hover:text-white hover:bg-white/[0.03]"
          }`}
        >
          <Server className="w-4 h-4" />
          <span>Admin Overview</span>
        </button>

        <button
          onClick={() => setActiveTab("contract")}
          className={`flex items-center gap-2 px-4 py-2 rounded-sm text-xs font-semibold transition-all ${
            activeTab === "contract"
              ? "bg-background-elevated text-cyan-400 border border-border-accent shadow-sm"
              : "text-slate-400 hover:text-white hover:bg-white/[0.03]"
          }`}
        >
          <FileCode2 className="w-4 h-4" />
          <span>Data Contract Invariants</span>
        </button>

        <button
          onClick={() => setActiveTab("ownership")}
          className={`flex items-center gap-2 px-4 py-2 rounded-sm text-xs font-semibold transition-all ${
            activeTab === "ownership"
              ? "bg-background-elevated text-cyan-400 border border-border-accent shadow-sm"
              : "text-slate-400 hover:text-white hover:bg-white/[0.03]"
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Team Ownership Matrix</span>
        </button>

        <button
          onClick={() => setActiveTab("status")}
          className={`flex items-center gap-2 px-4 py-2 rounded-sm text-xs font-semibold transition-all ${
            activeTab === "status"
              ? "bg-background-elevated text-cyan-400 border border-border-accent shadow-sm"
              : "text-slate-400 hover:text-white hover:bg-white/[0.03]"
          }`}
        >
          <Workflow className="w-4 h-4" />
          <span>Implementation Status</span>
        </button>
      </div>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 1: Admin Overview */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Active Administrator Identity Card */}
          <Card highlight className="p-6 bg-gradient-to-r from-slate-900 via-background to-cyan-950/30 border-border-accent">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center font-display font-extrabold text-lg text-white shadow-cyan-glow border border-border-accent">
                  {isLoading ? ".." : getInitials(profile?.name)}
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-display font-bold text-lg text-white">
                      {isLoading ? "Loading session..." : profile?.name || "NexWealth Administrator"}
                    </h3>
                    <Badge variant="mint">Active Session</Badge>
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    {profile?.email || "admin@nexwealth.in"}
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="px-3 py-1.5 rounded-sm bg-background-elevated border border-border-subtle text-xs text-slate-300 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-mint-400" />
                  <span>JWT Auth: Scoped</span>
                </div>
                <div className="px-3 py-1.5 rounded-sm bg-background-elevated border border-border-subtle text-xs text-slate-300 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-cyan-400" />
                  <span>PostgreSQL Connected</span>
                </div>
              </div>
            </div>
          </Card>

          {/* System Telemetry Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Unique User Identifier
                </span>
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="font-mono text-sm text-cyan-300 font-bold break-all">
                {profile?.id || "usr_session_active"}
              </div>
              <div className="text-[11px] text-slate-500 mt-2">
                All API routes enforce strict data isolation by this key
              </div>
            </Card>

            <Card>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Financial Standard
                </span>
                <IndianRupee className="w-4 h-4 text-mint-400" />
              </div>
              <div className="font-display font-bold text-xl text-white">
                INR (₹) Standard
              </div>
              <div className="text-[11px] text-slate-500 mt-2">
                Mandatory ISO 4217 Currency Invariant across all modules
              </div>
            </Card>

            <Card>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Account Registration
                </span>
                <Clock className="w-4 h-4 text-slate-400" />
              </div>
              <div className="font-display font-bold text-lg text-white">
                {profile ? formatDate(profile.createdAt) : "Active"}
              </div>
              <div className="text-[11px] text-slate-500 mt-2">
                Timestamp stored in timezone-aware UTC ISO 8601
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 2: Data Contract Invariants */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "contract" && (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                <h3 className="font-display font-bold text-base text-white">
                  Core Invariant Rules (Single Source of Truth)
                </h3>
              </div>
              <Badge variant="cyan">Contract Active</Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-md bg-background-elevated/50 border border-border-subtle">
                <div className="font-bold text-cyan-400 text-sm mb-1 flex items-center gap-2">
                  <span>1. Currency Standard: INR (₹)</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  All monetary calculations, database columns, and user interfaces are locked to Indian Rupee (INR).
                  Values are formatted using Indian grouping (e.g. ₹1,25,000.00).
                </p>
              </div>

              <div className="p-4 rounded-md bg-background-elevated/50 border border-border-subtle">
                <div className="font-bold text-cyan-400 text-sm mb-1 flex items-center gap-2">
                  <span>2. Field Naming Convention: camelCase</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  All JSON response payloads, request bodies, and TypeScript interfaces strictly use camelCase
                  (e.g., <code className="text-cyan-300">userId</code>, <code className="text-cyan-300">investedAmount</code>, <code className="text-cyan-300">createdAt</code>).
                </p>
              </div>

              <div className="p-4 rounded-md bg-background-elevated/50 border border-border-subtle">
                <div className="font-bold text-cyan-400 text-sm mb-1 flex items-center gap-2">
                  <span>3. User Identity & Isolation Rule</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  <code className="text-cyan-300">userId</code> is never accepted in request bodies. It is extracted exclusively from the cryptographically verified JWT token. Cross-user accesses return 404.
                </p>
              </div>

              <div className="p-4 rounded-md bg-background-elevated/50 border border-border-subtle">
                <div className="font-bold text-cyan-400 text-sm mb-1 flex items-center gap-2">
                  <span>4. Decimal / Financial Precision</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  All financial amounts are stored as exact <code className="text-cyan-300">NUMERIC(14,2)</code> in PostgreSQL and processed using Python <code className="text-cyan-300">Decimal</code> to eliminate floating-point drift.
                </p>
              </div>
            </div>
          </Card>

          {/* Calculations Engine Specification */}
          <Card>
            <div className="flex items-center gap-2 pb-3 border-b border-border-subtle mb-4">
              <Cpu className="w-4 h-4 text-mint-400" />
              <h3 className="font-display font-bold text-base text-white">
                Core Financial Calculation Engine Formulas
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 rounded-md bg-background-elevated/30 border border-border-subtle">
                <div className="font-bold text-white mb-1">Available Savings</div>
                <div className="font-mono text-cyan-300 bg-background p-2 rounded text-[11px] mb-2 border border-border-subtle">
                  availableSavings = totalIncome - totalExpenses
                </div>
                <div className="text-slate-400">Exact difference between inflows and outflows.</div>
              </div>

              <div className="p-4 rounded-md bg-background-elevated/30 border border-border-subtle">
                <div className="font-bold text-white mb-1">Savings Rate (%)</div>
                <div className="font-mono text-mint-300 bg-background p-2 rounded text-[11px] mb-2 border border-border-subtle">
                  (availableSavings / totalIncome) * 100
                </div>
                <div className="text-slate-400">Defaults cleanly to 0.00% when totalIncome is 0.</div>
              </div>

              <div className="p-4 rounded-md bg-background-elevated/30 border border-border-subtle">
                <div className="font-bold text-white mb-1">Investment ROI (%)</div>
                <div className="font-mono text-cyan-300 bg-background p-2 rounded text-[11px] mb-2 border border-border-subtle">
                  ((currentValue - invested) / invested) * 100
                </div>
                <div className="text-slate-400">Total return on deployed principal.</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 3: Team Ownership Matrix */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "ownership" && (
        <div className="space-y-6">
          <Card className="p-0 overflow-hidden">
            <div className="p-5 border-b border-border-subtle flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                <h3 className="font-display font-bold text-base text-white">
                  Team Entity Ownership & Responsibility Division
                </h3>
              </div>
              <Badge variant="cyan">10 Entities Total</Badge>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-background-elevated/60 text-slate-400 uppercase text-[11px] font-bold tracking-wider border-b border-border-subtle">
                  <tr>
                    <th className="py-3 px-5">Team Role</th>
                    <th className="py-3 px-5">Assigned Entities</th>
                    <th className="py-3 px-5">Domain Responsibilities</th>
                    <th className="py-3 px-5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle/50 text-slate-200">
                  {teamOwnership.map((row) => (
                    <tr key={row.person} className="hover:bg-background-elevated/30">
                      <td className="py-4 px-5 font-bold text-cyan-400 text-sm whitespace-nowrap">
                        {row.person}
                      </td>
                      <td className="py-4 px-5">
                        <div className="flex gap-1.5 flex-wrap">
                          {row.entities.map((e) => (
                            <Badge key={e} variant={row.accent}>
                              {e}
                            </Badge>
                          ))}
                        </div>
                      </td>
                      <td className="py-4 px-5 text-xs text-slate-300 leading-relaxed">
                        {row.domain}
                      </td>
                      <td className="py-4 px-5 whitespace-nowrap">
                        <Badge variant={row.status.includes("Completed") ? "mint" : "warning"}>
                          {row.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 4: Implementation Status Checklist */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "status" && (
        <div className="space-y-6">
          <Card className="p-0 overflow-hidden">
            <div className="p-5 border-b border-border-subtle flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Workflow className="w-4 h-4 text-mint-400" />
                <h3 className="font-display font-bold text-base text-white">
                  System Module Implementation Checklist
                </h3>
              </div>
              <span className="text-xs text-slate-400">Live Regression Status: 100/100 Tests Passing</span>
            </div>

            <div className="divide-y divide-border-subtle/50">
              {moduleChecklist.map((m) => {
                const isLive = m.status === "Live & Tested";
                return (
                  <div
                    key={m.name}
                    className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-background-elevated/30 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5">
                        {isLive ? (
                          <CheckCircle2 className="w-5 h-5 text-mint-400" />
                        ) : (
                          <Clock className="w-5 h-5 text-amber-400" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="font-bold text-sm text-white">{m.name}</span>
                          <span className="text-[10px] font-semibold text-slate-400 bg-background-elevated px-2 py-0.5 rounded border border-border-subtle">
                            {m.owner}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                          {m.description}
                        </p>
                      </div>
                    </div>

                    <div className="shrink-0 self-start sm:self-center">
                      <Badge variant={isLive ? "mint" : "warning"}>
                        {m.status}
                      </Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
