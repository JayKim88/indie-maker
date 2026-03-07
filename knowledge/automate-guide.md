# Automate Guide

> Phase: post-launch (D15+) and ongoing
> Stack: Resend + Supabase (pg_cron + Edge Functions) + Vercel Analytics
> Principle: automate only what you do repeatedly and what is worth the time saved.

---

## When to Automate (and When Not To)

Before automating anything, apply the MAKE principle:

**Automate if**: you do it more than once a week AND it takes >15 minutes AND it's repeatable with no judgment required.
**Do manually if**: it requires human judgment, you've only done it once, or the automation takes longer to build than the task itself.

| Task | Automate? | Why |
|------|-----------|-----|
| Welcome email to new signup | Yes | Every signup, zero judgment needed |
| Stripe payment confirmation email | Yes | Webhook trigger, 100% repeatable |
| D14 launch day DMs | No | Too personal — authenticity > automation |
| Weekly MRR check | Yes after $100 MRR | Before that, just check Stripe dashboard |
| Responding to support emails | No | Requires context and judgment |
| Churned user win-back | Yes (template) | After you've written it once manually |

---

## Part 1: Email Automation (Resend + Supabase)

### Architecture Overview

```
User signs up
  → Supabase inserts row into users table
  → Supabase trigger fires Edge Function
  → Edge Function calls Resend API
  → Email sent

OR

pg_cron job runs on schedule
  → Queries users table (e.g., "users who signed up 3 days ago")
  → Calls Edge Function for each matching user
  → Edge Function calls Resend API
```

### Setup: Resend Integration

```typescript
// lib/email.ts
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function sendEmail({
  to,
  subject,
  html,
  from = 'Your Name <hello@yourdomain.com>',
}: {
  to: string
  subject: string
  html: string
  from?: string
}) {
  return resend.emails.send({ from, to, subject, html })
}
```

```sql
-- Supabase: store email_log to avoid duplicates
create table email_log (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  email_type text not null,  -- 'welcome', 'day3', 'trial_ending', etc.
  sent_at timestamptz default now(),
  unique(user_id, email_type)  -- prevent duplicate sends
);
```

---

### Email Sequence: Standard Drip (7 emails)

These cover the full conversion journey from signup to paying customer.
Timing is relative to `created_at` in the users table.

| Email | When | Goal | Subject line pattern |
|-------|------|------|---------------------|
| D0: Welcome | Immediate | Activate | "Here's how to get started with [product]" |
| D3: Value | +3 days | Reinforce value | "What [similar users] do with [product]" |
| D6: Trial end (if trial) | +6 days | Convert | "Your trial ends tomorrow" |
| D7: Conversion ask | +7 days | Upgrade | "Ready to upgrade? Here's what you get" |
| D14: Re-engagement | +14 days (inactive) | Retain | "You haven't been back — here's a shortcut" |
| D21: Feature nudge | +21 days (free) | Upgrade | "[Feature] is now live — Pro users only" |
| D30: Win-back | +30 days (churned) | Recover | "We improved [thing you complained about]" |

---

### Email D0: Welcome (trigger on signup)

**Trigger**: Supabase Auth hook or `users` table insert trigger

```typescript
// supabase/functions/on-user-signup/index.ts
import { sendEmail } from '../_shared/email.ts'

Deno.serve(async (req) => {
  const { record } = await req.json()  // new user row
  const { id, email } = record

  await sendEmail({
    to: email,
    subject: 'Welcome — here\'s how to get started',
    html: welcomeEmailHtml({ email }),
  })

  // Log to prevent re-sends
  await supabase.from('email_log').insert({
    user_id: id,
    email_type: 'welcome',
  })

  return new Response('ok')
})
```

**Welcome email content formula**:
```
Subject: Get to [aha moment] in 5 minutes

Hi,

Welcome to [product name].

One thing to do right now:
→ [Single action that leads to aha moment — e.g., "Connect your first data source"]

[Link to that specific page/action]

If you get stuck: reply to this email. I read every reply.

— [Your name]

P.S. [Optional: 1 sentence about what you're building next — builds relationship]
```

**Do NOT**: put 5 things in the welcome email. One CTA only.

---

### Email D3: Value Reminder

**Trigger**: pg_cron job, runs daily, queries users signed up 3 days ago

```sql
-- Enable pg_cron extension (Supabase Dashboard → Extensions → pg_cron)
-- Then in SQL editor:

select cron.schedule(
  'day3-email',
  '0 10 * * *',  -- 10 AM UTC daily
  $$
  select
    net.http_post(
      url := 'https://[project].supabase.co/functions/v1/send-drip-email',
      headers := '{"Authorization": "Bearer [service_role_key]", "Content-Type": "application/json"}'::jsonb,
      body := json_build_object(
        'email_type', 'day3',
        'user_ids', (
          select array_agg(id)
          from public.users
          where created_at::date = (current_date - interval '3 days')::date
          and id not in (
            select user_id from email_log where email_type = 'day3'
          )
        )
      )::text
    )
  $$
);
```

**Day 3 email content formula**:
```
Subject: What [role, e.g., "freelancers"] use [product] for

Hi,

3 days in — quick question: did you [aha moment action]?

If yes: here's what's next → [feature 2 or deeper use case]
If not yet: it takes 5 minutes → [link]

Most common use case I see:
"[Specific outcome from a real beta user — e.g., 'I saved 2 hours last week on client reports']"

— [Your name]
```

---

### Email D6: Trial Ending (subscription products only)

**Trigger**: pg_cron, daily, queries users whose trial ends in 1 day

```sql
select cron.schedule(
  'trial-ending-email',
  '0 9 * * *',
  $$
  select net.http_post(...)
  where trial_ends_at::date = (current_date + interval '1 day')::date
  and subscription_status = 'trial'
  $$
);
```

**Trial ending email content**:
```
Subject: Your trial ends tomorrow — here's what happens

Hi,

Your [product] trial ends tomorrow.

After that, you'll lose access to:
- [Feature 1 they used]
- [Feature 2 they used]
- [Their data/work created during trial]

Keep everything: $[X]/month → [payment link]

Or if now isn't the right time, I'd love to know why:
→ [Link to 2-question survey: "What would make it worth paying for?"]

— [Your name]
```

**Psychology**: "here's what you'll lose" outperforms "here's what you get" by 30-40%.
This is loss aversion — use it honestly (not manipulatively).

---

### Email D14: Re-engagement (inactive users)

**Trigger**: pg_cron, daily, queries users with no activity in 7+ days

```sql
-- Requires an activity tracking table
-- Simplest: track last_seen_at on users table
-- Update via: supabase.from('users').update({ last_seen_at: new Date() }) on each page load

select cron.schedule(
  'reengagement-email',
  '0 11 * * *',
  $$
  select net.http_post(...)
  where last_seen_at < current_date - interval '7 days'
  and subscription_status = 'free'
  and id not in (select user_id from email_log where email_type = 're-engagement')
  $$
);
```

**Re-engagement email content**:
```
Subject: One thing that might help

Hi,

You signed up for [product] [N] days ago but haven't been back.

Most common reason people don't come back: [most common onboarding failure point].

Here's a shortcut: [link that bypasses the friction point]

If [product] isn't useful for you, I'd genuinely appreciate knowing why.
Reply with one sentence — it helps me build the right thing.

— [Your name]
```

---

## Part 2: Metrics Automation

### What to Track (and Where)

| Metric | Source | When to set up |
|--------|--------|----------------|
| Pageviews, referrers | Vercel Analytics (auto) | D6 deploy |
| Signups/day | Supabase dashboard | D6 |
| Active users (DAU/WAU) | Supabase query | D15 |
| MRR | Stripe dashboard | First payment |
| Churn rate | Stripe dashboard | After 10+ customers |
| Activation rate | Supabase query | D15 |
| Email open rate | Resend dashboard | D0 |

**Rule for early-stage** (pre $500 MRR): check manually. Automation before this is premature.
**Rule for growth stage** ($500+ MRR): automate what you're checking more than daily.

---

### MRR Dashboard: Supabase SQL View

```sql
-- Create a view for quick MRR calculation
-- Assumes you store subscription data after Stripe webhooks

create view mrr_summary as
select
  date_trunc('day', current_date) as as_of,
  count(*) filter (where subscription_status = 'active') as active_subscribers,
  sum(monthly_amount) filter (where subscription_status = 'active') as mrr_cents,
  sum(monthly_amount) filter (where subscription_status = 'active') / 100.0 as mrr_usd,
  count(*) filter (where subscription_status = 'trial') as trial_users,
  count(*) filter (where subscription_status = 'churned'
    and updated_at > current_date - interval '30 days') as churned_30d
from subscriptions;
```

Query it anytime: `select * from mrr_summary;`

---

### Stripe Webhook → Supabase Sync

Essential events to handle (set up in D5 build sprint):

```typescript
// app/api/webhooks/stripe/route.ts
export async function POST(req: Request) {
  const event = stripe.webhooks.constructEvent(
    await req.text(),
    req.headers.get('stripe-signature')!,
    process.env.STRIPE_WEBHOOK_SECRET!
  )

  switch (event.type) {
    case 'checkout.session.completed':
      // User paid — upgrade their tier in Supabase
      await supabase
        .from('subscriptions')
        .upsert({
          user_id: event.data.object.metadata.user_id,
          subscription_status: 'active',
          stripe_subscription_id: event.data.object.subscription,
          monthly_amount: event.data.object.amount_total,
          updated_at: new Date().toISOString(),
        })
      // Send payment confirmation email via Resend
      await sendEmail({ to: event.data.object.customer_email, ... })
      break

    case 'customer.subscription.deleted':
      // User churned
      await supabase
        .from('subscriptions')
        .update({ subscription_status: 'churned', updated_at: new Date().toISOString() })
        .eq('stripe_subscription_id', event.data.object.id)
      // Optional: trigger win-back email sequence
      break

    case 'invoice.payment_failed':
      // Payment failed — send dunning email
      await sendEmail({ to: ..., subject: 'Payment failed — update your card', ... })
      break
  }

  return new Response('ok')
}
```

---

### Weekly Metrics Digest (optional, post $100 MRR)

Auto-send yourself a weekly summary every Monday morning:

```sql
-- pg_cron: weekly metrics digest
select cron.schedule(
  'weekly-digest',
  '0 8 * * 1',  -- Monday 8 AM UTC
  $$
  select net.http_post(
    url := 'https://[project].supabase.co/functions/v1/weekly-digest',
    headers := '...',
    body := json_build_object(
      'mrr', (select mrr_usd from mrr_summary),
      'new_signups', (
        select count(*) from users
        where created_at > current_date - interval '7 days'
      ),
      'new_paying', (
        select count(*) from subscriptions
        where subscription_status = 'active'
        and created_at > current_date - interval '7 days'
      ),
      'churned', (
        select count(*) from subscriptions
        where subscription_status = 'churned'
        and updated_at > current_date - interval '7 days'
      )
    )::text
  )
  $$
);
```

The Edge Function emails you a plain-text weekly digest. No dashboards to build.

---

## Part 3: Automation Roadmap by Stage

Don't build all of this at once. Follow this sequence:

### D6 (Deploy day) — Required
- [ ] Stripe webhook handler (checkout.session.completed + subscription.deleted + payment_failed)
- [ ] Welcome email on signup (Resend)

### D15 (Post-launch) — High value
- [ ] D3 value reminder email (pg_cron)
- [ ] D14 re-engagement email (pg_cron)
- [ ] MRR view in Supabase

### After $100 MRR — Worth automating now
- [ ] D6 trial-ending email (if subscription model)
- [ ] D7 conversion ask email
- [ ] Weekly metrics digest to yourself
- [ ] Churned user win-back email (D30)

### After $500 MRR — Scale automation
- [ ] Behavioral trigger emails (based on feature usage)
- [ ] Segmented sequences by plan tier
- [ ] Stripe dunning sequence (3 emails over 7 days for failed payments)
- [ ] NPS survey trigger (after 30 days active)

---

## Reference

- Resend docs: resend.com/docs
- Supabase pg_cron: supabase.com/docs/guides/database/extensions/pg_cron
- Supabase Edge Functions: supabase.com/docs/guides/functions
- Email sequence strategy: `pricing-strategy.md` (indie-monetize output)
