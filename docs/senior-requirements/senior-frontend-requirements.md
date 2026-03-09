# Senior Frontend Engineer — Common Requirements (2025-2026)

Wellfound, LinkedIn, Indeed, GitLab Handbook, Workable 등 주요 채용 플랫폼의
시니어 프론트엔드 엔지니어 JD를 종합 분석한 결과.

---

## 1. Technical Skills (Hard Skills)

| Category | Common Requirements | Notes |
|----------|-------------------|-------|
| **Core Language** | JavaScript (ES6+), TypeScript, HTML5, CSS3 | 거의 100% 필수 |
| **Framework** | React (압도적 1위), Vue, Angular 중 1개 이상 | Next.js 언급 빈도 급증 |
| **State Management** | Redux, Context API, Zustand 등 | 대규모 앱 경험 강조 |
| **Testing** | Jest, Cypress, Playwright, React Testing Library | "테스트 작성 경험" 거의 필수 |
| **Performance** | Core Web Vitals, 번들 최적화, 렌더링 성능 | 시니어 차별화 포인트 |
| **Accessibility** | WCAG, Semantic HTML, Screen reader 호환 | 점점 필수화 추세 |
| **Responsive/Cross-browser** | Mobile-first, PWA, Cross-browser compatibility | 기본 기대치 |
| **Build/DevOps** | Git, CI/CD pipeline, Module bundler | 배포 자동화 이해 |
| **Architecture** | Component design, Design System, Modular Architecture | 시니어 핵심 역량. Micro-frontends는 대규모 팀 한정 |
| **API Integration** | REST, GraphQL, WebSocket | 백엔드 협업 필수 |

---

## 2. Senior Differentiators (Mid → Senior Gap)

시니어의 핵심 차별점은 "더 잘 코딩하는 것"이 아니라
**아키텍처 의사결정 + 성능 최적화 + 멘토링 + 크로스팀 영향력**.

| Competency | Description | Source |
|-----------|-------------|--------|
| **Technical Decision-Making** | 프레임워크/아키텍처 선택의 근거를 제시하고 트레이드오프 설명 | Workable, GitLab |
| **Complex Problem Solving** | "High scope and complexity" 문제를 독립적으로 해결 | GitLab Handbook |
| **Code Quality Leadership** | 코드 리뷰, 코딩 표준 수립, 기술 부채 식별 및 개선 | GitLab, LinkedIn |
| **Performance Engineering** | 단순 구현이 아닌 최적화/확장성 관점의 설계 | Indeed, Workable |
| **Autonomous Execution** | 팀 감독 없이 독립적으로 기능을 설계·구현·배포. "Ship features with minimal guidance" | GitLab, Wellfound |
| **Cross-team Influence** | 팀 경계를 넘어 코드베이스 개선, 전사적 기술 방향 제안 | GitLab |

---

## 3. Soft Skills

| Skill | Detail |
|-------|--------|
| **Communication** | 복잡한 기술 문제를 비기술 이해관계자에게 명확하게 설명 |
| **Collaboration** | PM, Designer, Backend Engineer와의 cross-functional 협업 |
| **Self-management** | Self-motivated, self-managing (특히 리모트 환경) |
| **Business Translation** | 비즈니스 요구사항을 기술 솔루션으로 번역 |
| **Consensus Building** | "Regularly achieve consensus with peers" (GitLab) |

---

## 4. Experience Requirements

| Condition | Typical Range |
|-----------|--------------|
| **Experience** | CS 학위 + 3년 또는 학위 무관 5년+ |
| **Salary (US)** | $120K–$200K (시니어 기준) |
| **Preferred Background** | 스타트업/프로덕트 회사 경험, 오픈소스 기여, 리모트 경험 |

---

## 5. 2025-2026 Trend Keywords

| Trend | Status |
|-------|--------|
| **TypeScript** | "nice-to-have" → 필수로 격상 |
| **Next.js / SSR / RSC** | React 생태계의 기본 기대치 |
| **Design System** | 재사용 가능한 UI 프레임워크 구축/유지 경험 |
| **Micro-frontends / Module Federation** | 대규모 팀 한정 — 인디/소규모 팀에서는 불필요 |
| **AI Tool Proficiency** | Copilot 등 AI 기반 개발 도구 경험 (신규 트렌드) |

---

## 7. Gap Analysis — indie-frontend Coverage

현재 `SKILL.md` + `frontend-guide.md` 대비 시니어 요구역량 커버리지.

| Senior Requirement | SKILL.md | frontend-guide.md | Gap Level |
|-------------------|----------|-------------------|-----------|
| React/Next.js/TypeScript | Deep | Deep | None |
| Component Architecture / RSC | Deep | Deep | None |
| Testing (Unit/Integration/E2E) | None | None | **Critical** |
| Performance Optimization | CWV mention only | Guidelines only | **High** |
| Accessibility (a11y) | Semantic HTML only | WCAG principles only | **High** |
| State Management | Zustand mentioned | No depth | Medium |
| Error Handling | error.tsx pattern | Covered | None |
| SEO | metadata API | Covered | None |
| Design System Building | shadcn usage only | No depth | Medium |
| CI/CD / Build | None | None | indie-infra scope |
| Code Review / Mentoring | None | None | N/A (tool context) |
| Micro-frontends | None | None | Out of indie MVP scope |

### Actionable Enhancement Areas

1. **Testing Patterns** — 시니어 JD 100% 필수
   - Unit: Vitest + React Testing Library
   - Integration: Component + API mocking
   - E2E: Playwright (핵심 플로우만)

2. **Performance Optimization Patterns** — CWV 수치 넘어서 구체적 코드 패턴
   - Dynamic imports / lazy loading
   - Image optimization strategy
   - Bundle analysis + tree shaking
   - React profiler 기반 re-render 최적화

3. **Accessibility Patterns** — WCAG 원칙 넘어서 컴포넌트별 실전 체크
   - Focus management (modal, drawer, toast)
   - ARIA attributes for custom components
   - Keyboard navigation patterns
   - Color contrast + motion preferences

---

## 6. Role Boundary Note

**Frontend vs Backend**: 프론트엔드 시니어는 API 설계·DB 스키마가 아닌, 클라이언트 성능·접근성·UI 아키텍처를 소유. Supabase/BaaS 사용 시 경계가 흐려지지만 렌더링 책임은 프론트엔드.

---

## Sources

- [GitLab Senior Frontend Engineer Handbook](https://handbook.gitlab.com/job-families/engineering/development/frontend/senior/)
- [Workable Senior Frontend Engineer JD Template](https://resources.workable.com/senior-frontend-engineer-job-description)
- [Indeed Front End Developer JD 2026](https://www.indeed.com/hire/job-description/front-end-developer)
- [theSeniorDev Roadmap 2025](https://www.theseniordev.com/blog/senior-frontend-developer-roadmap-2025)
- [Wellfound Frontend Engineer Jobs](https://wellfound.com/role/frontend-engineer)
- [ZipRecruiter Senior Frontend Skills](https://www.zippia.com/senior-front-end-developer-jobs/skills/)
- [Cleverism Senior Frontend Developer Profile](https://www.cleverism.com/job-profiles/senior-frontend-developer/)
