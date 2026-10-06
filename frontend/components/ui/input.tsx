import React from "react";
import { cn } from "@/lib/utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  prefixSymbol?: string;
}

export const Input: React.FC<InputProps> = ({ className, prefixSymbol, ...props }) => {
  return (
    <div className="relative flex items-center w-full">
      {prefixSymbol && (
        <span className="absolute left-3.5 text-cyan-400 font-bold pointer-events-none select-none">
          {prefixSymbol}
        </span>
      )}
      <input
        className={cn(
          "w-full bg-background-elevated border border-border-light rounded-sm text-sm text-white placeholder-slate-500 py-2.5 px-3.5 outline-none transition-all duration-150 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-subtle",
          prefixSymbol && "pl-8",
          className
        )}
        {...props}
      />
    </div>
  );
};
