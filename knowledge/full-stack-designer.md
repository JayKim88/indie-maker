# Full-Stack Designer Knowledge Base

> Extended intelligence layer for Vera (Full-Stack Designer agent).
> Reference: `design-guide.md` covers Non-Negotiable Rules — treat it as Vera's constitution.
> This document adds: pattern library, CRO, psychology, brand voice, decision trees, microcopy, motion, critique.

---

## 1. Product Type Context Matrix

Design personality changes significantly by product type.
**First question Vera must ask if not available in prd-lean.md: "What type of product is this?"**

| Product Type | Visual Tone | Color Bias | Density | Trust Signal Priority |
|-------------|------------|-----------|---------|----------------------|
| **B2B SaaS** | Minimal, professional | Blue/Indigo/Slate | High — data tables, filters | Logos of known customers |
| **Consumer App** | Warm, emotional | Orange/Violet/Teal | Low — breathing room | User counts, reviews, testimonials |
| **Dev Tool** | Dark mode default, technical | Slate/Zinc/Green | High — code, configs | GitHub stars, OSS credibility |
| **Marketplace** | Discovery-first, visual | Amber/Emerald | Medium — browsable cards | Verified badges, transaction count |
| **Creator Tool** | Expressive, free | Purple/Pink/Gradient | Low-medium | Portfolio examples |
| **Productivity** | Focus, calm | Blue/Teal/Slate | Medium | "X hours saved" stats |

---

## 2. Psychological Principles

### 2.1 Hick's Law — Decision Speed
**More choices = slower decisions = higher abandonment.**
- CTAs: 1 primary per section. Never 2 equal-weight primary buttons side by side.
- Onboarding: Maximum 3 required fields on first screen.
- Navigation: 5-7 items max. Group beyond that.
- Pricing: 2-3 tiers maximum. 4+ tiers cause paralysis.

### 2.2 F-Pattern & Z-Pattern Scanning
Users don't read — they scan.

**F-Pattern** (content-heavy pages: docs, dashboards):
```
████████████████  ← Full horizontal scan (H1, navigation)
████████████      ← Second horizontal scan (first content)
████              ← Vertical scan down the left edge
```
→ Place critical information on the left edge and first 2 lines.

**Z-Pattern** (landing pages, simple layouts):
```
[Logo]────────────[CTA]    ← Top: logo left, CTA right
          ╲
          ╲
[Value]────────[Social proof]  ← Bottom: value left, proof right
```
→ Landing hero: logo top-left, primary CTA top-right, headline center, social proof below.

### 2.3 Social Proof Hierarchy
Ranked by conversion impact:

1. **Specific numbers** — "2,400 teams" beats "thousands of teams"
2. **Recognizable logos** — 3-5 logos of known companies
3. **Named testimonials** — Full name + company + photo > anonymous quote
4. **Star ratings** — 4.8★ (1,200 reviews) > "Loved by customers"
5. **User-generated content** — Screenshots of actual usage

**When to include:** After hero section, before or after pricing. Never before the value proposition.

### 2.4 Anchoring Effect
First number seen anchors perception.

- Show the annual price crossed out before monthly price
- Show the "Enterprise" tier first (or most expensive) to make Pro look reasonable
- On free tier: list limitations clearly so Pro feels like the obvious upgrade

### 2.5 Progressive Disclosure
Never show everything at once.
- Onboarding: 1 decision per screen
- Complex forms: step-by-step wizard over single long form
- Feature discovery: core features visible first, advanced features behind "More options"

### 2.6 Loss Aversion (Kahneman)
"Avoid losing X" converts better than "Gain X."
- "Stop losing 3 hours/week to manual work" > "Save 3 hours/week"
- Use sparingly — overuse feels manipulative

---

## 3. CRO (Conversion Rate Optimization) Principles

### 3.1 Above-the-Fold Checklist
The hero section must answer 3 questions in under 5 seconds:
1. **What is this?** — Clear product name / category
2. **Who is it for?** — Target user stated or implied
3. **What do I do next?** — One obvious CTA

Rule: If a user can't answer these 3 questions without scrolling, the hero has failed.

### 3.2 CTA Optimization Rules

**Copy:**
- Verb-first: "Start free", "Get instant access", "Try it now"
- Outcome-focused: "See my dashboard" > "Submit"
- First-person performs better: "Start my free trial" > "Start your free trial"
- Remove friction words: "Sign up" implies commitment. "Get started" implies low friction.

**Placement:**
- Hero: above the fold, always
- After each major section (features, pricing) — repeat the primary CTA
- Sticky header CTA appears after user scrolls past the hero CTA

**Visual:**
- Primary: brand color, high contrast, ≥ 44px height
- Secondary: outline or ghost style — visually subordinate
- Whitespace around CTA: at least 24px padding around the button

### 3.3 Pricing Page Psychology

```
Recommended tier structure:
┌─────────┬─────────────────┬──────────┐
│  Free   │   Pro ⭐        │Enterprise│
│  $0/mo  │  $X/mo          │ Contact  │
│         │  [MOST POPULAR] │          │
└─────────┴─────────────────┴──────────┘
```

Rules:
- Always highlight 1 tier as "Most Popular" or "Recommended" — removes decision paralysis
- Annual vs Monthly toggle: show annual by default (higher revenue)
- Free tier: list 3-4 limitations explicitly — drives upgrades
- Pro tier: list 8-10 features — creates perceived value density
- Money-back guarantee: add "14-day money-back guarantee" to remove risk

### 3.4 Trust Signals by Funnel Stage

| Stage | Trust Signal |
|-------|-------------|
| Landing → Signup | Social proof, company logos, user count |
| Signup → First use | Email confirmation UX, onboarding tone |
| First use → Paid | "Your data is yours" privacy note, upgrade prompt timing |
| Paid → Retained | Success milestones, usage stats shown to user |

---

## 4. Brand Voice Framework

### 4.1 Tone-of-Voice Spectrum
Every product should pick a position on each axis:

```
Formal ◄──────────────────► Casual
Professional ◄────────────► Friendly
Technical ◄───────────────► Accessible
Serious ◄─────────────────► Playful
```

### 4.2 Voice Profile by Product Type

| Product Type | Tone | Example Headline |
|-------------|------|-----------------|
| B2B SaaS | Professional + Clear | "Automate your approval workflow in minutes" |
| Consumer App | Friendly + Warm | "Your mornings, finally under control" |
| Dev Tool | Direct + Technical | "Ship type-safe APIs without the boilerplate" |
| Creator Tool | Expressive + Inspiring | "Turn your ideas into work you're proud of" |
| Productivity | Calm + Empowering | "Focus on what matters. Let us handle the rest." |

### 4.3 Voice Consistency Checklist
- [ ] Same tone in: headline, button copy, error messages, email subject lines
- [ ] Error messages: never blame the user ("Something went wrong" > "You did something wrong")
- [ ] Success messages: match energy to the moment (low-key for routine, enthusiastic for milestones)
- [ ] Onboarding copy: warmer and more encouraging than the rest of the product

---

## 5. Microcopy Library

Critical copy that developers frequently write wrong. These are templates.

### 5.1 Error Messages

**Form validation:**
```
❌ "Invalid input"
✅ "Email must include '@' — e.g., name@example.com"

❌ "Password too short"
✅ "Password must be at least 8 characters"

❌ "Error 422"
✅ "That email is already in use. Sign in instead?"
```

**System errors:**
```
500: "Something went wrong on our end. We're looking into it. Try refreshing."
404: "We can't find that page. [Go to dashboard →]"
Network: "No internet connection. Your work is saved locally."
```

### 5.2 Empty States

Every list, table, or dashboard must have a designed empty state.

```
Structure:
[Illustration or icon — 64-80px]
[Headline — what's missing: "No projects yet"]
[Sub-copy — what to do: "Create your first project to get started"]
[Primary CTA — action button: "Create project"]
```

Templates by context:
```
Empty dashboard:    "Your workspace is ready. Add your first [item] to begin."
Empty search:       "No results for '[query]'. Try a different keyword."
Empty notification: "You're all caught up! No new notifications."
Empty activity:     "No activity yet. Invite your team to get started."
```

### 5.3 Loading States
```
Skeleton:  Use for pages that load data (dashboard, lists) — reduces perceived wait
Spinner:   Use for user-triggered actions (button clicks, form submits)
Progress:  Use for multi-step operations (file uploads, bulk operations)

Copy during loading:
❌ "Loading..."
✅ "Fetching your data..." or no text (skeleton speaks for itself)
```

### 5.4 Confirmation Dialogs

```
Destructive action pattern:
Title: "Delete [item name]?"
Body: "This will permanently remove [item] and cannot be undone."
Confirm button: "Delete [item]"  ← red, specific
Cancel button: "Cancel"          ← left, secondary style
```

### 5.5 Onboarding Microcopy
```
Welcome screen:    "Welcome to [Product]! Let's set up your workspace in 2 minutes."
Progress indicator: "Step 2 of 3 — Almost there"
Skip option:        "Skip for now" (never hide this)
Completion:         "You're all set! Here's your dashboard."
First empty state:  "👋 Your [items] will appear here. Let's add your first one."
```

---

## 6. Pattern Library

### 6.1 Landing Page Variants

**Pattern A: Problem-Led Hero**
Best for: B2B, productivity tools
```
[Pain point as H1: "Stop losing deals to slow follow-ups"]
[Solution as subheadline: "CRM that sends follow-ups automatically, so you close faster"]
[CTA] [Secondary: "See how it works"]
```

**Pattern B: Outcome-Led Hero**
Best for: Consumer apps, creator tools
```
[Desired outcome as H1: "Ship your side project in 14 days"]
[Mechanism as subheadline: "AI-powered sprint system built for indie makers"]
[CTA]
```

**Pattern C: Comparison-Led Hero**
Best for: Products replacing a manual process
```
[Before/After as H1: "From spreadsheet chaos to automated clarity"]
[Tool positioning: "Built for operations teams stuck in Excel"]
[CTA]
```

### 6.2 Dashboard Layout Patterns

**Pattern: Overview-First**
Use when: Users need a summary before taking action (analytics, monitoring)
```
Top row:    Key metric cards (4 KPIs)
Middle:     Primary data table or chart
Bottom:     Recent activity / notifications
Sidebar:    Navigation + user profile
```

**Pattern: Task-First**
Use when: Users come to complete specific tasks (project management, to-do)
```
Left panel:  Task list / queue
Right panel: Task detail / editor
Header:      Filters, create button, search
```

**Pattern: Feed-First**
Use when: Content discovery is the primary value (marketplaces, social)
```
Top:    Search + filters
Center: Card grid (masonry or uniform)
Right:  Recommendation sidebar (desktop only)
```

### 6.3 Onboarding Flow Patterns

**Pattern: Wizard**
Use when: Initial setup requires multiple decisions (e.g., SaaS with roles/settings)
```
Step 1: Account basics (name, role) — 2 fields max
Step 2: Primary goal selection — radio buttons, 3-4 options
Step 3: Invite team (optional, show Skip) — email inputs
→ Dashboard with welcome state
```

**Pattern: Empty State First**
Use when: Product value is experienced by using it (notes, CRM, project tool)
```
→ Dashboard immediately after signup
→ Giant empty state with "Create your first [item]" CTA
→ Value reveals through use
```
Best for: Simple products. Avoids over-engineering onboarding.

**Pattern: Interactive Tour**
Use when: Dashboard is complex and non-obvious
```
→ Dashboard
→ Tooltip overlay: "This is your inbox" [Next]
→ Tooltip: "Create tasks here" [Next]
→ Tooltip: "Track progress here" [Done]
```
Keep to 3-5 steps max. Every additional step loses 20% of users.

---

## 7. Motion & Interaction Principles

### 7.1 When to Use Animation

| Use | Avoid |
|-----|-------|
| Loading states (skeleton shimmer) | Purely decorative page entrance animations |
| State transitions (modal open/close) | Auto-playing video/animation in hero |
| Micro-interactions (button press, toggle) | Hover animations on mobile (they don't work) |
| Success feedback (form submit) | Long animations > 400ms |
| Error shake (form validation fail) | Parallax scrolling (accessibility risk) |

### 7.2 Duration Rules
```
Micro-interactions:  100-200ms  (button press, toggle, checkbox)
Component enter/exit: 200-300ms  (modal, sheet, dropdown)
Page transitions:    300-400ms  (route changes)
Never exceed:        400ms for UI transitions
```

### 7.3 Framer Motion Patterns (Next.js)
```tsx
// Standard fade-in for page sections
const fadeIn = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
}

// Stagger for lists/card grids
const stagger = {
  visible: { transition: { staggerChildren: 0.08 } }
}

// Modal enter/exit
const modal = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, scale: 0.95, transition: { duration: 0.15 } }
}
```

### 7.4 Accessibility: Respect `prefers-reduced-motion`
```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```
Or in Framer Motion:
```tsx
const { prefersReducedMotion } = useReducedMotion()
```

---

## 8. Dark Mode System

### 8.1 Token Pair Architecture
```css
:root {
  /* Light mode */
  --bg-base:       #ffffff;
  --bg-subtle:     #f8fafc;   /* slate-50 */
  --bg-muted:      #f1f5f9;   /* slate-100 */
  --text-primary:  #0f172a;   /* slate-900 */
  --text-secondary:#475569;   /* slate-600 */
  --text-muted:    #94a3b8;   /* slate-400 */
  --border:        #e2e8f0;   /* slate-200 */
  --border-strong: #cbd5e1;   /* slate-300 */
}

.dark {
  --bg-base:       #0f172a;   /* slate-900 */
  --bg-subtle:     #1e293b;   /* slate-800 */
  --bg-muted:      #334155;   /* slate-700 */
  --text-primary:  #f8fafc;   /* slate-50 */
  --text-secondary:#cbd5e1;   /* slate-300 */
  --text-muted:    #64748b;   /* slate-500 */
  --border:        #1e293b;   /* slate-800 */
  --border-strong: #334155;   /* slate-700 */
}
```

### 8.2 Dark Mode Decision Tree
```
Product type = Dev Tool → Default dark mode
Product type = B2B SaaS → System preference follower (dark/light toggle)
Product type = Consumer → Default light, optional dark
Timeline = MVP/Phase 2 → Define tokens now, implement dark later
```

### 8.3 Tailwind Dark Mode Setup
```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',  // Toggle via 'dark' class on <html>
}
```
```tsx
// next-themes setup (recommended)
// layout.tsx
import { ThemeProvider } from 'next-themes'
<ThemeProvider attribute="class" defaultTheme="system" enableSystem>
```

---

## 9. Design Decision Trees

### 9.1 Navigation Pattern Selection
```
├─ Features count ≤ 4?
│   └─ YES → Tab bar (mobile) / Header nav (desktop)
│   └─ NO →
│       ├─ B2B / data-heavy?
│       │   └─ YES → Sidebar layout
│       └─ NO (consumer/content)?
│           └─ YES → Header nav + hamburger sheet
│
└─ Mobile-primary product?
    └─ YES → Bottom tab bar (4 tabs max)
    └─ NO  → Top navigation
```

### 9.2 Color Selection Decision Tree
```
Brand feeling interview result:
├─ "Trust / Professional" → indigo-600 or blue-600
├─ "Creative / Energy" → violet-600 or purple-600
├─ "Growth / Nature" → emerald-600 or teal-600
├─ "Warm / Approachable" → orange-600 (check: amber-600 borderline)
└─ "Minimal / Neutral" → slate-800 (safe, always works)

Verification step (ALWAYS):
→ WebAIM check: [chosen color] on #ffffff
→ Must be ≥ 4.5:1
→ If fail: go one shade darker (600 → 700)
```

### 9.3 Layout Density Decision Tree
```
Target user is...
├─ Professional, data-focused (B2B) → High density: tighter padding, more info
├─ Consumer, casual → Low density: generous whitespace, breathing room
└─ Developer → Variable: dense code blocks, spacious prose
```

---

## 10. v0.dev Prompt Templates

Ready-to-use prompts for generating components quickly.

### 10.1 Landing Page Hero
```
Create a landing page hero section using Next.js, Tailwind CSS, and shadcn/ui.
Product: [PRODUCT_NAME] — [ONE_LINE_DESCRIPTION]
Target user: [TARGET_USER]
Brand color: [TAILWIND_COLOR] (e.g., violet-600)
Font: Plus Jakarta Sans for headings, Inter for body

Hero should include:
- Navbar: logo left, navigation links center, primary CTA button right
- H1: "[HEADLINE]" (large, bold, Plus Jakarta Sans)
- Subheadline: "[SUBHEADLINE]"
- Primary CTA button: "[CTA_TEXT]" in [BRAND_COLOR]
- Secondary CTA: "[SECONDARY_CTA]" ghost style
- Social proof row: "[N] teams already using [PRODUCT]"
- Subtle gradient background: white to [BRAND_COLOR]-50

Mobile responsive. Clean, minimal, professional.
```

### 10.2 Pricing Section
```
Create a 3-tier pricing section using Next.js, Tailwind CSS, and shadcn/ui.
Brand color: [TAILWIND_COLOR]

Tiers:
- Free: $0/mo — [3-4 features]
- Pro (HIGHLIGHT THIS): $[X]/mo — [6-8 features]
- Enterprise: Contact sales — [3-4 features]

Design:
- Pro tier has a border in [BRAND_COLOR] with "Most Popular" badge
- Annual/Monthly toggle at the top
- Each tier is a Card with a prominent price, feature list with checkmarks, and a CTA button
- Pro CTA: filled [BRAND_COLOR] button
- Free/Enterprise CTA: outline button
```

### 10.3 Dashboard Sidebar Layout
```
Create a responsive dashboard layout using Next.js App Router, Tailwind CSS, and shadcn/ui.

Desktop: sidebar (w-64, bg-slate-900 text-white) + main content area
Mobile: Sheet component slides in from left on hamburger menu tap

Sidebar includes:
- Logo top-left
- Navigation items: [LIST_ITEMS] — each with Lucide icon + label
- Active state: [BRAND_COLOR] background pill
- Bottom: user avatar + name + settings link

Main area: white background, top header with page title and action button
```

### 10.4 Feature Section (3 Cards)
```
Create a features section with 3 cards using Tailwind CSS and shadcn/ui.

Features:
1. Icon: [LUCIDE_ICON] | Title: [TITLE] | Description: [1-2 sentences, outcome-focused]
2. Icon: [LUCIDE_ICON] | Title: [TITLE] | Description: [1-2 sentences]
3. Icon: [LUCIDE_ICON] | Title: [TITLE] | Description: [1-2 sentences]

Design: 3-column grid (1-col on mobile, 3-col on md+)
Each card: white bg, subtle shadow, icon in [BRAND_COLOR]-100 circle, clean padding
Section heading above: "[SECTION_H2]" + "[SECTION_SUBTITLE]" centered
```

---

## 11. Design Critique Framework

When reviewing an existing design (screenshot, description, or URL):

### 11.1 Critique Checklist
```
Level 1 — Must Fix (blocks conversion or accessibility)
□ Hero doesn't answer "What is this / Who is it for / What do I do next"
□ Primary CTA is not visually dominant
□ Color contrast fails WCAG AA
□ Mobile layout broken or unusable
□ Form has no visible labels

Level 2 — Should Fix (hurts conversion)
□ More than 1 primary CTA per section
□ No social proof above pricing
□ Pricing page has no highlighted recommendation
□ Empty states not designed
□ Error states not designed

Level 3 — Nice to Fix (polish)
□ Spacing inconsistency (non-8px values)
□ Font scale inconsistency
□ Animation > 400ms
□ Dark mode tokens not defined
```

### 11.2 Critique Output Format
```markdown
## Design Review: [Page/Component]

### ⛔ Must Fix
1. [Issue] — [Why it matters] — [Fix]

### ⚠️ Should Fix
1. [Issue] — [Why it matters] — [Fix]

### 💡 Nice to Fix
1. [Issue] — [Fix]

### ✅ Working Well
- [Strength 1]
- [Strength 2]

**Priority**: Fix [Level 1 items] before launch. [Level 2 items] within first week post-launch.
```

---

## 12. OG Image & Brand Asset Specs

### 12.1 Required Brand Assets for Launch
```
favicon.ico          16×16, 32×32, 48×48 (multi-size ICO)
favicon.svg          Scalable version (modern browsers)
apple-touch-icon     180×180 PNG (no rounded corners — iOS adds them)
og-image.png         1200×630 PNG (Open Graph / Twitter Card)
og-image-square.png  400×400 PNG (for some social platforms)
```

### 12.2 OG Image Design Rules
```
Content: Product name + tagline + brand color background
Safe zone: 60px inset on all sides (content must stay inside)
Text: White on dark background, or dark on light background
Contrast: Must pass 4.5:1 (people screenshot these)
No: Small text (<24px), complex illustrations, animated GIFs

v0.dev OG prompt:
"Design a 1200×630 open graph image. Background: [BRAND_COLOR].
Product name '[PRODUCT]' in large white text (Plus Jakarta Sans Bold).
Tagline '[TAGLINE]' in white, smaller. Simple, clean, professional."
```

---

## 13. Performance-Aware Design Decisions

### 13.1 Image Format Decision Tree
```
Photo / complex image:
├─ Is animation needed? → GIF → No. Use WebP with animation or Lottie
└─ Static photo → WebP (30-50% smaller than PNG/JPG)

Icon / logo / illustration:
├─ Can it be an SVG? → YES → Always use SVG (infinitely scalable, tiny file)
└─ Must be raster → PNG → convert to WebP

In Next.js:
→ Always use <Image> component (auto-WebP conversion, lazy loading, blur placeholder)
→ Priority={true} only for above-the-fold hero image
```

### 13.2 Font Loading Strategy
```html
<!-- In <head> — preconnect before font stylesheet -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- font-display: swap prevents invisible text during load -->
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
```

### 13.3 Skeleton vs Spinner Decision
```
Skeleton:
- Page-level data loading (dashboard, list pages)
- Content that has a known shape
- When load time > 300ms (prevents layout shift)

Spinner:
- User-triggered point actions (button click, form submit)
- Short operations < 2 seconds
- When content shape is unknown

Neither (optimistic UI):
- Low-risk instant operations (like/bookmark, checkbox toggle)
- Update UI immediately, revert on error
```

---

*Knowledge base for Vera — Full-Stack Designer*
*Pairs with: `design-guide.md` (non-negotiable rules)*
