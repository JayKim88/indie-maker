# MyTimeline Planning - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `my-timeline/`

## Session: 2026-03-07 22:34

> **Context**: Full Next.js MVP build — design system implementation, all core components, bug fixes (form state, infinite loop, dialog behavior), and project relocation into indie-maker monorepo.

### Done

- feat: ran indie-designer (Vera) — produced `docs/indie-designer/design-brief.md` (Stone+Amber, Pretendard font, oklch tokens) and `docs/indie-designer/landing-copy.md`
- feat: ran indie-frontend (Rex) — scaffolded new Next.js 16 project with Tailwind v4 + shadcn/ui Nova preset (Base UI)
- feat: implemented `src/app/globals.css` — `@theme inline` with oklch category color tokens and Pretendard Variable font
- feat: implemented `src/app/layout.tsx` — Pretendard CDN, Korean lang, OG metadata
- feat: implemented `src/app/page.tsx` — full landing page (Header, Hero, Features, FAQ, FinalCTA, Footer)
- feat: implemented `src/types/timeline.ts` — CATEGORIES, Category, CATEGORY_COLOR, TimelineEntry, Profile, date helpers
- feat: implemented `src/lib/storage.ts` — LocalStorage load/save/clear, URL hash encode/decode, buildShareUrl, entriesToCsv
- feat: implemented `src/store/timeline-store.ts` — Zustand store with subscribeWithSelector, all CRUD actions, derived selectors
- feat: implemented `src/lib/export.ts` — exportAsPng, exportAsPdf, exportAsHtml, downloadCsvTemplate
- feat: implemented `src/components/ui/form.tsx` — manual react-hook-form wrapper (FormProvider pattern) since Nova preset lacks it
- feat: implemented `src/components/layout/app-header.tsx` — sticky header, Import/Export modal triggers, Share handler
- feat: implemented `src/components/features/timeline/timeline-app.tsx` — root client component with Skeleton/BlankSlate/main branch
- feat: implemented `src/components/features/timeline/blank-slate.tsx` — profile input form with two CTAs
- feat: implemented `src/components/features/timeline/profile-header.tsx` — name/birthDate display, inline edit, +Add button
- feat: implemented `src/components/features/timeline/entry-form-dialog.tsx` — full entry form (Zod, category tabs, YYYY-MM dates, isCurrent)
- feat: implemented `src/components/features/timeline/entry-card.tsx` — card with color bar, edit/delete hover actions
- feat: implemented `src/components/features/timeline/timeline-chart.tsx` — SVG Gantt chart with year axis and entry bars
- feat: implemented `src/components/features/timeline/import-modal.tsx` — react-dropzone + papaparse CSV import with row-level validation
- feat: implemented `src/components/features/timeline/export-modal.tsx` — PDF/PNG/HTML format selector with progress bar
- fix: `Form` component changed from native `<form>` wrapper to `FormProvider` — resolved `useFormContext()` null crash
- fix: entry-form-dialog tab switching — added per-category value cache (`useRef`) to preserve/restore field values per tab
- fix: entry-form-dialog close behavior — `handleClose` resets form + clears cache; `disablePointerDismissal={true}` prevents outside-click dismiss
- fix: entry-form-dialog default tab changed from `'직장'` to `'교육'`
- fix: `selectSortedEntries` / `selectYearRange` infinite loop — applied `useShallow` to prevent new-reference-per-call issue
- fix: Base UI `asChild` → `render` prop migration throughout codebase (Button, SheetTrigger, etc.)
- fix: `onInteractOutside` (Radix API) → `disablePointerDismissal` (Base UI API) on Dialog.Root
- chore: moved `/Users/jaykim/Documents/Projects/my-timeline` → `indie-maker/projects/my-timeline/` (merged docs + Next.js source)

### Decisions

- **Base UI vs Radix**: shadcn/ui Nova preset uses `@base-ui/react` — API differs from Radix: `render` prop instead of `asChild`, `nativeButton={false}` for Link renders, `disablePointerDismissal` instead of `onInteractOutside`
- **form.tsx manual**: Nova preset registry doesn't include the form component; created manually using `FormProvider` pattern
- **Per-tab form cache**: Category tab switches preserve field values via `useRef` cache — save on leave, restore on return; cleared on dialog close
- **`useShallow` for derived array selectors**: Any Zustand selector that returns a new array/tuple must use `useShallow` to avoid infinite render loops

### Issues

- `dismissible` prop (attempted) — does not exist in Base UI 1.2.0; correct prop is `disablePointerDismissal` on `Dialog.Root`
- `form.tsx` from Nova preset returns nothing — had to manually implement with `FormProvider`

### Next

- [ ] Implement URL hash shared view — `/#[hash]` read-only route for sharing timeline
- [ ] Validate URL hash length limit — test with max entry count (~20–30 items)
- [ ] Set Kill Criteria numbers in `docs/indie-planner/prd-lean.md`
- [ ] QA pass — test full user flow: blank slate → add entries → chart render → export PDF/PNG → CSV import
- [ ] Run `/indie-infra` — Vercel deployment setup, custom domain, launch checklist

---

## Session: 2026-03-07 17:07

> **Context**: MyTimeline 웹 서비스 전체 기획 — planning-interview(PRD + User Journey Map) + indie-ux(UX Flow + Wireframes) 완료. No-Login/Privacy-First 아키텍처로 최종 확정.

### Done

- docs: planning-interview Solo 모드 Phase 1 인터뷰 진행 (4문항 + follow-up 2회)
- docs: `my-timeline/prd.md` 생성 — Lean Canvas (문제/솔루션/타겟/기능/채널/수익모델/지표)
- docs: planning-interview Phase 2 인터뷰 진행 (3문항, 데모 UX 흐름 기반)
- docs: `my-timeline/user-journey-map.md` 생성 — 핵심 여정 + Aha Moment + 바이럴 루프
- docs: `my-timeline/ux-flow.md` 생성 — Mental Model + Task Flow + Screen Inventory + Onboarding + User Flow
- docs: `my-timeline/wireframes.md` 생성 — 5개 핵심 화면 ASCII 와이어프레임 + Interaction States + Nielsen Review
- refactor: No-Login/Privacy-First 아키텍처로 PRD + UX Flow + Wireframes 전면 수정
  - 로그인/가입 제거 → 즉시 사용
  - Supabase → LocalStorage
  - 서버 링크 공유 → URL 해시 인코딩
  - 신규: CSV/Excel 임포트 기능
  - 신규: PDF/PNG/HTML 다운로드 기능

### Decisions

- **No-Login 아키텍처 확정**: 개인 정보 민감성으로 인해 서버 저장 없이 LocalStorage 사용. 기기 변경 시 CSV 내보내기로 이전.
- **데이터 입력 이중화**: 폼 직접 입력 + CSV/Excel 임포트 병행 — 이미 데이터가 있는 사용자(노션 등)를 위한 빠른 진입점
- **링크 공유 방식**: URL 해시에 데이터 base64 인코딩 — 서버 불필요. 데이터 대량 시 URL 길이 한계 → 기술 검증 필요
- **UX 핵심 변경**: 데모의 "생성 버튼" 제거 → 차트 상시 표시. 항목 편집을 모달/Sheet로 처리해 차트 컨텍스트 유지
- **화면 수 극적 단순화**: 7개 → 1개 앱 + 모달 3개 (로그인 UI 제거 효과)
- **Aha Moment 정의**: 첫 항목 저장 후 차트에 막대 렌더링 (폼 루트) OR CSV 임포트 후 전체 타임라인 즉시 렌더링 (임포트 루트 — 더 강력)

### Issues

- URL 해시 공유의 URL 길이 한계 미검증: 항목이 많은 경우 브라우저 URL 길이 제한(~2000자)을 초과할 수 있음. 기술 구현 전 최대 데이터 크기 테스트 필요. 폴백: HTML 파일 다운로드 후 공유.
- Kill Criteria 미확정: PRD의 D29 Kill 기준 수치 미설정 (TODO로 마킹됨)

### Next

- [x] `/indie-designer` 실행 — Vera가 design-brief.md + landing-copy.md 생성
- [ ] URL 해시 인코딩 기술 검증 — 최대 항목 수 기준 URL 길이 측정
- [ ] Kill Criteria 수치 확정 — PRD `prd.md` TODO 항목 채우기
- [x] CSV 템플릿 설계 — 임포트에 필요한 컬럼 구조 정의 (카테고리별 필드 매핑)
- [x] `/indie-frontend` 실행 — 프론트엔드 구현 시작 (indie-designer 완료 후)
- [ ] `/indie-backend` 실행 — 필요 시 (현재 아키텍처는 순수 클라이언트 사이드이므로 불필요할 수 있음)
