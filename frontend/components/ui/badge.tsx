import React from "react";
import { cn } from "@/lib/utils/cn";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "cyan" | "mint" | "warning" | "danger" | "neutral";
}

export const Badge: React.FC<BadgeProps> = ({ children, className, variant = "cyan", ...props }) => {
  const variants = {
    cyan: "bg-cyan-subtle text-cyan-300 border-border-accent",
    mint: "bg-mint-subtle text-mint-400 border-border-mint",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/25",
    danger: "bg-red-500/10 text-red-400 border-red-500/30",
    neutral: "bg-white/5 text-slate-400 border-border-subtle",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded-full border leading-none",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
