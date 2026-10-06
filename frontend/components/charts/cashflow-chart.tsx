"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface CashflowChartProps {
  data?: Array<{ month: string; income: number; expense: number }>;
}

const defaultData = [
  { month: "May", income: 210000, expense: 78000 },
  { month: "Jun", income: 225000, expense: 84000 },
  { month: "Jul", income: 215000, expense: 91000 },
  { month: "Aug", income: 240000, expense: 88000 },
  { month: "Sep", income: 260000, expense: 95000 },
  { month: "Oct", income: 280500, expense: 72800 },
];

export const CashflowChart: React.FC<CashflowChartProps> = ({ data = defaultData }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="incomeGlow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00f2fe" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00f2fe" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="expenseGlow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00f5a0" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#00f5a0" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            tickFormatter={(val) => `₹${val / 1000}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0c1824",
              borderColor: "rgba(0,242,254,0.3)",
              borderRadius: "8px",
              color: "#fff",
              fontSize: "12px",
            }}
            formatter={(value: any) => [`₹${Number(value).toLocaleString("en-IN")}`, ""]}
          />
          <Area
            type="monotone"
            dataKey="income"
            name="Income"
            stroke="#00f2fe"
            strokeWidth={2.5}
            fillOpacity={1}
            fill="url(#incomeGlow)"
          />
          <Area
            type="monotone"
            dataKey="expense"
            name="Expense"
            stroke="#00f5a0"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#expenseGlow)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
