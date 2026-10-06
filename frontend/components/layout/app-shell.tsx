"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { AuthUtils } from "@/lib/auth/jwt";

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();

  useEffect(() => {
    if (!AuthUtils.isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  return (
    <div className="flex min-h-screen w-full bg-background text-white selection:bg-cyan-500 selection:text-background">
      <Sidebar />
      <div className="ml-64 flex-1 flex flex-col min-w-0 min-h-screen">
        <Header />
        <main className="flex-1 p-8 max-w-[1440px] w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};

