"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "../../../components/Navbar";
import { ShieldCheck, ArrowRight, AlertCircle, KeyRound } from "lucide-react";
import { challengeMFA } from "../../../lib/auth";

export default function MFAChallengePage() {
  const router = useRouter();
  const [code, setCode] = useState("");
  const [tempToken, setTempToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isBackup, setIsBackup] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem("nyayasaathi_mfa_token");
    if (!stored) {
      router.push("/signin");
    } else {
      setTempToken(stored);
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await challengeMFA(tempToken, code.trim());
      sessionStorage.removeItem("nyayasaathi_mfa_token");
      router.push("/app");
    } catch (err: any) {
      setError(err.message || "Invalid 2FA code or backup recovery code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-md">
          <div className="text-center mb-6">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-amber-500/20">
              <ShieldCheck className="h-6 w-6 text-slate-950" />
            </div>
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Two-Factor Authentication</h1>
            <p className="text-xs text-slate-400 mt-1">
              {isBackup
                ? "Enter one of your 10 single-use backup recovery codes"
                : "Enter the 6-digit code from your Authenticator app (Google, Microsoft, Authy)"}
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                {isBackup ? "Single-Use Backup Code" : "6-Digit Authenticator Code"}
              </label>
              <input
                type="text"
                required
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={isBackup ? "e.g. 8a9f2c3d4e" : "123456"}
                className={`w-full py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-amber-400 font-mono text-center focus:outline-none focus:border-amber-500 transition-colors ${
                  isBackup ? "text-sm tracking-widest px-3" : "text-xl tracking-[0.5em]"
                }`}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !code}
              className="w-full py-2.5 rounded-xl text-xs font-semibold text-slate-950 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 shadow-md shadow-amber-500/20 flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
            >
              <span>{loading ? "Authenticating..." : "Verify & Sign In"}</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
            <button
              type="button"
              onClick={() => {
                setIsBackup(!isBackup);
                setCode("");
                setError(null);
              }}
              className="text-amber-400 hover:text-amber-300 font-medium inline-flex items-center gap-1 transition-colors"
            >
              <KeyRound className="h-3.5 w-3.5" />
              <span>{isBackup ? "Use Authenticator App instead" : "Lost access? Use a Backup Recovery Code"}</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
