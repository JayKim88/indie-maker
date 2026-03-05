# Indie Maker Infrastructure Guide

Reference for the Sam (Platform Engineer) agent.
Covers security, cost, observability, performance, incident response, CI/CD, and deployment
for Vercel + Supabase + Stripe indie MVPs.

Sources: The Twelve-Factor App (Heroku), OWASP Top 10, Google SRE Book,
AWS Well-Architected Framework, NIST Cybersecurity Framework.

---

## Non-Negotiable Rules

Rules a Platform Engineer enforces before any production deployment.
Violation of any Must-Have rule blocks go-live.

### The 12-Factor App (Required Compliance)

1. **Factor I — Codebase**: One codebase in version control, multiple deployments. Never branch by environment (no `prod` branch). Feature branches only.
2. **Factor II — Dependencies**: All dependencies explicitly declared in `package.json`. Lock file (`package-lock.json` or `pnpm-lock.yaml`) committed to git. Zero reliance on system-global packages.
3. **Factor III — Config in environment variables**: All environment-specific config (API keys, URLs, feature flags) injected as environment variables. Never hardcoded in source. `.env.local` for development (git-ignored). `.env.example` for documentation of required vars.
4. **Factor IV — Backing services as attached resources**: Database (Supabase), email (Resend), payments (Stripe) are attached resources — swappable by changing an env var, not code changes.
5. **Factor V — Strict build/release/run separation**: Build (compile, asset generation) → Release (build + config) → Run (execute). Each stage is immutable. A Vercel deployment represents this automatically.
6. **Factor VI — Stateless processes**: The app process stores no in-memory state between requests. All state lives in the database (Supabase). Sticky sessions are never used. Horizontal scaling is possible at any time.
7. **Factor VII — Port binding**: Next.js is self-contained. No external application server dependency. The app exports its own HTTP service.
8. **Factor VIII — Concurrency**: Scale out by running more instances (Vercel handles this). Never solve scaling by making a single instance larger.
9. **Factor IX — Disposability**: Fast startup. Graceful shutdown (complete in-flight requests on SIGTERM). Robust against sudden crashes.
10. **Factor X — Dev/prod parity**: Same Supabase plan type in dev and prod. Same Node.js version. Same npm packages. "Works on my machine" is a production bug in waiting.
11. **Factor XI — Logs as event streams**: Write logs to stdout/stderr. Never manage log files. Let the platform (Vercel, Sentry) aggregate, route, and store logs.
12. **Factor XII — Admin processes**: Database migrations, one-off scripts run as standalone processes against the same codebase. Never run ad-hoc admin code in production routes.

### Security Engineering (Pre-Launch Mandatory)

13. **Secrets never in git — enforce with pre-commit** — No API key, password, JWT secret, or service role key ever touches version control. Add a pre-commit hook or use `detect-secrets` / `gitleaks` to catch accidental commits before they happen.
14. **Least privilege for every service key** — The browser client uses the Anon Key (RLS enforced). Server code uses the Service Role Key only when RLS bypass is explicitly required. Stripe webhooks use the Webhook Secret only for signature verification. Never grant more permissions than the current operation requires.
15. **HTTPS + security headers enforced everywhere** — No HTTP in production. HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy all set in `vercel.json`. Any HTTP endpoint is a credential-theft risk.
16. **RLS on every public-facing table** — `ENABLE ROW LEVEL SECURITY` before any Supabase table is accessible from the client. No table without a policy is acceptable. Audit by checking `pg_tables` for tables with `rowsecurity = false`.
17. **Rate limiting on all auth and mutation endpoints** — Authentication routes (`/api/auth/*`) and any state-changing API routes must have rate limiting. Absence invites brute-force and API abuse. Use Vercel Edge Middleware or Upstash Redis for rate limiting.
18. **Content Security Policy (CSP) configured** — CSP header blocks inline scripts and unauthorized origins. Prevents XSS escalation. At minimum: `default-src 'self'`, whitelist only explicitly needed CDN domains.
19. **OWASP Top 10 review before launch** — Check A01 (broken access control), A03 (injection via Supabase queries), A05 (misconfiguration), A07 (auth failures) at minimum. These are the top attack vectors for web apps.
20. **Dependencies audited and pinned** — Run `npm audit` before every production deploy. Fix Critical and High severity vulnerabilities before launch. Secrets rotation documented: API keys quarterly, webhook secrets on compromise.

### Cost Engineering (Surprise Bill Prevention)

21. **Know your free tier ceilings before go-live** — Supabase free: 500MB DB, 1GB storage, 5GB bandwidth, 50K MAU. Vercel free: 100GB bandwidth/month, 100 serverless function executions/day limit on Hobby. Sentry free: 5K errors/month. Exceeding without warning = instant bill.
22. **Cost simulation at 1K, 10K, 100K users** — Before launching, estimate monthly cost at each scale milestone. If 10K MAU would exceed your runway, the architecture or pricing needs to change before launch, not after.
23. **Usage-based service monitoring** — Set Supabase and Vercel usage alerts at 80% of free tier limits. Unmonitored usage spikes cause bill shock. Use billing alert emails in every service dashboard.
24. **Rollback has a cost plan** — Rolling back a bad migration or deployment should not incur extra charges. Vercel instant rollback is free. Supabase schema rollback requires a migration file — plan it before you need it.

### Observability (Day-One Non-Negotiable)

25. **Error tracking before first user** — Sentry (or equivalent) configured and verified to receive at least one test error before go-live. An unmonitored production error is an invisible outage. The first error should be caught by monitoring, not a user complaint.
26. **Uptime monitoring registered at launch** — UptimeRobot or equivalent checking from multiple regions. Alert threshold: 2 failed checks. Notification: email + optional Slack. Cover both `/` and `/api/health`.
27. **Structured logging from day one** — All server logs in JSON with consistent fields: `{ timestamp, level, message, user_id, request_id, duration_ms, error_code }`. Unstructured logs cannot be queried, alerted on, or used for debugging at scale.
28. **Meaningful alerts, not noise** — Alert on error rate > 1% over 5 minutes, not on every single error. Alert on p95 response time > 2s, not on individual slow requests. Alert fatigue kills monitoring. Every alert must require action.
29. **SLO defined before launch** — Set measurable targets: availability ≥ 99.5% (allows ~3.6 hours/month downtime), p95 API response < 500ms. SLOs make incident severity objective, not subjective.
30. **Analytics baseline active** — Vercel Analytics + Speed Insights embedded before launch. Acquisition data from day one is invaluable; retrofitting analytics loses early cohort data forever.

### Performance Engineering

31. **Core Web Vitals targets enforced** — LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1. Measure on production URL with Lighthouse CI or Vercel Speed Insights after every deploy. Google uses these for search ranking.
32. **DB queries reviewed for N+1 before launch** — Every page that lists records must be audited for N+1 query patterns. One Supabase call per list item = N+1 = exponential latency. Use `select('*, related_table(*)')` to join eagerly.
33. **Indexes on every FK column and high-frequency WHERE clause** — A table with 10K rows and no index on a filter column causes a full table scan on every request. Run `EXPLAIN ANALYZE` on all queries that touch large tables.
34. **Edge vs. Serverless deployment decided consciously** — Edge Functions: <1ms cold start, global, limited Node.js APIs. Serverless Functions: full Node.js, ~100ms cold start, single region by default. Route latency-critical paths (auth checks, API gateway) to Edge; heavy computation to Serverless.

### Deployment

35. **No production secrets in Preview deployments** — Vercel Preview environments use test/staging secrets. `STRIPE_SECRET_KEY` must be `sk_test_` in Preview and `sk_live_` in Production only. Verify this in Vercel Dashboard → Settings → Environment Variables → scope.
36. **Verify webhook signatures — always** — Stripe webhooks without `stripe.webhooks.constructEvent()` are a critical vulnerability. An attacker can send fake events (fake payments, fake upgrades). This check takes 3 lines to add and blocks an entire attack class.
37. **Database migrations are versioned and tested** — Every schema change is a migration file in `supabase/migrations/`. Migrations run in staging before production. Backward-compatible changes only: add columns before removing, never rename columns in place.
38. **Rollback plan documented before every deploy** — Before deploying to production, the engineer must be able to answer: "If this deploy breaks production, how do I roll back in under 5 minutes?" Vercel: instant rollback button. Supabase: reverting migration requires a compensating migration file.

### Incident Response

39. **Runbook for the top 3 failure modes** — Before launch, write a one-page runbook for each: (1) Supabase connection failure, (2) Stripe webhook processing failure, (3) Vercel deploy failure. Runbook format: Symptom → Root cause → Recovery steps → Escalation. Written calmly before an incident, not during one.
40. **RTO and RPO defined** — Recovery Time Objective (RTO): how long until service is restored — target < 30 minutes for indie MVP. Recovery Point Objective (RPO): how much data loss is acceptable — Supabase daily backup means max 24h RPO unless custom backup schedule is set. Know these numbers; they determine your backup strategy.

---

## Architecture Decision Guide

### Edge vs. Serverless Function

| Criterion | Edge Function | Serverless Function |
|-----------|--------------|---------------------|
| Cold start | ~0ms | ~100-500ms |
| Region | Global (all regions) | Single region (default) |
| Node.js APIs | Limited (Web APIs only) | Full Node.js |
| Max duration | 30s | 60s (Hobby), 300s (Pro) |
| Use for | Auth middleware, A/B routing, geo-redirect | DB queries, Stripe, email, heavy compute |

**Rule**: Default to Serverless. Move to Edge only when latency is the bottleneck and you've verified Edge API compatibility.

---

### Supabase RLS Policy Patterns

```sql
-- Pattern 1: User owns their own rows (most common)
CREATE POLICY "Users can only access their own data"
ON public.todos
FOR ALL
USING (auth.uid() = user_id);

-- Pattern 2: Public read, owner write
CREATE POLICY "Public profiles are viewable"
ON public.profiles FOR SELECT USING (true);

CREATE POLICY "Users can update own profile"
ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Pattern 3: Subscription-gated access
CREATE POLICY "Pro users only"
ON public.premium_content FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.subscriptions
    WHERE user_id = auth.uid()
    AND status = 'active'
    AND plan = 'pro'
  )
);

-- Audit: find tables with RLS disabled (run in Supabase SQL editor)
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = false;
```

---

### Rate Limiting with Upstash Redis

```typescript
// src/middleware.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'
import { NextRequest, NextResponse } from 'next/server'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
})

export async function middleware(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1'
  const { success, limit, reset, remaining } = await ratelimit.limit(ip)

  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests', code: 'RATE_LIMITED' },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': new Date(reset).toISOString(),
        },
      }
    )
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/api/auth/:path*', '/api/:path*'],
}
```

---

### Cost Simulation Template

```
Monthly cost at scale — fill before launch:

Service             Free ceiling    1K MAU    10K MAU   100K MAU
────────────────────────────────────────────────────────────────
Supabase DB         500MB           Free      Free      $25
Supabase Auth       50K MAU         Free      Free      $25
Vercel bandwidth    100GB           Free      Free      $20+
Sentry errors       5K/mo           Free      $26       $26+
Resend emails       3K/mo           Free      $20       $20+
────────────────────────────────────────────────────────────────
TOTAL                               ~$0       ~$0       ~$90+

Revenue needed to cover infra at 100K MAU:
  If Pro plan = $19/mo → need ~5 Pro subscribers to break even on infra
```

---

### Rollback Decision Tree

```
Deploy went live → Issue detected?
  │
  ├─ Yes: Is it a code bug (not data)?
  │       ├─ Yes → Vercel Dashboard → Deployments → Previous → Promote to Production
  │       │         (instant, zero downtime)
  │       └─ No: Is it a schema migration?
  │               ├─ Yes → Write compensating migration:
  │               │         supabase migration new revert_[change_name]
  │               │         supabase db push
  │               └─ No: Is it a config/env var?
  │                       └─ Yes → Update env var in Vercel → Redeploy (auto)
  │
  └─ No → Monitor for 30 minutes before declaring stable
```

---

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      # Type check
      - run: npx tsc --noEmit

      # Lint
      - run: npm run lint

      # Secrets scan — block if any secret pattern found
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # Tests (if present)
      - run: npm test --if-present

  # Preview deploy happens automatically via Vercel GitHub integration
  # Production deploy: push to main → Vercel auto-deploys
```

---

---

## Vercel Deployment

### Initial Setup

```bash
# Option 1: Vercel CLI
npm install -g vercel
vercel login
vercel                  # First deploy (interactive setup)
vercel --prod           # Production deploy

# Option 2: GitHub Integration (recommended)
# vercel.com → Import → Connect GitHub → Auto-deploy on push to main
```

### vercel.json Configuration

```json
{
  "functions": {
    "src/app/api/stripe/webhook/route.ts": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=63072000; includeSubDomains; preload"
        }
      ]
    }
  ]
}
```

### Environment Variables by Context

```bash
# Development (.env.local — git-ignored)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...  # from: stripe listen --print-secret
STRIPE_PRO_PRICE_ID=price_...
RESEND_API_KEY=re_...
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Production (Vercel Dashboard → Settings → Environment Variables)
# Same keys, different values:
STRIPE_SECRET_KEY=sk_live_...     ⚠️ Live key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...   ⚠️ Production webhook secret (different from local)
NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

---

## Custom Domain Setup

```
1. Purchase domain: Cloudflare Domains (at-cost) or Namecheap (~$10-15/yr)

2. Vercel Dashboard → Settings → Domains → Add Domain
   Enter: yourdomain.com

3. DNS Records (set in domain registrar's DNS panel):
   Type: A     Name: @    Value: 76.76.21.21
   Type: CNAME Name: www  Value: cname.vercel-dns.com

4. SSL/TLS: Vercel provisions Let's Encrypt certificate automatically
   Allow 10-30 minutes for DNS propagation + cert issuance

5. Update Supabase:
   Authentication → URL Configuration
   Site URL: https://yourdomain.com
   Redirect URLs: https://yourdomain.com/auth/callback

6. Update environment variable:
   NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

---

## Stripe Production Setup

### Webhook Configuration

```
1. Stripe Dashboard → Developers → Webhooks → + Add endpoint
   Endpoint URL: https://yourdomain.com/api/stripe/webhook

2. Select events:
   ✅ checkout.session.completed
   ✅ customer.subscription.updated
   ✅ customer.subscription.deleted
   ✅ invoice.payment_failed
   ✅ invoice.payment_succeeded

3. Click "Add endpoint" → Copy "Signing secret"
   → STRIPE_WEBHOOK_SECRET in Vercel environment variables

4. Switch from test to live:
   pk_test_ → pk_live_  (NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
   sk_test_ → sk_live_  (STRIPE_SECRET_KEY)

5. Test with a real $1 charge → verify it appears in Supabase subscription table
   → refund immediately via Stripe Dashboard
```

### Pre-Launch Stripe Checklist

```
- [ ] Stripe account fully verified (bank account connected)
- [ ] Business information complete (required for payouts)
- [ ] Products and prices created in Live mode (not Test)
- [ ] Live webhook endpoint created and tested
- [ ] STRIPE_WEBHOOK_SECRET updated to live webhook secret
- [ ] Test purchase successful with real card
- [ ] Refund process tested
- [ ] Customer portal configured (for self-service cancellation)
```

---

## Monitoring Setup

### Sentry Error Tracking (Free Tier)

```bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
# Follow prompts — auto-configures sentry.client.config.ts and sentry.server.config.ts
```

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,   // 10% of transactions traced (save quota)
  environment: process.env.NODE_ENV,
  beforeSend(event) {
    // Remove PII from events
    if (event.user) {
      delete event.user.ip_address
    }
    return event
  },
})
```

### Vercel Analytics (Zero-Config)

```typescript
// src/app/layout.tsx
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
```

### UptimeRobot Setup

```
1. uptimerobot.com → Free account → New Monitor
   Type: HTTP(s)
   URL: https://yourdomain.com
   Check interval: 5 minutes
   Alert contacts: your email

2. Add monitors for key pages:
   - / (landing page)
   - /api/health (create a simple health endpoint)

3. Embed status badge in your README or footer (optional)
```

### Simple Health Endpoint

```typescript
// src/app/api/health/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: process.env.NEXT_PUBLIC_APP_VERSION ?? 'unknown',
  })
}
```

---

## Email with Resend

```bash
npm install resend
```

```typescript
// src/lib/email.ts
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function sendWelcomeEmail(to: string, name: string) {
  await resend.emails.send({
    from: 'hello@yourdomain.com',   // requires domain verification
    to,
    subject: `Welcome to [Product]!`,
    html: `
      <h1>Welcome, ${name}!</h1>
      <p>You're now signed up for [Product]. Here's what you can do next:</p>
      <ul>
        <li><a href="${process.env.NEXT_PUBLIC_APP_URL}/dashboard">Go to your dashboard</a></li>
      </ul>
    `,
  })
}
```

```
Domain Verification in Resend:
1. Resend Dashboard → Domains → Add Domain → yourdomain.com
2. Add DNS records (SPF, DKIM, DMARC) to your domain registrar
3. Wait for verification (5-30 minutes)
4. From address: anything@yourdomain.com
```

---

## Legal Documents

### Minimum Required (before accepting payments)

```markdown
<!-- /privacy — required by GDPR, CCPA, Apple/Google stores -->
# Privacy Policy

Last updated: [Date]

## Information We Collect
- Email address (account creation, login)
- Usage data (pages visited, features used — via Vercel Analytics)
- Payment information (processed by Stripe directly; we never store card data)

## How We Use Information
- Provide and improve the service
- Send transactional emails (account confirmation, receipts)
- Contact you about your account

## Third-Party Services
- **Supabase** (data storage) — USA
- **Stripe** (payment processing) — USA
- **Vercel** (hosting) — USA
- **Resend** (email delivery) — USA

## Data Retention
Account data retained until account deletion request.

## Your Rights
You may request data deletion by emailing: privacy@yourdomain.com

## Cookies
Session cookies only (for authentication). No tracking cookies.

---

<!-- /terms — required before charging users -->
# Terms of Service

Last updated: [Date]

## Service Description
[Product name] provides [one-line description].

## Acceptable Use
- No abuse, scraping, or reverse engineering
- No use for illegal purposes
- One account per person

## Payments and Refunds
Subscriptions billed monthly. Cancel anytime. [Refund policy].

## Liability Limitation
Service provided "as is." We are not liable for data loss or indirect damages.

## Account Termination
We may terminate accounts that violate these terms.

## Contact
legal@yourdomain.com
```

---

## D14 Deploy Day QA Checklist

Work through all 4 sections before marking the launch as ready.

### [1/4] Core Flow Testing

```
- [ ] Sign up with new email → confirmation email received
- [ ] Click confirmation link → onboarding / dashboard loads
- [ ] Sign in with existing account → dashboard loads
- [ ] Complete core user flow E2E (the one scenario from prd-lean.md)
- [ ] Test payment: card 4242 4242 4242 4242 → subscription activates
- [ ] Pro feature accessible after payment
- [ ] Unauthenticated access to /dashboard → redirects to /login
- [ ] Invalid login credentials → error message, no crash
```

### [2/4] Infrastructure Verification

```
- [ ] Custom domain loads: https://yourdomain.com
- [ ] SSL certificate valid (no browser warning)
- [ ] All environment variables set to production values (not test keys)
- [ ] Vercel build: zero errors in Build Logs
- [ ] Stripe Live webhook: test event received successfully (Stripe Dashboard → Webhooks → Send test event)
- [ ] Supabase Auth: Site URL and Redirect URLs updated to production domain
- [ ] Sentry: test error captured (throw an error and verify it appears in Sentry)
- [ ] UptimeRobot: monitor registered and showing "UP"
```

### [3/4] Performance & UX

```
- [ ] Lighthouse Performance score ≥ 70 (run on production URL)
- [ ] Mobile layout at 375px: no horizontal scroll, all text readable
- [ ] All interactive elements have visible focus states
- [ ] Loading states present for all async operations
- [ ] Empty states present for all data-driven components
- [ ] OG image set (appears correctly when URL shared on Twitter/Slack)
- [ ] Favicon set
- [ ] 404 page exists and is helpful
```

### [4/4] Legal & Compliance

```
- [ ] /privacy page accessible and linked from footer
- [ ] /terms page accessible and linked from footer
- [ ] Subscription cancellation method documented (self-service or email)
- [ ] Cookie consent (if targeting EU users)
- [ ] Contact email functional (hello@yourdomain.com)
```

---

## Cost Structure (MVP Scale)

| Service | Free Tier | Paid Threshold |
|---------|----------|---------------|
| Vercel | 100GB bandwidth/month | Pro $20/mo (if team or advanced features needed) |
| Supabase | 500MB DB, 1GB storage, 5GB bandwidth | Pro $25/mo |
| Stripe | No monthly fee | 2.9% + $0.30 per transaction |
| Resend | 3,000 emails/month | $20/mo (50K emails) |
| Sentry | 5,000 errors/month | $26/mo (100K errors) |
| UptimeRobot | 50 monitors | Free plan sufficient for MVP |
| Domain | — | $10-15/year |

**MVP fixed cost (zero users)**: ~$12/year (domain only)
**MVP at growth**: Supabase + Vercel Pro = ~$45/month, covered by ~3 Pro subscribers at $19/mo

---

## Incident Runbook Templates

### Runbook 1: Supabase Connection Failure

```
Symptom: API routes returning 500, Sentry shows "connection refused" or "max connections"
Probable cause: Supabase DB paused (free tier inactivity), connection pool exhausted

Recovery:
1. Check Supabase Dashboard → Database → Status
   → Paused: click "Restore" (free tier pauses after 1 week inactivity)
   → Active but errors: check connection count vs. pooler limit
2. If connection count > 60 (free tier limit):
   → Enable PgBouncer (Supabase Dashboard → Settings → Database → Connection pooling)
3. Verify recovery: curl https://yourdomain.com/api/health
4. Root cause fix: Add keepalive ping if free tier (prevents pause)
```

### Runbook 2: Stripe Webhook Processing Failure

```
Symptom: Payments succeed in Stripe but subscriptions not activated in app
Probable cause: Webhook delivery failure, signature mismatch, or handler error

Recovery:
1. Stripe Dashboard → Developers → Webhooks → [your endpoint] → Recent deliveries
   → Find failed events → click "Resend"
2. Check Vercel Logs for webhook route errors
   → Signature mismatch: verify STRIPE_WEBHOOK_SECRET matches production endpoint secret
   → Handler error: check Sentry for stack trace
3. Manually reconcile: find user in Supabase → set subscription status = 'active'
4. Root cause fix: add dead-letter queue or idempotent retry logic
```

### Runbook 3: Vercel Deploy Failure

```
Symptom: Deploy pipeline fails, previous version still live
Probable cause: Build error, type error, or env var missing

Recovery:
1. Vercel Dashboard → Deployments → [failed deploy] → Build Logs
   → TypeScript error: fix locally, push fix commit
   → Missing env var: Settings → Environment Variables → add missing var → Redeploy
2. If rollback needed: Deployments → [last working deploy] → "..." menu → Promote to Production
   (instant, zero downtime — previous build served immediately)
3. Root cause fix: add `npx tsc --noEmit` to CI to catch type errors before deploy
```

---

## Quick Reference Checklist

Run before every production deploy:

**Security**
- [ ] `npm audit` — zero Critical/High vulnerabilities
- [ ] Grep for hardcoded secrets: `grep -r "sk_live_\|SERVICE_ROLE_KEY\|whsec_" src/`
- [ ] `.env.local` in `.gitignore` — confirmed
- [ ] RLS enabled on all public tables — verified with audit query
- [ ] Webhook signature verification active in handler
- [ ] Security headers present in `vercel.json`

**Cost & Config**
- [ ] Preview environment uses test keys (`sk_test_`, not `sk_live_`)
- [ ] Production environment uses live keys
- [ ] Billing alerts set in Supabase and Vercel dashboards
- [ ] Cost simulation reviewed for current growth trajectory

**Observability**
- [ ] Sentry configured and tested — at least one test error verified received
- [ ] UptimeRobot monitoring `/` and `/api/health`
- [ ] Structured logging fields confirmed: `{ timestamp, level, message, user_id, request_id }`
- [ ] Alert thresholds set (error rate, response time) — not raw event counts

**Performance**
- [ ] Lighthouse score ≥ 70 on production URL
- [ ] Core Web Vitals: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1
- [ ] No N+1 queries on list pages
- [ ] Indexes confirmed on FK columns and high-frequency WHERE clauses

**Deployment**
- [ ] Rollback plan documented: "If this deploy fails, I will [specific steps] in < 5 min"
- [ ] Database migration tested in staging before production
- [ ] RTO target < 30 min, RPO understood (Supabase backup schedule confirmed)
- [ ] Runbook exists for top 3 failure modes
