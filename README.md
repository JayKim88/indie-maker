# Indie Maker

> AI-powered sprint system for indie makers — from idea to Kill/Go in 29 days.
> Powered by 12 specialized Claude Code skills covering every phase of the indie sprint.

---

## What is this?

A Claude Code skill system that automates the cognitive work of each sprint phase — market research, planning, UX, design, build, launch, and growth — so you can focus on judgment and execution.

**Target product stack**: Next.js + Tailwind + shadcn/ui + Supabase + Stripe + Vercel (Web SaaS)
**Runtime**: Claude Code (all skills run inside Claude Code sessions)
**Timeline**: D1-D6 (AI-accelerated) → D7-D29 (community/human-dependent)

---

## Full Sprint Map

```mermaid
flowchart TD
    subgraph row1[" "]
        direction LR
        A["Phase -1<br/>Market Research<br/>(optional)"] --> B["Phase 0+1<br/>Idea + Planning<br/>D1"] --> C["Phase 1.5<br/>UX Sprint<br/>D1 PM"] --> D["Phase 2<br/>Design<br/>D2"] --> E["Monetize<br/>Pricing<br/>D2–D3"]
    end
    subgraph row2[" "]
        direction RL
        H["Phase 6<br/>Launch Day<br/>D14"] --> G["Phase 5<br/>Launch Prep<br/>D7–D13"] --> F["Phase 3–5<br/>Build + Deploy<br/>D3–D6"]
    end
    subgraph row3[" "]
        direction LR
        I["Phase 7<br/>Post-Launch<br/>D15–D28"] --> J{{"Kill/Go<br/>Gate D29"}}
        J -->|Go| K["Phase 8+<br/>Growth<br/>D30+"]
        J -->|Kill| L["Phase 9<br/>Retro<br/>D29"]
    end

    E --> H
    F --> I

    style A fill:#f5f5f5,stroke:#999
    style J fill:#ffe0b2,stroke:#e65100
    style K fill:#c8e6c9,stroke:#2e7d32
    style L fill:#ffcdd2,stroke:#c62828
```

---

## Two Entry Paths

```mermaid
flowchart TD
    subgraph PA["Path A — Full Research First (권장)"]
        direction LR
        A1["/indie-market-researcher<br/>Desire-based research"] --> A2["/indie-planner<br/>Full interview"]
    end
    subgraph PB["Path B — Idea First, Validate Mid-Sprint"]
        direction LR
        B1["/indie-planner<br/>Q1–Q2 only"] --> B2["/indie-market-researcher<br/>--validate mode"] --> B3["/indie-planner<br/>Q3+ continues"]
    end

    A2 --> Merge["Both paths merge here<br/>/indie-ux → /indie-designer → Build → Launch"]
    B3 --> Merge

    style Merge fill:#e3f2fd,stroke:#1565c0
```

---

## Document Flow

```mermaid
flowchart TD
    R["research/*.md"]
    DV["demand-validation.md<br/>(Path B only)"]
    IC["idea-canvas.md"]
    PL["prd-lean.md"]
    UX["ux-flow.md"]
    WF["wireframes.md"]
    DB["design-brief.md"]
    LC["landing-copy.md"]
    PS["pricing-strategy.md"]
    MVP["Working MVP<br/>(live URL)"]
    LP["launch-plan.md<br/>bip-posts.md"]
    LIVE["Live Product"]
    KG["kill-go-report.md"]

    R --> IC
    IC --> PL
    DV -->|validates| PL
    PL --> UX
    UX --> WF
    UX --> DB
    DB --> LC
    PL --> PS
    WF --> MVP
    LC --> MVP
    PS --> MVP
    MVP --> LP
    LP --> LIVE
    LIVE --> KG

    KG --> Gate{D29 Gate}
    Gate -->|Go| GR["growth-experiments.md<br/>channel-strategy.md"]
    Gate -->|Kill| RT["retrospective.md<br/>lessons.md"]
    RT -->|next cycle| R

    style Gate fill:#ffe0b2,stroke:#e65100
    style GR fill:#c8e6c9,stroke:#2e7d32
    style RT fill:#ffcdd2,stroke:#c62828
```

---

## Skill Reference

| #   | Skill                      | Agent | Phase  | When to Run               | Output                                |
| --- | -------------------------- | ----- | ------ | ------------------------- | ------------------------------------- |
| 1   | `/indie-market-researcher` | Max   | -1     | Before any idea is set    | `docs/indie-market-researcher/`       |
| 2   | `/indie-planner`           | Reid  | 0+1    | D1 morning                | `docs/indie-planner/`                 |
| 3   | `/indie-ux`                | Kai   | 1.5    | D1 afternoon              | `docs/indie-ux/`                      |
| 4   | `/indie-designer`          | Vera  | 2      | D2                        | `docs/indie-designer/`                |
| 5   | `/indie-monetize`          | Finn  | 2–3    | D2–D3, before Stripe code | `docs/indie-monetize/`                |
| 6   | `/indie-frontend`          | Rex   | 3–5    | D3–D6 continuous          | — (interactive guide)                 |
| 7   | `/indie-backend`           | Axel  | 3–5    | D3–D6 continuous          | — (interactive guide)                 |
| 8   | `/indie-infra`             | Sam   | 3–5+6  | D6 QA + deploy            | — (guide + QA checklist)              |
| 9   | `/launch-kit`              | —     | 5      | D7, before indie-launcher | `launch-kit-output.md`                |
| 10  | `/indie-launcher`          | Leo   | 5      | D7–D13                    | `docs/indie-launcher/`                |
| 11  | `/indie-analyst`           | Nova  | 7+Gate | D21–D29                   | `docs/indie-analyst/`                 |
| 12  | `/indie-growth`            | Gio   | 8+ Go  | D30+                      | `docs/indie-growth/`                  |
| —   | `/indie-retro`             | Sage  | 9 Kill | D29 Kill verdict          | `docs/indie-retro/`                   |

---

## Kill/Go Gate (D29)

```mermaid
flowchart TD
    M["D29 Metrics Check"]

    M --> PH["PH votes"]
    M --> PA["Paid users"]
    M --> MR["MRR D21"]
    M --> RE["Retention"]
    M --> RV["Reviews"]

    PH & PA & MR & RE & RV --> V{Verdict}

    V -->|"Kill<br/>PH&lt;50 / paid=0<br/>MRR=$0 / ret&lt;10%"| K["/indie-retro<br/>retrospective.md<br/>lessons.md"]
    V -->|"Watch<br/>borderline"| W["Extend 30 days<br/>+ diagnose bottleneck"]
    V -->|"Go<br/>PH&gt;200 / paid≥4<br/>MRR&gt;$50 / ret&gt;30%"| G["/indie-growth<br/>growth-experiments.md<br/>channel-strategy.md"]

    style V fill:#ffe0b2,stroke:#e65100
    style K fill:#ffcdd2,stroke:#c62828
    style W fill:#fff9c4,stroke:#f9a825
    style G fill:#c8e6c9,stroke:#2e7d32
```

---

## Parallel Pipeline (3 Products)

```mermaid
gantt
    title 3-Product Parallel Pipeline (1-week stagger)
    dateFormat YYYY-MM-DD
    axisFormat W%W

    section Product A
    Build D1-D6        :a1, 2024-01-01, 6d
    Launch Prep D7-D13 :a2, after a1, 7d
    Post-Launch D14-D28 :a3, after a2, 15d
    Kill/Go D29        :milestone, after a3, 0d

    section Product B
    Build D1-D6        :b1, 2024-01-08, 6d
    Launch Prep D7-D13 :b2, after b1, 7d
    Post-Launch D14-D28 :b3, after b2, 15d
    Kill/Go D29        :milestone, after b3, 0d

    section Product C
    Build D1-D6        :c1, 2024-01-15, 6d
    Launch Prep D7-D13 :c2, after c1, 7d
    Post-Launch D14-D28 :c3, after c2, 15d
    Kill/Go D29        :milestone, after c3, 0d
```

> Staggered 1 week → bi-weekly launch rhythm → up to 12 experiments/year

---

## Knowledge Base

| Document                      | Content                                                     |
| ----------------------------- | ----------------------------------------------------------- |
| `knowledge/design-guide.md`   | Design system, WCAG AA, 8px grid, Atomic Design             |
| `knowledge/frontend-guide.md` | Next.js App Router, RSC rules, TypeScript strict, a11y      |
| `knowledge/backend-guide.md`  | Supabase, REST, OWASP Top 10, RLS patterns                  |
| `knowledge/infra-guide.md`    | Vercel, 12-Factor App, security hardening, observability    |
| `knowledge/automate-guide.md` | Email drip (Resend + pg_cron), Stripe webhooks, MRR view    |
| `knowledge/tech-stack.md`     | Canonical stack constraints — do not deviate without reason |

---

## Sprint Principles

1. **Kill criteria first** — set the D29 numbers before writing a line of code
2. **Pre-sale before build** — 3+ people pay → build; 0 pay → don't build
3. **One core flow only** — anything else goes to `backlog.md`
4. **Ship when it works** — perfection is the enemy of launch
5. **Automate after $100 MRR** — manual before that, or you're optimizing too early
6. **Kill = data, not failure** — run `/indie-retro` to extract learning for the next sprint

---

## Getting Started

```bash
# Option A: Start with market research (recommended)
/indie-market-researcher

# Option B: Start with an idea you already have
/indie-planner

# Mid-sprint: validate demand before committing to build
/indie-market-researcher --validate

# Need help at a specific phase?
/indie-ux           # UX + wireframes
/indie-designer     # Brand + landing copy
/indie-monetize     # Pricing strategy + first paying customer
/indie-backend      # Supabase + Stripe + API questions
/indie-launcher     # PH + Reddit + HN + Discord launch system
/indie-analyst      # Kill/Go analysis (run D21–D29)
```

---

## Reference

- [`indie-sprint-playbook.md`](indie-sprint-playbook.md) — Detailed phase-by-phase playbook
- [`CLAUDE.md`](CLAUDE.md) — Skill scope and system instructions
- [`knowledge/`](knowledge/) — Technical reference documents
