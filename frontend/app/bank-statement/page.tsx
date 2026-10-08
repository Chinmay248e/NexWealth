"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR, formatDate } from "@/lib/utils/currency";
import { BankStatement } from "@/types/contract";
import { BankStatementParseResult, ParsedTransaction } from "@/types/bank_statement";
import {
  getBankStatements,
  uploadBankStatement,
  parseBankStatement,
  importStatementTransactions,
  deleteBankStatement,
} from "@/lib/api/bank_statement";
import {
  UploadCloud,
  FileSpreadsheet,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Trash2,
  Eye,
  ArrowDownLeft,
  ArrowUpRight,
  X,
  Layers,
  Database,
  Paperclip,
} from "lucide-react";

export default function BankStatementPage() {
  const [statements, setStatements] = useState<BankStatement[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Upload Form State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [accountName, setAccountName] = useState<string>("HDFC Salary Account (..4081)");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  // Parse & Preview Modal State
  const [previewResult, setPreviewResult] = useState<BankStatementParseResult | null>(null);
  const [isParsing, setIsParsing] = useState<boolean>(false);
  const [isImporting, setIsImporting] = useState<boolean>(false);
  const [importError, setImportError] = useState<string | null>(null);

  // Delete State
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Success Notification State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchStatementList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getBankStatements();
      setStatements(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load bank statements";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatementList();
  }, [fetchStatementList]);

  // Handle File Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadError(null);
    }
  };

  // Handle Upload Submit
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError("Please select a statement file (CSV, Excel, or TSV).");
      return;
    }
    if (!accountName.trim()) {
      setUploadError("Please specify the Bank Account / Identifier.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const stmt = await uploadBankStatement(selectedFile, accountName.trim());
      setSuccessMessage(`Bank statement "${stmt.fileName}" uploaded & parsed successfully.`);
      setSelectedFile(null);
      await fetchStatementList();
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to upload bank statement.";
      setUploadError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  // Inspect & Preview Statement
  const handleInspectStatement = async (statementId: string) => {
    setIsParsing(true);
    setImportError(null);
    try {
      const result = await parseBankStatement(statementId);
      setPreviewResult(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to parse statement transactions.";
      setError(msg);
    } finally {
      setIsParsing(false);
    }
  };

  // Import Parsed Transactions to Ledger
  const handleImportToLedger = async () => {
    if (!previewResult || previewResult.transactions.length === 0) return;

    setIsImporting(true);
    setImportError(null);

    try {
      const res = await importStatementTransactions(
        previewResult.statementId,
        previewResult.transactions
      );
      setSuccessMessage(res.message);
      setPreviewResult(null);
      await fetchStatementList();
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to import transactions.";
      setImportError(msg);
    } finally {
      setIsImporting(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    setIsDeleting(true);
    try {
      await deleteBankStatement(id);
      setDeletingId(null);
      setSuccessMessage("Bank statement removed successfully.");
      await fetchStatementList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete statement.";
      setError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // KPI Summary Metrics
  const summaryMetrics = useMemo(() => {
    const total = statements.length;
    const parsed = statements.filter((s) => s.status.toLowerCase() === "parsed").length;
    return { total, parsed };
  }, [statements]);

  return (
    <AppShell>
      {/* Success / Error Banners */}
      {successMessage && (
        <div className="mb-6 p-4 rounded-md bg-mint-500/10 border border-border-mint flex items-center gap-3 text-mint-300 text-sm animate-fade-in shadow-sm">
          <CheckCircle2 className="w-5 h-5 shrink-0 text-mint-400" />
          <span>{successMessage}</span>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-md bg-red-500/10 border border-red-500/25 flex items-center justify-between text-red-300 text-sm shadow-sm">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
          <Button
            variant="ghost"
            onClick={fetchStatementList}
            className="text-xs text-red-400 hover:text-white"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">Bank Statement Ingestion</h2>
            <Badge variant="cyan">Person 2 Ingestion Engine</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Automated statement parsing, categorization, and ledger synchronization in INR (₹).
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={fetchStatementList}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Statements"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Upload Zone Card */}
      <Card className="border-dashed border-2 border-border-accent bg-cyan-subtle/10 p-6 md:p-8 mb-8">
        <form onSubmit={handleUploadSubmit} className="space-y-6">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="w-14 h-14 rounded-full bg-cyan-subtle border border-border-accent flex items-center justify-center text-cyan-400 mb-3 shadow-cyan-glow">
              <UploadCloud className="w-7 h-7" />
            </div>
            <h3 className="font-display font-bold text-lg text-white mb-1">
              Upload Bank Statement
            </h3>
            <p className="text-xs text-slate-400 max-w-md mb-4">
              Upload CSV, Excel, or TSV statement files from HDFC, ICICI, SBI, Axis, or Kotak for automatic transaction parsing.
            </p>
          </div>

          {uploadError && (
            <div className="p-3 rounded-sm bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center justify-center gap-2 max-w-lg mx-auto">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
            {/* Account Name */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Bank / Account Identifier *
              </label>
              <Input
                type="text"
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
                placeholder="e.g., HDFC Salary Account (..4081)"
              />
            </div>

            {/* File Input */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Statement File (.csv, .xlsx, .tsv) *
              </label>
              <div className="border border-border-subtle hover:border-border-accent rounded-md px-3 py-2 bg-background flex items-center justify-between cursor-pointer relative">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".csv,.xlsx,.xls,.tsv,.txt"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <div className="flex items-center gap-2 text-xs truncate">
                  <Paperclip className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span className={selectedFile ? "text-cyan-300 font-semibold truncate" : "text-slate-500"}>
                    {selectedFile ? selectedFile.name : "Choose CSV or Excel file..."}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 font-bold uppercase tracking-wider ml-2 shrink-0">
                  Browse
                </span>
              </div>
            </div>
          </div>

          <div className="flex justify-center">
            <Button
              type="submit"
              variant="primary"
              disabled={isUploading || !selectedFile}
              className="px-6"
            >
              {isUploading ? (
                <RefreshCw className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <UploadCloud className="w-4 h-4 mr-2" />
              )}
              Upload & Ingest Statement
            </Button>
          </div>
        </form>
      </Card>

      {/* Statement Archive Table */}
      <Card className="p-0 overflow-hidden">
        <div className="p-5 border-b border-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="font-display font-bold text-base text-white">
              Statement Archives ({statements.length})
            </h3>
            <Badge variant="mint">Active Parser Engine</Badge>
          </div>
          <div className="text-xs text-slate-400">
            {summaryMetrics.parsed} of {summaryMetrics.total} parsed
          </div>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
            <span className="text-sm">Loading statement archives...</span>
          </div>
        ) : statements.length === 0 ? (
          <div className="p-12 text-center flex flex-col items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div className="text-sm font-semibold text-white">No statements uploaded yet</div>
            <p className="text-xs text-slate-400 max-w-sm">
              Upload your monthly bank statement above to extract transactions and sync your financial ledger.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-background-elevated/60 text-slate-400 uppercase text-[11px] font-bold tracking-wider border-b border-border-subtle">
                <tr>
                  <th className="py-3.5 px-5">Statement ID</th>
                  <th className="py-3.5 px-5">File Name</th>
                  <th className="py-3.5 px-5">Account Name</th>
                  <th className="py-3.5 px-5">Status</th>
                  <th className="py-3.5 px-5">Uploaded Date</th>
                  <th className="py-3.5 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle/50 text-slate-200">
                {statements.map((s) => (
                  <tr key={s.id} className="hover:bg-background-elevated/40 transition-colors">
                    <td className="py-4 px-5 font-mono text-cyan-400 text-xs font-semibold">
                      {s.id}
                    </td>
                    <td className="py-4 px-5 font-bold text-white">
                      {s.fileName}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {s.accountName}
                    </td>
                    <td className="py-4 px-5">
                      <Badge
                        variant={
                          s.status.toLowerCase() === "parsed"
                            ? "mint"
                            : s.status.toLowerCase() === "failed"
                            ? "warning"
                            : "cyan"
                        }
                      >
                        {s.status.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-400">
                      {formatDate(s.uploadedAt)}
                    </td>
                    <td className="py-4 px-5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleInspectStatement(s.id)}
                          disabled={isParsing}
                          className="text-xs"
                        >
                          <Eye className="w-3.5 h-3.5 mr-1.5 text-cyan-400" />
                          Inspect & Import
                        </Button>
                        <button
                          onClick={() => setDeletingId(s.id)}
                          className="p-1.5 rounded-sm hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors"
                          title="Delete Statement"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Parse & Import Preview Modal */}
      {previewResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-3xl bg-background-surface border-border-accent shadow-2xl relative p-6 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-border-subtle mb-4 shrink-0">
              <div className="flex items-center gap-2 text-cyan-400">
                <FileSpreadsheet className="w-5 h-5" />
                <h3 className="font-display font-bold text-lg text-white">
                  Parsed Statement Details: {previewResult.fileName}
                </h3>
              </div>
              <button
                onClick={() => setPreviewResult(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {importError && (
              <div className="mb-4 p-3 rounded-sm bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{importError}</span>
              </div>
            )}

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-background-elevated rounded-md border border-border-subtle shrink-0">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                  Transactions Found
                </span>
                <div className="text-base font-black text-white">
                  {previewResult.transactionCount}
                </div>
              </div>
              <div>
                <span className="text-[10px] text-mint-400 uppercase font-bold tracking-wider">
                  Total Credits (Income)
                </span>
                <div className="text-base font-black text-mint-400">
                  +{formatINR(previewResult.totalCredits)}
                </div>
              </div>
              <div>
                <span className="text-[10px] text-red-400 uppercase font-bold tracking-wider">
                  Total Debits (Expense)
                </span>
                <div className="text-base font-black text-red-400">
                  -{formatINR(previewResult.totalDebits)}
                </div>
              </div>
            </div>

            {/* Transactions List */}
            <div className="flex-1 overflow-y-auto border border-border-subtle rounded-md mb-4">
              {previewResult.transactions.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No transaction records could be extracted from this statement format.
                </div>
              ) : (
                <table className="w-full text-left text-xs">
                  <thead className="bg-background-elevated text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-border-subtle sticky top-0">
                    <tr>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">Narration</th>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3 text-right">Amount (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-subtle/50 text-slate-300">
                    {previewResult.transactions.map((t, idx) => (
                      <tr key={idx} className="hover:bg-background-elevated/40">
                        <td className="py-2.5 px-3 text-slate-400">{t.date}</td>
                        <td className="py-2.5 px-3 font-semibold text-white max-w-xs truncate" title={t.description}>
                          {t.description}
                        </td>
                        <td className="py-2.5 px-3">
                          <Badge variant="cyan">{t.category}</Badge>
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`font-bold flex items-center gap-1 ${
                              t.type === "income" ? "text-mint-400" : "text-red-400"
                            }`}
                          >
                            {t.type === "income" ? (
                              <ArrowDownLeft className="w-3.5 h-3.5" />
                            ) : (
                              <ArrowUpRight className="w-3.5 h-3.5" />
                            )}
                            {t.type.toUpperCase()}
                          </span>
                        </td>
                        <td
                          className={`py-2.5 px-3 text-right font-mono font-bold ${
                            t.type === "income" ? "text-mint-400" : "text-red-400"
                          }`}
                        >
                          {t.type === "income" ? "+" : "-"}
                          {formatINR(t.amount)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* Footer Buttons */}
            <div className="pt-3 border-t border-border-subtle flex justify-between items-center shrink-0">
              <span className="text-xs text-slate-400">
                Importing will sync these records into your unified Ledger.
              </span>
              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  onClick={() => setPreviewResult(null)}
                  disabled={isImporting}
                >
                  Close
                </Button>
                <Button
                  variant="mint"
                  onClick={handleImportToLedger}
                  disabled={isImporting || previewResult.transactions.length === 0}
                >
                  {isImporting ? (
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Database className="w-4 h-4 mr-2" />
                  )}
                  Import {previewResult.transactions.length} Transactions
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-md bg-background-surface border-red-500/30 shadow-2xl p-6">
            <div className="flex items-center gap-3 text-red-400 mb-4">
              <AlertCircle className="w-6 h-6 shrink-0" />
              <h3 className="font-display font-bold text-lg text-white">
                Delete Statement
              </h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-6">
              Are you sure you want to delete this bank statement archive? The file and extraction cache will be permanently deleted.
            </p>
            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                onClick={() => setDeletingId(null)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => handleDelete(deletingId)}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Trash2 className="w-4 h-4 mr-2" />
                )}
                Delete Statement
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
