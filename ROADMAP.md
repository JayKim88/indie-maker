# Indie-Maker Roadmap

> **Vision**: Solo-maker가 29일 sprint를 반복하며 *자기 자신*에 대해 학습하는 메타-프레임워크.
> 매번 다른 이유로 실패한다고 느끼지만 실제론 같은 패턴 반복인 경우를 데이터로 반증하는 시스템.

이 문서는 *어디로 갈 것인가*만 다룹니다. *현재 작업 상태*는 [Execution Plans](#active-execution-plans) 참조.

---

## Releases

### v0.1 — Harness Hardening (진행 중)

**목표**: 텍스트 약속에 의존하던 부분을 hook/script/statusline으로 **기계적 강제**.
멀티-프로젝트 병렬 운영 시 인지 부하 감소.

| 상태 | 진행 |
|---|---|
| L0 knowledge 정리 | ✅ DONE |
| L1 Critical 버그 수정 | ✅ DONE |
| L2 스프린트 상태 머신 | 🟡 3.5/4 DONE |
| L3 Scope & Discipline 자동화 | ⬜ TODO |
| L5 Self-Correcting + OS Readiness | 🟡 1/7 DONE |

- **릴리스 기준** *[OPINION — revisit]*: L0-L4 완료 + L5 핵심 3개(L5.1/L5.2/L5.4)
- **트래커**: [`docs/exec-plans/active/track-1-harness-hardening.md`](docs/exec-plans/active/track-1-harness-hardening.md)

---

### v0.2 — Agent Runtime Layer

**목표**: indie-maker가 sprint 반복으로 *사용자에 대해* 학습.
"내가 항상 어느 phase에서 막히는가?" 자가 진단이 가능한 메타-프레임워크.

| 상태 | 진행 |
|---|---|
| M1 Portfolio DB | ⬜ TODO |
| M2 indie-mcp Server | ⬜ TODO |
| M3 text-to-sql tool | ⬜ TODO |
| M4 Mission Control | ⬜ TODO |

- **릴리스 기준** *[OPINION — revisit]*: M1-M4 완료 (M5 DEFER)
- **추정**: 3-4d 작업
- **블록**: v0.1의 T1.L2.4 (PostToolUse sync hook) 선행 필요
- **트래커**: [`docs/exec-plans/active/track-2-agent-runtime.md`](docs/exec-plans/active/track-2-agent-runtime.md)
- **설계**: [`docs/agent-runtime/README.md`](docs/agent-runtime/README.md)

---

### v0.3 — Open Source Release

**목표**: 외부 사용자가 clone → install → first sprint 까지 30분 내.

| 상태 | 진행 |
|---|---|
| Portability foundation (L5.0) | ✅ DONE |
| `INSTALL.md` + `bin/install-harness.sh` | ✅ DONE |
| Packaging (L5.6) | ⬜ TODO |
| CI workflow (L5.7) | ⬜ TODO |
| Sample sprint example | ⬜ TODO |

- **릴리스 기준** *[OPINION — revisit]*: L5.6 + L5.7 완료 + sample sprint 1개 실행 추적 가능
- **블록**: v0.1 완료 (mechanical enforcement가 있어야 외부 contribute 안전)

---

## Active Execution Plans

진행 중인 실행 계획은 `docs/exec-plans/active/`에 보관:

- [`track-1-harness-hardening.md`](docs/exec-plans/active/track-1-harness-hardening.md) — v0.1 L0-L5 체크리스트
- [`track-2-agent-runtime.md`](docs/exec-plans/active/track-2-agent-runtime.md) — v0.2 M1-M5 체크리스트
- [`harness-upgrade.md`](docs/exec-plans/active/harness-upgrade.md) — OpenAI Harness Engineering 패턴 적용 (보조)

완료된 plan은 `docs/exec-plans/completed/`로 이동.

---

## Reference

- [`README.md`](README.md) — 현재 시스템 소개 + 사용법
- [`CLAUDE.md`](CLAUDE.md) — Skill scope + 시스템 인스트럭션
- [`INSTALL.md`](INSTALL.md) — 설치 가이드
- [`docs/agent-runtime/README.md`](docs/agent-runtime/README.md) — Agent Runtime Layer 설계
