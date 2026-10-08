"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils/currency";
import { Document } from "@/types/contract";
import { DOCUMENT_CATEGORIES, DocumentCategory } from "@/types/document";
import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "@/lib/api/document";
import {
  FileText,
  UploadCloud,
  Trash2,
  X,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  FolderLock,
  ShieldCheck,
  FileCheck,
  Plus,
  Paperclip,
} from "lucide-react";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Upload Modal State
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docCategory, setDocCategory] = useState<string>("Tax Return");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  // Delete State
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Success Notification State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchDocumentList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const filter = selectedCategory === "All" ? undefined : selectedCategory;
      const data = await getDocuments(filter);
      setDocuments(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load documents";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    fetchDocumentList();
  }, [fetchDocumentList]);

  // Handle File Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadError(null);
    }
  };

  // Open Upload Modal
  const handleOpenUpload = () => {
    setSelectedFile(null);
    setDocCategory("Tax Return");
    setUploadError(null);
    setIsUploadModalOpen(true);
  };

  // Handle Upload Submit
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError("Please choose a file to upload.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      await uploadDocument(selectedFile, docCategory);
      setSuccessMessage(`Document "${selectedFile.name}" uploaded successfully.`);
      setIsUploadModalOpen(false);
      setSelectedFile(null);
      await fetchDocumentList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to upload document.";
      setUploadError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    setIsDeleting(true);
    try {
      await deleteDocument(id);
      setDeletingId(null);
      setSuccessMessage("Document removed from vault.");
      await fetchDocumentList();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete document.";
      setError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Summary Metrics
  const metrics = useMemo(() => {
    const total = documents.length;
    const verified = documents.filter((d) => d.status.toLowerCase() === "verified").length;
    const taxCount = documents.filter((d) => d.documentType.toLowerCase().includes("tax")).length;
    return { total, verified, taxCount };
  }, [documents]);

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
            onClick={fetchDocumentList}
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
            <h2 className="font-display font-bold text-2xl text-white">Document Vault</h2>
            <Badge variant="cyan">Person 2 Security Vault</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Encrypted storage and metadata indexing for tax returns, policies, and financial receipts.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={fetchDocumentList}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Vault"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
          <Button variant="primary" onClick={handleOpenUpload}>
            <Plus className="w-4 h-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </div>

      {/* Vault KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Documents
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <FolderLock className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-white">{metrics.total}</div>
          <div className="text-[11px] text-slate-500 mt-2">Indexed in your private vault</div>
        </Card>

        <Card highlight className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              Verified Records
            </span>
            <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-cyan-400">{metrics.verified}</div>
          <div className="text-[11px] text-slate-400 mt-2">Verified financial documents</div>
        </Card>

        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Tax & Compliance
            </span>
            <div className="w-8 h-8 rounded-sm bg-mint-500/10 border border-border-mint flex items-center justify-center text-mint-400">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="font-display font-black text-2xl text-mint-400">{metrics.taxCount}</div>
          <div className="text-[11px] text-slate-500 mt-2">ITR-V and tax invoices stored</div>
        </Card>
      </div>

      {/* Category Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-6 text-xs">
        <button
          onClick={() => setSelectedCategory("All")}
          className={`px-3.5 py-1.5 rounded-sm font-semibold transition-colors ${
            selectedCategory === "All"
              ? "bg-cyan-500/20 text-cyan-400 border border-border-accent"
              : "bg-background-elevated text-slate-400 hover:text-white border border-border-subtle"
          }`}
        >
          All Categories
        </button>
        {DOCUMENT_CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-sm font-semibold transition-colors whitespace-nowrap ${
              selectedCategory === cat
                ? "bg-cyan-500/20 text-cyan-400 border border-border-accent"
                : "bg-background-elevated text-slate-400 hover:text-white border border-border-subtle"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Documents Grid */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
          <span className="text-sm">Loading document vault...</span>
        </div>
      ) : documents.length === 0 ? (
        <Card className="p-12 text-center flex flex-col items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
            <FileText className="w-6 h-6" />
          </div>
          <div className="text-sm font-semibold text-white">No documents found</div>
          <p className="text-xs text-slate-400 max-w-sm">
            {selectedCategory === "All"
              ? "Your document vault is currently empty. Upload your tax returns, insurance policies, or investment receipts."
              : `No documents found in category "${selectedCategory}".`}
          </p>
          <Button variant="primary" onClick={handleOpenUpload} className="mt-2">
            <Plus className="w-4 h-4 mr-2" />
            Upload Document
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <Card
              key={doc.id}
              className="flex items-center gap-4 hover:border-border-accent transition-all group"
            >
              <div className="w-12 h-12 rounded-sm bg-background-elevated border border-border-subtle flex items-center justify-center text-cyan-400 shrink-0 group-hover:border-border-accent">
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
              <div className="flex items-center gap-2">
                <Badge variant={doc.status.toLowerCase() === "verified" ? "mint" : "cyan"}>
                  {doc.status}
                </Badge>
                <button
                  onClick={() => setDeletingId(doc.id)}
                  className="p-1.5 rounded-sm hover:bg-red-500/10 text-slate-500 hover:text-red-400 transition-colors"
                  title="Delete Document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Document Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fade-in">
          <Card className="w-full max-w-lg bg-background-surface border-border-accent shadow-2xl relative p-6">
            <div className="flex items-center justify-between pb-4 border-b border-border-subtle mb-6">
              <div className="flex items-center gap-2 text-cyan-400">
                <UploadCloud className="w-5 h-5" />
                <h3 className="font-display font-bold text-lg text-white">
                  Upload Document to Vault
                </h3>
              </div>
              <button
                onClick={() => setIsUploadModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              {uploadError && (
                <div className="p-3 rounded-sm bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}

              {/* Document Category */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Document Category *
                </label>
                <select
                  value={docCategory}
                  onChange={(e) => setDocCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border-subtle rounded-md text-sm text-white focus:outline-none focus:border-border-accent"
                >
                  {DOCUMENT_CATEGORIES.map((cat) => (
                    <option key={cat} value={cat} className="bg-background-surface text-white">
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {/* File Dropzone */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  File Attachment (PDF, Images, Excel, CSV) *
                </label>
                <div className="border-2 border-dashed border-border-subtle hover:border-border-accent rounded-md p-6 flex flex-col items-center justify-center text-center cursor-pointer bg-background transition-colors relative">
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.png,.jpg,.jpeg,.csv,.xlsx,.txt,.docx"
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  {selectedFile ? (
                    <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold">
                      <Paperclip className="w-4 h-4" />
                      <span>{selectedFile.name}</span>
                      <span className="text-xs text-slate-500">
                        ({(selectedFile.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                  ) : (
                    <>
                      <UploadCloud className="w-8 h-8 text-cyan-400 mb-2" />
                      <p className="text-xs text-slate-300 font-semibold mb-1">
                        Click or drag & drop to choose a file
                      </p>
                      <p className="text-[11px] text-slate-500">
                        PDF, PNG, JPG, CSV, XLSX up to 10MB
                      </p>
                    </>
                  )}
                </div>
              </div>

              <div className="pt-4 border-t border-border-subtle flex justify-end gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsUploadModalOpen(false)}
                  disabled={isUploading}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={isUploading || !selectedFile}>
                  {isUploading ? (
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <UploadCloud className="w-4 h-4 mr-2" />
                  )}
                  Upload Document
                </Button>
              </div>
            </form>
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
                Delete Document
              </h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-6">
              Are you sure you want to delete this document from your vault? The record and stored file will be permanently removed.
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
                Delete Document
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
