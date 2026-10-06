"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Bell, IndianRupee, LogOut } from "lucide-react";
import { AuthUtils } from "@/lib/auth/jwt";

export const Header: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    AuthUtils.removeToken();
    router.replace("/login");
  };

  const getPageTitle = () => {
    switch (pathname) {
      case "/dashboard":
        return "Executive Financial Dashboard";
      case "/income":
        return "Income Streams & Inflows";
      case "/expenses":
        return "Categorized Expenses";
      case "/transactions":
        return "Unified Financial Ledger";
      case "/investments":
        return "Investment Portfolio & Assets";
      case "/goals":
        return "Target Savings Goals";
      case "/bank-statement":
        return "Bank Statement Ingestion";
      case "/documents":
        return "Encrypted Document Vault";
      case "/ai-advisor":
        return "NexAdvisor AI Copilot";
      case "/analytics":
        return "Portfolio Analytics";
      case "/notifications":
        return "Alerts & Notifications";
      case "/profile":
        return "User Profile & Security";
      case "/admin":
        return "System Architecture & Contract";
      default:
        return "NexWealth";
    }
  };

  return (
    <header className="h-18 px-8 bg-background/85 backdrop-blur-md border-b border-border-subtle flex items-center justify-between sticky top-0 z-30">
      <div className="flex flex-col">
        <h1 className="font-display font-extrabold text-xl text-white tracking-tight">
          {getPageTitle()}
        </h1>
        <div className="text-xs text-slate-500">
          NexWealth / {pathname.replace("/", "").replace("-", " ") || "Dashboard"}
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Currency Badge */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-subtle border border-border-accent text-xs font-bold text-cyan-300">
          <IndianRupee className="w-3.5 h-3.5" />
          <span>Locked: INR (₹)</span>
        </div>

        {/* Notifications Icon */}
        <Link
          href="/notifications"
          className="w-9 h-9 rounded-sm bg-background-elevated border border-border-subtle flex items-center justify-center text-slate-400 hover:text-cyan-400 hover:border-border-accent transition-colors"
        >
          <Bell className="w-4 h-4" />
        </Link>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          title="Sign Out of NexWealth"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-sm bg-red-500/10 border border-red-500/25 text-xs font-semibold text-red-400 hover:bg-red-500 hover:text-white transition-all shadow-sm"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
};
