"use client";

import React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UploadCloud } from "lucide-react";
import { formatDate } from "@/lib/utils/currency";
import { BankStatement } from "@/types/contract";

const sampleStatements: BankStatement[] = [
  { id: "bst_001", userId: "usr_9f8b2c1a", fileName: "HDFC_Salary_Statement_Sep2026.pdf", accountName: "HDFC Salary Account (..4081)", status: "parsed", uploadedAt: "2026-10-01T10:00:00.000Z", createdAt: "2026-10-01T10:00:00.000Z" },
  { id: "bst_002", userId: "usr_9f8b2c1a", fileName: "ICICI_Direct_Savings_Aug2026.pdf", accountName: "ICICI Wealth Account (..8821)", status: "parsed", uploadedAt: "2026-09-02T12:30:00.000Z", createdAt: "2026-09-02T12:30:00.000Z" },
];

export default function BankStatementPage() {
  return (
    <AppShell>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl text-white">Bank Statement Ingestion</h2>
          <p className="text-xs text-slate-400 mt-0.5">Person 2 Domain: BankStatement Model & Parser</p>
        </div>
      </div>

      <Card className="border-dashed border-2 border-border-accent bg-cyan-subtle/20 p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-cyan-subtle/40 transition-colors mb-6">
        <div className="w-14 h-14 rounded-full bg-cyan-subtle border border-border-accent flex items-center justify-center text-cyan-400 mb-3 shadow-cyan-glow">
          <UploadCloud className="w-7 h-7" />
        </div>
        <h3 className="font-display font-bold text-lg text-white mb-1">Upload Bank Statement</h3>
        <p className="text-xs text-slate-400 max-w-sm mb-4">
          Upload PDF or CSV statements from HDFC, ICICI, SBI, or Axis for automated extraction.
        </p>
        <Button variant="primary" size="sm">
          Browse File
        </Button>
      </Card>

      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-display font-bold text-base text-white">Statement Archives</h3>
          <Badge variant="mint">OCR Pipeline Active</Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-background-elevated text-slate-400 uppercase text-[11px] tracking-wider border-b border-border-subtle">
              <tr>
                <th className="py-3 px-4">Statement ID</th>
                <th className="py-3 px-4">File Name</th>
                <th className="py-3 px-4">Account</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Uploaded At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle text-slate-200">
              {sampleStatements.map((s) => (
                <tr key={s.id} className="hover:bg-white/[0.02]">
                  <td className="py-3.5 px-4 font-mono text-cyan-400 text-xs">{s.id}</td>
                  <td className="py-3.5 px-4 font-semibold text-white">{s.fileName}</td>
                  <td className="py-3.5 px-4 text-xs text-slate-300">{s.accountName}</td>
                  <td className="py-3.5 px-4">
                    <Badge variant={s.status === "parsed" ? "mint" : "warning"}>
                      {s.status.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4 text-xs text-slate-400">{formatDate(s.uploadedAt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </AppShell>
  );
}
