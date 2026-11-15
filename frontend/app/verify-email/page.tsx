"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Navbar } from "../../components/Navbar";
import { Scale, MailCheck, ArrowRight, AlertCircle, RefreshCw } from "lucide-react";
import { verifyEmail, resendVerification } from "../../lib/auth";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialEmail = searchParams.get("email") || "";
  const initialCode = searchParams.get("code") || "";

  const [email, setEmail] = useState(initialEmail);
  const [code, setCode] = useState(initialCode);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (initialEmail) setEmail(initialEmail);
    if (initialCode) setCode(initialCode);
  }, [initialEmail, initialCode]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      await verifyEmail(email, code);
      router.push("/app");
    } catch (err: any) {
      setError(err.message || "Invalid or expired verification code.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (!email) {
      setError("Please enter your email address to resend code.");
      return;
    }
    setError(null);
    setResending(true);
    try {
      const res = await resendVerification(email);
      setMessage(res.message || "A new 6-digit verification code has been dispatched.");
    } catch (err: any) {
      setError(err.message || "Failed to resend verification code.");
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="w-full max-w-md p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-md">
      <div className="text-center mb-6">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-amber-500/20">
          <MailCheck className="h-6 w-6 text-slate-950" />
        </div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Verify Your Email</h1>
        <p className="text-xs text-slate-400 mt-1">
          Enter the 6-digit numeric verification code sent to your email
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {message && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
          {message}
        </div>
      )}

      <form onSubmit={handleVerify} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@example.com"
            className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">6-Digit Verification Code</label>
          <input
            type="text"
            required
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            placeholder="123456"
            className="w-full text-center tracking-[0.5em] text-lg font-mono py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-amber-400 placeholder-slate-600 focus:outline-none focus:border-amber-500 transition-colors"
          />
        </div>

        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className="w-full py-2.5 rounded-xl text-xs font-semibold text-slate-950 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 shadow-md shadow-amber-500/20 flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
        >
          <span>{loading ? "Verifying..." : "Verify & Continue"}</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </form>

      <div className="mt-6 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/80 pt-4">
        <span>Didn't receive the OTP?</span>
        <button
          onClick={handleResend}
          disabled={resending}
          className="text-amber-400 hover:text-amber-300 font-semibold flex items-center gap-1 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-3 w-3 ${resending ? "animate-spin" : ""}`} />
          <span>Resend OTP</span>
        </button>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />
      <main className="flex-1 flex items-center justify-center p-4">
        <Suspense fallback={<div className="text-xs text-amber-400">Loading verification form...</div>}>
          <VerifyEmailContent />
        </Suspense>
      </main>
    </div>
  );
}
