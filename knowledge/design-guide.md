# Indie Maker Design Guide

Design system reference for indie MVP development.
Goal: Establish brand identity, component system, and layout rules in one day.

---

## Non-Negotiable Rules

Rules every senior designer enforces regardless of timeline or budget.
Sources: WCAG 2.1, Atomic Design (Brad Frost), Nielsen Norman Group, Apple HIG, Material Design.

### Color & Contrast
1. **WCAG AA contrast is the floor, not the ceiling** — Normal text (< 18pt): 4.5:1 minimum against background. Large text (≥ 18pt or ≥ 14pt bold): 3:1 minimum. UI components (buttons, inputs, icons): 3:1. Check with [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/).
2. **Color alone never conveys meaning** — Never use color as the sole indicator of status, error, or information. Colorblind users (8% of males) will miss it. Pair color with an icon, text label, or pattern.
3. **Limit your palette** — Primary (1 color), Neutral (1 family: slate/gray/zinc), Semantic (success, warning, error). Every additional color increases cognitive load and implementation complexity.
4. **Design tokens first, hardcoded values never** — Define color, spacing, radius, and shadow as tokens before writing any component. Tokens enable one-place updates; hardcoded values require find-and-replace across the codebase.

### Spacing & Layout
5. **8px grid system — zero exceptions** — All spacing values must be multiples of 8: 8, 16, 24, 32, 48, 64, 80, 96. Use 4px only for micro-gaps within components. Arbitrary pixel values (13px, 27px) indicate broken design and make systems unmaintainable.
6. **Mobile layout first, always** — Design the smallest viewport (375px) first. Progressive enhancement for larger screens. Desktop-first "responsive" design consistently produces broken mobile UX. It costs 3x more to fix post-launch.
7. **Touch targets minimum 44×44px** — Every tappable element must be at least 44×44px (Apple HIG) or 48×48dp (Material Design). Smaller targets cause 40%+ tap error rates on mobile devices.

### Typography
8. **Maximum 2 font families** — One for display/headings, one for body. Never more unless brand guidelines explicitly require it. Every additional font is a network request, a rendering cost, and a visual inconsistency risk.
9. **Defined type scale only — no ad-hoc sizes** — Choose 6-8 sizes maximum. Every text in the product uses one of these sizes. No one-off font sizes. Consistent scale communicates hierarchy; arbitrary sizes break it.
10. **Line height rules are not suggestions** — Body text: 1.5 (WCAG recommends ≥ 1.5 for readability). Headings: 1.2. Display/hero text: 1.0-1.1. Browser default (1.0) for body copy is unacceptable.
11. **Maximum 3 font weights** — Regular (400), Semibold (500-600), Bold (700). Relying on more weights doesn't improve hierarchy; it adds visual noise and increases font load weight.

### Component Architecture
12. **Atomic Design hierarchy is non-negotiable** — Atoms (button, input, icon, badge) → Molecules (form field, search bar) → Organisms (header, pricing card) → Templates (page layouts) → Pages. Skip levels and you build unmaintainable one-off components.
13. **Every component has every state** — Default, Hover, Focus, Active, Disabled, Loading, Error. States discovered in production cost 5x more to fix than states designed upfront. No exceptions.
14. **Consistent border-radius across the system** — Pick one scale: sharp (0-2px), rounded (8px), or pill. Mixing arbitrary radii signals visual inconsistency and lack of system thinking.
15. **Whitespace is a design element, not an oversight** — Never fill empty space with decoration because it "looks empty." Intentional whitespace improves readability, focus, and perceived quality.

### Gestalt Principles (Required Application)
16. **Proximity groups related elements** — Elements physically closer together are perceived as belonging together. Unrelated elements need clear spatial separation. This is how users understand grouping without labels.
17. **Visual hierarchy through size and weight** — Users F-scan and Z-scan pages. The most important element must be visually dominant (larger, bolder, higher contrast). Treat all elements equally and nothing gets attention.
18. **Similarity creates pattern recognition** — Elements with consistent appearance are perceived as part of the same category. Use consistent styling for all items of the same type.

### Accessibility Baseline (WCAG 2.1 AA)
19. **Semantic HTML before ARIA** — `<button>`, `<nav>`, `<main>`, `<header>`, `<h1>-<h6>`, `<label>`, `<ul>`. ARIA supplements semantics; it doesn't replace them. A `<div role="button">` requires manual keyboard handling; a `<button>` provides it for free.
20. **Visible label on every input** — Placeholder text disappears when the user types. It is not a label. Every `<input>` needs a linked `<label>` via `for`/`id`. Placeholder is acceptable only as an example hint.
21. **Visible focus indicators everywhere** — Never remove `:focus` outline without replacing it with an equivalent. Keyboard users have no other way to know where they are. The replacement must meet 3:1 contrast.
22. **Heading hierarchy never skips** — h1 → h2 → h3, in order, always. Screen reader users navigate by headings. Skipping levels (h1 → h3) breaks the document structure.

---

## Color System

### MVP Color Formula

```
Primary:  1 color (your brand color)
Neutral:  slate / gray / zinc (text, backgrounds, borders)
Success:  green-500  (#22C55E)
Warning:  amber-500  (#F59E0B)
Error:    red-500    (#EF4444)
```

### Primary Color Quick Selection (Tailwind)

| Brand Feeling | Primary Color | Contrast on White |
|--------------|--------------|-------------------|
| Trust / Professional | blue-600, indigo-600 | ✅ 5.9:1 / 6.9:1 |
| Growth / Nature | emerald-600, teal-600 | ✅ 5.1:1 / 4.6:1 |
| Creative / Energy | violet-600, purple-600 | ✅ 5.9:1 / 7.4:1 |
| Warm / Approachable | orange-600, amber-600 | ✅ 4.5:1 / 4.6:1 |
| Minimal / Neutral | slate-800 | ✅ 13:1 |

> **Warning**: yellow-400, lime-400, cyan-300 fail WCAG AA on white. Use them only as accent, never as text or icon color.

### Design Token Naming

```css
/* Convention: [category]-[role]-[scale] */
:root {
  /* Colors */
  --color-primary-500: #7C3AED;
  --color-primary-600: #6D28D9;
  --color-neutral-50:  #F8FAFC;
  --color-neutral-900: #0F172A;
  --color-success:     #22C55E;
  --color-warning:     #F59E0B;
  --color-error:       #EF4444;

  /* Spacing (8px grid) */
  --space-1: 4px;   /* micro only */
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
  --space-7: 64px;
  --space-8: 96px;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;   /* default */
  --radius-lg: 12px;
  --radius-full: 9999px;
}
```

---

## Typography System

### Recommended Font Stacks

```
Display / Heading:  Plus Jakarta Sans, Outfit, Sora  (Google Fonts, free)
Body:               Inter  (Tailwind default, already optimized for Next.js)
Monospace:          JetBrains Mono  (only for code-related products)
```

### Type Scale (use only these sizes)

| Role | Size (px) | Weight | Line Height | Tailwind |
|------|----------|--------|-------------|---------|
| Display / Hero H1 | 48-60 | 700 | 1.1 | text-5xl/text-6xl font-bold |
| H1 | 36-40 | 700 | 1.2 | text-4xl font-bold |
| H2 | 24-30 | 600 | 1.2 | text-2xl/text-3xl font-semibold |
| H3 | 20-24 | 600 | 1.3 | text-xl/text-2xl font-semibold |
| Body Large | 18 | 400 | 1.5 | text-lg |
| Body (default) | 16 | 400 | 1.5 | text-base |
| Small / Caption | 14 | 400 | 1.5 | text-sm |
| Micro | 12 | 400 | 1.5 | text-xs |

### Tailwind Config

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      },
    },
  },
}
```

---

## shadcn/ui Component System

### Day-1 Installation

```bash
npx shadcn@latest init
# Prompts: Style → Default | Base color → Slate | CSS variables → Yes

# Core components (all MVPs need these)
npx shadcn@latest add button input card form label badge toast dialog dropdown-menu avatar
```

### Feature-Based Additions

```bash
# Data display
npx shadcn@latest add table tabs

# Forms & inputs
npx shadcn@latest add select textarea checkbox switch

# Navigation
npx shadcn@latest add sheet separator      # sheet = mobile slide-in sidebar

# Feedback & status
npx shadcn@latest add skeleton alert progress
```

### Component State Checklist

Before shipping any component, all states must exist:
- [ ] **Default** — base appearance
- [ ] **Hover** — cursor: pointer, subtle visual change
- [ ] **Focus** — visible outline (keyboard navigation)
- [ ] **Active / Pressed** — visual feedback on click/tap
- [ ] **Disabled** — reduced opacity, cursor: not-allowed, not interactive
- [ ] **Loading** — spinner overlay or skeleton replacement
- [ ] **Error** — red border, error message below
- [ ] **Empty** — for lists, tables, dashboards with no data

---

## Landing Page Structure (Standard Template)

```
[Navbar]
  Logo | Navigation links | Primary CTA button

[Hero Section]
  H1: Core value proposition (1-2 lines, starts with a verb or outcome)
  Subheadline: [Target user] who [current situation] can now [desired outcome]
  Primary CTA button + Secondary CTA (optional: "See demo" / "Learn more")
  Product screenshot or demo GIF (authentic > polished)

[Social Proof]   ← omit if zero users; add after launch
  "X teams already using" or real user avatars with short quotes

[Problem → Solution]
  3 concrete pain points the target user faces
  How this product addresses each one specifically

[Features]
  3 features: Lucide icon + bold title + 1-2 sentence description
  Focus on outcomes, not capabilities ("Save 2 hours/week" not "Has automation")

[How It Works]
  3-4 numbered steps with simple visuals

[Pricing]
  Free tier + Pro tier (or single tier with trial)
  Highlight the recommended plan

[FAQ]
  5-7 questions based on real objections to purchase

[Final CTA]
  Repeat the primary CTA with urgency or social proof

[Footer]
  Product name | Company | Privacy Policy | Terms of Service | Contact
```

---

## Core User Flow Wireframes

### Authentication Flow

```
Landing Page
  → [Sign Up CTA] → /signup
      Email + Password input
      → "Confirm your email" screen
          → User clicks email link
              → Onboarding (1-3 steps max)
                  → Dashboard

  → [Sign In] → /login
      Email + Password
      → Dashboard (if valid)
      → Error message (if invalid)
```

### Dashboard Layout

```
Desktop (md: and above):
┌────────────┬─────────────────────────────────┐
│  Sidebar   │  Main Content Area              │
│  (w-64)    │                                 │
│  - Logo    │  [Page Header]                  │
│  - Nav     │  [Primary Content]              │
│  - User    │  [Secondary Content]            │
└────────────┴─────────────────────────────────┘

Mobile (default):
┌─────────────────────────────────┐
│  [Hamburger] Logo  [User Avatar]│   ← Top navbar
├─────────────────────────────────┤
│  Main Content (full width)      │
└─────────────────────────────────┘
Sidebar = shadcn Sheet (slides in from left on hamburger tap)
```

### Responsive Breakpoints

```
Default (0px+):   Mobile layout, single column, full width
sm: (640px+):     2-column card grid, wider padding
md: (768px+):     Sidebar layout begins, desktop navigation
lg: (1024px+):    3-column card grid or expanded sidebar
xl: (1280px+):    max-width container centered (max-w-7xl mx-auto)
```

---

## Quick Reference Checklist

Run this before delivering any design artifact:

**Color**
- [ ] Primary color contrast ≥ 4.5:1 on white (verified with tool)
- [ ] Status indicators use icon + color, never color alone
- [ ] Maximum 3 primary colors used in the product

**Spacing**
- [ ] All spacing values are 8px multiples (8, 16, 24, 32, 48...)
- [ ] No arbitrary pixel values

**Typography**
- [ ] All font sizes from defined type scale
- [ ] Body line-height = 1.5
- [ ] Maximum 2 font families

**Accessibility**
- [ ] Touch targets ≥ 44×44px
- [ ] All inputs have visible `<label>` (not just placeholder)
- [ ] Focus states visible on all interactive elements
- [ ] Heading order: h1 → h2 → h3, no skipping

**Mobile**
- [ ] Mobile layout designed first (375px)
- [ ] No hover-only interactions on mobile

---

## Reference Tools

| Tool | Purpose | Cost |
|------|---------|------|
| v0.dev | AI component/page generation from prompt | Free credits |
| Figma | Wireframes, design system | Free plan |
| Canva | PH thumbnails, social images | Free plan |
| Lucide React | Icon library (1500+ icons) | Free, MIT |
| shadcn/ui | Component library | Free, MIT |
| WebAIM Contrast Checker | WCAG contrast validation | Free |
| Unsplash / Pexels | Stock photography | Free |
| Lottie (lottiefiles.com) | Animated illustrations | Free plan |
