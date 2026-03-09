# DevJob AI — Planning - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `local-only/project-ideas/devjob-ai-product-idea-2026-03-07.md` + `projects/devjob-ai/docs/indie-planner/`

## Session: 2026-03-09 23:23

> **Context**: MODULE 1+2 deep-dive — partner concept expansion, FastAPI architecture decision, and product philosophy reframe from "tool" to "파트너 (career partner)"

### Done
- feat: updated 1-1 output definition — changed from "포지션 방향 3개" to actual JD listings (company name, position, match score, gap summary); flagged v2 dependency on Job API
- feat: added 1-3 Market Intelligence to service map with two views — View A (common pattern analysis across JDs), View B (personalized comparison ranking)
- feat: expanded MODULE 1 with three new sub-features — 1-4 Readiness Coach & Evaluation (prep roadmap → tracking → result eval → Readiness Signal), 1-5 Company Intelligence (v2+), 1-6 JD Freshness & Timing Alerts (v2+)
- feat: rewrote MODULE 2 with Before/During/After framework — enhanced 2-1 (quality diagnosis + global format conversion), added ATS optimization to 2-2, added 2-4 (resume ↔ cover letter consistency check), added 2-5 (version management & outcome tracking)
- docs: documented FastAPI hybrid architecture with explicit rationale table — MVP uses Next.js API Routes only; FastAPI added at D7+ for PDF parsing, batch JD processing, RAGAS eval, Voice Pipeline
- chore: synced prd-lean.md Profile Builder description to reflect PDF parsing as primary, form as fallback
- docs: read and analyzed user-updated idea document — Origin Story section added, product philosophy reframed to "파트너" ("혼자가 아니다는 경험")
- chore: established partner-lens evaluation framework for remaining modules — "What would a genuine partner do that no tool does?"

### Decisions
- **FastAPI architecture**: MVP = Next.js API Routes only (zero infra overhead, single JD analysis completes within 10s); FastAPI on Railway added at D7+ specifically for pdfplumber (PDF parsing superiority), Vercel 60s timeout avoidance, RAGAS/LangChain (Python-only), Voice Pipeline (Whisper + VAD)
- **Module scope**: MODULE 1+2 are MVP core; Modules 3-5 are distinct product categories → roadmap only, not MVP
- **P0.5 Partner Layer**: Formally added to MVP scope between P0 (intelligence) and P1 (generation) — 1-4a/b/c/d at D11-D14; prevents the "analyzed gap, now what?" dead end
- **Product philosophy**: Reframed from "AI tool" to "career partner" — every feature must have an After loop (not just generation); partner initiates interaction, not user; "파트너가 먼저 말을 건다" design principle established
- **Partner-lens gaps identified**: MODULE 3 needs active evaluation (not checklist), MODULE 4/4-3 needs progress tracking (not just curation), MODULE 5 needs verdict (not just data)

### Issues
- Edit tool failed on Korean text encoding mismatch ("찾고 싶어요" vs "찾고 있어요") — resolved by Grep-first to extract exact string before editing

### Next
- [ ] Sync prd-lean.md with all latest decisions: 1-3 Market Intelligence, 1-4 Readiness Coach, 2-4/2-5 additions, FastAPI architecture table, P0.5 scope
- [ ] Decide MODULE 3 direction from partner perspective: 3-1 connects to 1-4c evaluation loop (skip or merge?); 3-2 needs active portfolio evaluation, not a checklist
- [ ] Decide whether MODULE 3 is MVP or roadmap
- [ ] Run `/indie-ux` once idea document and prd-lean.md are finalized
