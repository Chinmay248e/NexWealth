import { Notification as ContractNotification } from "./contract";

/**
 * Notification Types (Person 3)
 */
export interface Notification extends Omit<ContractNotification, "isRead"> {
  read: boolean;
  isRead: boolean;
}

export type NotificationType =
  | "budget_alert"
  | "goal_reached"
  | "system"
  | "warning"
  | "alert"
  | "info"
  | string;
