"use client";

import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

interface DonutChartProps {
  data?: Array<{ name: string; value: number }>;
}

const defaultData = [
  { name: "Food", value: 13000 },
  { name: "Bills", value: 14500 },
  { name: "Shopping", value: 18900 },
  { name: "Transport", value: 3400 },
  { name: "Travel", value: 15400 },
  { name: "Education", value: 6500 },
];

const COLORS = ["#00f2fe", "#00f5a0", "#38bdf8", "#fbbf24", "#a855f7", "#f87171"];

export const DonutChart: React.FC<DonutChartProps> = ({ data = defaultData }) => {
  return (
    <div className="w-full h-56">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
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
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
