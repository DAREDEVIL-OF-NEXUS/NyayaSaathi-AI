"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Scale, ShieldCheck, User, LogOut, LayoutDashboard, Cpu, HelpCircle, Info, Menu, X } from "lucide-react";
import { getStoredUser, signOut, UserProfile } from "../lib/auth";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setUser(getStoredUser());
  }, [pathname]);

  const handleSignOut = async () => {
    await signOut();
    setUser(null);
    router.push("/signin");
  };

  const navLinks = [
    { name: "Overview", href: "/" },
    { name: "How It Works", href: "/how-it-works" },
    { name: "Architecture", href: "/architecture" },
    { name: "About", href: "/about" },
    { name: "Knowledge Base", href: "/app?tab=knowledge" },
  ];

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-500 via-amber-600 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform">
              <Scale className="h-5 w-5 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-100 tracking-tight">NyayaSaathi AI</span>
                <span className="text-[11px] font-semibold px-1.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  न्यायसाथी
                </span>
              </div>
              <p className="text-[11px] text-slate-400 -mt-0.5 hidden sm:block">Indian Consumer Rights & Grievance Redressal</p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 lg:gap-2">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.name}
                  href={link.href}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-slate-800 text-amber-400 border border-slate-700 shadow-sm"
                      : "text-slate-300 hover:text-slate-100 hover:bg-slate-800/50"
                  }`}
                >
                  {link.name}
                </Link>
              );
            })}
          </nav>

          {/* Right Action / Auth Buttons */}
          <div className="hidden sm:flex items-center gap-2">
            {user ? (
              <div className="flex items-center gap-2">
                <Link
                  href="/settings/security"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-800/60 border border-slate-800 transition-colors"
                >
                  <ShieldCheck className="h-3.5 w-3.5 text-amber-400" />
                  <span>{user.full_name.split(" ")[0]}</span>
                </Link>
                <Link
                  href="/app"
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 hover:from-amber-400 hover:to-amber-500 shadow-md shadow-amber-500/20 transition-all"
                >
                  <LayoutDashboard className="h-3.5 w-3.5" />
                  <span>Workspace</span>
                </Link>
                <button
                  onClick={handleSignOut}
                  title="Sign Out"
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800/50 rounded-lg transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/signin"
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/app"
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all"
                >
                  <span>Start Consultation</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-slate-400 hover:text-slate-200 rounded-lg"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-800 bg-slate-950 px-4 py-3 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-amber-400"
            >
              {link.name}
            </Link>
          ))}
          <div className="pt-2 border-t border-slate-800 flex flex-col gap-2">
            {user ? (
              <>
                <Link
                  href="/app"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950"
                >
                  Open Workspace
                </Link>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleSignOut();
                  }}
                  className="w-full text-center py-2 rounded-lg text-xs font-medium text-rose-400 hover:bg-slate-900"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/signin"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-900 border border-slate-800"
                >
                  Sign In
                </Link>
                <Link
                  href="/app"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950"
                >
                  Start Consultation
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
