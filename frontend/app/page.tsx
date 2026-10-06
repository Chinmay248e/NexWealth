"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthUtils } from "@/lib/auth/jwt";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    if (AuthUtils.isAuthenticated()) {
      router.replace("/dashboard");
    } else {
      router.replace("/login");
    }
  }, [router]);

  return (
    <div className="min-h-screen w-full bg-background flex items-center justify-center">
      <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
    </div>
  );
}
