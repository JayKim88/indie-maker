# 인디 메이커 스프린트 플레이북

> MAKE 방법론 (Indie Maker Handbook) + Product Hunt 런치 가이드 + Business Avengers 프로세스 통합
> 목적: MVP 빌드 → 수익화 가능성 검증 → Kill/Go 결정
> 작성: 2026-03-05 | 업데이트: 2026-03-05 (Claude Code 가속 타임라인 반영)

---

## 개요

| 항목 | 내용 |
|------|------|
| 총 사이클 | **4주 (29일)** per 제품 (Claude Code 가속) |
| 동시 운영 | 최대 3개 파이프라인 (1주 스태거) |
| 연간 목표 | 8-12 제품 실험 |
| 핵심 스택 | Next.js + Tailwind + shadcn/ui + Supabase + Stripe + Vercel |
| 핵심 도구 | Claude Code, v0.dev, Product Hunt, Resend |

> **Claude Code 가속 원리**: 기획/디자인/빌드(D1-D6) → **6일**로 단축. 커뮤니티/런치/수확(D7-D29)은 인간 상호작용 의존으로 단축 불가.

---

## 핵심 원칙

| 원칙 | 내용 |
|------|------|
| **문제 우선** | 내가 실제 겪는 문제만. 억지 아이디어 금지. |
| **MVP 우선** | 핵심 플로우 1개만. 완벽함 금지. 동작하면 출시. |
| **Kill 선제 설정** | 시작 전 "어떤 숫자면 계속할지" 결정. |
| **데이터로 판단** | 직관이 아닌 지표로 Kill/Go 결정. |
| **파이프라인 유지** | 한 제품에 올인하지 않음. 병렬 실험. |

---

## 전체 스프린트 맵

```
[Phase -1]   [Phase 0+1]  [Phase 1.5]  [Phase 2]   [Phase 2.5]  [Phase 2.5-3]  [Phase 3-5]     [Phase 5]       [Phase 6]  [Phase 7]    [Gate]     [Phase 8+]  [Phase 9]
 Market     →  Idea +    → UX Sprint → Design   → Monetize   → Architecture → Build +       → Launch        → Launch  → Post      → Kill/Go → Growth  → Retro
 Research      Planning               Sprint     Pricing      Blueprint      Deploy Sprint     Prep Sprint      Day       Launch
 D-1 (opt)     D1 (1일)   D1 오후     D2 (1일)   D2-D3        D3 (30분)      D3-D6 (4일)     D7-D13 (7일)     D14       D15-D28      D29        D30+        D29(Kill)
               ◀─────────────── Claude Code 가속 (6일) ─────────────────────────▶  ◀── 커뮤니티/시간 의존 (23일) ──▶  ◀─Go─▶  ◀─Kill─▶
```

**산출물 흐름**: idea-canvas → prd-lean → **ux-flow + wireframes** → design-brief → pricing-strategy → **architecture.md** → working MVP → live product → traction data → Kill/Go → **growth-experiments / retrospective**

**가속 근거**:
| 작업 | 기존 소요시간 | Claude Code 후 | 이유 |
|------|-------------|----------------|------|
| PRD + 시장분석 | 1-2일 | 2-4시간 | `/indie-planner` 인터뷰 자동 생성 |
| 브랜드 + 랜딩 카피 + 디자인 방향 | 2-3일 | 반나절 | `/indie-designer` + v0.dev |
| Auth + DB + CRUD | 2-3일 | 1일 | Claude Code 보일러플레이트 즉시 생성 |
| UI 구현 | 2-3일 | 1-2일 | v0.dev → 컴포넌트 즉시 생성 |
| 결제 연동 | 1일 | 반나절 | Stripe 통합 Claude가 처음부터 설계 |

---

## Phase 0+1: Idea Canvas + Planning Sprint (D1, 하루)

**목표**: D1 하루 안에 기획 완료. Claude가 대부분 생성하므로 판단에만 집중.

### D1 오전+오후 (4-6시간): Idea Canvas + Planning Sprint

```bash
# (선택) D-1 또는 D1 시작 전: 욕망 기반 시장조사
/indie-market-researcher

# 이미 아이디어가 있는 경우: 수요 검증만 빠르게
/indie-market-researcher --validate

# D1 핵심: 아이디어 검증 + PRD + Kill 기준 설정 인터뷰 (2-4시간)
/indie-planner
# → idea-canvas.md, prd-lean.md 자동 생성
```

생성 결과 검토 후 사람이 할 일:
- PRD의 "MVP에 넣지 않을 것" 목록 직접 추가 (AI는 빼는 걸 못 함)
- Kill 기준 숫자 최종 확정 (D1에 결정, 이후 변경 금지)
- 가격 가설 확정 (AI 제안 → 내 판단으로 최종 결정)

### 산출물 (D1 종료 시)

| 파일 | 생성 방식 |
|------|---------|
| `idea-canvas.md` | `/indie-planner` 자동 생성 → 검토/수정 |
| `prd-lean.md` | `/indie-planner` 자동 생성 → 검토/수정 |

### D1 오후 선택: UX Sprint (1-2시간)

> **선택적이지만 권장**: 화면 구조가 머릿속에 없다면 D2 전에 실행. 이미 명확하다면 스킵해도 됨.

```bash
# 화면 흐름 + 와이어프레임 설계 (1-2시간)
/indie-ux
```

이 단계에서 결정하는 것:
- 핵심 기능 3개 → 화면 목록 (MVP ≤8 화면)
- 핵심 사용자 흐름 (랜딩 → 가입 → 핵심 액션)
- 주요 화면 텍스트 와이어프레임
- 인터랙션 상태 (empty / loading / error) 정의

**산출물**:
- `ux-flow.md` — 화면 목록 + 사용자 흐름 + IA
- `wireframes.md` — 핵심 3-5 화면 텍스트 와이어프레임

**권장 스택** (기본값, 이유 없으면 변경 금지)
```
Frontend : Next.js 14+ (App Router) + Tailwind CSS + shadcn/ui
Backend  : Next.js API Routes + Supabase (DB + Auth + Storage)
Payment  : Stripe (Checkout + Webhooks)
Deploy   : Vercel
Email    : Resend
Analytics: Vercel Analytics (무료)
```

**비즈니스 모델 선택 기준**

| 모델 | 언제 선택 |
|------|----------|
| One-time payment | 도구성 제품, 1회 가치 |
| Subscription | 지속 가치 제공, SaaS |
| Freemium | 바이럴 필요, 대규모 타겟 (MVP엔 비권장) |
| Usage-based | AI API 비용 직접 연동 |

### Kill 신호 (D1에 발견하면 즉시 중단)
- 내가 이 문제를 실제로 겪지 않음
- 유사 솔루션이 완벽히 해결됨 + 각도 재정의 불가
- 수익화 경로가 전혀 없음

---

## Phase 2: Design Sprint (D2, 하루)

**목표**: 빌드 시작 전 시각적 방향 확정. 하루 안에 완료.
> 완벽한 디자인 금지. "개발자(나)가 보고 바로 만들 수 있는 수준"이면 충분.

### D2 오전 (3-4시간): 브랜드 + 카피

```bash
# 브랜드 아이덴티티 + 랜딩 카피 생성 (1-2시간)
/indie-designer
# → design-brief.md, landing-copy.md 자동 생성
```

생성 후 직접 할 일:
- 제품명 최종 확정 (PH 규칙: 설명/이모지 금지)
- 컬러 팔레트 결정 (Tailwind 기본 팔레트 2-3색, 5분)
- 폰트 결정 (Google Fonts, 2개 이하, 5분)
- 로고: 텍스트 로고 우선 (런치 후 개선 가능)

**랜딩 카피 구조** (`/indie-designer`가 자동 생성)
```
Hero     → 1줄 가치 제안 + CTA 버튼
Problem  → 지금 어떤 불편함이 있는가
Solution → 우리가 해결하는 방법
Features → 핵심 기능 3개 (아이콘 + 한 줄)
CTA      → 가입/구매 버튼
```

### D2 오후 (3-4시간): 와이어프레임 + 컴포넌트

**와이어프레임** (v0.dev 활용으로 빠르게)
```
v0.dev 프롬프트 예시:
"Create a [product type] app with:
- Main page: [핵심 기능 설명]
- Use shadcn/ui components
- Tailwind CSS with [color] theme"
```
→ 생성된 UI를 기준으로 조정 (직접 그리지 않아도 됨)

**shadcn/ui 컴포넌트 목록 확정** (필요한 것만)
```
필수: Button, Card, Input, Toast
추가: Dialog, Badge, Avatar, Navigation Menu (필요시)
```

### 산출물 (D2 종료 시)

| 파일 | 생성 방식 |
|------|---------|
| `design-brief.md` | `/indie-designer` 자동 생성 → 검토 |
| `landing-copy.md` | `/indie-designer` 자동 생성 → 검토 |
| `wireframes/` | v0.dev 스크린샷 or 손그림 (빠르게) |

---

## Monetize: 가격 전략 + 첫 유료 고객 (D2-D3 또는 D15+)

**목표**: 얼마를 받을지, 어떻게 받을지, 누구에게 먼저 받을지 결정. 코드 짜기 전에 완료 권장.

> `/indie-planner`가 설정한 가격 가설을 실제 전략으로 전환하는 단계.
> 결제 코드(Stripe)는 D5에 구현하지만, **무엇을 얼마에 어떻게 팔지**는 D2-D3에 결정.

```bash
# 가격 전략 + 유료 전환 플레이북 생성
/indie-monetize
# → pricing-strategy.md 생성
#   - 비즈니스 모델 선택 (one-time / subscription / usage-based)
#   - 가격 티어 (최대 3개)
#   - 페이월 설계 (aha moment에 배치)
#   - Founding Plan 오퍼
#   - 첫 유료 고객 이메일 템플릿
#   - 전환 이메일 시퀀스 정의
```

Finn(indie-monetize)이 결정하는 것:
- 비즈니스 모델 + 가격대 (WTP calibration 포함)
- 어느 기능에 페이월을 걸지 (aha moment 기준)
- Founding Plan — 첫 10명에게 제공할 오퍼
- 런치 오퍼 (PH 코드: `PRODUCTHUNT`)

코드 구현은 Axel(`/indie-backend`)에게:
- Stripe Checkout 연동
- Webhook 처리 (구독 활성화 / 취소 / 결제 실패)
- D5 빌드 타임라인에서 처리

### 산출물 (D2-D3 또는 D15 기준)

| 파일 | 생성 방식 |
|------|---------|
| `pricing-strategy.md` | `/indie-monetize` 자동 생성 → 검토 |

---

## Architecture Sprint (D3 오전, 30분)

**목표**: 빌드 시작 전 Rex(프론트)/Axel(백엔드)/Sam(인프라)이 공유할 기술 청사진 1페이지 생성.

> 왜 필요한가: 아키텍처 없이 빌드를 시작하면 세 에이전트가 각자 파일 구조, API 설계, 타입 정의를 결정합니다.
> 이로 인해 프론트엔드가 호출하는 API와 백엔드가 만든 API가 안 맞거나, 타입이 중복 정의되는 문제가 발생합니다.

```bash
# D3 빌드 시작 전 (30분)
/indie-architect
# → docs/indie-architect/architecture.md 생성
#   - 파일 구조 (src/ 트리)
#   - DB 스키마 초안 (테이블 + 관계)
#   - API 엔드포인트 목록
#   - 공유 TypeScript 타입
#   - 환경변수 목록 (.env.example)
#   - 기술 리스크 1-2개
```

Arch가 결정하는 것:
- 프론트+백+인프라 전체를 아우르는 파일 구조
- PRD 엔티티 → DB 테이블 초안 매핑
- UX 플로우 화면 → API 엔드포인트 매핑
- 공유 타입 정의 (Rex와 Axel이 같은 타입 사용)
- 환경변수 전체 목록 (Sam이 배포 시 사용)

Arch가 결정하지 않는 것:
- RLS 정책 상세 → Axel이 빌드 중 설계
- 컴포넌트 구현 → Rex가 빌드 중 구현
- 배포 설정 → Sam이 D6에 처리

### 산출물 (D3 오전)

| 파일 | 생성 방식 |
|------|---------|
| `architecture.md` | `/indie-architect` 자동 생성 → 검토 |

### 코드 모듈러리티 규칙 (architecture.md에 포함)

빌드 중 Rex/Axel/Sam이 따르는 코드 구조 규칙:
- **파일당 200 LOC 제한** — 초과 시 분리 (프롬프트/설정 파일 제외)
- **catch-all 파일 금지** — `utils.ts`, `helpers.ts` 대신 기능별 파일 (`format-date.ts`, `calculate-price.ts`)
- **파일 하나 = 책임 하나** — 한 문장으로 설명 불가하면 분리
- **기능별 코로케이션** — `components/features/{feature}/`에 관련 컴포넌트/훅/액션 함께 배치

---

## Phase 3+4: Build + Deploy Sprint (D3-D6, 4일)

**목표**: 핵심 플로우 1개 동작 + 프로덕션 배포까지. Claude Code로 4일 완료.

### Claude Code 활용 원칙
- **세션 시작 시**: idea-canvas.md + prd-lean.md + architecture.md + tech-stack.md를 항상 컨텍스트로 제공
- **막히면 즉시**: 에러 메시지 + 현재 코드 전체를 Claude에 붙여넣고 질문
- **기능 크리프 차단**: 새 아이디어 → `backlog.md`에 기록, 즉시 구현 금지
- **완료 기준**: 유저가 가치를 경험하고 돈을 낼 수 있으면 충분

### 일별 타임라인

| 일 | 목표 | 완료 기준 | Claude Code 활용 |
|----|------|----------|----------------|
| **D3** | 셋업 + Auth + DB | 로그인/회원가입 동작, DB 스키마 확정 | 프로젝트 스캐폴딩, Auth 전체 코드 |
| **D4** | 핵심 API + UI (입력 화면) | 유저 핵심 액션 진입 가능 | API Route 전체, 컴포넌트 생성 |
| **D5** | UI (결과 화면) + Stripe | 핵심 플로우 E2E + 테스트 결제 성공 | Stripe Checkout 연동 전체 코드 |
| **D6** | 랜딩 + 배포 + QA | 라이브 URL + 프로덕션 결제 동작 | OG 이미지, 메타태그, 환경변수 |

### D3: 프로젝트 셋업 (Claude에 한 번에 요청 가능)

```bash
# 프로젝트 생성
npx create-next-app@latest [product-name] --typescript --tailwind --app

# shadcn/ui + 컴포넌트 (components.md 참조)
npx shadcn@latest init
npx shadcn@latest add button card input dialog toast badge

# 의존성
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs stripe @stripe/stripe-js resend
```

Claude Code 프롬프트 예시:
```
[idea-canvas.md 내용]
[prd-lean.md 내용]
[tech-stack.md 내용]

위 컨텍스트로 Next.js + Supabase 프로젝트를 시작합니다.
1. Supabase DB 스키마 (SQL) 작성
2. Auth 설정 (이메일/비밀번호)
3. 기본 폴더 구조
를 한 번에 생성해주세요.
```

### D6 오후: 배포 & QA 체크리스트

**배포**
- [ ] 커스텀 도메인 연결 (Vercel)
- [ ] 환경 변수 프로덕션 설정
- [ ] Stripe Webhook 프로덕션 등록 + 실제 카드 결제 테스트

**SEO & 공유**
- [ ] 메타 태그 (`title`, `description`)
- [ ] OG 이미지 1200×630
- [ ] favicon

**모니터링**
- [ ] Sentry 연동 (무료)
- [ ] Vercel Analytics 활성화

**QA (핵심만)**
- [ ] 핵심 플로우 E2E 수동 1회
- [ ] 모바일 반응형 확인

### 환경 변수 (`env.local`)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
RESEND_API_KEY=
```

---

## Phase 5: Launch Sprint (D7-D13, 7일)

**목표**: PH 런치 준비 완성 + Build in Public으로 사전 관심 확보 + 베타 유저 3-5명
> 이 단계는 커뮤니티/시간 의존. AI로 단축 불가. 7일은 최소 필요 기간.

### PH 제출 체크리스트 (D7-D8 완성 목표)

| 항목 | 규칙 | 완료 |
|------|------|------|
| 제품명 | 제품명만. 설명/이모지 금지 | [ ] |
| 태그라인 | 최대 60자. 명확하게 무엇을 하는지. 과장 금지 | [ ] |
| 썸네일 | 240×240. GIF 가능 (3MB 이하, 첫 프레임이 미리보기) | [ ] |
| 갤러리 | 최소 2장. 권장 1270×760 | [ ] |
| 영상 | YouTube 링크 (비공개 금지). Loom 가능. | [ ] |
| Interactive Demo | Arcade / Supademo / Storylane (모두 무료 플랜) | [ ] |
| 설명 | 최대 500자. 가치 제안 + 핵심 기능 | [ ] |
| 태그 | 최대 3개. 실제 관련 태그만 | [ ] |
| 가격 | Free / Paid / Freemium + 프로모 코드 (선택) | [ ] |
| 첫 코멘트 | 아래 가이드 참조 | [ ] |
| 예약 | D14 12:01 AM PST = KST 오전 5:01 | [ ] |

### 첫 코멘트 작성 가이드
> 탑 제품의 70%가 메이커 첫 코멘트 포함. 가장 중요한 요소 중 하나.

포함 내용:
1. 왜 만들었나 (나의 스토리, 1-2문장)
2. 누구를 위한 것인가 (타겟 유저)
3. 핵심 기능 3-5개 (이모지 bullet)
4. PH 특별 혜택 (있다면)
5. "업보트 눌러주세요" 금지 → "피드백 부탁드립니다" OK

톤: 겸손하고 진정성 있게. 마케팅 언어 지양.

### Build in Public 일정

| 채널 | 일정 | 콘텐츠 유형 |
|------|------|------------|
| X/Twitter | D7, 9, 11, 13 | 빌드 진행상황, 스크린샷, 배운 것 |
| LinkedIn | D8, D12 | 더 긴 스토리, 과정 공유 |
| Reddit (관련 서브) | D10 (규칙 확인 필수) | 피드백 요청 |
| Indie Hackers | D12 | 빌드 로그 |

**PH 사전 팔로워 확보**
- 예약 페이지 URL 공유 (팔로워 → 런치 당일 알림 자동 발송)
- PH 커뮤니티 멤버 팔로우 (관련 카테고리)

### 베타 유저 확보 (D9-D11)
- 목표: 3-5명 실제 사용자 (지인 포함 가능)
- 피드백 → 첫 코멘트 재료로 활용
- "D14에 런치해요, 그때 봐주세요" = 자연스러운 알림

### Claude 활용
```bash
# Phase 5 전체 런치 전략 (PH 패키지 + BIP 캘린더 + 베타 모집 + D14 플레이북)
/indie-launcher

# CRO 카피만 필요한 경우 (랜딩, 채널 포스트, 이메일 드립)
/indie-copy
```

**차이점**: `indie-launcher` = 런치 전략 + 실행 플랜 (어디에 뿌릴지) | `indie-copy` = CRO 전환 카피 (뭘 쓸지)
두 스킬은 독립적이지만 함께 쓰면 시너지: indie-copy 먼저 → indie-launcher가 카피 재활용

---

## Phase 6: 런치 데이 (D14, 하루)

**타이밍**: 12:01 AM PST = **KST 오전 5:01** (24시간 풀 사이클 확보)

### 시간별 플레이북

| KST | 활동 |
|-----|------|
| 05:01 | 런치 확인 + 첫 코멘트 게시 확인 |
| 05:01-08:00 | **골든 타임**: 서포터에게 DM/이메일 ("피드백 부탁드려요") |
| 08:00-12:00 | 모든 코멘트 즉시 응답 (빠를수록 알고리즘 유리) |
| 12:00-18:00 | 소셜 업데이트, 커뮤니티 링크 공유 |
| 18:00-22:00 | 유럽 타임존 피크 대응 |
| 22:00+ | 일일 결산, 감사 포스팅, Product Page 클레임 |

### 알고리즘 이해
- 리더보드 = 업보트 + 시간 + 코멘트 + 기타 (정확한 수식 비공개)
- 스팸 업보트 감지 시 순위 하락 → 진짜 유저만
- 모든 업보트는 동등 — 팔로워 많은 헌터 우위 없음

### 절대 금지
- "업보트해줘" 직접 요청 (PH 규정 위반)
- 스팸 커뮤니티 활용
- 업보트 거래/구매

---

## Phase 7: Post-Launch Sprint (D15-D28, 14일)

**목표**: 수익화 시그널 수집 + 유저 피드백 루프 + Kill/Go 데이터 확보

### D15-D17: 즉시 액션

- [ ] Product Page 클레임 ("Claim this page" — 영구 페이지)
- [ ] 업보터 팔로우 시작
- [ ] 코멘트 응답 계속 (D14 이후에도)
- [ ] 이메일 확보 유저 → 24시간 내 감사 + 온보딩 이메일
- [ ] "Leave a Review" 배지 웹사이트 삽입

### D15-D21: 수익화 실험

- 유료 전환 시도 (PH 특별 할인 코드 활용)
- 가격 가설 검증: 반응 보고 조정 가능 (±20% 테스트)
- 리텐션 지표 모니터링: 재방문율, 핵심 기능 사용율

**Lead Nurturing**: 유저가 고객이 되기까지 평균 10회 접촉 필요
- D15 감사 이메일 → D17 팁 이메일 → D21 사용 사례 이메일 → D25 업셀 이메일

### D21-D28: Kill/Go 데이터 수집

지속적 모니터링:
- Product of the Week / Month 狙 (업보트 계속 가능)
- 소셜 공유, 배지/임베드 활용
- 코멘트 피드백에서 로드맵 아이디어 추출

---

## Automate: 반복 작업 자동화 (D15+)

**목표**: 매주 반복하는 것만 자동화. D15 이전에는 수동으로.

> MAKE 원칙: "Only automate if it's worth the time saved."
> D15 이전에 자동화에 시간 쓰는 것 = 기능 크리프와 같음.

### 자동화 우선순위

| 단계 | 자동화 항목 | 구현 방식 |
|------|-----------|---------|
| D6 (필수) | Stripe webhook → Supabase 구독 상태 업데이트 | Stripe webhook handler |
| D6 (필수) | 회원가입 → 웰컴 이메일 | Supabase trigger + Resend |
| D15 (권장) | D+3 가치 리마인더 이메일 | pg_cron + Resend |
| D15 (권장) | D+14 재방문 유도 이메일 (비활성 유저) | pg_cron + Resend |
| D15 (권장) | MRR 대시보드 (Supabase SQL view) | SQL view |
| $100 MRR 후 | 트라이얼 종료 이메일, 주간 지표 digest | pg_cron + Resend |
| $500 MRR 후 | 결제 실패 dunning 시퀀스, NPS 트리거 | pg_cron + Resend |

```bash
# 자동화 구현 가이드 참조
# knowledge/automate-guide.md
# 포함: 이메일 drip 전체 코드, pg_cron 설정, Stripe webhook 패턴, MRR view
```

**자동화 의사결정 기준**:
- 주 1회 이상 반복? + 15분 이상 소요? + 판단 불필요? → 자동화
- 그 외 → 수동으로

이메일 시퀀스 전략은 `pricing-strategy.md` (indie-monetize 산출물) 참조.

---

## Kill/Go Gate (D29)

### 정량 지표

| 지표 | Kill | Watch | Go |
|------|------|-------|----|
| PH 업보트 | < 50 | 50-200 | > 200 |
| 유료 전환 | 0명 | 1-3명 | 4명+ |
| D21 MRR | $0 | $1-50 | $50+ |
| 반복 방문율 | < 10% | 10-30% | > 30% |
| 리뷰 수 | 0 | 1-2개 | 3개+ |

### 정성 지표
- "억지로" 계속하고 싶은가? → Kill 신호
- 유저 메일이 기다려지는가? → Go 신호
- 빌드하면서 즐거웠나? → Go 신호

### Kill이면 → Phase 9: Retrospective Sprint

```
/indie-retro
```

**Sage (Retro Lead)**가 30분 구조적 회고를 진행:
- 4-lens 실패 해부: 제품 / 시장 / 실행 / 타이밍
- 5 Whys 근본 원인 분석
- idea-canvas.md 가정 전체 감사
- 포트폴리오 보존 체크리스트 (48시간 내)
- 다음 스프린트에 가져갈 원칙 3개 (`lessons.md`)

산출물: `retrospective.md` + `lessons.md`
→ 완료 후 `/indie-market-researcher` 재실행 권장

### Go이면 → Phase 8+: Growth Sprint

```
/indie-growth
```

**Gio (Growth Strategist)**가 AARRR 병목 기반 성장 실험을 설계:
- Retention-first 게이트 (Day-7 < 25% → 성장 채널 확보 전 Retention 우선)
- Bull's Eye Framework: 19개 채널 → 3개 테스트 → 1개 집중
- ICE 스코어 기반 실험 백로그
- 6개월 로드맵: M1-2 Retention → M3-4 채널 → M5-6 V2 런치

산출물: `growth-experiments.md` + `channel-strategy.md`
MRR 마일스톤: $100 → $500 → $1,000

---

## 플러그인 연동 맵

| Phase | Claude 명령어 | 목적 | 시간 절감 |
|-------|-------------|------|----------|
| Phase -1 | `/indie-market-researcher` | 욕망 기반 시장조사 | 3-5시간 |
| Phase 0+1 | `/indie-planner` | 아이디어 검증 + PRD + Kill 기준 설정 | 5-8시간 |
| Phase 1.5 | `/indie-ux` | User Flow + 화면 IA + 와이어프레임 | 2-3시간 |
| Phase 2 | `/indie-designer` | 브랜드 + 랜딩 카피 + 디자인 시스템 | 3-4시간 |
| Phase 2-3 | `/indie-monetize` | 가격 전략 + 페이월 설계 + 첫 유료 고객 플레이북 | 2-3시간 |
| Phase 3-5 빌드 | `/indie-frontend` `/indie-backend` `/indie-infra` | 개발 가이드 | 지속적 |
| Phase 5 런치 준비 | `/indie-launcher` | PH + Reddit + HN + Discord 전략 + BIP 캘린더 | 4-6시간 |
| Phase 5 카피 | `/indie-copy` | CRO 전환 카피 생성 (indie-launcher와 병행) | 2-3시간 |
| Phase 7 분석 | `/indie-analyst` | Kill/Go 판단 + AARRR 분석 | 2-3시간 |
| Phase 7+ | `knowledge/automate-guide.md` 참조 | 이메일 drip + 지표 자동화 (D15 이후) | 3-5시간 |
| Phase 8+ (Go) | `/indie-growth` | 성장 실험 설계 + 채널 전략 | 3-5시간 |
| Phase 9 (Kill) | `/indie-retro` | 구조적 회고 + 다음 스프린트 원칙 | 1-2시간 |

---

## 파이프라인 운영 (다중 제품)

3개 제품을 1주 스태거로 동시 운영:

```
       W1          W2          W3          W4          W5
제품A  [P0-4: D1-6] [P5: D7-13] [P6+P7 초반] [P7 후반]   [Gate D29]
제품B               [P0-4: D1-6] [P5: D7-13]  [P6+P7 초반] [P7 후반]
제품C                            [P0-4: D1-6] [P5: D7-13]  [P6+P7]
```

격주 런치 리듬 = 월 2회 런치 가능 = 연간 최대 12개 제품 실험

**운영 원칙**
- 각 제품은 독립적인 Go/Kill 기준 보유
- 한 제품이 Watch/Go → 다른 제품 파이프라인은 계속
- 인지 부하 관리: 한 번에 같은 단계 제품 2개 이하

---

## 자동화 로드맵

| 단계 | 현재 | 목표 자동화 |
|------|------|-----------|
| D-1 (선택): 시장조사 | 수동 3-5시간 | `/indie-market-researcher` (1-2시간) |
| D1: 아이디어 검증 + PRD | 수동 4-8시간 | `/indie-planner` (2-4시간) |
| D2 오전: 브랜드 + 랜딩 카피 | 수동 3-5시간 | `/indie-designer` (1-2시간) |
| D2 오후: UI 프로토타입 | Figma 2-3시간 | v0.dev 프롬프트 (30분) |
| D3-D6: 개발 | 수동 코딩 | Claude Code 페어 프로그래밍 (2-3배 가속) |
| D7-D13: BIP 포스팅 | 수동 작성 | Claude Code 초안 배치 생성 후 편집 |
| D15 팔로업 이메일 | 수동 발송 | Resend + Supabase drip 시퀀스 |
| D21 지표 수집 | 수동 확인 | PH API + Vercel Analytics 집계 |
| D29 Kill/Go 판단 | 직관 | 지표 기반 체크리스트 자동 집계 |

---

## 첫 사이클 시작 가이드

### Week 0 (사이클 시작 전)
- [ ] Product Hunt 계정 생성 + 프로필 완성 (3개월 워밍업 권장)
- [ ] X/Twitter #buildinginpublic 해시태그 팔로우
- [ ] Indie Hackers 계정 생성
- [ ] 아이디어 후보 1-3개 리스트업

### 첫 제품 선택 기준
- 내가 실제로 쓰고 있거나 절실히 필요한가?
- 남에게 설명할 때 "이런 게 있으면 좋겠죠?" 반응이 오는가?
- 1주 안에 MVP 가능한 규모인가?
- 결제 가능한 가치를 제공하는가?

---

## 참고 문서

- `CLAUDE.md` — 스킬 레퍼런스 + 문서 흐름 요약
- `knowledge/` — 개발 가이드 (design / frontend / backend / infra)
