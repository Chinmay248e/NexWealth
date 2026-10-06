"use client";

import React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText } from "lucide-react";
import { formatDate } from "@/lib/utils/currency";
import { Document } from "@/types/contract";

const sampleDocs: Document[] = [
  { id: "doc_001", userId: "usr_9f8b2c1a", fileName: "ITR-V_AY2026_27_Acknowledged.pdf", documentType: "Income Tax", status: "verified", uploadedAt: "2026-07-28T14:20:00.000Z", createdAt: "2026-07-28T14:20:00.000Z" },
  { id: "doc_002", userId: "usr_9f8b2c1a", fileName: "Health_Insurance_Policy_2026.pdf", documentType: "Insurance", status: "verified", uploadedAt: "2026-08-10T11:00:00.000Z", createdAt: "2026-08-10T11:00:00.000Z" },
  { id: "doc_003", userId: "usr_9f8b2c1a", fileName: "Demat_Holding_Statement_Q2.pdf", documentType: "Investment", status: "uploaded", uploadedAt: "2026-09-30T16:45:00.000Z", createdAt: "2026-09-30T16:45:00.000Z" },
];

export default function DocumentsPage() {
  return (
    <AppShell>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl text-white">Document Vault</h2>
          <p className="text-xs text-slate-400 mt-0.5">Person 2 Domain: Document Model & Encryption</p>
        </div>
        <Button variant="primary">+ Upload Document</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sampleDocs.map((doc) => (
          <Card key={doc.id} className="flex items-center gap-4 hover:border-border-accent">
            <div className="w-12 h-12 rounded-sm bg-background-elevated border border-border-subtle flex items-center justify-center text-cyan-400 shrink-0">
              <FileText className="w-6 h-6" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-bold text-white truncate" title={doc.fileName}>
                {doc.fileName}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                {doc.documentType} • {formatDate(doc.uploadedAt)}
              </div>
            </div>
            <Badge variant={doc.status === "verified" ? "mint" : "cyan"}>{doc.status}</Badge>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
