# Indie Maker Analytics Guide

AARRR framework, benchmarks, cohort analysis, and growth experiment design for indie SaaS MVPs.
Provide this document as context to Claude Code / Nova for consistent, data-driven analysis.

---

## Indie SaaS Benchmarks

Use these when `idea-canvas.md` kill criteria are missing or incomplete.
Sources: Baremetrics Open Metrics, PH launch post-mortems (2023-2025), Indie Hackers data.

### Launch Day (D22 ProductHunt)

| Metric | Kill Signal | Watch | Go |
|--------|------------|-------|-----|
| PH upvotes | < 30 | 30–80 | > 80 |
| Website visitors | < 100 | 100–300 | > 300 |
| Visitor → sign-up | < 3% | 3–8% | > 8% |
| Sign-ups | < 10 | 10–50 | > 50 |

### First Week (D23-28)

| Metric | Kill Signal | Watch | Go |
|--------|------------|-------|-----|
| Day-1 retention | < 15% | 15–35% | > 35% |
| Day-3 retention | < 10% | 10–25% | > 25% |
| Activation rate (sign-up → core action) | < 20% | 20–50% | > 50% |
| Free → paid conversion | 0% | 0–2% | > 2% |

### Kill/Go Gate (D29)

| Metric | Kill Signal | Watch | Go |
|--------|------------|-------|-----|
| Paying customers | 0 | 1–3 | > 3 |
| MRR | $0 | $1–$99 | > $100 |
| Day-7 retention | < 10% | 10–20% | > 20% |
| Any "can't live without this" signal | None | Unclear | Yes |
| Sean Ellis score (very disappointed if gone) | < 20% | 20–40% | > 40% |

> **Important**: Qualitative signals outweigh quantitative at sub-50 user stage. One user who "would be very disappointed" is more signal than 100 passive sign-ups.

---

## AARRR Funnel Framework

### Stage Definitions (Indie SaaS)

```
Acquisition  → User lands on your site (traffic source matters)
Activation   → User experiences core value (first "aha moment")
Retention    → User returns without being prompted
Revenue      → User pays
Referral     → User brings another user
```

### Bottleneck Identification

**Always fix the bottleneck first** — growth tactics on a leaky funnel waste money.

```
If Acquisition is low (< 100 visitors):
  → Distribution problem. Fix: PH follow-up posts, Reddit, cold outreach.
  → Do NOT optimize conversion rate yet.

If Activation is low (< 30% sign-up → core action):
  → Onboarding problem. Fix: Reduce steps to "aha moment", add progress indicator.
  → Do NOT run paid ads yet.

If Retention is low (< 20% D7):
  → Product-market fit problem. Fix: Talk to churned users, find retention cohort.
  → Do NOT optimize pricing yet.

If Revenue is low (< 2% free → paid):
  → Pricing/value communication problem. Fix: User interviews, pricing page A/B test.
  → Do NOT invest in SEO yet.

If Referral is low (0 organic sign-ups):
  → PMF is not strong enough. Fix: Focus on retention first.
```

### North Star Metric Selection

| Product Type | North Star Metric |
|-------------|------------------|
| SaaS productivity tool | Weekly active users completing core workflow |
| Marketplace | GMV (gross merchandise value) |
| Content/community | DAU/MAU ratio |
| API/developer tool | API calls per active user per week |
| E-commerce | Repeat purchase rate |

**Rule**: The North Star should be the single metric that, if it grows, everything else grows too. Revenue is an outcome, not a North Star.

---

## Cohort Retention Analysis

### Why Cohorts Matter

Aggregate retention (e.g., "we have 40% monthly active users") hides decay. A product with 1,000 sign-ups and 400 MAU might be losing 80% of each new cohort, sustained only by new acquisitions.

Cohort analysis shows retention per signup week — revealing the true decay curve.

### Reading a Retention Curve

```
Retention Curve Shape → Diagnosis

Flat at 0% after D7:    Product is not sticky. PMF issue.
Gradual decay to 0%:    Weak habit formation. Onboarding issue.
Decay then flattening:  Power users emerging. Optimize for this segment.
Rising after D30:       Viral loop working. Invest in referral.
```

**Healthy indie SaaS retention benchmarks:**
```
D1:  35-45% (lost after first day)
D7:  20-30% (weekly habit users)
D30: 10-20% (monthly habit users)
```

### Cohort Table Template

```
Sign-up Week | D0  | D1  | D3  | D7  | D14 | D30
─────────────────────────────────────────────────
Week 1       | 100%| 40% | 28% | 22% | 18% | 12%
Week 2       | 100%| 38% | 25% | 19% | 15% | —
Week 3       | 100%| 42% | 30% | —   | —   | —
─────────────────────────────────────────────────
Trend:       Stable (✅) / Declining (⚠️) / Improving (🚀)
```

### How to Pull Cohort Data

**PostHog (free tier):**
1. Insights → Retention
2. Group by: Sign-up date (weekly)
3. Returning event: [core action event name]
4. Export as CSV

**Vercel Analytics:** No cohort capability — use only for traffic/geography data.

**No analytics tool:** Fall back to manual — ask user "How many of your Week 1 sign-ups are still using it?"

---

## LTV:CAC Calculation

### Formulas

```
LTV  = ARPU × avg_subscription_months
     = ARPU / monthly_churn_rate  (if churn rate known)

CAC  = total_marketing_spend / paid_customers_acquired
     = $0 for fully organic launches

LTV:CAC = LTV / CAC  (target: > 3x for sustainable growth)
```

### Churn Rate → Avg Lifetime Conversion

| Monthly Churn Rate | Avg Customer Lifetime |
|-------------------|----------------------|
| 2% | ~50 months |
| 5% | ~20 months |
| 10% | ~10 months |
| 20% | ~5 months |
| 50% | ~2 months |

> For early-stage (< 3 months of data): use conservative 20% monthly churn as default.

### Example Calculation

```
ARPU:                $29/month
Est. monthly churn:  15% (early estimate)
LTV:                 $29 / 0.15 = $193
CAC:                 $0 (organic PH launch)
LTV:CAC:             ∞ → rephrase as "all-organic, unit economics positive"

Or if paid acquisition:
PH sponsorship:      $500 for 50 sign-ups, 3 converted to paid
CAC:                 $500 / 3 = $167
LTV:CAC:             $193 / $167 = 1.16x → ⚠️ borderline
```

---

## PMF Signal Framework

### Sean Ellis Test

**Question to ask users (in-app survey or email):**
> "How would you feel if you could no longer use [Product]?"
> A) Very disappointed  B) Somewhat disappointed  C) Not disappointed

**Interpretation:**
- > 40% "very disappointed" → Strong PMF signal
- 20–40% → Emerging PMF — keep iterating
- < 20% → Weak PMF — pivot or kill

**For indie makers with < 50 users:** Direct qualitative equivalent:
> Has any user said "I need this", "I check this daily", or "what would I do without this"?
> Yes → treat as PMF signal.  No → warning signal.

### Qualitative PMF Checklist

- [ ] At least one user checks the product unprompted (without email reminder)
- [ ] At least one user requested a feature that shows they're planning to stay
- [ ] Any user referred another user organically (without incentive)
- [ ] Founder receives inbound emails from users, not just support requests
- [ ] Founder wants to keep building (intrinsic motivation check)

---

## Growth Experiment Design

### Experiment Template

Every growth experiment must include all four elements:

```
Hypothesis:     If we [change X], then [metric Y] will improve by [Z]%
                because [reason based on data].

Method:         [Specific change — A/B test / feature flag / copy change / etc.]

Measurement:    [What to measure, how, with which tool]

Duration:       [2-4 weeks standard; minimum 7 days for weekly patterns]
Sample size:    [Minimum N users for statistical significance — use analytics-guide.md calculator]
Success metric: [Specific number that constitutes a win]
```

### Statistical Significance Estimator (simplified)

For conversion rate improvements:

| Current conversion | Minimum detectable change | Min sample size per variant |
|-------------------|--------------------------|----------------------------|
| 2% | 1% absolute (50% relative) | ~2,000 |
| 5% | 2% absolute (40% relative) | ~800 |
| 10% | 3% absolute (30% relative) | ~500 |
| 20% | 5% absolute (25% relative) | ~300 |

> **For indie MVPs with < 200 users:** Abandon statistical rigor — run qualitative user interviews instead. A/B tests require traffic you don't have yet.

### Growth Experiment Prioritization

Apply ICE framework before running any experiment:

```
ICE Score = Impact × Confidence × Ease  (each 1–10)

Impact:     How much will this move the North Star?
Confidence: How confident are we this will work (based on data)?
Ease:       How fast can we ship this (days, not weeks)?

Sort by ICE score descending. Run highest-score experiment first.
```

### AARRR-Matched Experiment Playbook

| Bottleneck Stage | High-ICE Experiments |
|-----------------|---------------------|
| Acquisition | Reddit launch post in niche sub, Twitter thread with demo gif, cold outreach to 10 ideal users |
| Activation | Remove steps to core action, add in-app tooltip at first friction point, onboarding email D+1 |
| Retention | Weekly digest email, "your progress this week" notification, core workflow shortcut |
| Revenue | Annual plan offer (saves 20%), pricing page social proof, free trial → paid conversion email sequence |
| Referral | Referral link in dashboard, "invite a teammate" for B2B, PH re-submit with changelog |

---

## Review & Feedback Collection

### Review Request Email Template

```
Subject: Quick question about [Product Name]

Hi [First Name],

You've been using [Product Name] for [X days/weeks].

If it's been useful, would you mind leaving a quick review on Product Hunt?
It takes 2 minutes and helps other [target users] find us.

→ [ProductHunt review link]

Alternatively, just hit reply — any feedback helps.

[Your name]
```

**Send timing:** D+7 after sign-up (high enough intent, low enough churn).

### Feedback Classification

| Type | Signal | Action |
|------|--------|--------|
| Bug report | Product quality issue | Fix within 48h if blocking |
| Feature request (core) | Product-market fit signal | Add to backlog |
| Feature request (scope expansion) | Next product idea | Log separately, do not build now |
| Praise | Social proof material | Ask permission to quote on landing page |
| Pricing concern | Willingness to pay signal | Log for pricing iteration |
| "Too complex / confusing" | Onboarding/UX issue | Fix activation funnel |

---

## Analytics Tool Setup (Pre-Launch)

### Recommended for Indie Makers

| Tool | Use Case | Cost |
|------|----------|------|
| **PostHog** (cloud free tier) | Events, funnels, cohorts, session replay | Free up to 1M events/month |
| **Vercel Analytics** | Traffic, geography, page performance | Free with Vercel |
| **Stripe Dashboard** | Revenue, MRR, churn | Free |
| **Resend** | Email open/click rates | Free up to 3,000 emails/month |

### Minimum Viable Tracking (launch day)

```typescript
// posthog.ts — install: npm install posthog-js
import posthog from 'posthog-js'

// Initialize in root layout (client component)
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://app.posthog.com',
})

// Key events to track from day 1:
posthog.capture('signed_up')                    // Acquisition → Activation
posthog.capture('completed_core_action', {      // Activation
  action_type: '[your core action]'
})
posthog.capture('returned_to_app')              // Retention proxy
posthog.capture('upgrade_clicked', {            // Revenue intent
  plan: 'pro',
  source: 'pricing_page'
})
posthog.capture('referral_link_copied')         // Referral
```

---

## Quick Reference: Kill/Go Decision Logic

```
Score each AARRR stage: 🔴 (Kill signal) / 🟡 (Watch) / 🟢 (Go signal)

3+ 🟢 and North Star positive     → Go
2 🟢 + strong qualitative signal  → Go (with caveats)
Majority 🟡                       → Watch (extend 2 weeks)
2+ 🔴 and no qualitative signal   → Kill (with retrospective)
Any single 🔴 on Revenue at D29  → Watch if qualitative is strong,
                                    Kill if no user engagement

Override rule: If one user says "I would be very disappointed without this"
and is actively using the product daily → treat as Watch minimum, never Kill.
```

---

## Post-D29: Nova의 분석 한계

Nova는 **D0–D29 초기 검증 구간**에 최적화되어 있습니다.
Go 판정 이후 성장 가속 단계에서 다음이 필요하다면 `/indie-growth`를 사용하세요.

| 필요 시점 | 분석 영역 | Nova 한계 |
|-----------|-----------|-----------|
| 유료 광고 시작 시 | CAC by channel, ROAS, payback period | organic 전제로 설계됨 |
| 유저 100명+ 이후 | Power user 세그먼트 분리, tier별 리텐션 | aggregate cohort만 지원 |
| 이탈 급증 시 | 이탈 예고 지표 (로그인 빈도 감소, feature 미사용) | Kill/Go 시점 이후 개념 없음 |
| 가격 인상 검토 시 | Willingness to pay 곡선, Van Westendorp | "pricing concern" 분류에서 멈춤 |
| B2B 전환 시 | NRR, expansion MRR, logo retention | B2C 지표 중심 |
| 바이럴 루프 측정 시 | k-factor = 초대 전환율 × 초대 수 | referral = 리뷰 수집 수준 |

> **요약**: Nova는 "살릴 것인가 말 것인가"에 집중합니다.
> "어떻게 100배 성장할 것인가"는 `/indie-growth`의 영역입니다.
