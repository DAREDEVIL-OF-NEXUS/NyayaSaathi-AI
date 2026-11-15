import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NyayaSaathi AI (न्यायसाथी AI) | Consumer Protection & Grievance Platform",
  description: "Official legal assistance for Indian consumers powered by hybrid RAG, legal knowledge graphs, and verified government sources.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-900 text-slate-100 flex flex-col antialiased selection:bg-amber-500 selection:text-slate-950">
        {children}
      </body>
    </html>
  );
}
