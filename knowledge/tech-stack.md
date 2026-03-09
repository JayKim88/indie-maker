# Indie Maker Tech Stack

> **Shared constraint document** — all agents (Vera, Axel, indie-frontend, indie-infra) read this first.
> Individual agents make decisions *within* this stack. They do NOT override these choices.
>
> Stack last updated: 2026-03
> To change the stack: edit this file only. All agents adapt automatically.

---

## Default Stack (Recommended for most indie makers)

> **Target product type**: Web SaaS (browser-based).
> For mobile apps → see [Variant: Mobile](#variant-mobile-react-native--expo).
> For developer API tools → see [Variant: API-Only](#variant-api-only-no-frontend).

### Core Framework
| Layer | Technology | Version | Reason |
|-------|-----------|---------|--------|
| **Framework** | Next.js App Router | 15.x | Full-stack, SSR/SSG, API Routes in one repo |
| **Language** | TypeScript | 5.x | Type safety, better DX with Supabase generated types |
| **Package Manager** | npm / pnpm | latest | pnpm preferred for speed; npm if simpler |
| **Runtime** | Node.js 20+ / Vercel Edge | — | Vercel auto-selects optimal runtime |

### Frontend
| Layer | Technology | Reason |
|-------|-----------|--------|
| **CSS** | Tailwind CSS v4 | Utility-first, zero-config purge, design tokens |
| **Components** | shadcn/ui (Radix UI) | Accessible, unstyled base, copy-paste composable |
| **Icons** | Lucide React | MIT, consistent stroke width, tree-shakeable |
| **Fonts** | Plus Jakarta Sans (display) + Inter (body) | Google Fonts, free, optimized for Next.js |
| **Animation** | Framer Motion | React-native integration, `useReducedMotion` support |
| **Forms** | React Hook Form + Zod | Performance, revalidation, server-side schema reuse |
| **State** | React built-in (useState/useContext) → Zustand if complex | Start minimal |
| **Data fetching** | Server Components (default) → SWR/TanStack Query (client) | Server-first |

### Backend
| Layer | Technology | Reason |
|-------|-----------|--------|
| **Database** | Supabase (PostgreSQL) | RLS, Auth, Storage, Realtime — all-in-one |
| **Auth** | Supabase Auth | Email/OAuth, JWT managed, SSR cookie support |
| **API** | Next.js API Routes (Route Handlers) | Co-located, no separate server |
| **Validation** | Zod | Shared between client and server |
| **ORM** | Supabase client (typed) | Supabase-generated types eliminate N+1 mistakes |
| **File Storage** | Supabase Storage | Auth-integrated, CDN included |

### Payments & Services
| Layer | Technology | Reason |
|-------|-----------|--------|
| **Payments** | Stripe | Industry standard, best webhook DX |
| **Email** | Resend + React Email | Developer-first, React templates |
| **Rate Limiting** | Upstash Redis | Serverless-compatible, no persistent connection |
| **AI/LLM** | Vercel AI SDK + Anthropic/OpenAI | Streaming, useChat hook, provider-agnostic |
| **Vector Search** | pgvector (Supabase Extension) | No separate service needed for MVP |

### Infrastructure
| Layer | Technology | Reason |
|-------|-----------|--------|
| **Hosting** | Vercel | Zero-config Next.js deploy, edge network |
| **Domain** | Vercel Domains or external (Namecheap/Cloudflare) | Vercel DNS simplest |
| **CDN** | Vercel Edge Network (included) | Automatic |
| **Monitoring** | Sentry (errors) + BetterStack (uptime) | Free tiers sufficient for MVP |
| **Analytics** | Vercel Analytics (built-in) | Zero setup |

### Dev Tooling
| Layer | Technology | Reason |
|-------|-----------|--------|
| **Linting** | ESLint + Prettier | Next.js default config |
| **Testing** | Vitest + Supabase Local | Fast, Node-compatible |
| **Types** | `supabase gen types typescript` | Auto-generated from schema |
| **Git hooks** | Husky + lint-staged | Pre-commit lint + type check |

---

## Stack Variants (Override when needed)

When a project deviates from the default, record it in `idea-canvas.md` under `tech_stack`:

```yaml
# idea-canvas.md — tech_stack section
tech_stack:
  variant: default          # default | mobile | api-only | custom
  overrides:
    css: "CSS Modules"      # replaces Tailwind
    payments: "LemonSqueezy" # replaces Stripe
    ai: false               # no AI features
  notes: "Reason for deviation"
```

### Variant: Mobile (React Native / Expo)
Use when: Primary platform is iOS/Android.
```
Framework:  Expo (React Native)
UI:         NativeWind (Tailwind for React Native) + React Native Paper
Backend:    Same Supabase + Next.js API Routes (shared backend)
Payments:   RevenueCat (mobile IAP)
```

### Variant: API-Only (No Frontend)
Use when: Building a developer API product.
```
Framework:  Next.js (API Routes only) or Hono.js
Auth:       API key auth (custom) — Supabase Auth optional
Docs:       Mintlify or Scalar
Rate limiting: Upstash Redis (same as default)
```

---

## Version Compatibility Matrix

```
Next.js 15.x  →  React 19.x  →  Node.js 20+
Supabase JS 2.x  →  @supabase/ssr 0.x
Tailwind 4.x  →  shadcn/ui latest  →  Radix UI 2.x
Stripe 16.x
Zod 3.x  →  React Hook Form 7.x
Vitest 2.x
```

---

## What Each Agent Does With This Stack

| Agent | Constraint Applied |
|-------|-------------------|
| **indie-planner** | Proposes stack variant based on product type; records in idea-canvas.md |
| **Vera (designer)** | Uses Tailwind tokens, shadcn/ui components, Plus Jakarta Sans + Inter |
| **Arch (architect)** | Designs file structure, DB schema draft, API endpoints, shared types using this stack |
| **indie-frontend** | Uses Next.js App Router, shadcn/ui, Framer Motion, SWR/TanStack Query |
| **Axel (backend)** | Uses Supabase, Next.js Route Handlers, Zod, Stripe, Resend, Upstash |
| **indie-infra** | Deploys on Vercel, Supabase project, sets env vars, configures Stripe live |
| **indie-analyst** | Reads Vercel Analytics + Supabase metrics; no stack changes |

**Rule**: No agent changes the tech stack without updating this file first.

---

## Stack Change Protocol

If you want to switch a technology (e.g., replace Stripe with LemonSqueezy):

1. Update this file — `tech-stack.md`
2. Update `idea-canvas.md` → `tech_stack.overrides`
3. Inform relevant agents: "Stack updated: payments → LemonSqueezy. See tech-stack.md."

Agents will read this file at the start of each session and adapt their guidance.

---

## Non-Negotiable Constraints

These cannot be overridden regardless of variant:

- **TypeScript only** — no plain JS files in `src/`
- **Zod validation on all API inputs** — server-side, always
- **Supabase RLS on all tables** — no exceptions, even for MVP
- **Environment variables via `.env.local`** — never hardcode secrets
- **`NEXT_PUBLIC_` prefix only for client-safe values** — SUPABASE_SERVICE_ROLE_KEY never has this prefix
