# Indie Maker Backend Guide

Supabase + Next.js API Routes patterns for indie MVPs.
DB design, RLS policies, REST conventions, security, and Stripe integration.

---

## Non-Negotiable Rules

Rules every senior backend engineer enforces — not negotiable regardless of deadline.
Sources: Google Cloud API Design Guide, OWASP Top 10:2025, Supabase Docs, PostgreSQL Best Practices.

### REST API Design
1. **Resources are nouns, never verbs** — URL paths identify resources (things), not actions. Use HTTP methods to express the action. `GET /users` ✅ `GET /getUsers` ❌ `DELETE /users/123` ✅ `POST /deleteUser` ❌.
2. **HTTP methods carry semantic meaning — always** — GET: read-only, side-effect-free, cacheable. POST: create, not idempotent. PUT/PATCH: update (PUT replaces, PATCH modifies). DELETE: remove. Using GET to mutate state is a critical security vulnerability (CSRF, caching bugs).
3. **Status codes communicate outcomes precisely** — 200 (OK), 201 (Created — always on successful POST), 204 (No Content — DELETE success), 400 (Bad Request — validation failure), 401 (Unauthenticated), 403 (Unauthorized — authenticated but lacking permission), 404 (Not Found), 422 (Unprocessable Entity — semantic error), 429 (Rate Limited), 500 (Server Error). Using 200 for everything breaks clients and monitoring.
4. **Consistent error response shape** — Every error response follows the same schema: `{ error: string, code: string, status: number, details?: object }`. Clients must be able to parse errors programmatically without inspecting message strings.
5. **Never expose internals in error messages** — Stack traces, database column names, table structures, file paths — never in API responses. Log them server-side (Sentry). Return user-friendly messages to clients.

### Database Design
6. **Every table has a surrogate primary key** — Use `uuid DEFAULT gen_random_uuid()` as PK. Never expose sequential integers as primary keys (information disclosure, enumeration attacks). UUIDs are safe to use in URLs and APIs.
7. **Every user-owned table has `user_id` with CASCADE** — `user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE`. Missing this means orphaned data when users delete their accounts.
8. **Index every foreign key column** — PostgreSQL does not automatically index FK columns. Every `user_id`, `organization_id`, or relationship FK needs an explicit index. Missing FK indexes cause sequential scans and O(n) query times as data grows.
9. **Index columns used in WHERE, ORDER BY, JOIN** — Any column frequently used in filtering, sorting, or joining needs an index. Use `EXPLAIN ANALYZE` before and after adding indexes in production.
10. **snake_case for all identifiers** — Table names, column names, function names in snake_case. Use singular table names (`user`, `item`, `subscription`). Boolean columns prefixed with `is_` or `has_`. This convention is universal in PostgreSQL and prevents collisions with SQL reserved words.
11. **NOT NULL with meaningful defaults** — Every column should be NOT NULL unless null has explicit semantic meaning. Use `DEFAULT now()` for timestamps, `DEFAULT false` for booleans, `DEFAULT 'active'` for status fields. Nulls proliferate complexity.
12. **created_at + updated_at on every table** — `created_at timestamptz DEFAULT now() NOT NULL`. `updated_at timestamptz DEFAULT now() NOT NULL` with an automatic trigger. These fields cost nearly nothing and are invaluable for debugging, auditing, and analytics.

### Security (OWASP Top 10:2025)
13. **RLS enabled before any table is exposed — no exceptions** — `ALTER TABLE [table] ENABLE ROW LEVEL SECURITY` is executed before any application code reads from or writes to the table. A table without RLS is accessible to all authenticated users.
14. **RLS policies use `auth.uid()`, never `user_metadata`** — User metadata is user-modifiable. `auth.uid()` is set by Supabase Auth and cannot be spoofed. Never write RLS policies that trust `user_metadata` fields.
15. **Service Role Key is server-only — never client-accessible** — The Service Role Key bypasses RLS entirely. Never prefix it with `NEXT_PUBLIC_`. Never expose it in client-side code. Always use the Anon Key in browser clients.
16. **All user input validated server-side with Zod** — Client-side validation is UX. Server-side validation is security. Client validation can be bypassed in milliseconds. Both are required; server-side is authoritative.
17. **Zero SQL string concatenation — parameterized queries only** — String-concatenated SQL queries enable SQL injection. Supabase's query builder uses parameterized queries automatically. If writing raw SQL, use `$1, $2` parameters. This rule has zero exceptions.
18. **HTTPS everywhere — no plaintext HTTP in production** — All cookies, JWTs, and sensitive data transmitted over HTTPS only. Stripe requires it. Supabase Auth requires it. CORS headers restricted to trusted origins.
19. **Authentication failures don't leak user existence** — "Invalid email or password" — not "Email not found" or "Password incorrect." Distinguishing between the two enables user enumeration attacks.
20. **Rate limiting on sensitive endpoints** — Auth endpoints (login, signup, password reset), payment endpoints, and any endpoint accepting user-provided content must have rate limiting. Return 429 with `Retry-After` header.

### Error Handling
21. **Fail fast at validation** — Validate input at the top of every route handler. Return 400/422 immediately on validation failure. Don't proceed to database operations with invalid data.
22. **Log server errors with context** — Log errors with: user_id (if authenticated), request path, request body (sanitized, no PII), timestamp, error message, stack trace. Use Sentry or equivalent.
23. **Graceful degradation for external services** — When Stripe, Resend, or other external services fail, fail gracefully. Return 503 with a user-friendly message. Implement retry logic with exponential backoff for background operations.

### Query Performance
24. **Paginate all list endpoints** — No endpoint returns unbounded result sets. Use cursor-based pagination (`WHERE created_at < $cursor ORDER BY created_at DESC LIMIT 20`) for infinite scroll, or offset-based for numbered pages. Default limit: 20, max limit: 100.
25. **Select only needed columns** — `.select('id, title, created_at')` not `.select('*')`. Selecting all columns transfers unnecessary data, prevents index-only scans, and leaks internal fields to clients. Explicit selects also serve as documentation.
26. **N+1 queries are bugs** — If a loop executes a query per iteration, it's an N+1. Use Supabase joins (`.select('*, comments(*)')`) or batch queries. Detect N+1s by counting queries per request during development (log query count per route).
27. **Explain before optimizing** — Run `EXPLAIN ANALYZE` on slow queries before adding indexes. Premature indexing adds write overhead. Target: single-table queries < 5ms, joined queries < 20ms. Monitor query times in production.

### Testing Strategy
28. **Every API route has a test** — Test the route handler directly: valid input returns correct status + body, invalid input returns 400/422, unauthenticated request returns 401, unauthorized access returns 403. Use Vitest + Supabase local.
29. **Database constraints are tested** — Test that CHECK constraints reject invalid data, NOT NULL prevents missing fields, FK constraints prevent orphaned references, and RLS policies block cross-user access. If the constraint matters, it has a test.
30. **Webhook handlers have integration tests** — Stripe webhooks are the most critical backend code. Test with mock Stripe events: checkout.session.completed creates subscription, subscription.deleted downgrades plan, invalid signature returns 400.

### Resilience Patterns
31. **Idempotent mutations** — POST endpoints that create resources should handle duplicate submissions gracefully. Use idempotency keys (Stripe provides these), unique constraints, or `INSERT ... ON CONFLICT DO NOTHING`. A user double-clicking "Pay" must not be charged twice.
32. **Webhook retry safety** — Stripe retries failed webhooks. Webhook handlers must be idempotent: check if the action was already processed before executing. Use `stripe_sub_id` unique constraint or an event log table to prevent double-processing.
33. **Timeout boundaries for external calls** — Set explicit timeouts on all external API calls (Stripe, Resend, third-party APIs). Default: 10s for payment APIs, 5s for email, 30s for AI/LLM calls. A missing timeout blocks the event loop indefinitely.

### Observability
34. **Structured logging, not string concatenation** — Log as structured objects: `log.error({ route: '/api/items', userId, error: err.message, duration_ms })`. Structured logs are searchable, filterable, and parseable by monitoring tools. Never log `"Error: " + err`.
35. **Request duration tracking** — Measure and log the duration of every API request. Set alerts for p95 response time > 500ms. Track separately: DB query time, external API time, total response time. Slow endpoints are bugs.
36. **Health check endpoint** — `GET /api/health` returns 200 with `{ status: 'ok', db: 'connected', timestamp }`. Used by uptime monitors (BetterStack) and deployment health checks. Include DB connectivity check (simple query).

---

## Supabase Project Setup

### Initial Configuration

```
1. supabase.com → New Project (choose region closest to users)
2. Copy: Project URL + Anon Key → .env.local
3. Authentication → Providers → Email: enabled
4. Authentication → URL Configuration:
   - Site URL: http://localhost:3000 (update to production URL later)
   - Redirect URLs: http://localhost:3000/auth/callback
```

### Base Schema (apply to every project)

```sql
-- Run in Supabase SQL Editor

-- Updated-at auto-trigger function (create once, reuse everywhere)
CREATE OR REPLACE FUNCTION handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- User profiles table
CREATE TABLE profile (
  id          uuid REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email       text NOT NULL,
  full_name   text,
  avatar_url  text,
  created_at  timestamptz DEFAULT now() NOT NULL,
  updated_at  timestamptz DEFAULT now() NOT NULL
);

CREATE TRIGGER profile_updated_at
  BEFORE UPDATE ON profile
  FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

ALTER TABLE profile ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON profile FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
  ON profile FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

-- Subscriptions table (for paid products)
CREATE TABLE subscription (
  id                  uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id             uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  stripe_customer_id  text UNIQUE,
  stripe_sub_id       text UNIQUE,
  plan                text NOT NULL DEFAULT 'free'
                        CHECK (plan IN ('free', 'pro')),
  status              text NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'canceled', 'past_due')),
  current_period_end  timestamptz,
  created_at          timestamptz DEFAULT now() NOT NULL,
  updated_at          timestamptz DEFAULT now() NOT NULL
);

CREATE TRIGGER subscription_updated_at
  BEFORE UPDATE ON subscription
  FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

ALTER TABLE subscription ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own subscription"
  ON subscription FOR SELECT USING (auth.uid() = user_id);

-- Auto-create profile and subscription on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profile (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name'
  );
  INSERT INTO subscription (user_id) VALUES (NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### Feature Table Template

```sql
-- Template for any user-owned resource
CREATE TABLE item (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at  timestamptz DEFAULT now() NOT NULL,
  updated_at  timestamptz DEFAULT now() NOT NULL,

  -- Feature-specific columns
  title       text NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
  content     text,
  status      text NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'active', 'archived'))
);

-- Index on FK (required)
CREATE INDEX item_user_id_idx ON item (user_id);
-- Index for common sort (if sorted by created_at frequently)
CREATE INDEX item_created_at_idx ON item (created_at DESC);

CREATE TRIGGER item_updated_at
  BEFORE UPDATE ON item
  FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

ALTER TABLE item ENABLE ROW LEVEL SECURITY;

-- Standard CRUD policies
CREATE POLICY "Users view own items"
  ON item FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users create own items"
  ON item FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users update own items"
  ON item FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users delete own items"
  ON item FOR DELETE USING (auth.uid() = user_id);
```

---

## API Route Patterns

### Standard GET + POST Handler

```typescript
// src/app/api/items/route.ts
import { createClient } from '@/lib/supabase/server'
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const createItemSchema = z.object({
  title:   z.string().min(1).max(200),
  content: z.string().optional(),
})

export async function GET() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json(
      { error: 'Unauthorized', code: 'AUTH_REQUIRED', status: 401 },
      { status: 401 }
    )
  }

  const { data, error } = await supabase
    .from('item')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    console.error('[GET /api/items]', error)
    return NextResponse.json(
      { error: 'Failed to fetch items', code: 'DB_ERROR', status: 500 },
      { status: 500 }
    )
  }

  return NextResponse.json(data)
}

export async function POST(request: NextRequest) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json(
      { error: 'Unauthorized', code: 'AUTH_REQUIRED', status: 401 },
      { status: 401 }
    )
  }

  const body = await request.json()
  const parsed = createItemSchema.safeParse(body)

  if (!parsed.success) {
    return NextResponse.json(
      { error: 'Validation failed', code: 'VALIDATION_ERROR', status: 400, details: parsed.error.flatten() },
      { status: 400 }
    )
  }

  const { data, error } = await supabase
    .from('item')
    .insert({ ...parsed.data, user_id: user.id })
    .select()
    .single()

  if (error) {
    console.error('[POST /api/items]', error)
    return NextResponse.json(
      { error: 'Failed to create item', code: 'DB_ERROR', status: 500 },
      { status: 500 }
    )
  }

  return NextResponse.json(data, { status: 201 })
}
```

### Pro Plan Gate Pattern

```typescript
// Check subscription before allowing Pro features
async function requireProPlan(userId: string, supabase: SupabaseClient) {
  const { data: sub } = await supabase
    .from('subscription')
    .select('plan, status')
    .eq('user_id', userId)
    .single()

  if (!sub || sub.plan !== 'pro' || sub.status !== 'active') {
    return NextResponse.json(
      { error: 'Pro subscription required', code: 'UPGRADE_REQUIRED', status: 403 },
      { status: 403 }
    )
  }
  return null  // null = passed
}
```

---

## Stripe Integration

### Checkout Session

```typescript
// src/app/api/stripe/checkout/route.ts
import Stripe from 'stripe'
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized', code: 'AUTH_REQUIRED', status: 401 }, { status: 401 })
  }

  const { data: sub } = await supabase
    .from('subscription')
    .select('stripe_customer_id')
    .eq('user_id', user.id)
    .single()

  const session = await stripe.checkout.sessions.create({
    customer: sub?.stripe_customer_id ?? undefined,
    customer_email: sub?.stripe_customer_id ? undefined : user.email,
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [{ price: process.env.STRIPE_PRO_PRICE_ID!, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?success=true`,
    cancel_url:  `${process.env.NEXT_PUBLIC_APP_URL}/pricing?canceled=true`,
    metadata: { user_id: user.id },
  })

  return NextResponse.json({ url: session.url })
}
```

### Webhook Handler

```typescript
// src/app/api/stripe/webhook/route.ts
import Stripe from 'stripe'
import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

// Service Role client — bypasses RLS, server-only
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(request: NextRequest) {
  const body = await request.text()
  const sig  = request.headers.get('stripe-signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return NextResponse.json({ error: 'Invalid webhook signature' }, { status: 400 })
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.CheckoutSession
      const userId  = session.metadata?.user_id
      if (!userId) break
      await supabaseAdmin.from('subscription').update({
        stripe_customer_id: session.customer as string,
        stripe_sub_id:      session.subscription as string,
        plan:               'pro',
        status:             'active',
      }).eq('user_id', userId)
      break
    }

    case 'customer.subscription.updated': {
      const sub = event.data.object as Stripe.Subscription
      await supabaseAdmin.from('subscription').update({
        status:             sub.status,
        current_period_end: new Date(sub.current_period_end * 1000).toISOString(),
      }).eq('stripe_sub_id', sub.id)
      break
    }

    case 'customer.subscription.deleted': {
      const sub = event.data.object as Stripe.Subscription
      await supabaseAdmin.from('subscription').update({
        plan:   'free',
        status: 'canceled',
      }).eq('stripe_sub_id', sub.id)
      break
    }
  }

  return NextResponse.json({ received: true })
}
```

---

## Architecture Decision Guide

| Scenario | Decision | Reason |
|----------|---------|--------|
| Data owned by a user | RLS + anon client | Most secure; least privilege |
| Admin operations (Stripe webhook, cron) | Service Role client | RLS bypass required; server-only |
| Complex multi-table transactions | Supabase DB function (plpgsql) | Atomic execution, avoids partial updates |
| Real-time data push | Supabase Realtime | WebSocket subscription managed by Supabase |
| File storage | Supabase Storage + RLS bucket policies | Integrated auth, CDN included |
| Full-text search | Supabase `websearch_to_tsquery` | Built-in, no extra service needed for MVP |
| Background jobs | Supabase Edge Functions + pg_cron | No separate infrastructure |

---

## Quick Reference Checklist

Before delivering any API or database output:

**Security**
- [ ] RLS enabled on every table (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`)
- [ ] Service Role Key used only in server files (no `NEXT_PUBLIC_` prefix)
- [ ] All user input validated with Zod before DB operation
- [ ] No SQL string concatenation anywhere
- [ ] Error responses contain no stack trace or DB schema
- [ ] Auth check at top of every protected route handler

**Database**
- [ ] FK columns have explicit indexes
- [ ] `updated_at` trigger exists on every mutable table
- [ ] HTTP status codes are semantically correct
- [ ] List endpoints are paginated (no unbounded queries)
- [ ] `.select()` specifies columns, not `*`

**Performance**
- [ ] No N+1 queries (use joins or batch)
- [ ] External API calls have explicit timeouts
- [ ] Mutations are idempotent (safe on retry/double-click)

**Testing**
- [ ] Every API route has tests (valid, invalid, auth)
- [ ] Webhook handlers tested with mock events
- [ ] DB constraints tested (RLS, CHECK, FK)

**Observability**
- [ ] Errors logged with context (userId, route, duration)
- [ ] `/api/health` endpoint exists
- [ ] Request duration tracked
