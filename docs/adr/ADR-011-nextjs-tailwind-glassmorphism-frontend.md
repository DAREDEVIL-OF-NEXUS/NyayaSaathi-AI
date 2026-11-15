# ADR-011: Next.js 14 App Router with Tailwind Glassmorphism Legal-Tech UI

## Status
Accepted

## Context
Legal technology platforms in India frequently suffer from archaic, non-intuitive interfaces that intimidate citizens. A modern consumer grievance assistant requires an authoritative yet accessible interface with clear visual hierarchy, multi-step guidance, dark mode support, and interactive architectural transparency.

## Decision
Build the user interface with Next.js 14 App Router and Tailwind CSS:
1. **Design System:**
   - Palette: Deep midnight navy background (`#0b1120`, `#0f172a`), warm amber/saffron accents (`#f59e0b`, `#d97706`) symbolizing justice and vigilance.
   - Glassmorphism cards: Frosted backdrop blur (`backdrop-blur-md bg-slate-900/60 border border-slate-700/60`).
2. **Page Architecture:**
   - Public Discovery: Landing (`/`), About (`/about`), How It Works (`/how-it-works`), Interactive Architecture & Diagrams (`/architecture`).
   - Secure Identity: Sign In (`/signin`), Sign Up (`/signup`), Email Verification (`/verify-email`), Forgot Password (`/forgot-password`), MFA Enrollment & Challenge (`/mfa/setup`, `/mfa/challenge`), Security Settings (`/settings/security`).
   - Consumer Workspace (`/app`): AI Consultation (`/assistant`), Complaint Studio (`/complaint-studio`), Document Ingestion (`/case`), Knowledge Base (`/knowledge-base`).
3. **Interactive Diagrams:**
   - Client-side Mermaid.js rendering with interactive zooming, raw code copying, and architectural rationale cards.

## Consequences
- **Positive:** Intuitive, fast, mobile-responsive experience for citizens across desktop and mobile browsers.
- **Positive:** Clear separation of concerns between marketing/explanatory pages and authenticated legal workflows.
