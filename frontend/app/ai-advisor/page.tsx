"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, Sparkles, Send } from "lucide-react";

export default function AiAdvisorPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello Aarav! I am NexAdvisor, your financial copilot. Based on your current ₹2,07,700 monthly surplus and 74% savings rate, how would you like to optimize your portfolio today?",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userQuery = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setInput("");

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `I analyzed your query: "${userQuery}". With your ₹1.2L Emergency Fund at 78% completion and your healthcare tax deductions under Section 80D, deploying surplus funds into Nifty 50 Index direct plans will yield optimal post-tax growth.`,
        },
      ]);
    }, 400);
  };

  return (
    <AppShell>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl text-white">NexAdvisor AI Copilot</h2>
          <p className="text-xs text-slate-400 mt-0.5">Person 2 Domain: AI Financial Intelligence</p>
        </div>
        <Badge variant="cyan">Neural Engine Active</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 h-[580px] flex flex-col p-0 border-border-accent">
          {/* Header */}
          <div className="p-4 bg-background-elevated border-b border-border-subtle flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-md bg-cyan-400 text-background flex items-center justify-center shadow-cyan-glow">
                <Bot className="w-5 h-5" />
              </div>
              <span className="font-bold text-sm text-white">NexAdvisor Neural Chat</span>
            </div>
            <span className="text-[11px] text-mint-400 font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-mint-400 animate-pulse" />
              Online
            </span>
          </div>

          {/* Messages */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-3 max-w-[85%] ${
                  m.role === "user" ? "ml-auto flex-row-reverse" : ""
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                    m.role === "user"
                      ? "bg-background-elevated border border-border-subtle text-white"
                      : "bg-cyan-500 text-background font-black"
                  }`}
                >
                  {m.role === "user" ? "ME" : "AI"}
                </div>
                <div
                  className={`p-3.5 rounded-md text-xs leading-relaxed ${
                    m.role === "user"
                      ? "bg-cyan-subtle border border-border-accent text-white"
                      : "bg-background-elevated border border-border-subtle text-slate-200"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} className="p-4 bg-background-elevated border-t border-border-subtle flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask NexAdvisor about tax shields, budgeting, or investments..."
            />
            <Button type="submit" variant="primary">
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </Card>

        {/* Side Recommendations */}
        <div className="space-y-4">
          <Card className="hover:border-border-mint">
            <div className="text-[11px] font-bold text-mint-400 uppercase tracking-wider mb-1">
              Optimization
            </div>
            <h4 className="font-bold text-sm text-white mb-1">Liquidity Allocation</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Deploy ₹50,000 monthly surplus to Nifty 50 Index funds to boost CAGR by 12.4%.
            </p>
          </Card>

          <Card className="hover:border-border-accent">
            <div className="text-[11px] font-bold text-cyan-300 uppercase tracking-wider mb-1">
              Tax Strategy
            </div>
            <h4 className="font-bold text-sm text-white mb-1">Section 80D Utilization</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Your family health insurance policy qualifies for full ₹12,000 deduction.
            </p>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
