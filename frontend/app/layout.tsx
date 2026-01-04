import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ThinkAloud AI",
  description: "A voice-first learning companion",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

