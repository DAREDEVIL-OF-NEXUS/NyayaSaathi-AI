"use client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  is_verified: boolean;
  mfa_enabled: boolean;
  created_at: string;
}

export interface AuthResponse {
  user?: UserProfile;
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  mfa_required?: boolean;
  mfa_temp_token?: string;
  message?: string;
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("nyayasaathi_token");
}

export function setStoredToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("nyayasaathi_token", token);
  }
}

export function clearStoredToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("nyayasaathi_token");
    localStorage.removeItem("nyayasaathi_user");
  }
}

export function getStoredUser(): UserProfile | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("nyayasaathi_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredUser(user: UserProfile): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("nyayasaathi_user", JSON.stringify(user));
  }
}

export function authHeaders(): Record<string, string> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function signUp(email: string, password: string, fullName: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Sign up failed");
  return data;
}

export async function signIn(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Sign in failed");
  if (data.access_token) {
    setStoredToken(data.access_token);
    if (data.user) setStoredUser(data.user);
  }
  return data;
}

export async function verifyEmail(email: string, code: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/verify-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, code }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Email verification failed");
  if (data.access_token) {
    setStoredToken(data.access_token);
    if (data.user) setStoredUser(data.user);
  }
  return data;
}

export async function resendVerification(email: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/auth/resend-verification`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to resend code");
  return data;
}

export async function forgotPassword(email: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to process request");
  return data;
}

export async function resetPassword(token: string, newPassword: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Password reset failed");
  return data;
}

export async function setupMFA(): Promise<{ secret: string; qr_code_data_uri: string; provisioning_uri: string }> {
  const res = await fetch(`${API_BASE}/auth/mfa/setup`, {
    method: "POST",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to setup MFA");
  return data;
}

export async function verifyMFASetup(secret: string, code: string): Promise<{ status: string; message: string; backup_codes: string[] }> {
  const res = await fetch(`${API_BASE}/auth/mfa/verify`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ secret, code }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to verify MFA code");
  return data;
}

export async function challengeMFA(mfaTempToken: string, code: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/mfa/challenge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mfa_temp_token: mfaTempToken, code }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Invalid 2FA code or backup code");
  if (data.access_token) {
    setStoredToken(data.access_token);
    if (data.user) setStoredUser(data.user);
  }
  return data;
}

export async function getMe(): Promise<UserProfile> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load profile");
  setStoredUser(data);
  return data;
}

export async function signOut(): Promise<void> {
  try {
    await fetch(`${API_BASE}/auth/signout`, {
      method: "POST",
      headers: authHeaders(),
    });
  } catch {}
  clearStoredToken();
}
