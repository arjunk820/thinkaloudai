import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ThinkAloud AI",
  description: "A voice-first learning companion that helps you discover answers through Socratic questioning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
