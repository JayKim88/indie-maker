# Market Intelligence Guide

## Non-Negotiable Rules

A 20-year market veteran applies these rules without exception.
Violating them produces analysis that feels insightful but leads to bad product decisions.

### Market Structure (Rules 1–8)

1. **Always run Porter's Five Forces before sizing the market.**
   Market size is meaningless without knowing whether you can capture any of it. A $10B market you cannot enter profitably is worse than a $100M market you can dominate.
   [Source: Porter, "How Competitive Forces Shape Strategy", HBR 1979]

2. **Supplier power determines your margin ceiling, not your product.**
   If your key input (API, data, distribution) is controlled by one supplier, your business model is a subsidy for them. Identify and quantify dependency before committing.

3. **Buyer power determines your pricing power.**
   Low switching costs + many alternatives = commoditized pricing. Name the switching cost before setting a price. If there is no switching cost, you must create one (data lock-in, habit, network effect).

4. **Map substitutes, not just direct competitors.**
   The real threat is often a different category solving the same job. "Habit continuation" (doing nothing, using Excel, or asking a friend) is always a substitute.

5. **Rivalry intensity sets your marketing spend baseline.**
   High rivalry + low differentiation = high CAC. Estimate the average competitor CAC before projecting your own. Never project CAC lower than the market average without a structural reason.

6. **Barrier to entry determines defensibility window.**
   For indie makers: you have 6–18 months before a well-funded team copies you. Name the moat you'll build in that window: distribution, data, brand, or integrations.

7. **Network effects require critical mass — define what "critical mass" means for your product.**
   A network with no density is worthless. If your value proposition depends on network effects, specify the minimum viable network size before declaring the model viable.
   [Source: Metcalfe's Law applied to product design]

8. **Blue ocean ≠ no competition.**
   No direct competitors usually means: (a) market does not exist yet, (b) others tried and failed, or (c) the problem is real but no one has found the right solution. Investigate all three before treating it as opportunity.

### Demand Validation (Rules 9–14)

9. **Stated intent ≠ revealed preference. Always test with money or real effort.**
   "Yes, I'd use that" costs a user nothing. "Yes, I'll pay $29 today" is real signal. Design every validation to require a non-trivial commitment from the user.
   [Source: Predictably Irrational, Dan Ariely; The Mom Test, Rob Fitzpatrick]

10. **Run the cheapest test first, then escalate.**
    Smoke test ($0) → Fake Door test ($50–200 in ads) → Pre-order (real money) → MVP (weeks of code). Never skip to MVP before the cheaper tests pass.

11. **Smoke test requires a 2% email signup conversion rate to proceed.**
    Below 2%: problem is not urgent enough or the copy failed to communicate value. Above 5%: strong signal. Measure, do not guess.
    ⚠ Assumption: traffic to the landing page is targeted (not family/friends).

12. **Fake Door test requires click-through rate on the CTA > 8% to proceed.**
    A CTA click ("Start Free Trial") that leads to a waitlist page measures purchase intent without a product. Under 8% CTR: the offer is not compelling.

13. **Pre-order requires ≥ 3 paying customers before writing production code.**
    One customer can be an outlier. Two can be coincidence. Three is a pattern. This threshold applies even if order value is small.

14. **Demand validation must target a specific segment, not "everyone."**
    If your target is "busy professionals," your test will fail. "B2B SaaS product managers at 50-person startups in the US" is a testable segment. Be specific enough to recruit 10 users manually.

### Behavioral Economics (Rules 15–20)

15. **Loss aversion is 2× stronger than equivalent gain. Frame your value proposition around what users lose by NOT using your product.**
    "Save 3 hours/week" is weaker than "Stop losing 3 hours/week to [specific pain]." Use loss framing in messaging unless brand voice prohibits it.
    [Source: Kahneman & Tversky, Prospect Theory, 1979]

16. **Switching costs are a design decision, not a side effect.**
    Design for switching costs from day one: import user data, learn their preferences, integrate with their existing tools, store their history. A product with zero switching costs competes on price alone.

17. **Hook Model sequence must be present for habit-forming products.**
    External Trigger → Action → Variable Reward → Investment. If your product skips "Investment" (user cannot put something of value into the product), it will not form habits.
    [Source: Hooked, Nir Eyal]

18. **Status signaling works best in visible, social domains.**
    If your users can show others they use your product, you have a free growth channel. Design "shareable moments" (achievements, outputs, results) into the core flow.

19. **Anchoring: present the high-tier plan first.**
    When showing pricing, always reveal the most expensive option first. It anchors the user's perception of value and makes the mid-tier plan look like a rational choice, not a compromise.

20. **Scarcity and social proof only work when authentic.**
    "Only 3 spots left" when you have unlimited capacity is dark pattern and destroys trust at scale. Use real scarcity (beta cohort size, office hours slots, founding member count) or skip it.

### Technology Adoption Curve (Rules 21–24)

21. **Identify which adopter segment you are targeting — the crossing-the-chasm gap exists between Early Adopters and Early Majority, and it requires a completely different product, channel, and message.**
    Early Adopters tolerate rough edges, buy on vision, and don't need references. Early Majority need ROI proof, references, and a complete solution. The same product positioning cannot serve both.
    [Source: Crossing the Chasm, Geoffrey Moore]

22. **Enter via a niche where you can dominate, then expand.**
    Early Majority adoption requires "whole product" completeness. Dominate one vertical or segment before expanding. Being "pretty good for everyone" is worse than being "the best for [specific niche]."

23. **Early Adopter success metrics are not Early Majority success metrics.**
    Early Adopters measure: novelty, capability, vision alignment. Early Majority measures: time-to-value, ROI, peer references. Reframe all marketing and onboarding when crossing the chasm.

24. **Innovators (2.5% of market) are the wrong target for revenue, but the right target for product feedback.**
    Sell to Early Adopters (13.5%). Get product feedback from Innovators. Never confuse their enthusiasm for market validation — they will love almost anything new.

---

## Core Frameworks & Application

### Framework 1: Porter's Five Forces

```
                    [New Entrants]
                         ↓
[Suppliers] → [Industry Rivalry] ← [Buyers]
                         ↑
                    [Substitutes]
```

**Indie Maker Scoring Template:**

| Force | Rating (Low/Med/High) | Key Signal | Your Answer |
|-------|----------------------|------------|-------------|
| Threat of new entrants | | API access / regulatory barrier / capital required | |
| Supplier power | | Number of key APIs/platforms you depend on | |
| Buyer power | | How many alternatives a buyer has in 60 seconds | |
| Threat of substitutes | | Non-consumption + existing habits as alternatives | |
| Rivalry intensity | | Average competitor CAC, ad spend, funding | |

**Decision Rule:**
- 3+ forces rated "High" → niche down further or find a different angle
- Supplier power "High" → validate that supplier will not compete with you directly
- Buyer power "High" + Rivalry "High" → requires strong switching cost design from day one

---

### Framework 2: Demand Validation Ladder

```
Step 1 (Cheapest)     Step 2              Step 3              Step 4 (Most Expensive)
   Smoke Test    →   Fake Door Test  →   Pre-Order      →      MVP Build
   D1–D3              D4–D7              D8–D14               D15+
   Cost: $0           Cost: $50-200      Cost: $0-$200        Cost: weeks of dev
   Success: 2%        Success: 8% CTR    Success: 3 paying    Success: retention
   signup rate        on "buy" button    customers            > 30%
```

**Smoke Test Setup (D1–D3):**
```
1. Write a one-paragraph description of the product
2. Create a landing page: Problem → Solution → Email capture (Carrd or v0)
3. Drive 200–500 targeted visitors (personal network, Reddit, targeted Twitter post)
4. Measure: email signup rate
   - < 2%: stop or reframe value proposition
   - 2–5%: test is valid, continue
   - > 5%: strong signal — escalate to Fake Door or Pre-order immediately
```

**Fake Door Test Setup:**
```
1. Add a "Start Free Trial" or "Buy Now" CTA to the smoke test landing page
2. Clicking the CTA leads to: "We're building this — join the waitlist"
3. Capture email, optionally ask 1 question: "What made you click?"
4. Measure CTR on the CTA button
   - < 8%: offer framing is wrong — test alternative headline
   - 8–15%: valid signal, proceed to pre-order
   - > 15%: urgent demand — prioritize shipping
5. Run for 48–72 hours minimum, minimum 100 unique visitors
```

**Pre-Order Design:**
```
Pricing: $29–$199 one-time (lifetime deal framing works well for early adopters)
Platform: Stripe + Carrd, or Gumroad
Offer: "Founding member" pricing + early access + direct line to founder
Goal: 3 paying customers before writing any production code
If failed after 2 weeks: kill or pivot the angle — demand is not there
```

---

### Framework 3: Behavioral Economics Applied

#### Switching Cost Design Matrix

| Switching Cost Type | How to Build It | Example |
|--------------------|-----------------|---------|
| **Data lock-in** | Store user history, preferences, progress | Fitness app with 6 months of workout logs |
| **Habit formation** | Daily trigger + variable reward + streak | Duolingo streak mechanics |
| **Integration depth** | Connect to user's existing tools (Notion, Slack, Jira) | Synced data that breaks if they leave |
| **Social graph** | Mutual connections that are lost on exit | LinkedIn connections |
| **Learning investment** | Product learns user preferences over time | Email filter trained on 500 emails |
| **Network effects** | Value comes from other users' presence | Slack team channels |

**Indie Maker Rule**: As a solo developer, prioritize **Data lock-in** and **Learning investment** — they require no network effect and no team to execute.

#### Hook Model Implementation Checklist

```
Trigger (External → Internal)
  External: Email, push notification, cron job, social share
  Internal: Emotion or situation that becomes the trigger over time
  ✓ Define: "The internal trigger fires when user feels [emotion/situation]"

Action (Simplest behavior in anticipation of reward)
  The action must require minimum effort
  ✓ Define: "The core action is [verb] and takes < 30 seconds"

Variable Reward (3 types)
  - Rewards of the tribe: social validation, comparison, status
  - Rewards of the hunt: information, resources, deals
  - Rewards of the self: mastery, completion, control
  ✓ Define: "The variable element is [what changes between sessions]"

Investment (User puts something in that improves future experience)
  Data, content, social capital, reputation, skill
  ✓ Define: "After each session, the product improves because user added [X]"
```

#### Loss Aversion Copy Template

| Weak (Gain frame) | Strong (Loss frame) |
|-------------------|---------------------|
| "Save 3 hours per week" | "Stop losing 3 hours every week to [task]" |
| "Get better results" | "Stop leaving results on the table" |
| "Improve your X" | "Your X is declining while competitors automate this" |
| "Learn faster" | "Every week without this skill is falling further behind" |

**Rule**: Test loss-frame vs. gain-frame copy in A/B test on landing page. Loss frame typically outperforms by 20–40% in financial and productivity contexts.

---

### Framework 4: Technology Adoption Curve

```
                                                    ← Chasm →
   Innovators    Early Adopters    Early Majority    Late Majority    Laggards
      2.5%            13.5%            34%               34%             16%

  "Techies"        "Visionaries"     "Pragmatists"    "Conservatives"  "Skeptics"
  Love novelty     Buy on vision     Buy on ROI        Buy on safety    Buy last
  No references    1-2 references    Many references   Industry std.    No choice
  needed           needed            required          required         required
```

**Segment Identification Questions:**

For your target user, ask:
1. Do they actively seek out new tools and beta products? → **Innovator/Early Adopter**
2. Do they only adopt after seeing 3 peer references? → **Early Majority**
3. Do they only switch when their current tool breaks or dies? → **Late Majority**

**Chasm-Crossing Playbook (for indie makers):**

```
Phase 1: Dominate a niche (Early Adopter → Early Majority)
  1. Choose ONE beachhead segment: the highest-pain niche within your market
     Criteria: can be reached directly, small enough to win, large enough to matter
  2. Build "whole product" for that segment only
     Whole product = core product + integrations + support + community for that niche
  3. Get 3 published case studies with ROI metrics from that segment
  4. Build reference channel: customer referrals + niche community presence

Phase 2: Expand from the beachhead
  Only after dominating the beachhead:
  - Adjacent segment with same buying behavior
  - Same product, different vertical
  - International version of same niche
```

**Adopter Segment Decision Table:**

| If your user... | Likely segment | Required to sell | Red flag if... |
|-----------------|----------------|------------------|---------------|
| Signs up for betas without referrals | Innovator / Early Adopter | Vision + potential | They never pay full price |
| Asks "who else is using this?" | Early Majority | Case studies + integration | No references available |
| Has internal approval process | Late Majority | Security docs + SLA | Product is too niche |
| Uses product only because mandated | Laggard | N/A — they don't choose | You're targeting them intentionally |

---

## Architecture Decision Guide

### When to Apply Each Framework

| Situation | Framework to Apply First |
|-----------|--------------------------|
| "Is this market worth entering?" | Porter's Five Forces |
| "Is my idea real?" | Demand Validation Ladder (Smoke Test) |
| "Why are users not converting?" | Behavioral Economics (Hook Model gap) |
| "How do I grow after launch?" | Adoption Curve → identify current segment |
| "Why is my CAC so high?" | Porter's Rivalry + Buyer Power |
| "How do I build retention?" | Switching Cost Design + Hook Model |
| "Should I expand to a new segment?" | Adoption Curve beachhead analysis |

### Market Entry Decision Tree

```
Is the market size > $100M (TAM)?
├── No → niche too small (unless solo-dev, low competition, high margin: reconsider)
└── Yes ↓

Are 3+ forces in Porter's analysis rated "High"?
├── Yes → differentiation required before entering. What's your structural advantage?
└── No ↓

Is there evidence of real demand? (Smoke test passed 2%?)
├── No → validate demand before building. Run smoke test first.
└── Yes ↓

Which adopter segment is your beachhead?
├── Early Adopter → emphasize vision + capability + direct founder access
└── Early Majority → you need references before targeting them. Build Early Adopter base first.
```

---

## Quick Reference Checklist

### Market Structure (before choosing an idea)
- [ ] Porter's Five Forces completed with ratings and evidence
- [ ] Switching cost in current market identified
- [ ] Entry barrier estimated (time, capital, or regulatory)
- [ ] Moat you'll build in first 12 months named explicitly

### Demand Validation (before writing production code)
- [ ] Smoke test run with ≥ 200 targeted visitors
- [ ] Email signup rate ≥ 2% confirmed
- [ ] At least one demand test escalated (Fake Door or Pre-order)
- [ ] 3 paying customers confirmed before MVP (if pre-order used)

### Behavioral Design (before finalizing product spec)
- [ ] Switching cost type selected and designed into product
- [ ] Hook Model completed: Trigger / Action / Variable Reward / Investment all defined
- [ ] Loss-frame copy tested on landing page
- [ ] "Shareable moment" in core flow (status signaling channel)

### Adoption Strategy (before choosing GTM channel)
- [ ] Target adopter segment identified (Early Adopter vs Early Majority)
- [ ] Beachhead segment defined (specific enough to name 10 users manually)
- [ ] "Whole product" requirements for beachhead listed
- [ ] Chasm crossing plan outlined (Phase 1 niche domination milestones)

### RAT (Riskiest Assumption Test)
- [ ] Single riskiest assumption named: "We assume [X]"
- [ ] Test for that assumption designed: "We'll know this is true when [Y]"
- [ ] Kill criteria set: "If we don't see [Y] by [date], we kill/pivot"
