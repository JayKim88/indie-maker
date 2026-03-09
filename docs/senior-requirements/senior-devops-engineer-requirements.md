# Senior DevOps Engineer / SRE — Common Requirements (2025-2026)

주요 채용 플랫폼의 시니어 DevOps/SRE 엔지니어 JD 종합 분석.
indie-infra 스킬 강화를 위한 참고 자료.

---

## 1. Technical Skills (Hard Skills)

| Category | Common Requirements | Notes |
|----------|-------------------|-------|
| **Cloud Platforms** | AWS, Azure, GCP — 최소 1개 deep + 1개 working knowledge | AWS가 가장 높은 수요; Multi-cloud 경험 우대 |
| **Containers & Orchestration** | Docker, Kubernetes (CRDs, Operators, Helm, multi-cluster), ECS/EKS/GKE | K8s 고급 기능 (Service Mesh, GitOps with ArgoCD/Flux) 시니어 필수 |
| **IaC (Infrastructure as Code)** | Terraform (가장 높은 수요), Pulumi, CloudFormation, Ansible | Terraform + Ansible 조합이 JD에서 가장 빈번 |
| **CI/CD** | GitHub Actions, GitLab CI/CD, Jenkins, ArgoCD, Flux | GitOps 패턴 (ArgoCD/Flux) 2025-2026 급부상 |
| **Programming / Scripting** | Python, Go, Bash — 최소 2개 | Go 수요 급증 (K8s ecosystem) |
| **Observability & Monitoring** | OpenTelemetry, Prometheus, Grafana, Datadog, PagerDuty, ELK/EFK | OpenTelemetry가 2026년 사실상 표준 |
| **Networking** | TCP/IP, DNS, Load Balancing, CDN, VPN, Service Mesh (Istio, Linkerd) | Service Mesh 경험이 시니어 JD에서 점점 명시적으로 요구 |
| **Security (DevSecOps)** | SAST/DAST, Secret Management (Vault), RBAC, Policy-as-Code (OPA), Supply Chain Security | 80%+ 조직이 CI/CD에 보안 통합; Shift-left 접근 필수 |
| **OS & Virtualization** | Linux (필수), VMware/KVM | Linux 심화 (kernel tuning, systemd, cgroups) 시니어 차별화. Windows Server는 Enterprise 환경 한정 |
| **Database & Storage** | PostgreSQL, MySQL, Redis, S3/Blob Storage, DB migration 자동화 | DBA 수준은 아니나 운영 레벨 이해 필요 |
| **Version Control** | Git (advanced — rebase, bisect, submodules), Monorepo 경험 | advanced Git workflow 이해 차별화 |

## 2. Senior Differentiators (Mid → Senior Gap)

| Competency | Description | Source |
|-----------|-------------|--------|
| **System Architecture Design** | 확장 가능하고 복원력 있는 인프라 설계를 주도; 마이크로서비스, 서버리스, 이벤트 기반 아키텍처 | Teal HQ, Naresh IT |
| **Strategic Vision & Planning** | 단순 구현이 아닌 조직 전체 DevOps 전략 수립; 기술 로드맵 주도 | Coursera |
| **Incident Command & Post-mortem** | 장애 대응 프로토콜 설계, On-call 로테이션 관리, Blameless Post-mortem 문화 정착 | Splunk, LinkedIn |
| **Advanced Kubernetes** | CRDs, Custom Operators/Controllers, Service Mesh, Multi-cluster Management, GitOps | Teal HQ |
| **Autonomous Infrastructure Ownership** | 인프라 설계·구축·운영·개선 전 사이클을 단독 추진. 멘토링/팀 리딩은 팀 환경 한정 | BetterTeam, iMocha |
| **Cross-functional Influence** | Dev, QA, Security, Product 팀 간 브릿지 역할 | Remotely |
| **Cost Optimization (FinOps)** | 클라우드 비용 분석, Reserved/Spot 인스턴스 전략, 단위 비용 메트릭 기반 의사결정 | RealVNC, Ksolves |
| **Reliability Engineering** | SLO/SLI/Error Budget 설정 및 운영, Chaos Engineering, Capacity Planning | GitLab Handbook |

## 3. Soft Skills

| Skill | Detail |
|-------|--------|
| **Communication** | 기술 개념을 비기술 이해관계자에게 명확히 전달; 문서화 주도 |
| **Collaboration** | 개발, 보안, 프로덕트 등 교차 기능 팀과의 효과적 협업 |
| **Problem-solving** | 가설 기반 디버깅, 데이터 기반 의사결정, Root Cause Analysis |
| **Leadership** | 팀 방향 설정, 기술 결정 주도, 주니어 성장 지원 |
| **Continuous Learning** | 빠른 기술 변화에 대한 자기주도 학습, 실험 문화 주도 |
| **Stakeholder Management** | 경영진/PM에게 인프라 리스크와 투자 필요성을 비즈니스 언어로 전달 |
| **Empathy** | 개발자 경험(DX) 관점에서 도구와 프로세스 설계 |

## 4. Experience Requirements

| Condition | Typical Range |
|-----------|--------------|
| **총 경력** | 5-10년 (DevOps/SRE/인프라/소프트웨어 엔지니어링 합산) |
| **시니어 타이틀 기준** | 5-7년 이상이 가장 빈번; 일부 JD는 7-10년 요구 |
| **프로덕션 시스템 운영** | 대규모(large-scale) 프로덕션 환경 운영 경험 필수 |
| **클라우드 네이티브 경험** | 3년 이상 컨테이너/K8s 기반 프로덕션 운영 |
| **학력** | CS/Engineering 학사 (또는 동등 경력); 석사 우대이나 필수 아님 |
| **인증** | AWS SA Pro, CKA/CKAD, Terraform Associate 우대 (+$15K-$30K 연봉 프리미엄) |
| **연봉 (US)** | $146K-$221K (25th-75th percentile); 평균 ~$178K |
| **On-call 경험** | 거의 모든 시니어 JD에서 on-call rotation 경험/의지 요구 |

## 5. 2025-2026 Trend Keywords

| Trend | Status |
|-------|--------|
| **Platform Engineering / IDP** | 주류 — 80% 엔지니어링 조직이 Internal Developer Platform 운영 |
| **AIOps** | 급부상 — 73% 기업이 AIOps 도입; 예측적 장애 탐지 및 자동 복구 |
| **FinOps** | 필수화 — 모든 스케일링 정책이 단위 비용 메트릭과 연동 |
| **DevSecOps (Shift-Left Security)** | 표준 — 80%+ 조직이 CI/CD에 보안 검사 통합 |
| **GitOps (ArgoCD, Flux)** | 주류 — 선언적 인프라 관리 + 자동 reconciliation |
| **OpenTelemetry** | 사실상 표준 — 2026년 관측성 프레임워크의 기본 |
| **MLOps / AI Infra** | 급성장 — 시니어 DevOps에게 ML 파이프라인 인프라 관리 요구 증가 |
| **Green DevOps** | [SPECULATIVE] 초기 도입 — 탄소 발자국 감소, 에너지 효율 최적화가 메트릭에 포함 (실제 JD 요구 사례 아직 드묾) |
| **Chaos Engineering** | 확산 — Reliability 검증을 위한 프로액티브 장애 주입 테스트 |
| **AI-assisted DevOps** | 전환기 — 스크립트 직접 작성에서 AI 출력 검증/감독 역할로 전환 |
| **DORA Metrics** | 성숙 — Deployment Frequency, Lead Time, MTTR, Change Failure Rate를 팀 성과 측정 기준으로 활용 |

## Sources

- [Mad Devs — Skills Every DevOps Engineer Must Have in 2026](https://maddevs.io/blog/devops-engineer-skills-matrix/)
- [Teal HQ — Senior DevOps Engineer Skills 2025](https://www.tealhq.com/skills/senior-devops-engineer)
- [Splunk — Site Reliability Engineer Roles and Salaries](https://www.splunk.com/en_us/blog/learn/site-reliability-engineer-sre-role.html)
- [GitLab Handbook — Site Reliability Engineer](https://handbook.gitlab.com/job-families/engineering/infrastructure/site-reliability-engineer/)
- [RealVNC — DevOps Trends 2026](https://www.realvnc.com/en/blog/devops-trends/)
- [DevOps Training Institute — 10 DevOps Predictions 2026](https://www.devopstraininginstitute.com/blog/10-DevOps-Predictions)
- [Coursera — DevOps Career Path 2026](https://www.coursera.org/articles/devops-career-path)
- [Glassdoor — Senior DevOps Engineer Salary 2026](https://www.glassdoor.com/Salaries/senior-devops-engineer-salary-SRCH_KO0,22.htm)
