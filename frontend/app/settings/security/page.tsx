"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "../../../components/Navbar";
import {
  ShieldCheck,
  ShieldAlert,
  KeyRound,
  Laptop,
  Smartphone,
  LogOut,
  AlertCircle,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { getMe, UserProfile, getStoredToken, authHeaders } from "../../../lib/auth";

interface SessionInfo {
  id: string;
  user_agent: string | null;
  ip_address: string | null;
  is_revoked: boolean;
  created_at: string;
  is_current: boolean;
}

export default function SecuritySettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getStoredToken()) {
      router.push("/signin");
      return;
    }

    Promise.all([
      getMe().then(setUser),
      fetch("http://localhost:8000/api/v1/auth/sessions", { headers: authHeaders() })
        .then((res) => (res.ok ? res.json() : []))
        .then(setSessions)
        .catch(() => setSessions([])),
    ]).finally(() => setLoading(false));
  }, [router]);

  const handleRevokeSession = async (sessionId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/auth/sessions/${sessionId}`, {
        method: "DELETE",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error("Failed to revoke session");
      setSessions((s) => s.filter((item) => item.id !== sessionId));
      setMessage("Session successfully revoked.");
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to revoke session");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-8 md:py-12">
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100">Security & Authentication</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage Two-Factor Authentication (MFA), active browser sessions, and personal security settings
          </p>
        </div>

        {message && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-6">
          {/* MFA Status Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div
                className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${
                  user?.mfa_enabled
                    ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                    : "bg-amber-500/10 border border-amber-500/20 text-amber-400"
                }`}
              >
                <ShieldCheck className="h-6 w-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-slate-100">Two-Factor Authentication (TOTP)</h3>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      user?.mfa_enabled
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    }`}
                  >
                    {user?.mfa_enabled ? "ACTIVE" : "DISABLED"}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1 max-w-xl">
                  Protects your account by requiring an authenticator code (RFC 6238) from your phone whenever you sign in.
                </p>
              </div>
            </div>

            <div>
              {user?.mfa_enabled ? (
                <Link
                  href="/mfa/setup"
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                >
                  Reconfigure 2FA
                </Link>
              ) : (
                <Link
                  href="/mfa/setup"
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-400 hover:bg-amber-300 text-slate-950 shadow-md shadow-amber-500/20 transition-all whitespace-nowrap block text-center"
                >
                  Enable 2FA
                </Link>
              )}
            </div>
          </div>

          {/* Active Sessions Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h3 className="text-base font-bold text-slate-100 mb-1">Active Login Sessions</h3>
            <p className="text-xs text-slate-400 mb-4">
              Devices and browsers currently logged into your NyayaSaathi account.
            </p>

            <div className="space-y-3">
              {sessions.length > 0 ? (
                sessions.map((sess) => (
                  <div
                    key={sess.id}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between gap-4 text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-9 w-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 shrink-0">
                        {sess.user_agent?.toLowerCase().includes("mobile") ? (
                          <Smartphone className="h-4 w-4" />
                        ) : (
                          <Laptop className="h-4 w-4" />
                        )}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-200 flex items-center gap-2">
                          <span>{sess.user_agent ? sess.user_agent.slice(0, 40) + "..." : "Web Browser"}</span>
                          {sess.is_current && (
                            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400">
                              CURRENT
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          IP: {sess.ip_address || "Localhost"} • Logged in: {new Date(sess.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    {!sess.is_current && (
                      <button
                        onClick={() => handleRevokeSession(sess.id)}
                        className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-medium border border-rose-500/20 transition-colors"
                      >
                        Revoke
                      </button>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 py-3">Current active session maintained via Bearer token.</div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
