# Senior Reference

> Knowledge documents that are **NOT used by indie-maker SKILLs**, but preserved as senior-level reference material and for non-default stacks.

---

## Why this folder exists

The indie-maker default stack is **Supabase + Next.js App Router** (see `knowledge/tech-stack.md`).
The 14 indie-* SKILLs reference `knowledge/{frontend,backend,...}-guide.md` and `full-stack-*.md` files that match this stack.

These principles/senior documents target different contexts:

| File | Stack | Purpose |
|------|-------|---------|
| `frontend-senior-guide.md` | indie stack (Next.js + Tailwind + shadcn/ui) | Structured senior reference with Philosophy + Quick Decision Guide — alternative to the recipe-style `frontend-guide.md`. Use for learning / decision rationale, not as SKILL input. |
| `frontend-principles.md` | Next.js + React Native + Apollo Client + Supabase + Vitest + Storybook | Larger-team frontend principles. Includes JavaScript fundamentals (closures, prototypes, execution context). Reference when reviewing senior-level concepts. |
| `backend-principles.md` | TypeScript + Node 20 + **NestJS** + Postgres + Prisma + Redis + BullMQ + Docker | Non-Supabase backend stack. Applicable to projects like Pulse that use NestJS. Includes a "Frontend → Backend learning path" section. |

## When to use

- **SKILL execution**: do NOT reference these files. SKILLs use `knowledge/{frontend,backend,infra,design}-guide.md`.
- **Project on a non-default stack** (e.g. Pulse on NestJS): manually reference `backend-principles.md` during planning/build phases.
- **Senior learning / interview prep**: read these to deepen understanding of fundamentals.

## Reactivation criteria

If a project's stack consistently diverges from Supabase + Next.js, consider:
1. Promoting the relevant principles document to the parent `knowledge/` folder under a stack-specific name (e.g., `backend-guide-nestjs.md`)
2. Creating a stack-specific SKILL variant
3. Or replacing the default — only after 2+ projects validate the new stack as primary

## Review schedule

Re-evaluate this folder on **2026-08-12** (3 months after creation):
- Files unused by any project → delete
- Files actively referenced by a project → promote to `knowledge/`
