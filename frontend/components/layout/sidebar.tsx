"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  ArrowLeftRight,
  LineChart,
  Target,
  FileSpreadsheet,
  FolderLock,
  Bot,
  PieChart,
  Bell,
  User,
  ShieldCheck,
  Layers,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { AuthUtils } from "@/lib/auth/jwt";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    AuthUtils.removeToken();
    router.replace("/login");
  };

  const navSections = [
    {
      title: "Core Banking",
      items: [
        { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        { label: "Income", href: "/income", icon: TrendingUp },
        { label: "Expenses", href: "/expenses", icon: TrendingDown },
        { label: "Transactions", href: "/transactions", icon: ArrowLeftRight },
      ],
    },
    {
      title: "Wealth & Vault",
      items: [
        { label: "Investments", href: "/investments", icon: LineChart },
        { label: "Goals", href: "/goals", icon: Target },
        { label: "Bank Statement", href: "/bank-statement", icon: FileSpreadsheet },
        { label: "Documents", href: "/documents", icon: FolderLock },
        { label: "AI Advisor", href: "/ai-advisor", icon: Bot, badge: "Neural" },
        { label: "Analytics", href: "/analytics", icon: PieChart },
      ],
    },
    {
      title: "System & Controls",
      items: [
        { label: "Notifications", href: "/notifications", icon: Bell },
        { label: "Profile", href: "/profile", icon: User },
        { label: "Admin & Contract", href: "/admin", icon: ShieldCheck },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-background-surface border-r border-border-subtle flex flex-col fixed inset-y-0 left-0 z-40">
      {/* Brand Header */}
      <div className="p-5 border-b border-border-subtle flex items-center gap-3">
        <div className="w-9 h-9 rounded-sm bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-cyan-glow text-background font-black">
          <Layers className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <span className="font-display font-extrabold text-lg tracking-tight text-white leading-tight">
            Nex<span className="text-cyan-400">Wealth</span>
          </span>
          <span className="text-[10px] font-bold tracking-wider text-mint-400 uppercase">
            Fintech • INR (₹)
          </span>
        </div>
      </div>

      {/* Nav Menu */}
      <div className="flex-1 overflow-y-auto p-3 space-y-6">
        {navSections.map((section, idx) => (
          <div key={idx}>
            <div className="px-3 mb-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              {section.title}
            </div>
            <ul className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3.5 py-2.5 rounded-sm text-sm font-semibold transition-all duration-150 text-slate-400 hover:text-white hover:bg-white/[0.03]",
                        isActive &&
                          "bg-background-elevated text-cyan-400 border border-border-accent shadow-[0_0_15px_rgba(0,242,254,0.12)]"
                      )}
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      <span>{item.label}</span>
                      {item.badge && (
                        <span className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-cyan-glow text-cyan-300 border border-border-accent">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>

      {/* User Footer & Logout */}
      <div className="p-4 border-t border-border-subtle bg-card-subtle space-y-2">
        <Link
          href="/profile"
          className="flex items-center gap-3 p-2 rounded-sm bg-background-elevated border border-border-subtle hover:border-border-accent transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-800 to-cyan-500 flex items-center justify-center font-bold text-xs text-white border border-border-accent">
            ND
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-bold text-white truncate">NexWealth Demo</div>
            <div className="text-[10px] text-mint-400 flex items-center gap-1">
              <span>● Verified (INR)</span>
            </div>
          </div>
        </Link>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 rounded-sm text-xs font-semibold text-slate-400 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/25 transition-all"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
