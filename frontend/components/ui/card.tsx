import React from "react";
import { cn } from "@/lib/utils/cn";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  highlight?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className, highlight = false, ...props }) => {
  return (
    <div
      className={cn(
        "bg-card rounded-lg p-6 border border-border-subtle shadow-card-subtle transition-all duration-200 hover:border-border-light",
        highlight && "border-border-accent shadow-[0_4px_24px_rgba(0,0,0,0.6),0_0_15px_rgba(0,242,254,0.12)]",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
