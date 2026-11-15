"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "../../../components/Navbar";
import { ShieldCheck, ArrowRight, AlertCircle, Copy, Check, Download, KeyRound } from "lucide-react";
import { setupMFA, verifyMFASetup, getStoredToken } from "../../../lib/auth";

export default function MFASetupPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [secret, setSecret] = useState("");
  const [qrCodeUri, setQrCodeUri] = useState("");
  const [code, setCode] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copiedSecret, setCopiedSecret] = useState(false);
  const [copiedBackup, setCopiedBackup] = useState(false);

  useEffect(() => {
    if (!getStoredToken()) {
      router.push("/signin");
      return;
    }

    setupMFA()
      .then((data) => {
        setSecret(data.secret);
        setQrCodeUri(data.qr_code_data_uri);
      })
      .catch((err) => {
        setError(err.message || "Failed to initialize 2FA setup");
      });
  }, [router]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await verifyMFASetup(secret, code.trim());
      setBackupCodes(res.backup_codes);
      setStep(2);
    } catch (err: any) {
      setError(err.message || "Invalid verification code. Please check your authenticator clock.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopySecret = () => {
    navigator.clipboard.writeText(secret);
    setCopiedSecret(true);
    setTimeout(() => setCopiedSecret(false), 2000);
  };

  const handleCopyBackup = () => {
    navigator.clipboard.writeText(backupCodes.join("\n"));
    setCopiedBackup(true);
    setTimeout(() => setCopiedBackup(false), 2000);
  };

  const handleDownloadBackup = () => {
    const blob = new Blob([backupCodes.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "nyayasaathi_backup_recovery_codes.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-lg p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-md">
          {step === 1 ? (
            <>
              <div className="text-center mb-6">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-amber-500/20">
                  <ShieldCheck className="h-6 w-6 text-slate-950" />
                </div>
                <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Set Up Authenticator MFA</h1>
                <p className="text-xs text-slate-400 mt-1">
                  Secure your account using Google Authenticator, Microsoft Authenticator, or 1Password
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {qrCodeUri ? (
                <div className="space-y-4">
                  {/* QR Code Container */}
                  <div className="p-4 rounded-2xl bg-white flex items-center justify-center max-w-[220px] mx-auto shadow-inner">
                    <img src={qrCodeUri} alt="TOTP MFA QR Code" className="w-full h-auto" />
                  </div>

                  {/* Manual Key Fallback */}
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider">Manual Setup Key</div>
                      <code className="font-mono text-amber-400 font-bold">{secret}</code>
                    </div>
                    <button
                      onClick={handleCopySecret}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                    >
                      {copiedSecret ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                    </button>
                  </div>

                  {/* Verification Form */}
                  <form onSubmit={handleVerify} className="space-y-3 pt-2">
                    <label className="block text-xs font-semibold text-slate-300">
                      Enter 6-Digit Code from App
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      value={code}
                      onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                      placeholder="123456"
                      className="w-full text-center tracking-[0.5em] text-xl font-mono py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-amber-400 placeholder-slate-600 focus:outline-none focus:border-amber-500 transition-colors"
                    />

                    <button
                      type="submit"
                      disabled={loading || code.length !== 6}
                      className="w-full py-2.5 rounded-xl text-xs font-semibold text-slate-950 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 shadow-md shadow-amber-500/20 flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
                    >
                      <span>{loading ? "Activating 2FA..." : "Verify & Enable 2FA"}</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </button>
                  </form>
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">Loading MFA security parameters...</div>
              )}
            </>
          ) : (
            /* Step 2: Backup Codes */
            <div className="space-y-4">
              <div className="text-center mb-4">
                <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-2">
                  <KeyRound className="h-6 w-6" />
                </div>
                <h2 className="text-xl font-bold text-slate-100">Save Your Backup Recovery Codes</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Keep these 10 single-use codes in a safe place. If you ever lose your phone or authenticator app, these codes are the only way to recover access.
                </p>
              </div>

              {/* Codes Grid */}
              <div className="grid grid-cols-2 gap-2 p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs text-amber-400">
                {backupCodes.map((c, i) => (
                  <div key={i} className="p-1.5 rounded bg-slate-900/60 text-center border border-slate-800">
                    {c}
                  </div>
                ))}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleCopyBackup}
                  className="flex-1 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
                >
                  {copiedBackup ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                  <span>{copiedBackup ? "Copied" : "Copy Codes"}</span>
                </button>
                <button
                  onClick={handleDownloadBackup}
                  className="flex-1 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Download (.txt)</span>
                </button>
              </div>

              <Link
                href="/settings/security"
                className="w-full py-2.5 rounded-xl text-xs font-semibold text-slate-950 bg-amber-400 hover:bg-amber-300 flex items-center justify-center gap-1.5 transition-all text-center block mt-4"
              >
                Done • Return to Security Settings
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
