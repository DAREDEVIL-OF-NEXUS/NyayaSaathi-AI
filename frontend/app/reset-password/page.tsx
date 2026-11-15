"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Navbar } from "../../components/Navbar";
import { Lock, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";
import { resetPassword } from "../../lib/auth";

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!token) {
      setError("Reset token is missing or invalid. Please request a new link.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    setLoading(true);

    try {
      const res = await resetPassword(token, password);
      setMessage(res.message || "Password reset successfully. You can now sign in.");
      setTimeout(() => router.push("/signin"), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to reset password. Link may have expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-md">
      <div className="text-center mb-6">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-amber-500/20">
          <Lock className="h-6 w-6 text-slate-950" />
        </div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Create New Password</h1>
        <p className="text-xs text-slate-400 mt-1">Enter your new secure password below</p>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {message && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">New Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Minimum 8 characters"
            className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Confirm New Password</label>
          <input
            type="password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-enter new password"
            className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 rounded-xl text-xs font-semibold text-slate-950 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 shadow-md shadow-amber-500/20 flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
        >
          <span>{loading ? "Updating Password..." : "Reset Password"}</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </form>

      <div className="mt-6 text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
        <Link href="/signin" className="text-amber-400 hover:text-amber-300 font-semibold transition-colors">
          Return to Sign In
        </Link>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />
      <main className="flex-1 flex items-center justify-center p-4">
        <Suspense fallback={<div className="text-xs text-amber-400">Loading reset form...</div>}>
          <ResetPasswordContent />
        </Suspense>
      </main>
    </div>
  );
}
