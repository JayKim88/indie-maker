# Full-Stack Backend Knowledge Base

> Extended intelligence layer for Axel (Full-Stack Backend agent).
> Reference: `backend-guide.md` covers Non-Negotiable Rules — treat it as Axel's constitution.
> This document adds: architecture decision trees, patterns library, performance, real-time,
> background jobs, multi-tenancy, email, rate limiting, migrations, and environment setup.

---

## 1. Product Type Architecture Matrix

Backend architecture changes significantly by product type.
**First check prd-lean.md for product type. If missing, ask before designing schema.**

| Product Type | Auth Model | Data Model | Key Tables | Critical Concern |
|-------------|-----------|-----------|------------|-----------------|
| **Solo SaaS** | user-owned rows | Simple, flat | profile, subscription, [feature] | RLS per user |
| **Team SaaS (B2B)** | org-scoped rows | Organization → members → resources | organization, member, [feature] | Multi-tenancy RLS |
| **Marketplace** | buyer + seller | Dual-role users, listings, transactions | listing, order, review, payout | Transaction integrity |
| **Content Platform** | creator + viewer | Public + private content | post, follower, like, view_count | Read-heavy queries |
| **Dev Tool / API** | API key auth | Usage tracking | api_key, usage_log, rate_limit | Rate limiting, quotas |

---

## 2. Architecture Decision Trees

### 2.1 Server Component vs API Route vs Supabase Direct

```
Need data for a page?
├─ Initial page render, SEO matters
│   └─ Server Component: await supabase.from(...) directly
│       - No API route needed
│       - Fastest (no extra round trip)
│       - Data never exposed to client
│
├─ After user action (button click, form submit)
│   └─ API Route + fetch from client
│       - Validate server-side with Zod
│       - Auth check in route handler
│
└─ Real-time (live updates without refresh)
    └─ Supabase Realtime subscription
        - Client subscribes to table changes
        - See Section 6 for patterns
```

### 2.2 When to Use Service Role Client

```
Service Role Key bypasses ALL RLS — treat it like root access.

USE Service Role ONLY when:
├─ Stripe webhook handler (writes subscription on behalf of user)
├─ Cron jobs / scheduled tasks (no user session available)
├─ Admin operations (e.g., data migration, bulk update)
└─ Creating cross-user data (e.g., shared resources)

NEVER USE Service Role for:
├─ Regular API routes with user sessions → use createClient() instead
├─ Any client-side code
└─ Server Components (use createClient() with user session cookie)
```

### 2.3 Database Function vs Application Code

```
Use Supabase DB function (plpgsql) when:
├─ Multiple tables must update atomically (transaction required)
├─ Operation must be consistent regardless of which service calls it
└─ Complex business logic that must run in the DB for performance

Use Application code (API Route) when:
├─ External service calls required (Stripe, Resend, etc.)
├─ Complex conditional logic
└─ Response needs transformation before returning to client

Example — Use DB function for:
  transfer_credits(from_user, to_user, amount)
  → debit one user, credit another — MUST be atomic
```

### 2.4 Pagination Strategy Selection

```
Offset pagination (LIMIT/OFFSET):
├─ PROS: Easy to implement, supports "Go to page N"
└─ CONS: Slow on large datasets (full scan), inconsistent on inserts

Cursor pagination:
├─ PROS: O(log n) regardless of dataset size, consistent
└─ CONS: No "Go to page N", slightly more complex

Rule:
├─ Dashboard lists, recent activity → Cursor pagination
├─ Admin panels, small datasets (<10K rows) → Offset is fine
└─ Infinite scroll → Always cursor

Cursor pattern:
SELECT * FROM item
WHERE (created_at, id) < ($cursor_created_at, $cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

### 2.5 Soft Delete vs Hard Delete

```
Hard Delete (DELETE FROM table WHERE id = $1):
├─ Use when: Data has no audit/recovery requirements
├─ Use when: GDPR "right to be forgotten" must be absolute
└─ Simpler RLS, no stale data

Soft Delete (is_deleted = true, deleted_at = now()):
├─ Use when: Users might want to recover data
├─ Use when: Other tables reference this data (avoids FK cascade complexity)
└─ Use when: Audit trail required

Soft delete implementation:
ALTER TABLE item ADD COLUMN is_deleted bool NOT NULL DEFAULT false;
ALTER TABLE item ADD COLUMN deleted_at timestamptz;

-- Update RLS to exclude deleted rows
CREATE POLICY "Users view own active items"
  ON item FOR SELECT USING (auth.uid() = user_id AND is_deleted = false);

-- Partial index (only index non-deleted rows)
CREATE INDEX item_user_id_active_idx ON item (user_id) WHERE is_deleted = false;
```

---

## 3. Multi-Tenancy (Team/Org SaaS)

### 3.1 Organization Schema

```sql
-- Organizations
CREATE TABLE organization (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name        text NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
  slug        text NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9-]+$'),
  plan        text NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
  created_at  timestamptz DEFAULT now() NOT NULL,
  updated_at  timestamptz DEFAULT now() NOT NULL
);

CREATE TRIGGER organization_updated_at
  BEFORE UPDATE ON organization FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

ALTER TABLE organization ENABLE ROW LEVEL SECURITY;

-- Organization Members (join table with roles)
CREATE TABLE organization_member (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  user_id         uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role            text NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
  created_at      timestamptz DEFAULT now() NOT NULL,
  UNIQUE (organization_id, user_id)
);

CREATE INDEX organization_member_org_id_idx  ON organization_member (organization_id);
CREATE INDEX organization_member_user_id_idx ON organization_member (user_id);

ALTER TABLE organization_member ENABLE ROW LEVEL SECURITY;

-- RLS: users can see orgs they belong to
CREATE POLICY "Members can view own organization"
  ON organization FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM organization_member
      WHERE organization_id = organization.id AND user_id = auth.uid()
    )
  );

-- RLS: only owners/admins can update org
CREATE POLICY "Admins can update organization"
  ON organization FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM organization_member
      WHERE organization_id = organization.id
        AND user_id = auth.uid()
        AND role IN ('owner', 'admin')
    )
  );

-- Feature table with org scope (replace user_id with organization_id)
CREATE TABLE project (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  created_by      uuid NOT NULL REFERENCES auth.users(id),
  name            text NOT NULL,
  created_at      timestamptz DEFAULT now() NOT NULL,
  updated_at      timestamptz DEFAULT now() NOT NULL
);

CREATE INDEX project_organization_id_idx ON project (organization_id);
ALTER TABLE project ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Org members can view projects"
  ON project FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM organization_member
      WHERE organization_id = project.organization_id AND user_id = auth.uid()
    )
  );
```

### 3.2 Helper Function for Role Checks

```typescript
// lib/auth/org.ts
export async function requireOrgRole(
  supabase: SupabaseClient,
  organizationId: string,
  userId: string,
  minRole: 'member' | 'admin' | 'owner' = 'member'
) {
  const roleOrder = { member: 0, admin: 1, owner: 2 }

  const { data } = await supabase
    .from('organization_member')
    .select('role')
    .eq('organization_id', organizationId)
    .eq('user_id', userId)
    .single()

  if (!data) return { error: 'Not a member', status: 403 }
  if (roleOrder[data.role as keyof typeof roleOrder] < roleOrder[minRole]) {
    return { error: 'Insufficient permissions', status: 403 }
  }
  return { role: data.role }
}
```

---

## 4. Rate Limiting

### 4.1 Upstash Redis Rate Limiter (Recommended)

```bash
npm install @upstash/ratelimit @upstash/redis
```

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

// Sliding window: 10 requests per 10 seconds
export const apiRateLimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
})

// Stricter for auth endpoints
export const authRateLimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(5, '60 s'),
})
```

```typescript
// Usage in API route
import { apiRateLimit } from '@/lib/rate-limit'

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1'
  const { success, limit, reset, remaining } = await apiRateLimit.limit(ip)

  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests', code: 'RATE_LIMITED', status: 429 },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': String(limit),
          'X-RateLimit-Remaining': String(remaining),
          'X-RateLimit-Reset': String(reset),
          'Retry-After': String(Math.ceil((reset - Date.now()) / 1000)),
        },
      }
    )
  }
  // ... rest of handler
}
```

### 4.2 Simple DB-Based Rate Limit (No Redis — for MVP)

```typescript
// Simpler approach using Supabase — good for MVP before Redis setup
async function checkRateLimit(userId: string, action: string, limit: number, windowSeconds: number) {
  const windowStart = new Date(Date.now() - windowSeconds * 1000).toISOString()

  const { count } = await supabaseAdmin
    .from('rate_limit_log')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId)
    .eq('action', action)
    .gte('created_at', windowStart)

  return { allowed: (count ?? 0) < limit, count: count ?? 0 }
}
```

---

## 5. Email Integration (Resend)

### 5.1 Setup

```bash
npm install resend
```

```typescript
// lib/email.ts
import { Resend } from 'resend'

export const resend = new Resend(process.env.RESEND_API_KEY!)

export const FROM_EMAIL = 'noreply@yourdomain.com'
export const SUPPORT_EMAIL = 'support@yourdomain.com'
```

### 5.2 Email Templates

```typescript
// lib/emails/welcome.tsx
import { Html, Head, Body, Container, Text, Button, Hr } from '@react-email/components'

interface WelcomeEmailProps {
  userName: string
  dashboardUrl: string
}

export function WelcomeEmail({ userName, dashboardUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Body style={{ fontFamily: 'Inter, sans-serif', backgroundColor: '#f8fafc' }}>
        <Container style={{ maxWidth: '560px', margin: '0 auto', padding: '40px 20px' }}>
          <Text style={{ fontSize: '24px', fontWeight: 'bold', color: '#0f172a' }}>
            Welcome to [Product], {userName}!
          </Text>
          <Text style={{ color: '#475569', lineHeight: '1.6' }}>
            You're all set. Head to your dashboard to get started.
          </Text>
          <Button href={dashboardUrl}
            style={{ backgroundColor: '#7C3AED', color: '#fff', padding: '12px 24px', borderRadius: '8px' }}>
            Go to Dashboard
          </Button>
          <Hr style={{ borderColor: '#e2e8f0', margin: '32px 0' }} />
          <Text style={{ color: '#94a3b8', fontSize: '14px' }}>
            Questions? Reply to this email or contact {SUPPORT_EMAIL}
          </Text>
        </Container>
      </Body>
    </Html>
  )
}
```

```typescript
// Sending email in API route
import { resend, FROM_EMAIL } from '@/lib/email'
import { WelcomeEmail } from '@/lib/emails/welcome'

await resend.emails.send({
  from: FROM_EMAIL,
  to: user.email,
  subject: 'Welcome to [Product]!',
  react: WelcomeEmail({ userName: user.full_name ?? 'there', dashboardUrl: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard` }),
})
```

### 5.3 Email Trigger Points

| Trigger | Template | Send in |
|---------|---------|---------|
| Signup complete | Welcome | handle_new_user() → Edge Function |
| Subscription activated | Upgrade confirmed | Stripe webhook |
| Subscription canceled | Cancellation + offboarding | Stripe webhook |
| Password reset | Reset link | Supabase Auth (built-in) |
| Invitation to team | Invite link | API route |
| Usage limit warning (80%) | Upgrade prompt | Cron job / pg_cron |

---

## 6. Real-Time Patterns (Supabase Realtime)

### 6.1 Client-Side Subscription

```typescript
// hooks/useRealtimeItems.ts
import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

export function useRealtimeItems(userId: string) {
  const [items, setItems] = useState<Item[]>([])
  const supabase = createClient()

  useEffect(() => {
    // Initial fetch
    supabase.from('item').select('*').eq('user_id', userId).order('created_at', { ascending: false })
      .then(({ data }) => setItems(data ?? []))

    // Realtime subscription
    const channel = supabase
      .channel('items-changes')
      .on('postgres_changes', {
        event: '*',          // INSERT | UPDATE | DELETE | *
        schema: 'public',
        table: 'item',
        filter: `user_id=eq.${userId}`,
      }, (payload) => {
        if (payload.eventType === 'INSERT') {
          setItems(prev => [payload.new as Item, ...prev])
        } else if (payload.eventType === 'UPDATE') {
          setItems(prev => prev.map(i => i.id === payload.new.id ? payload.new as Item : i))
        } else if (payload.eventType === 'DELETE') {
          setItems(prev => prev.filter(i => i.id !== payload.old.id))
        }
      })
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [userId])

  return items
}
```

### 6.2 When to Use Realtime

```
USE Realtime when:
├─ Collaborative features (multiple users see same data)
├─ Notification inbox (user gets live alerts)
├─ Live dashboard metrics
└─ Chat / messaging features

AVOID Realtime when:
├─ Data changes rarely (polling or manual refresh is fine)
├─ Strict data consistency required (realtime has ~100ms delay)
└─ You're on free tier and have many concurrent users (channel limits)

Free tier limit: 200 concurrent realtime connections
```

---

## 7. Background Jobs (Edge Functions + pg_cron)

### 7.1 pg_cron Setup (Supabase Dashboard)

```sql
-- Enable pg_cron extension (Supabase Dashboard → Extensions → pg_cron)
SELECT cron.schedule(
  'daily-usage-reset',           -- job name
  '0 0 * * *',                   -- cron expression (midnight UTC daily)
  $$
    UPDATE usage_log
    SET daily_count = 0
    WHERE date < now() - INTERVAL '1 day';
  $$
);

-- View scheduled jobs
SELECT * FROM cron.job;

-- Remove a job
SELECT cron.unschedule('daily-usage-reset');
```

### 7.2 Supabase Edge Function Pattern

```typescript
// supabase/functions/send-usage-warnings/index.ts
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { Resend } from 'https://esm.sh/resend@2'

Deno.serve(async (req) => {
  // Verify this is called by cron (or Supabase internal)
  const authHeader = req.headers.get('Authorization')
  if (authHeader !== `Bearer ${Deno.env.get('CRON_SECRET')}`) {
    return new Response('Unauthorized', { status: 401 })
  }

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // Find users at 80% of their usage limit
  const { data: users } = await supabase
    .from('usage_summary')
    .select('user_id, email, usage_count, limit')
    .gte('usage_percent', 80)
    .lt('usage_percent', 100)
    .eq('warning_sent', false)

  // Send emails and mark as warned
  for (const user of users ?? []) {
    await resend.emails.send({ /* ... */ })
    await supabase.from('usage_summary').update({ warning_sent: true }).eq('user_id', user.user_id)
  }

  return new Response(JSON.stringify({ processed: users?.length ?? 0 }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
```

---

## 8. Usage Limits & Feature Flags

### 8.1 Usage Limit Pattern

```sql
-- Track usage per user per billing period
CREATE TABLE usage_log (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  action      text NOT NULL,         -- e.g., 'api_call', 'export', 'project_created'
  period      text NOT NULL,         -- e.g., '2026-03' (year-month)
  count       int NOT NULL DEFAULT 0,
  created_at  timestamptz DEFAULT now() NOT NULL,
  updated_at  timestamptz DEFAULT now() NOT NULL,
  UNIQUE (user_id, action, period)
);

-- Atomic increment (upsert)
INSERT INTO usage_log (user_id, action, period, count)
VALUES ($1, $2, to_char(now(), 'YYYY-MM'), 1)
ON CONFLICT (user_id, action, period)
DO UPDATE SET count = usage_log.count + 1, updated_at = now();
```

```typescript
// lib/usage.ts
const PLAN_LIMITS = {
  free: { api_calls: 100, projects: 3, exports: 5 },
  pro:  { api_calls: 10000, projects: 999, exports: 999 },
}

export async function checkUsageLimit(
  supabase: SupabaseClient,
  userId: string,
  action: string,
  plan: 'free' | 'pro'
): Promise<{ allowed: boolean; current: number; limit: number }> {
  const period = new Date().toISOString().slice(0, 7) // 'YYYY-MM'
  const limit = PLAN_LIMITS[plan][action as keyof typeof PLAN_LIMITS.free] ?? 0

  const { data } = await supabase
    .from('usage_log')
    .select('count')
    .eq('user_id', userId)
    .eq('action', action)
    .eq('period', period)
    .single()

  const current = data?.count ?? 0
  return { allowed: current < limit, current, limit }
}
```

### 8.2 Simple Feature Flag (DB-Based)

```sql
CREATE TABLE feature_flag (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  key         text NOT NULL UNIQUE,          -- e.g., 'new_dashboard'
  enabled     bool NOT NULL DEFAULT false,
  plan_gate   text[],                        -- e.g., ARRAY['pro'] — null = all plans
  user_ids    uuid[],                        -- specific user overrides
  created_at  timestamptz DEFAULT now() NOT NULL
);
```

```typescript
export async function isFeatureEnabled(
  key: string, userId: string, plan: string
): Promise<boolean> {
  const { data } = await supabaseAdmin
    .from('feature_flag')
    .select('enabled, plan_gate, user_ids')
    .eq('key', key)
    .single()

  if (!data || !data.enabled) return false
  if (data.user_ids?.includes(userId)) return true            // Override
  if (!data.plan_gate) return true                            // All plans
  return data.plan_gate.includes(plan)                       // Plan gate
}
```

---

## 9. TypeScript Types from Supabase

### 9.1 Generate Types

```bash
# Install Supabase CLI
npm install -g supabase

# Login and link project
supabase login
supabase link --project-ref [YOUR_PROJECT_REF]

# Generate types
supabase gen types typescript --linked > src/types/database.types.ts
```

### 9.2 Usage Pattern

```typescript
// src/types/database.types.ts is auto-generated — never edit manually
import type { Database } from '@/types/database.types'

// Convenient type aliases
export type Tables<T extends keyof Database['public']['Tables']> =
  Database['public']['Tables'][T]['Row']

export type Profile      = Tables<'profile'>
export type Item         = Tables<'item'>
export type Subscription = Tables<'subscription'>

// For insert/update operations
export type InsertItem = Database['public']['Tables']['item']['Insert']
export type UpdateItem = Database['public']['Tables']['item']['Update']
```

```typescript
// Typed Supabase client setup
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { Database } from '@/types/database.types'

export function createClient() {
  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { /* cookies config */ }
  )
}
```

---

## 10. Database Migration Patterns

### 10.1 Safe Migration Rules

```
Never do in production without a plan:
├─ DROP COLUMN — data is gone
├─ NOT NULL addition to existing table with data
├─ Rename column — breaks all queries instantly
└─ Change column type — may truncate data

Safe migration patterns:

Adding a column (safe):
  ALTER TABLE item ADD COLUMN priority int DEFAULT 0 NOT NULL;
  → Default ensures existing rows are valid immediately

Renaming a column (safe, 3-step):
  Step 1: Add new column, copy data → ALTER TABLE ADD COLUMN new_name ...; UPDATE item SET new_name = old_name;
  Step 2: Deploy code using new_name (dual-read if needed)
  Step 3: Drop old column → ALTER TABLE DROP COLUMN old_name;

Adding NOT NULL to existing column (safe):
  Step 1: UPDATE item SET col = 'default' WHERE col IS NULL;
  Step 2: ALTER TABLE item ALTER COLUMN col SET NOT NULL;
```

### 10.2 Supabase Migration Workflow

```bash
# Create a new migration
supabase migration new add_priority_to_item

# Edit the generated file: supabase/migrations/[timestamp]_add_priority_to_item.sql

# Apply to local (Docker)
supabase db reset

# Apply to production
supabase db push
```

---

## 11. Performance Patterns

### 11.1 N+1 Query Prevention

```typescript
// BAD — N+1 queries
const items = await supabase.from('item').select('*')
for (const item of items.data) {
  const user = await supabase.from('profile').select('*').eq('id', item.user_id)
  // This fires one query per item!
}

// GOOD — Single query with join
const { data } = await supabase
  .from('item')
  .select(`
    *,
    profile (
      id,
      full_name,
      avatar_url
    )
  `)
```

### 11.2 Select Only What You Need

```typescript
// BAD — select * fetches all columns including large text/JSON
const { data } = await supabase.from('item').select('*')

// GOOD — select only what the UI needs
const { data } = await supabase
  .from('item')
  .select('id, title, status, created_at')  // specific columns
  .order('created_at', { ascending: false })
  .limit(20)
```

### 11.3 Partial Indexes for Hot Queries

```sql
-- Most queries filter by user + active status
-- Partial index dramatically speeds this up
CREATE INDEX item_user_active_idx
  ON item (user_id, created_at DESC)
  WHERE is_deleted = false AND status = 'active';

-- After adding index, verify it's being used
EXPLAIN ANALYZE
  SELECT * FROM item
  WHERE user_id = '...' AND is_deleted = false AND status = 'active'
  ORDER BY created_at DESC LIMIT 20;
-- Should show "Index Scan" not "Seq Scan"
```

### 11.4 Query Performance Debugging

```sql
-- Find slow queries (enable in Supabase: Dashboard → Database → Query Performance)
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Check missing indexes on FK columns
SELECT
  tc.table_name, kcu.column_name,
  ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu USING (constraint_name, table_schema)
JOIN information_schema.constraint_column_usage AS ccu USING (constraint_name, table_schema)
WHERE constraint_type = 'FOREIGN KEY'
AND NOT EXISTS (
  SELECT 1 FROM pg_indexes
  WHERE tablename = tc.table_name AND indexdef LIKE '%' || kcu.column_name || '%'
);
```

---

## 12. Error Monitoring (Sentry)

```bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

```typescript
// lib/errors.ts
import * as Sentry from '@sentry/nextjs'

export function captureAPIError(
  error: unknown,
  context: { path: string; userId?: string; body?: unknown }
) {
  Sentry.withScope(scope => {
    scope.setTag('api_path', context.path)
    if (context.userId) scope.setUser({ id: context.userId })
    if (context.body) scope.setExtra('request_body', context.body)
    Sentry.captureException(error)
  })
}

// Usage in API route:
} catch (error) {
  captureAPIError(error, { path: '/api/items', userId: user.id })
  return NextResponse.json({ error: 'Internal server error', code: 'INTERNAL_ERROR', status: 500 }, { status: 500 })
}
```

---

## 13. Environment Variables — Complete Template

```bash
# .env.local (never commit — add to .gitignore)

# ─── Supabase ───────────────────────────────────────
NEXT_PUBLIC_SUPABASE_URL=https://[project-ref].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...    # Server-only — NEVER prefix with NEXT_PUBLIC_

# ─── App ────────────────────────────────────────────
NEXT_PUBLIC_APP_URL=http://localhost:3000  # Change to production domain before deploy

# ─── Stripe ─────────────────────────────────────────
STRIPE_SECRET_KEY=sk_test_...             # Server-only
STRIPE_WEBHOOK_SECRET=whsec_...           # From: stripe listen output or Dashboard
STRIPE_PRO_PRICE_ID=price_...             # From Stripe Dashboard → Products

# ─── Email (Resend) ──────────────────────────────────
RESEND_API_KEY=re_...

# ─── Rate Limiting (Upstash) ─────────────────────────
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...

# ─── Error Monitoring (Sentry) ───────────────────────
SENTRY_DSN=https://...@sentry.io/...
NEXT_PUBLIC_SENTRY_DSN=https://...@sentry.io/...   # Same value — needed client-side

# ─── Background Jobs ─────────────────────────────────
CRON_SECRET=generate_a_random_secret_here  # Protect cron endpoints
```

---

## 14. Security Hardening Checklist

Applied on top of `backend-guide.md` Non-Negotiable Rules.

### Pre-Launch Security Review

**Authentication**
- [ ] OAuth providers configured (Google, GitHub) if needed — Supabase Dashboard → Auth Providers
- [ ] Email OTP or magic link as backup (in case password auth has issues)
- [ ] Password requirements set (min 8 chars) in Supabase Auth settings
- [ ] `auth.uid()` used in all RLS policies — never `user_metadata`

**API Security**
- [ ] CORS restricted to production domain (`NEXT_PUBLIC_APP_URL` only)
- [ ] Rate limiting on all public endpoints
- [ ] Auth endpoints rate limited more strictly (5 req/min)
- [ ] File upload: MIME type verified server-side, not just file extension
- [ ] File upload: max size enforced server-side (not just client)

**Data Security**
- [ ] `SUPABASE_SERVICE_ROLE_KEY` not in any `NEXT_PUBLIC_` variable
- [ ] `.env.local` in `.gitignore`
- [ ] No PII logged to console or Sentry (sanitize request bodies before logging)
- [ ] Stripe secret key not in any client-facing file

**Stripe Security**
- [ ] Webhook signature verified with `constructEvent()` — no exceptions
- [ ] `metadata.user_id` used to link Stripe customer to Supabase user
- [ ] Test mode keys in dev, live keys only in production env

---

---

## 15. AI/LLM Integration Patterns

### 15.1 Vercel AI SDK Setup (Recommended for Next.js)

```bash
npm install ai @ai-sdk/anthropic @ai-sdk/openai
```

```typescript
// lib/ai.ts
import { createAnthropic } from '@ai-sdk/anthropic'
import { createOpenAI } from '@ai-sdk/openai'

export const anthropic = createAnthropic({ apiKey: process.env.ANTHROPIC_API_KEY! })
export const openai = createOpenAI({ apiKey: process.env.OPENAI_API_KEY! })

// Model selection by use case
export const AI_MODELS = {
  fast:    anthropic('claude-haiku-4-5-20251001'),   // Quick responses, low cost
  balanced: anthropic('claude-sonnet-4-6'),           // Default for most tasks
  powerful: anthropic('claude-opus-4-6'),             // Complex reasoning
  embedding: openai('text-embedding-3-small'),        // Vector search
}
```

### 15.2 Streaming API Route

```typescript
// src/app/api/ai/chat/route.ts
import { streamText } from 'ai'
import { anthropic } from '@/lib/ai'
import { createClient } from '@/lib/supabase/server'
import { z } from 'zod'

const chatSchema = z.object({
  messages: z.array(z.object({
    role: z.enum(['user', 'assistant']),
    content: z.string().max(10000),
  })).max(50),
})

export async function POST(request: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return new Response('Unauthorized', { status: 401 })

  // Check usage limit before calling AI (AI calls are expensive)
  const { allowed, current, limit } = await checkUsageLimit(supabase, user.id, 'ai_call', userPlan)
  if (!allowed) {
    return Response.json(
      { error: `Monthly AI limit reached (${current}/${limit})`, code: 'USAGE_LIMIT', status: 429 },
      { status: 429 }
    )
  }

  const body = await request.json()
  const parsed = chatSchema.safeParse(body)
  if (!parsed.success) return Response.json({ error: 'Invalid input' }, { status: 422 })

  // Stream response — client reads via useChat() hook
  const result = streamText({
    model: AI_MODELS.balanced,
    system: 'You are a helpful assistant for [Product].', // Product-specific system prompt
    messages: parsed.data.messages,
    maxTokens: 2000,
    onFinish: async ({ usage }) => {
      // Log token usage after stream completes
      await supabase.from('ai_usage_log').insert({
        user_id: user.id,
        tokens_input:  usage.promptTokens,
        tokens_output: usage.completionTokens,
        model: 'claude-sonnet-4-6',
      })
    },
  })

  return result.toDataStreamResponse()
}
```

### 15.3 Token Usage Tracking Schema

```sql
CREATE TABLE ai_usage_log (
  id             uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id        uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  model          text NOT NULL,
  tokens_input   int NOT NULL DEFAULT 0,
  tokens_output  int NOT NULL DEFAULT 0,
  cost_usd       numeric(10, 6),   -- calculated cost
  feature        text,              -- which feature triggered this call
  created_at     timestamptz DEFAULT now() NOT NULL
);

CREATE INDEX ai_usage_log_user_id_idx  ON ai_usage_log (user_id);
CREATE INDEX ai_usage_log_created_idx  ON ai_usage_log (created_at DESC);

ALTER TABLE ai_usage_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users view own AI usage" ON ai_usage_log
  FOR SELECT USING (auth.uid() = user_id);

-- Monthly cost view
CREATE VIEW ai_monthly_cost AS
SELECT
  user_id,
  date_trunc('month', created_at) AS month,
  SUM(tokens_input + tokens_output) AS total_tokens,
  SUM(cost_usd) AS total_cost_usd
FROM ai_usage_log
GROUP BY user_id, date_trunc('month', created_at);
```

### 15.4 Token Cost Reference (2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| claude-haiku-4-5 | $0.80 | $4.00 |
| claude-sonnet-4-6 | $3.00 | $15.00 |
| claude-opus-4-6 | $15.00 | $75.00 |
| gpt-4o-mini | $0.15 | $0.60 |

```typescript
// lib/ai-cost.ts — calculate cost before inserting log
const COST_PER_MILLION = {
  'claude-haiku-4-5-20251001': { input: 0.80, output: 4.00 },
  'claude-sonnet-4-6':          { input: 3.00, output: 15.00 },
}

export function calculateCost(model: string, inputTokens: number, outputTokens: number) {
  const rates = COST_PER_MILLION[model as keyof typeof COST_PER_MILLION]
  if (!rates) return 0
  return (inputTokens / 1_000_000 * rates.input) + (outputTokens / 1_000_000 * rates.output)
}
```

### 15.5 AI Feature Architecture Decision Tree

```
AI integration approach:
├─ Simple Q&A / chat → streamText (Vercel AI SDK) + useChat hook
├─ Structured output (JSON from AI) → generateObject with Zod schema
├─ Long background task (>30s) → Edge Function + job queue (not API Route)
├─ Semantic search → pgvector (Supabase) + embedding API
└─ RAG (Retrieval-Augmented Generation) → embed documents → pgvector → query

Prompt versioning:
├─ Store system prompts in DB (easy to update without redeploy)
├─ Version each prompt: prompt_version table
└─ A/B test prompts by randomly assigning versions per user
```

### 15.6 pgvector for Semantic Search

```sql
-- Enable pgvector extension (Supabase Dashboard → Extensions)
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to searchable table
ALTER TABLE article ADD COLUMN embedding vector(1536);  -- OpenAI text-embedding-3-small

-- Create HNSW index for fast approximate nearest neighbor search
CREATE INDEX article_embedding_hnsw_idx
  ON article USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Similarity search query
SELECT id, title, 1 - (embedding <=> $1::vector) AS similarity
FROM article
WHERE 1 - (embedding <=> $1::vector) > 0.7  -- similarity threshold
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

---

## 16. Service Layer Pattern

### 16.1 Why Service Layer

```
Problem: API Routes grow into 200+ line files mixing auth, validation,
         business logic, DB queries, and email sends.

Solution: Thin API Routes → call Service functions → Service handles logic

API Route responsibility:  Auth check + input validation + call service + return HTTP response
Service responsibility:    Business logic + DB operations + side effects (email, etc.)
```

### 16.2 Structure

```
src/
├── app/
│   └── api/
│       └── items/
│           └── route.ts          ← Thin: auth + zod + call service
├── services/
│   ├── item.service.ts           ← Business logic for items
│   ├── user.service.ts           ← User-related logic
│   └── subscription.service.ts  ← Subscription + billing logic
├── repositories/                 ← Optional: pure DB access layer
│   └── item.repository.ts
└── lib/
    ├── supabase/
    └── ai.ts
```

### 16.3 Service Pattern

```typescript
// services/item.service.ts
import { SupabaseClient } from '@supabase/supabase-js'
import type { Database } from '@/types/database.types'
import type { InsertItem, UpdateItem, Item } from '@/types/database.types'

type Supabase = SupabaseClient<Database>

export const ItemService = {
  async list(supabase: Supabase, userId: string): Promise<Item[]> {
    const { data, error } = await supabase
      .from('item')
      .select('id, title, status, created_at')
      .eq('user_id', userId)
      .eq('is_deleted', false)
      .order('created_at', { ascending: false })
      .limit(50)

    if (error) throw new ServiceError('Failed to fetch items', 'DB_ERROR', 500)
    return data
  },

  async create(supabase: Supabase, userId: string, input: InsertItem): Promise<Item> {
    // Business rule: free plan max 3 items
    const count = await this.countByUser(supabase, userId)
    if (count >= 3) throw new ServiceError('Item limit reached. Upgrade to Pro.', 'LIMIT_REACHED', 403)

    const { data, error } = await supabase
      .from('item')
      .insert({ ...input, user_id: userId })
      .select()
      .single()

    if (error) throw new ServiceError('Failed to create item', 'DB_ERROR', 500)
    return data
  },

  async countByUser(supabase: Supabase, userId: string): Promise<number> {
    const { count } = await supabase
      .from('item')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId)
      .eq('is_deleted', false)
    return count ?? 0
  },
}

// Typed error for service layer
export class ServiceError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number
  ) {
    super(message)
    this.name = 'ServiceError'
  }
}
```

### 16.4 Thin API Route (using service)

```typescript
// app/api/items/route.ts
import { ItemService, ServiceError } from '@/services/item.service'
import { createItemSchema } from '@/lib/schemas/item'
import { createClient } from '@/lib/supabase/server'

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return Response.json({ error: 'Unauthorized', code: 'AUTH_REQUIRED', status: 401 }, { status: 401 })

  try {
    const items = await ItemService.list(supabase, user.id)
    return Response.json(items)
  } catch (e) {
    if (e instanceof ServiceError) return Response.json({ error: e.message, code: e.code, status: e.status }, { status: e.status })
    return Response.json({ error: 'Internal server error', code: 'INTERNAL_ERROR', status: 500 }, { status: 500 })
  }
}

export async function POST(request: Request) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return Response.json({ error: 'Unauthorized', code: 'AUTH_REQUIRED', status: 401 }, { status: 401 })

  const body = await request.json()
  const parsed = createItemSchema.safeParse(body)
  if (!parsed.success) return Response.json({ error: 'Validation failed', code: 'VALIDATION_ERROR', status: 422, details: parsed.error.flatten() }, { status: 422 })

  try {
    const item = await ItemService.create(supabase, user.id, parsed.data)
    return Response.json(item, { status: 201 })
  } catch (e) {
    if (e instanceof ServiceError) return Response.json({ error: e.message, code: e.code, status: e.status }, { status: e.status })
    return Response.json({ error: 'Internal server error', code: 'INTERNAL_ERROR', status: 500 }, { status: 500 })
  }
}
```

---

## 17. Testing Strategy

### 17.1 Testing Pyramid for Indie SaaS

```
          /  E2E (Playwright) — 5%  \
         /  Critical flows only      \
        ──────────────────────────────
       /  Integration — 25%           \
      /  API routes + DB interactions  \
     ────────────────────────────────────
    /  Unit tests — 70%                  \
   /  Services, utilities, schemas        \
  ──────────────────────────────────────────
```

### 17.2 Vitest Setup

```bash
npm install -D vitest @vitejs/plugin-react @testing-library/react
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['./src/tests/setup.ts'],
    env: {
      NEXT_PUBLIC_SUPABASE_URL: 'http://localhost:54321',
      NEXT_PUBLIC_SUPABASE_ANON_KEY: 'test-anon-key',
      SUPABASE_SERVICE_ROLE_KEY: 'test-service-role-key',
    },
  },
})
```

### 17.3 Service Unit Tests

```typescript
// src/tests/services/item.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ItemService, ServiceError } from '@/services/item.service'

// Mock Supabase client
const mockSupabase = {
  from: vi.fn().mockReturnThis(),
  select: vi.fn().mockReturnThis(),
  insert: vi.fn().mockReturnThis(),
  eq: vi.fn().mockReturnThis(),
  order: vi.fn().mockReturnThis(),
  limit: vi.fn().mockReturnThis(),
  single: vi.fn(),
}

describe('ItemService', () => {
  beforeEach(() => vi.clearAllMocks())

  it('throws LIMIT_REACHED when free user has 3 items', async () => {
    vi.spyOn(ItemService, 'countByUser').mockResolvedValue(3)

    await expect(
      ItemService.create(mockSupabase as any, 'user-1', { title: 'New item' })
    ).rejects.toThrow(ServiceError)

    await expect(
      ItemService.create(mockSupabase as any, 'user-1', { title: 'New item' })
    ).rejects.toMatchObject({ code: 'LIMIT_REACHED', status: 403 })
  })

  it('returns items ordered by created_at desc', async () => {
    const mockItems = [{ id: '1', title: 'A' }, { id: '2', title: 'B' }]
    mockSupabase.limit.mockResolvedValue({ data: mockItems, error: null })

    const result = await ItemService.list(mockSupabase as any, 'user-1')
    expect(result).toEqual(mockItems)
  })
})
```

### 17.4 RLS Policy Tests (Supabase Local)

```typescript
// src/tests/rls/item.rls.test.ts
// Requires: supabase start (local Docker)
import { createClient } from '@supabase/supabase-js'

const LOCAL_URL = 'http://localhost:54321'
const ANON_KEY  = 'eyJ...' // from supabase status

describe('Item RLS Policies', () => {
  it('user cannot read another user\'s items', async () => {
    // Create two clients with different user sessions
    const client1 = createClient(LOCAL_URL, ANON_KEY)
    const client2 = createClient(LOCAL_URL, ANON_KEY)

    await client1.auth.signInWithPassword({ email: 'user1@test.com', password: 'test1234' })
    await client2.auth.signInWithPassword({ email: 'user2@test.com', password: 'test1234' })

    // Create item as user1
    const { data: item } = await client1.from('item').insert({ title: 'Private item' }).select().single()

    // Try to read as user2
    const { data, error } = await client2.from('item').select('*').eq('id', item!.id)

    expect(data).toHaveLength(0)   // RLS blocks access
  })
})
```

### 17.5 Stripe Webhook Test Pattern

```typescript
// src/tests/api/stripe-webhook.test.ts
import { describe, it, expect, vi } from 'vitest'

// Mock stripe.webhooks.constructEvent
vi.mock('stripe', () => ({
  default: vi.fn().mockImplementation(() => ({
    webhooks: {
      constructEvent: vi.fn().mockImplementation((body, sig, secret) => {
        if (sig === 'valid-sig') return JSON.parse(body)
        throw new Error('Invalid signature')
      }),
    },
  })),
}))

describe('POST /api/stripe/webhook', () => {
  it('returns 400 for invalid signature', async () => {
    const response = await fetch('http://localhost:3000/api/stripe/webhook', {
      method: 'POST',
      headers: { 'stripe-signature': 'invalid-sig' },
      body: JSON.stringify({ type: 'checkout.session.completed' }),
    })
    expect(response.status).toBe(400)
  })
})
```

---

## 18. Caching Strategy

### 18.1 Caching Decision Tree

```
Should I cache this?
├─ Does the data change per user? → User-scoped cache (Redis key: userId:resource)
├─ Is it the same for all users? → Global cache (Redis key: resource)
├─ How often does it change?
│   ├─ Rarely (plan limits, feature flags) → Cache long (1 hour+)
│   ├─ Sometimes (user profile) → Cache medium (5-15 min)
│   └─ Frequently (notifications) → Cache short (<1 min) or skip
└─ Is stale data dangerous? (payments, auth) → NEVER cache
```

### 18.2 Next.js unstable_cache (Server Components)

```typescript
// Caches the result at build time or on first call
import { unstable_cache } from 'next/cache'

// Cache plan limits (global, changes rarely)
export const getPlanLimits = unstable_cache(
  async (plan: string) => {
    const { data } = await supabaseAdmin.from('plan_config').select('*').eq('plan', plan).single()
    return data
  },
  ['plan-limits'],        // cache key
  { revalidate: 3600 }   // 1 hour TTL
)

// Cache user dashboard (per-user, 30 seconds)
export const getDashboardData = unstable_cache(
  async (userId: string) => {
    const [items, stats] = await Promise.all([
      supabase.from('item').select('*').eq('user_id', userId).limit(10),
      supabase.from('usage_log').select('*').eq('user_id', userId),
    ])
    return { items: items.data, stats: stats.data }
  },
  ['dashboard'],
  { revalidate: 30, tags: ['dashboard'] }  // tag for manual invalidation
)
```

### 18.3 Cache Invalidation

```typescript
import { revalidateTag, revalidatePath } from 'next/cache'

// After mutation, invalidate related cache
export async function POST(request: Request) {
  // ... create item logic
  revalidateTag('dashboard')         // Invalidate all caches tagged 'dashboard'
  revalidatePath('/dashboard')       // Invalidate specific path cache
  return Response.json(item, { status: 201 })
}
```

### 18.4 Redis Cache Layer (for API Routes)

```typescript
// lib/cache.ts
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

export async function withCache<T>(
  key: string,
  ttlSeconds: number,
  fetcher: () => Promise<T>
): Promise<T> {
  const cached = await redis.get<T>(key)
  if (cached !== null) return cached

  const data = await fetcher()
  await redis.setex(key, ttlSeconds, data)
  return data
}

export async function invalidateCache(pattern: string) {
  const keys = await redis.keys(pattern)
  if (keys.length > 0) await redis.del(...keys)
}

// Usage:
const userProfile = await withCache(
  `profile:${userId}`,
  300,  // 5 minutes
  () => supabase.from('profile').select('*').eq('id', userId).single().then(r => r.data)
)
```

---

## 19. Idempotency

### 19.1 Why Idempotency Matters

```
Problem: User clicks "Subscribe" button twice (double-click, network retry)
Without idempotency: Two Stripe charges created, two subscription rows inserted

Solution: Idempotency key ensures the same operation is only executed once
```

### 19.2 Stripe Idempotency (Built-in)

```typescript
// Stripe natively supports idempotency keys
const idempotencyKey = `checkout_${userId}_${Date.now()}`

const session = await stripe.checkout.sessions.create(
  {
    // ... session params
  },
  {
    idempotencyKey,  // Stripe deduplicates calls with same key within 24h
  }
)
```

### 19.3 Custom Idempotency for Critical Operations

```sql
-- Idempotency store
CREATE TABLE idempotency_key (
  key         text PRIMARY KEY,
  user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  endpoint    text NOT NULL,
  response    jsonb,          -- cached response
  created_at  timestamptz DEFAULT now() NOT NULL
);

-- Auto-expire after 24 hours (pg_cron job)
SELECT cron.schedule('cleanup-idempotency', '0 * * * *', $$
  DELETE FROM idempotency_key WHERE created_at < now() - INTERVAL '24 hours';
$$);
```

```typescript
// lib/idempotency.ts
export async function withIdempotency<T>(
  supabase: SupabaseClient,
  key: string,
  userId: string,
  endpoint: string,
  handler: () => Promise<T>
): Promise<{ data: T; fromCache: boolean }> {
  // Check if key already exists
  const { data: existing } = await supabase
    .from('idempotency_key')
    .select('response')
    .eq('key', key)
    .eq('user_id', userId)
    .single()

  if (existing) {
    return { data: existing.response as T, fromCache: true }
  }

  // Execute operation
  const result = await handler()

  // Store result
  await supabase.from('idempotency_key').insert({
    key, user_id: userId, endpoint, response: result,
  })

  return { data: result, fromCache: false }
}

// Usage in API Route:
const idempotencyKey = request.headers.get('Idempotency-Key')
if (!idempotencyKey) {
  return Response.json({ error: 'Idempotency-Key header required' }, { status: 400 })
}

const { data, fromCache } = await withIdempotency(
  supabase, idempotencyKey, user.id, '/api/orders',
  () => OrderService.create(supabase, user.id, parsed.data)
)

return Response.json(data, {
  status: fromCache ? 200 : 201,
  headers: fromCache ? { 'Idempotent-Replayed': 'true' } : {},
})
```

---

## 20. Structured Logging & Observability

### 20.1 Structured Logging with Pino

```bash
npm install pino pino-pretty
```

```typescript
// lib/logger.ts
import pino from 'pino'

export const logger = pino({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  ...(process.env.NODE_ENV !== 'production' && {
    transport: { target: 'pino-pretty', options: { colorize: true } }
  }),
  // Never log PII — redact sensitive fields
  redact: ['body.password', 'body.card_number', 'user.email'],
})

// Structured log fields — always include:
export function createRequestLogger(request: Request, userId?: string) {
  return logger.child({
    path: new URL(request.url).pathname,
    method: request.method,
    userId,
    requestId: crypto.randomUUID(),
  })
}
```

```typescript
// Usage in API route
export async function POST(request: Request) {
  const log = createRequestLogger(request)

  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) {
    log.warn('Unauthenticated request')
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const reqLog = log.child({ userId: user.id })
  reqLog.info('Creating item')

  try {
    const item = await ItemService.create(supabase, user.id, parsed.data)
    reqLog.info({ itemId: item.id }, 'Item created successfully')
    return Response.json(item, { status: 201 })
  } catch (error) {
    reqLog.error({ error }, 'Failed to create item')
    throw error
  }
}
```

### 20.2 Uptime Monitoring

```
Recommended tools (free tiers):
├─ BetterStack (betterstack.com) — uptime + log aggregation, free tier
├─ Checkly — synthetic monitoring, API checks every 1 min, free tier
└─ Vercel Analytics — built-in, zero setup

Minimum monitoring setup for launch:
├─ Ping /api/health every 1 min
├─ Alert if response > 2s or status ≠ 200
└─ Alert if error rate > 1% in 5-min window
```

```typescript
// src/app/api/health/route.ts — simple health check endpoint
export async function GET() {
  try {
    // Verify DB is reachable
    const supabase = await createClient()
    const { error } = await supabase.from('profile').select('id').limit(1)
    if (error) throw error

    return Response.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version ?? '0.0.0',
    })
  } catch {
    return Response.json({ status: 'error' }, { status: 503 })
  }
}
```

### 20.3 Performance Metrics Pattern

```typescript
// lib/metrics.ts — simple timing utility
export function measureAsync<T>(label: string, fn: () => Promise<T>): Promise<T> {
  const start = performance.now()
  return fn().then(
    result => {
      logger.info({ label, durationMs: performance.now() - start }, 'Operation completed')
      return result
    },
    error => {
      logger.error({ label, durationMs: performance.now() - start, error }, 'Operation failed')
      throw error
    }
  )
}

// Usage:
const items = await measureAsync('ItemService.list', () => ItemService.list(supabase, userId))
```

---

## 21. Local Development Environment

### 21.1 Supabase Local Stack

```bash
# Install Supabase CLI
npm install -g supabase

# Start local Supabase (requires Docker Desktop)
supabase start

# Output:
# API URL:    http://localhost:54321
# Studio URL: http://localhost:54323  ← Visual DB editor
# Anon key:   eyJ...
# Service key: eyJ...
```

### 21.2 Environment Files

```bash
# .env.local — local development (never commit)
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...   # from supabase start output
SUPABASE_SERVICE_ROLE_KEY=eyJ...        # from supabase start output
NEXT_PUBLIC_APP_URL=http://localhost:3000
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...         # from stripe listen output
# ... other keys

# .env.test — for vitest (uses same local Supabase)
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### 21.3 Seed Data Pattern

```typescript
// supabase/seed.ts — run with: npx tsx supabase/seed.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient('http://localhost:54321', process.env.SUPABASE_SERVICE_ROLE_KEY!)

async function seed() {
  console.log('Seeding test data...')

  // Create test users via Admin API
  const { data: { user: user1 } } = await supabase.auth.admin.createUser({
    email: 'user1@test.com', password: 'test1234', email_confirm: true,
  })

  // Insert test data
  await supabase.from('item').insert([
    { user_id: user1!.id, title: 'Test Item 1', status: 'active' },
    { user_id: user1!.id, title: 'Test Item 2', status: 'draft' },
  ])

  console.log('Seed complete.')
}

seed().catch(console.error)
```

### 21.4 Local Development Workflow

```bash
# Terminal 1: Supabase local
supabase start

# Terminal 2: Stripe webhook forwarding
stripe login
stripe listen --forward-to localhost:3000/api/stripe/webhook
# Copy "Signing secret" → STRIPE_WEBHOOK_SECRET in .env.local

# Terminal 3: Next.js dev server
npm run dev

# Supabase Studio (visual DB editor):
open http://localhost:54323
```

---

*Knowledge base for Axel — Full-Stack Backend*
*Pairs with: `backend-guide.md` (non-negotiable rules)*
