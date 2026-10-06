"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Layers, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { AuthUtils } from "@/lib/auth/jwt";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Prefetch dashboard route bundle for instant transition after registration
    router.prefetch("/dashboard");

    if (AuthUtils.isAuthenticated()) {
      router.replace("/dashboard");
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // 1. Register new user
      await apiClient("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          password: password,
        }),
      });

      // 2. Automatically log in to get JWT token
      const loginRes = await apiClient<{
        access_token: string;
        token_type: string;
      }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim(),
          password: password,
        }),
      });

      if (loginRes && loginRes.access_token) {
        AuthUtils.setToken(loginRes.access_token);
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Registration failed. Please try again.";
      setError(msg);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-background">
      <Card className="w-full max-w-md p-8 border-border-mint shadow-[0_0_30px_rgba(0,245,160,0.15)]">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-md bg-gradient-to-br from-mint-400 to-cyan-500 flex items-center justify-center shadow-mint-glow text-background mb-3">
            <Layers className="w-7 h-7" />
          </div>
          <h1 className="font-display font-bold text-2xl text-white">Create Account</h1>
          <p className="text-xs text-slate-400 mt-1">Start your wealth journey with secure account protection</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded bg-red-500/10 border border-red-500/25 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Full Legal Name
            </label>
            <Input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Aarav Sharma"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Email Address
            </label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="aarav.sharma@example.com"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              disabled={isLoading}
            />
          </div>

          <Button
            type="submit"
            variant="mint"
            className="w-full mt-2"
            disabled={isLoading}
          >
            {isLoading ? "Creating Account..." : "Create NexWealth Account"}
          </Button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-400">
          Already registered?{" "}
          <Link href="/login" className="text-mint-400 font-semibold hover:underline">
            Sign in here
          </Link>
        </div>
      </Card>
    </div>
  );
}
