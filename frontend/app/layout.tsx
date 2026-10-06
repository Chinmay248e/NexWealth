import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NexWealth — Futuristic Financial Intelligence & Portfolio Hub",
  description: "Next-generation personal wealth management platform exclusively in Indian Rupee (INR / ₹)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-white antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
