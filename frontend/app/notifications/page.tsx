"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils/currency";
import { Notification } from "@/types/notification";
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
} from "@/lib/api/notification";
import {
  Bell,
  AlertTriangle,
  CheckCircle2,
  Info,
  AlertCircle,
  Check,
  Trash2,
  RefreshCw,
  Filter,
  CheckCheck,
} from "lucide-react";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters & State
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [isMarkingAll, setIsMarkingAll] = useState<boolean>(false);

  const fetchNotificationList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getNotifications(unreadOnly);
      setNotifications(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load notifications.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [unreadOnly]);

  useEffect(() => {
    fetchNotificationList();
  }, [fetchNotificationList]);

  // Handle Mark as Read
  const handleMarkAsRead = async (id: string) => {
    setProcessingId(id);
    try {
      await markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true, isRead: true } : n))
      );
      if (unreadOnly) {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to mark notification as read.";
      setError(msg);
    } finally {
      setProcessingId(null);
    }
  };

  // Handle Mark All as Read
  const handleMarkAllAsRead = async () => {
    setIsMarkingAll(true);
    try {
      const res = await markAllNotificationsRead();
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, read: true, isRead: true }))
      );
      if (unreadOnly) {
        setNotifications([]);
      }
      setSuccessMessage(
        res.count > 0
          ? `Marked ${res.count} notification${res.count > 1 ? "s" : ""} as read.`
          : "All notifications are already marked as read."
      );
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to mark all as read.";
      setError(msg);
    } finally {
      setIsMarkingAll(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    setProcessingId(id);
    try {
      await deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setSuccessMessage("Notification deleted.");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to delete notification.";
      setError(msg);
    } finally {
      setProcessingId(null);
    }
  };

  // Computed unread count
  const unreadCount = useMemo(() => {
    return notifications.filter((n) => !n.read).length;
  }, [notifications]);

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "budget_alert":
        return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      case "goal_reached":
        return <CheckCircle2 className="w-5 h-5 text-mint-400" />;
      case "warning":
      case "alert":
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case "system":
      default:
        return <Info className="w-5 h-5 text-cyan-400" />;
    }
  };

  return (
    <AppShell>
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display font-bold text-2xl text-white">
              System Notifications
            </h2>
            <Badge variant="cyan">Person 3 Engine</Badge>
            {unreadCount > 0 && (
              <Badge variant="mint">{unreadCount} UNREAD</Badge>
            )}
          </div>
          <p className="text-xs text-slate-400">
            Real-time financial alerts, budget warnings, goal milestones, and system updates.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="ghost"
            onClick={() => setUnreadOnly(!unreadOnly)}
            className={`text-xs gap-1.5 ${
              unreadOnly
                ? "bg-cyan-500/10 text-cyan-300 border border-border-accent"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>{unreadOnly ? "Showing Unread" : "All Alerts"}</span>
          </Button>

          <Button
            variant="ghost"
            onClick={fetchNotificationList}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>

          <Button
            variant="primary"
            onClick={handleMarkAllAsRead}
            disabled={isMarkingAll || unreadCount === 0}
            className="text-xs"
          >
            {isMarkingAll ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin mr-1.5" />
            ) : (
              <CheckCheck className="w-3.5 h-3.5 mr-1.5" />
            )}
            Mark All Read
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
            onClick={fetchNotificationList}
            className="text-xs text-red-400 hover:text-white"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Notifications List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
            <span className="text-sm">Loading notifications...</span>
          </div>
        ) : notifications.length === 0 ? (
          <Card className="p-12 text-center flex flex-col items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-border-accent flex items-center justify-center text-cyan-400">
              <Bell className="w-6 h-6" />
            </div>
            <div className="text-sm font-semibold text-white">
              {unreadOnly ? "No unread notifications" : "No notifications found"}
            </div>
            <p className="text-xs text-slate-400 max-w-sm">
              {unreadOnly
                ? "You have reviewed all your active notifications. Switch to All Alerts to view past history."
                : "You're all caught up! New transaction confirmations, budget notices, and investment milestones will appear here."}
            </p>
          </Card>
        ) : (
          notifications.map((n) => {
            const isUnread = !n.read;
            const isProcessing = processingId === n.id;

            return (
              <Card
                key={n.id}
                className={`flex items-start gap-4 p-4 transition-all duration-200 ${
                  isUnread
                    ? "border-border-accent bg-cyan-subtle/10 shadow-[0_0_12px_rgba(0,242,254,0.06)]"
                    : "border-border-subtle bg-card/60 opacity-85 hover:opacity-100 hover:border-border-light"
                }`}
              >
                {/* Type Icon */}
                <div className="w-10 h-10 rounded-md bg-background-elevated border border-border-subtle flex items-center justify-center shrink-0">
                  {getTypeIcon(n.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">
                        {n.title}
                      </span>
                      {isUnread && <Badge variant="cyan">NEW</Badge>}
                    </div>
                    <span className="text-[11px] text-slate-400">
                      {formatDate(n.createdAt)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {n.message}
                  </p>
                </div>

                {/* Inline Action Buttons */}
                <div className="flex items-center gap-1 shrink-0 pt-0.5">
                  {isUnread && (
                    <button
                      onClick={() => handleMarkAsRead(n.id)}
                      disabled={isProcessing}
                      title="Mark as Read"
                      className="p-1.5 rounded-sm hover:bg-mint-500/10 text-slate-400 hover:text-mint-400 transition-colors"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(n.id)}
                    disabled={isProcessing}
                    title="Delete Notification"
                    className="p-1.5 rounded-sm hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </Card>
            );
          })
        )}
      </div>
    </AppShell>
  );
}
