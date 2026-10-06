import React from "react";
import { cn } from "@/lib/utils/cn";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "mint" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = "primary",
  size = "md",
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-semibold rounded-sm transition-all duration-200 outline-none active:scale-95 disabled:opacity-50 disabled:pointer-events-none";

  const variants = {
    primary:
      "bg-cyan-500 text-[#04121a] hover:bg-[#38f4ff] shadow-[0_2px_12px_rgba(0,242,254,0.25)] hover:shadow-[0_4px_20px_rgba(0,242,254,0.4)] hover:-translate-y-0.5",
    mint:
      "bg-mint-500 text-[#04140e] hover:bg-[#26f6ab] shadow-[0_2px_12px_rgba(0,245,160,0.25)] hover:shadow-[0_4px_20px_rgba(0,245,160,0.4)] hover:-translate-y-0.5",
    outline:
      "bg-transparent text-cyan-400 border border-border-accent hover:bg-cyan-subtle hover:text-white hover:-translate-y-0.5",
    ghost:
      "bg-background-elevated text-slate-300 border border-border-subtle hover:bg-card-hover hover:text-white",
    danger:
      "bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500 hover:text-white",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2.5 text-sm",
    lg: "px-6 py-3.5 text-base",
  };

  return (
    <button className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {children}
    </button>
  );
};
