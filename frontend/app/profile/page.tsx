"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatDate } from "@/lib/utils/currency";
import { getUserProfile, updateUserProfile } from "@/lib/api/profile";
import { UserProfile } from "@/types/profile";
import {
  User,
  Mail,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Lock,
  Save,
  RotateCcw,
  Fingerprint,
} from "lucide-react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getUserProfile();
      setProfile(data);
      setFormData({
        name: data.name,
        email: data.email,
      });
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load user profile.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  // Compute Initials
  const getInitials = (fullName: string) => {
    if (!fullName) return "NW";
    const parts = fullName.trim().split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return fullName.slice(0, 2).toUpperCase();
  };

  // Validate Form
  const validate = () => {
    const errors: { [key: string]: string } = {};
    if (!formData.name.trim()) {
      errors.name = "Full name is required.";
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      errors.email = "Email address is required.";
    } else if (!emailRegex.test(formData.email.trim())) {
      errors.email = "Please enter a valid email address.";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle Save
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const updated = await updateUserProfile({
        name: formData.name.trim(),
        email: formData.email.trim(),
      });
      setProfile(updated);
      setFormData({
        name: updated.name,
        email: updated.email,
      });
      setSuccessMessage("Profile updated successfully.");
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to update profile.";
      setError(msg);
    } finally {
      setIsSaving(false);
    }
  };

  // Reset Form
  const handleReset = () => {
    if (profile) {
      setFormData({
        name: profile.name,
        email: profile.email,
      });
      setFormErrors({});
      setError(null);
    }
  };

  const isFormDirty =
    profile &&
    (formData.name !== profile.name || formData.email !== profile.email);

  return (
    <AppShell>
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">
              Account Profile & Security
            </h2>
            <Badge variant="cyan">Person 3 Profile</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Manage your personal credentials, communication preferences, and security protocols.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={fetchProfile}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh Profile"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Success Notification */}
      {successMessage && (
        <div className="mb-6 p-4 rounded-md bg-mint-500/10 border border-border-mint flex items-center gap-3 text-mint-300 text-sm shadow-sm animate-fade-in">
          <CheckCircle2 className="w-5 h-5 shrink-0 text-mint-400" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mb-6 p-4 rounded-md bg-red-500/10 border border-red-500/25 flex items-center justify-between text-red-300 text-sm shadow-sm">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
          <Button
            variant="ghost"
            onClick={fetchProfile}
            className="text-xs text-red-400 hover:text-white"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Profile Overview Card */}
      <Card highlight className="mb-8 p-6 bg-gradient-to-r from-slate-900 via-background to-cyan-950/30 border-border-accent">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center font-display font-extrabold text-xl text-white shadow-cyan-glow border border-border-accent shrink-0">
            {isLoading ? "..." : getInitials(profile?.name || "")}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h3 className="font-display font-bold text-xl text-white truncate">
                {isLoading ? "Loading profile..." : profile?.name}
              </h3>
              <Badge variant="mint">Verified Account</Badge>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
              <div className="flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-cyan-400" />
                <span>{profile?.email}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-mint-400" />
                <span>Member since {profile ? formatDate(profile.createdAt) : "..."}</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Profile Grid: Edit Form & Compliance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Edit Personal Details */}
        <Card>
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
            <User className="w-4 h-4 text-cyan-400" />
            <h3 className="font-display font-bold text-base text-white">
              Edit Personal Credentials
            </h3>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            {/* User ID (Immutable) */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                <span>Unique Account ID</span>
                <span className="text-[10px] text-slate-500 font-normal">Immutable</span>
              </label>
              <div className="relative">
                <Input
                  value={profile?.id || ""}
                  disabled
                  readOnly
                  className="opacity-60 bg-background-elevated/40 font-mono text-xs cursor-not-allowed pl-8"
                />
                <Fingerprint className="w-4 h-4 text-slate-500 absolute left-2.5 top-2.5" />
              </div>
            </div>

            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Full Legal Name *
              </label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="e.g. Aarav Sharma"
                disabled={isLoading || isSaving}
              />
              {formErrors.name && (
                <div className="text-xs text-red-400 mt-1">{formErrors.name}</div>
              )}
            </div>

            {/* Email Address */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Email Address *
              </label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                placeholder="e.g. user@example.com"
                disabled={isLoading || isSaving}
              />
              {formErrors.email && (
                <div className="text-xs text-red-400 mt-1">{formErrors.email}</div>
              )}
            </div>

            {/* Locked Currency Standard */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                <span>Financial Currency Standard</span>
                <span className="text-[10px] text-mint-400 font-normal">Mandatory</span>
              </label>
              <Input
                value="Indian Rupee (₹ / INR)"
                disabled
                readOnly
                className="opacity-60 bg-background-elevated/40 text-xs cursor-not-allowed"
              />
            </div>

            {/* Action Buttons */}
            <div className="pt-4 border-t border-border-subtle flex items-center justify-between">
              <Button
                type="button"
                variant="ghost"
                onClick={handleReset}
                disabled={!isFormDirty || isSaving}
                className="text-xs text-slate-400 hover:text-white"
              >
                <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
                Reset Form
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={!isFormDirty || isSaving || isLoading}
              >
                {isSaving ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                Save Changes
              </Button>
            </div>
          </form>
        </Card>

        {/* Security & Authentication Protocol Card */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <ShieldCheck className="w-4 h-4 text-mint-400" />
              <h3 className="font-display font-bold text-base text-white">
                Security & Encryption Protocols
              </h3>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-md bg-mint-500/10 border border-border-mint">
                <div className="text-xs font-bold text-mint-400 flex items-center gap-2 mb-1">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Authentication Token: Active JWT Session</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Cryptographically signed JSON Web Token scoped to your unique account session.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Password Encryption Hash
                </label>
                <div className="relative">
                  <Input
                    value="bcrypt algorithm (salted & securely encrypted)"
                    disabled
                    readOnly
                    className="opacity-60 bg-background-elevated/40 text-xs cursor-not-allowed pl-8"
                  />
                  <Lock className="w-4 h-4 text-slate-500 absolute left-2.5 top-2.5" />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Passwords are never stored in plaintext and never transmitted via profile APIs.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Account Registration Timestamp
                </label>
                <Input
                  value={profile ? new Date(profile.createdAt).toUTCString() : "..."}
                  disabled
                  readOnly
                  className="opacity-60 bg-background-elevated/40 font-mono text-xs cursor-not-allowed"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 mt-6 border-t border-border-subtle text-[11px] text-slate-500 flex items-center justify-between">
            <span>System Data Contract: NEXWEALTH_DATA_CONTRACT.md</span>
            <span className="text-mint-400 font-semibold">● Operational</span>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
