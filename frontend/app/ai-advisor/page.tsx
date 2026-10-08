"use client";

import React, { useState, useEffect, useRef } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatINR } from "@/lib/utils/currency";
import {
  ChatMessage,
  AdvisorInsightCard,
  FinancialContextSummary,
} from "@/types/ai_advisor";
import { queryAdvisor, getAdvisorInsights } from "@/lib/api/ai_advisor";
import {
  Bot,
  Sparkles,
  Send,
  RefreshCw,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  ShieldAlert,
  Award,
  Zap,
  CheckCircle2,
  DollarSign,
  PiggyBank,
  Target,
} from "lucide-react";

const SUGGESTED_PROMPTS = [
  "What are my biggest spending categories?",
  "How much am I saving monthly?",
  "How am I progressing toward my goals?",
  "What should I improve in my spending?",
  "Give me an overview of my finances.",
];

export default function AiAdvisorPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello! I am NexAdvisor, your AI Financial Intelligence copilot. I analyze your verified income, expenses, investments, and savings goals in real-time. How would you like to optimize your wealth today?",
    },
  ]);
  const [input, setInput] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [insights, setInsights] = useState<AdvisorInsightCard[]>([]);
  const [summary, setSummary] = useState<FinancialContextSummary | null>(null);
  const [activeModel, setActiveModel] = useState<string>("NexAdvisor Neural Engine");
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Load initial proactive insights and user summary
  const loadInsights = async () => {
    try {
      const data = await getAdvisorInsights();
      setInsights(data.insights);
      setSummary(data.summary);
    } catch (err) {
      // Non-blocking for chat
    }
  };

  useEffect(() => {
    loadInsights();
  }, []);

  const handleSendMessage = async (queryText: string) => {
    const text = queryText.trim();
    if (!text || isTyping) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setInput("");
    setIsTyping(true);
    setError(null);

    try {
      // Send chat request with history
      const response = await queryAdvisor(text, messages);
      const aiMsg: ChatMessage = { role: "assistant", content: response.reply };
      setMessages([...newHistory, aiMsg]);
      if (response.insights && response.insights.length > 0) {
        setInsights(response.insights);
      }
      if (response.contextSummary) {
        setSummary(response.contextSummary);
      }
      if (response.model) {
        setActiveModel(response.model);
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to communicate with NexAdvisor.";
      setError(msg);
      setMessages([
        ...newHistory,
        {
          role: "assistant",
          content: `⚠️ I encountered a temporary processing error: ${msg}. Please try again or rephrase your question.`,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(input);
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case "optimization":
        return <TrendingUp className="w-4 h-4 text-mint-400" />;
      case "strategy":
        return <Lightbulb className="w-4 h-4 text-cyan-300" />;
      case "warning":
        return <ShieldAlert className="w-4 h-4 text-amber-400" />;
      case "achievement":
        return <Award className="w-4 h-4 text-purple-400" />;
      default:
        return <Zap className="w-4 h-4 text-cyan-400" />;
    }
  };

  return (
    <AppShell>
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">
              NexAdvisor AI Copilot
            </h2>
            <Badge variant="cyan">Person 2 Intelligence</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Real-time financial diagnosis, tax shields, surplus optimization, and budgeting guidance in INR (₹).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="mint" className="flex items-center gap-1.5 py-1">
            <span className="w-2 h-2 rounded-full bg-mint-400 animate-pulse" />
            <span>{activeModel.includes("Gemini") ? "Gemini 1.5 Active" : "Neural Engine Active"}</span>
          </Badge>
        </div>
      </div>

      {/* Quick Financial Health Pill Bar */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-3.5 flex items-center gap-3">
            <div className="w-9 h-9 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400 shrink-0">
              <DollarSign className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                Monthly Inflow
              </span>
              <span className="font-display font-bold text-sm text-white">
                {formatINR(summary.totalIncome)}
              </span>
            </div>
          </Card>

          <Card className="p-3.5 flex items-center gap-3">
            <div className="w-9 h-9 rounded-sm bg-mint-500/10 border border-border-mint flex items-center justify-center text-mint-400 shrink-0">
              <PiggyBank className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                Net Surplus (Savings)
              </span>
              <span className="font-display font-bold text-sm text-mint-400">
                {formatINR(summary.availableSavings)}
              </span>
            </div>
          </Card>

          <Card className="p-3.5 flex items-center gap-3">
            <div className="w-9 h-9 rounded-sm bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400 shrink-0">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                Savings Rate
              </span>
              <span className="font-display font-bold text-sm text-white">
                {summary.savingsRate}%
              </span>
            </div>
          </Card>

          <Card className="p-3.5 flex items-center gap-3">
            <div className="w-9 h-9 rounded-sm bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
              <Target className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                Goals Saved
              </span>
              <span className="font-display font-bold text-sm text-purple-300">
                {formatINR(summary.totalGoalsSaved)}
              </span>
            </div>
          </Card>
        </div>
      )}

      {/* Main Grid: Chat Window + Side Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Chat Container */}
        <Card className="lg:col-span-2 h-[640px] flex flex-col p-0 border-border-accent overflow-hidden">
          {/* Header */}
          <div className="p-4 bg-background-elevated border-b border-border-subtle flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-md bg-gradient-to-br from-cyan-400 to-blue-600 text-background flex items-center justify-center shadow-cyan-glow">
                <Bot className="w-5 h-5 text-black" />
              </div>
              <div>
                <span className="font-bold text-sm text-white block">NexAdvisor Neural Chat</span>
                <span className="text-[10px] text-slate-400">Authenticated • Single-User Isolated</span>
              </div>
            </div>
            <button
              onClick={() => {
                setMessages([
                  {
                    role: "assistant",
                    content:
                      "Conversation reset. How can I assist with your finances today?",
                  },
                ]);
              }}
              className="p-1.5 rounded-sm hover:bg-white/[0.05] text-slate-400 hover:text-white transition-colors text-xs flex items-center gap-1"
              title="Reset Conversation"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-3 max-w-[88%] ${
                  m.role === "user" ? "ml-auto flex-row-reverse" : ""
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                    m.role === "user"
                      ? "bg-background-elevated border border-border-subtle text-white"
                      : "bg-cyan-400 text-background font-black shadow-cyan-glow"
                  }`}
                >
                  {m.role === "user" ? "ME" : "AI"}
                </div>
                <div
                  className={`p-4 rounded-md text-xs leading-relaxed whitespace-pre-line ${
                    m.role === "user"
                      ? "bg-cyan-subtle/80 border border-border-accent text-white"
                      : "bg-background-elevated border border-border-subtle text-slate-200"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-3 max-w-[80%]">
                <div className="w-7 h-7 rounded-full bg-cyan-400 text-background font-black flex items-center justify-center text-xs shrink-0 shadow-cyan-glow">
                  AI
                </div>
                <div className="p-3.5 rounded-md bg-background-elevated border border-border-subtle flex items-center gap-2 text-xs text-slate-400">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  <span>NexAdvisor is analyzing your financial records...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Quick Prompts */}
          <div className="px-4 py-2 bg-background-surface/80 border-t border-border-subtle/50 overflow-x-auto flex items-center gap-2 shrink-0">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider shrink-0 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Suggested:
            </span>
            {SUGGESTED_PROMPTS.map((prompt, pIdx) => (
              <button
                key={pIdx}
                onClick={() => handleSendMessage(prompt)}
                disabled={isTyping}
                className="px-2.5 py-1 rounded-sm bg-background-elevated hover:bg-cyan-500/10 text-slate-300 hover:text-cyan-300 border border-border-subtle hover:border-border-accent text-[11px] whitespace-nowrap transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Chat Input Bar */}
          <form
            onSubmit={handleFormSubmit}
            className="p-3.5 bg-background-elevated border-t border-border-subtle flex gap-2 shrink-0"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about spending categories, tax exemptions, savings rate, or goal timelines..."
              disabled={isTyping}
              className="text-xs"
            />
            <Button
              type="submit"
              variant="primary"
              disabled={isTyping || !input.trim()}
              className="px-4 shrink-0"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </Card>

        {/* Right 1 Col: Dynamic Strategic Recommendations */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display font-bold text-sm text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Proactive Strategies
            </h3>
            <Badge variant="mint">Live Insights</Badge>
          </div>

          {insights.length === 0 ? (
            <Card className="p-6 text-center text-xs text-slate-400">
              Generating personalized financial recommendations based on your ledger...
            </Card>
          ) : (
            insights.map((card) => (
              <Card
                key={card.id}
                className="hover:border-border-accent transition-all cursor-pointer"
                onClick={() =>
                  handleSendMessage(
                    `Tell me more about how to execute: ${card.title}`
                  )
                }
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    {getInsightIcon(card.type)}
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      {card.tag}
                    </span>
                  </div>
                  {card.impact && (
                    <Badge variant="cyan" className="text-[10px]">
                      {card.impact}
                    </Badge>
                  )}
                </div>
                <h4 className="font-bold text-xs text-white mb-1.5">{card.title}</h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {card.description}
                </p>
              </Card>
            ))
          )}

          <Card className="p-4 bg-background-elevated/40 border-border-subtle text-xs text-slate-400 leading-relaxed">
            <div className="flex items-center gap-2 text-cyan-400 font-bold mb-1">
              <Bot className="w-4 h-4" />
              <span>Fintech Advisory Notice</span>
            </div>
            NexAdvisor recommendations are mathematically computed estimates designed to assist your financial planning. Always consult certified financial experts for accredited investment advice.
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
