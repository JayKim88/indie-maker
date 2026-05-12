# Senior Backend Developer Principles

> Companion to `frontend-principles.md`. Written for engineers who have shipped backends to production and want a reference for non-negotiable standards.
> Reference stack: TypeScript + Node.js 20 LTS + NestJS + PostgreSQL 16 (pgvector) + Prisma + Redis + BullMQ + Docker.
> Where alternatives matter (Supabase, FastAPI), they are noted explicitly.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy) — *includes Learning Path for frontend engineers*
2. [TypeScript Discipline](#typescript-discipline)
3. [Node.js Runtime Fundamentals](#nodejs-runtime-fundamentals)
4. [Project Architecture](#project-architecture) — *Modular Monolith, Clean/Hexagonal, DDD, EDA, CQRS, NestJS specifics*
5. [API Design](#api-design) — *includes Webhook Handling*
6. [Database Architecture](#database-architecture) — *includes Outbox Pattern (deep)*
7. [Caching Strategy](#caching-strategy)
8. [Background Jobs & Queues](#background-jobs--queues)
9. [Real-time Communication](#real-time-communication)
10. [Authentication & Authorization](#authentication--authorization) — *includes JWT CVE classes*
11. [Security](#security)
12. [Performance & Scaling](#performance--scaling)
13. [AI / LLM Backend](#ai--llm-backend) — *fixed agent loop with `tool_call_id`*
14. [Multi-tenancy](#multi-tenancy) — **NEW**
15. [File Storage](#file-storage) — **NEW**
16. [Email & Notifications](#email--notifications) — **NEW**
17. [Internationalization (i18n) and Time](#internationalization-i18n-and-time) — **NEW**
18. [Audit Logging](#audit-logging) — **NEW**
19. [Reliability & Error Handling](#reliability--error-handling)
20. [Observability](#observability)
21. [Testing Strategy](#testing-strategy)
22. [Deployment & DevOps](#deployment--devops)
23. [Team Standards](#team-standards)
24. [Quick Reference Checklist](#quick-reference-checklist)

---

## Core Philosophy

### Five Principles That Override Everything Else

1. **Correctness before performance.** A fast wrong answer is worse than a slow correct one. Optimize only after the system is correct, observable, and load-tested.

2. **Boundaries are sacred.** The boundary between your service and the outside world (HTTP, queues, DB, third-party APIs) is where bugs live. Validate everything that crosses a boundary. Trust nothing inside the boundary you did not validate at the boundary.

3. **The database is the source of truth, not the cache.** Every cache is a lie waiting to be discovered. Design with the assumption that any cache can disappear at any moment without breaking correctness.

4. **Failure is the default state.** Networks fail, disks fill, processes crash. Code that assumes the happy path is broken — it just hasn't been observed broken yet. Plan for retries, idempotency, and partial failure.

5. **Operability is a feature.** A service you cannot debug at 3am is a liability. Logs, traces, metrics, and dashboards are not "nice to have" — they ship with the feature or the feature does not ship.

### Learning Path for Frontend Engineers Moving to Backend

This document is comprehensive on purpose. If you are coming from frontend, do not try to read it linearly — you will drown in vocabulary. Read in this order:

**Stage 1 — Get something running (Week 1-2)**
1. Node.js Runtime Fundamentals — understand why blocking is fatal
2. Project Architecture — basic layered structure
3. API Design — REST + validation
4. Database Architecture — schema, transactions, indexes

**Stage 2 — Make it correct (Week 3-4)**
5. Authentication & Authorization
6. Security — OWASP Top 10
7. Reliability & Error Handling — timeouts, retries, idempotency

**Stage 3 — Make it operable (Week 5-6)**
8. Observability — logs, metrics, tracing
9. Testing Strategy
10. Deployment & DevOps

**Stage 4 — Domain depth (later)**
11. Caching Strategy
12. Background Jobs & Queues
13. AI / LLM Backend
14. Performance & Scaling

**Skip until you need them**: Microservice decomposition, Saga, Event Sourcing, CQRS, Service Mesh. These solve organizational scale problems. A solo or small team product does not have those problems yet — adopting them early adds complexity without benefit.

### Frontend → Backend Mental Model Shifts

Things that surprise frontend engineers learning backend:

| You believed (frontend) | Backend reality |
|------------------------|-----------------|
| State lives in components | State lives in the database; the process is mostly stateless |
| Re-render is cheap | Every request costs CPU, DB connections, and memory |
| Errors are toasts | Errors are HTTP status codes that drive client retry behavior |
| Performance = fast UI | Performance = p50/p95/p99 latency under concurrent load |
| Refresh fixes weird state | Once committed to DB, "weird state" persists until migrated |
| `console.log` is enough | Logs are structured JSON shipped to a log aggregator |
| Deploy = push to Vercel | Deploy = rolling instances, backward-compatible migrations, health checks |
| One user at a time | N concurrent requests; race conditions are real |

---

## TypeScript Discipline

### Strict Mode is the Minimum

Backend `tsconfig.json` runs with `strict: true`, `noUncheckedIndexedAccess: true`, `noImplicitOverride: true`, and `exactOptionalPropertyTypes: true`. These are not stylistic choices — they catch real production bugs (off-by-one indexing, optional/undefined confusion, accidental override of base methods).

### Where Types Come From

Types should flow from the database schema upward, not be hand-written and kept in sync. With Prisma, types are generated from `schema.prisma`. With Zod, runtime validators *are* the type via `z.infer<typeof schema>`. Hand-maintained types covering the same shape as a schema is duplication waiting to drift.

### The Boundary Rule

Every value entering the process must be parsed by a runtime schema (Zod/class-validator) before any business logic touches it. HTTP body, query, headers, environment variables, queue payloads, third-party API responses — all of them. After the boundary, types from the parser carry through; no `any`, no `as`.

### The `any` Prohibition

`any` disables the compiler. The only legitimate use is in adapter code wrapping an untyped third-party library, and it must be confined to one small function that returns a typed result. Anywhere else, use `unknown` and narrow.

### Discriminated Unions for Domain State

Order state is not `{ status: string }` — it is a discriminated union: `{ status: 'pending' } | { status: 'paid', paidAt: Date } | { status: 'refunded', refundedAt: Date, reason: string }`. The compiler then refuses to read `paidAt` on a pending order. This eliminates an entire class of "I forgot to check the status first" bugs.

### Branded Types for Identifiers

`type UserId = string & { __brand: 'UserId' }`. The compiler will refuse to pass a `OrderId` where a `UserId` is expected, even though both are strings at runtime. This catches a real category of bug — you cannot accidentally use a customer ID where a payment ID belongs.

### Result Types Over Throwing

For domain errors (validation failures, not-found, business rule violations), prefer `Result<T, E>` types or NestJS exceptions with explicit error classes — not generic `throw new Error('...')`. The caller should see "this can fail in these specific ways" in the type signature.

---

## Node.js Runtime Fundamentals

### The Event Loop

Node.js runs JavaScript on a single thread. Every async operation goes to libuv's thread pool or the kernel and returns to the event loop. **A single CPU-bound operation blocks every request to the process** — including health checks, which is why orchestrators may kill a hung pod.

Implications:
- Never `for` over a million records and call a sync hash on each. Move it to a worker thread or stream.
- Avoid `JSON.parse` on payloads larger than a few MB on the request thread.
- A regex with catastrophic backtracking on user input is a denial-of-service vector.

### Promises, Microtasks, and the Order of Execution

Microtasks (resolved promises) run before the next event loop tick. `setImmediate` runs on the next tick. Mixing these without understanding leads to ordering bugs that only appear under load. Read [Node.js event loop docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick) once and refer back.

### Async/Await is Not Free

`await` inside a tight loop serializes the operations. Use `Promise.all` for independent work, `Promise.allSettled` when you want all results regardless of failure. For unbounded concurrency over a large array, use a concurrency limiter (`p-limit`, `bottleneck`) to avoid exhausting connection pools.

```ts
// ❌ Serial — slow
for (const url of urls) await fetch(url);

// ❌ Unbounded — exhausts FD/connections
await Promise.all(urls.map(fetch));

// ✅ Bounded
const limit = pLimit(10);
await Promise.all(urls.map(url => limit(() => fetch(url))));
```

### Streams for Large Payloads

Loading a 1GB file into memory crashes the process. Use streams for file uploads, large query results (`pg-cursor`), CSV/JSON line processing, and HTTP response bodies. Backpressure (`pipeline()` from `node:stream/promises`) is what keeps memory bounded.

### Worker Threads for CPU-Bound Work

Image processing, PDF generation, heavy parsing — these belong in a `Worker` thread or, better, a separate service consumed via a queue. The main process must stay responsive.

### Process Lifecycle

A production server must handle `SIGTERM` gracefully:
1. Stop accepting new connections.
2. Drain in-flight requests with a timeout.
3. Close DB / Redis / queue connections.
4. Exit with code 0.

Without this, a rolling deploy drops requests and leaves connections hanging.

---

## Project Architecture

### [OPINION] Modular Monolith as the Default

Microservices solve **organizational problems** (multiple teams, independent deploys), not technical ones. For a single team, a **modular monolith** — strong module boundaries inside one deployable — gets you most of the benefit without the distributed-systems tax.

**Decision matrix — split to microservices only when:**

| Signal | Why split helps |
|--------|----------------|
| Module has 10x different scaling profile | Independent autoscaling reduces cost |
| Module written in a different language | Python ML, Go networking |
| Module owned by a different team | Independent deploy cadence |
| Module has different reliability budget | Critical path isolated from experimental |
| Module has different compliance scope | PCI/HIPAA isolation |

**Counter-evidence**: Stripe ran a monolith to ~$1B revenue. Shopify's modular monolith handles Black Friday. "We need microservices" is rarely the right first answer.

### Clean Architecture (Layered) Inside a Module

Each domain module owns four layers, with strict dependency direction:

```
┌─────────────────────────────────────────┐
│  controller/  ← HTTP routes (NestJS)    │
│      ↓                                   │
│  application/ ← Use cases               │
│      ↓                                   │
│  domain/      ← Pure business logic     │
│      ↑                                   │
│  infrastructure/ ← DB, queues, APIs     │
│  (implements interfaces from domain)     │
└─────────────────────────────────────────┘
```

**The Dependency Rule** (Robert C. Martin's Clean Architecture):
- Outer layers depend on inner layers, never the reverse.
- The domain knows nothing about HTTP, Prisma, or BullMQ — it is pure business logic.
- This is what makes the domain testable in milliseconds without spinning up a database.

**Layer responsibilities:**

```
controller/     → Translates HTTP ↔ application. No business logic. No DB.
application/    → Orchestrates: pull data, call domain, persist, emit events.
                  Use cases as classes/functions; one per business operation.
domain/         → Entities, value objects, domain services, domain events.
                  Pure TypeScript. No framework imports.
infrastructure/ → Repository implementations, external API clients,
                  queue producers, email senders. All side effects live here.
```

### Hexagonal Architecture (Ports & Adapters) — Properly Explained

Hexagonal Architecture (Alistair Cockburn) is the same dependency rule expressed geometrically:

```
            ┌────────────────────────┐
HTTP API ──→│       Inbound Port     │──→ Use Case
                                          ↓
                                       Domain
                                          ↓
Postgres  ←── Outbound Port  ←─────── Use Case
```

- **Port** = an interface owned by the domain (e.g., `UserRepository`, `EmailSender`).
- **Adapter** = an implementation owned by infrastructure (e.g., `PrismaUserRepository`, `ResendEmailSender`).
- Inbound adapters drive the application (HTTP controller, queue consumer, CLI).
- Outbound adapters are driven by the application (DB, email, message bus).

**Why this matters in practice:**
1. Tests substitute in-memory adapters → domain tests run in milliseconds.
2. Swapping Postgres for another store is a 1-file change, not a refactor.
3. The domain is provider-independent — you can describe it without naming a framework.

```ts
// domain/user-repository.ts (port)
export interface UserRepository {
  findById(id: UserId): Promise<User | null>;
  save(user: User): Promise<void>;
}

// infrastructure/prisma-user-repository.ts (adapter)
@Injectable()
export class PrismaUserRepository implements UserRepository {
  constructor(private prisma: PrismaService) {}
  async findById(id: UserId) { /* ... */ }
  async save(user: User) { /* ... */ }
}

// application/register-user.usecase.ts
export class RegisterUserUseCase {
  constructor(private users: UserRepository) {} // depends on port, not adapter
}
```

### Domain-Driven Design (DDD) — The Vocabulary You Need

DDD is overhyped, but its vocabulary genuinely helps modeling. The 80% you actually use:

- **Entity**: an object with an identity that persists over time. Two entities with the same fields but different IDs are different. (User, Order, Insight.)
- **Value Object**: an object defined by its values, no identity. Equal values = equal objects. (Money, EmailAddress, DateRange.) Immutable.
- **Aggregate**: a cluster of entities + value objects treated as one unit for consistency. The aggregate root is the only entry point — outside code never touches inner entities directly. (Order is the root; OrderLines are inside.)
- **Domain Event**: something meaningful that happened, named in past tense. (`OrderPlaced`, `PaymentFailed`, `InsightGenerated`.) Domain events drive eventual consistency between modules.
- **Bounded Context**: a region where a domain term has one meaning. "User" in `billing` context (has a payment method) is different from "User" in `auth` context (has a password hash). Each bounded context = one module.
- **Ubiquitous Language**: every term in the code matches what domain experts say. If your code says `Account` but the team says `Customer`, fix the code.

### Module Boundary Rules

A module's public surface is its NestJS module exports — services and DTOs that other modules may import. Anything else is internal. **Importing from another module's `domain/` or `infrastructure/` directly is a boundary violation.**

If module A needs data from module B, two options:
1. **Synchronous query**: A calls B's service (creates coupling, but simple).
2. **Domain event**: B emits `XHappened`, A subscribes and maintains its own read model (no coupling, eventual consistency).

Circular module dependencies are always a sign of:
- A missing third module that owns the shared concept, or
- Two modules that should be merged because they were never separate concerns.

### Communication Patterns: Sync vs Async

| Pattern | When | Trade-off |
|---------|------|-----------|
| **Sync REST/RPC** | Caller needs answer now (e.g., authorize payment) | Tight coupling, cascading failures |
| **Async event (pub/sub)** | Caller doesn't block on outcome (e.g., send welcome email) | Eventual consistency, harder debugging |
| **Async command (queue)** | Caller dispatches work to be done | Work survives crashes, but order matters |
| **Streaming (SSE/WS)** | Long-running output (LLM, progress bar) | Connection management |

**Default rule**: if the caller doesn't *need* the answer to complete its work, make it async. Sync calls between services are where outages cascade.

### Event-Driven Architecture (EDA)

In EDA, modules communicate by emitting and consuming events instead of calling each other directly.

```
Order Module: emits OrderPlaced event
  → Inventory Module: decrements stock
  → Email Module: sends confirmation
  → Analytics Module: updates dashboard
```

**Benefits:**
- Loose coupling: order module doesn't know who listens.
- Resilient: if email is down, order still completes.
- Auditable: events are an audit log by default.

**Costs:**
- Eventual consistency: stock count is briefly stale.
- Debugging: tracing a flow requires correlation IDs across logs.
- Schema evolution: changing an event shape breaks consumers.

Use EDA between modules where consistency can be eventual. Use sync calls where it cannot (authorization, payment confirmation).

### CQRS (Command Query Responsibility Segregation) — The Pragmatic Version

The full CQRS / Event Sourcing pattern is overkill for most products. The 20% that pays:

- Reads and writes have different shapes. The write model is normalized; the read model is denormalized for query patterns.
- Implement reads as direct queries (or materialized views) optimized for the API response shape.
- Implement writes through use cases that enforce invariants on the aggregate.

You don't need a separate database, separate service, or event sourcing to benefit from this separation.

```ts
// Command side — enforces invariants
class PlaceOrderUseCase {
  execute(cmd: PlaceOrderCommand): Promise<void> { ... }
}

// Query side — optimized for read shape
class OrderQueryService {
  getOrderHistory(userId: UserId): Promise<OrderHistoryView[]> {
    // SELECT with joins, projections, denormalization
  }
}
```

### API Gateway and BFF Patterns

**API Gateway**: a single entry point that routes to backend services, handles auth, rate limiting, and response shaping. Use it when you have multiple backend services and want one place for cross-cutting concerns. AWS API Gateway, Kong, Traefik, or NestJS as a thin gateway in front of microservices.

**BFF (Backend for Frontend)**: one gateway per frontend type (web, mobile, partner API). Each BFF aggregates downstream services into the exact response the client needs. Reduces over-fetching and chatty frontends. Pay attention to the maintenance cost — N BFFs is N codebases.

For an indie / single-team product: skip both. One backend serving one frontend doesn't need a gateway.

### Microservice Decomposition: When the Time Comes

If you eventually split, decompose by **bounded context**, not by technical layer. "Auth service, DB service, API service" is wrong. "Identity, Billing, Inventory, Notifications" is right — each owns its domain end-to-end.

Each microservice should:
- Own its database (never share a DB across services).
- Communicate via well-defined APIs or events.
- Be independently deployable.
- Have one team accountable.

### Folder Structure

```
src/
├── modules/
│   ├── user/
│   │   ├── user.controller.ts
│   │   ├── user.service.ts          # application
│   │   ├── domain/
│   │   │   ├── user.entity.ts
│   │   │   └── user.repository.ts   # interface
│   │   ├── infrastructure/
│   │   │   └── prisma-user.repository.ts
│   │   └── user.module.ts
│   └── insight/
│       └── ...
├── shared/
│   ├── prisma/
│   ├── redis/
│   ├── queue/
│   └── observability/
├── config/
└── main.ts
```

### Configuration Discipline

All configuration comes from environment variables, parsed by Zod at startup. The process must refuse to start with invalid config — never default silently to "localhost" in production.

```ts
const Env = z.object({
  NODE_ENV: z.enum(['development', 'staging', 'production']),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  OPENAI_API_KEY: z.string().startsWith('sk-'),
});
export const env = Env.parse(process.env);
```

### NestJS Specifics

If you chose NestJS as the framework, these are the framework-specific patterns that matter.

**Request Lifecycle Order** (memorize this):

```
Incoming Request
  → Middleware       (raw req/res, cors, helmet, body parsers)
  → Guards           (authn/authz — return false to reject with 403)
  → Interceptors (before)  (logging, transaction begin, request ID)
  → Pipes            (validation, transformation — Zod runs here)
  → Controller / Handler
  → Interceptors (after)   (response transform, transaction commit)
  → Exception Filters      (catch & format errors)
Outgoing Response
```

Knowing this order tells you where to put each concern. Auth check → Guard. Validation → Pipe. Logging → Interceptor. Error formatting → Filter.

**Dependency Injection Scope:**

| Scope | When | Cost |
|-------|------|------|
| `DEFAULT` (singleton) | Stateless services, repositories | Cheapest |
| `REQUEST` | Per-request state (current user, request ID) | New instance per request |
| `TRANSIENT` | Always a new instance | Every injection allocates |

Default to `DEFAULT`. Use `REQUEST` only for genuinely per-request concerns. Misusing `REQUEST` cascades — every consumer of a request-scoped provider also becomes request-scoped.

**Circular Module Dependencies:**

`forwardRef()` is the escape hatch. Using it once = pragma; using it three times = your modules are wrong. Refactor to extract the shared concept into a third module.

```ts
// Smell — forwardRef
@Module({
  imports: [forwardRef(() => UserModule)],
})
export class OrderModule {}

// Better — shared concept lives in its own module
@Module({
  providers: [SharedAuthService],
  exports: [SharedAuthService],
})
export class AuthModule {}
```

**Custom Decorators for Cross-Cutting Concerns:**

```ts
// Extract authenticated user
export const CurrentUser = createParamDecorator(
  (_data, ctx: ExecutionContext) => ctx.switchToHttp().getRequest().user,
);

// Use in handler
@Get('me')
me(@CurrentUser() user: User) { return user; }
```

**Module Hygiene:**

- Each domain module exports exactly what other modules need — services and DTOs.
- Never export internal repositories or domain entities. Other modules go through the service.
- `imports`: dependencies of this module. `exports`: what this module provides to others.
- Global modules (`@Global()`) are convenient and dangerous — every import becomes implicit. Use sparingly (Prisma, Logger).

**Microservice Patterns** (NestJS strength):

NestJS has first-class support for transports beyond HTTP — TCP, NATS, Redis Streams, Kafka, gRPC. You can run the same controller code as HTTP and as a queue consumer with one annotation change. Useful when transitioning to event-driven architecture.

---

## API Design

### REST as the Default

REST over HTTP is the lowest-friction interop choice. Use it unless you have a concrete reason to choose GraphQL (a frontend that consumes nested graphs from many services) or RPC (internal service-to-service with shared types).

### Resources, Not Verbs

`POST /orders/:id/cancel` ❌ — that's an RPC pretending to be REST.
`PATCH /orders/:id { status: "canceled" }` ✅ — state transition on a resource.

When the operation does not map to a resource state change (e.g., "send password reset email"), accept that REST does not fit and use a clearly named action endpoint. Don't bend the data model to fit REST.

### HTTP Status Codes Carry Meaning

**2xx — Success**
- **200 OK** — success with body
- **201 Created** — resource created (return `Location` header pointing to it)
- **202 Accepted** — work queued, not yet done (return job/poll URL)
- **204 No Content** — success without body (DELETE, PUT)

**3xx — Redirection**
- **301 Moved Permanently** — old URL is dead
- **304 Not Modified** — client's cached copy is still valid (ETag/If-None-Match)

**4xx — Client error**
- **400 Bad Request** — malformed: bad JSON, missing required field
- **401 Unauthorized** — *we don't know who you are* (no/invalid credentials)
- **403 Forbidden** — *we know who you are, but you can't do this*
- **404 Not Found** — resource doesn't exist *or* deliberately hidden (auth bypass defense — return 404 instead of 403 when leaking existence is itself a leak)
- **405 Method Not Allowed** — endpoint exists but not for this verb
- **409 Conflict** — duplicate, version mismatch, concurrent modification
- **410 Gone** — resource permanently deleted (vs 404 = unknown if existed)
- **412 Precondition Failed** — `If-Match` ETag mismatch (optimistic locking)
- **415 Unsupported Media Type** — wrong `Content-Type`
- **422 Unprocessable Entity** — semantically invalid (validation failed). [OPINION] RFC 9110 leaves this WebDAV-flavored; some teams use 400 for all client validation. Pick one and document it.
- **429 Too Many Requests** — rate limited (return `Retry-After`)

**5xx — Server error**
- **500 Internal Server Error** — bug in our code
- **502 Bad Gateway** — upstream returned malformed response
- **503 Service Unavailable** — we are down or overloaded (return `Retry-After`)
- **504 Gateway Timeout** — upstream timed out
- 5xx codes auto-retry on most HTTP clients; 4xx do not. This is critical to get right.

**The classic mistake**: returning `200 { error: "..." }` instead of `400`. This breaks every HTTP-aware tool — load balancers, monitoring, retry middleware, browser dev tools. `200` means success.

**401 vs 403 — the persistent confusion:**
```
No `Authorization` header        → 401
Invalid/expired token            → 401
Token valid but user lacks role  → 403
Token valid, user owns nothing   → 404 (defense) or 403
```

### Idempotency Keys for Mutating Requests

`POST /payments` from a flaky network might retry. Without an idempotency key, you double-charge. Standard pattern: client sends `Idempotency-Key: <uuid>` header; server stores `(key → result)` for 24h and returns the original result on retry.

### Webhook Handling

Webhooks are inbound HTTP from third parties (Stripe, GitHub, Slack). They look like API calls but the security model is reversed — *you* must verify *them*.

**Five rules every webhook handler must follow:**

1. **Verify signature on raw body, before parsing.** Stripe / GitHub / others sign the raw bytes; if your framework parses JSON before you check the signature, the signature won't match. NestJS: configure `rawBody: true` and use the raw buffer for HMAC verification.

   ```ts
   const expected = crypto
     .createHmac('sha256', WEBHOOK_SECRET)
     .update(rawBody)
     .digest('hex');
   if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(received))) {
     throw new UnauthorizedException();
   }
   ```

   Use `timingSafeEqual` to prevent timing attacks. Plain `===` leaks signature bytes.

2. **Reject expired timestamps.** Webhooks include a timestamp; reject anything older than 5 minutes to defend against replay attacks.

3. **Idempotency by event ID.** The same webhook will arrive multiple times (provider retries). Store processed event IDs (`webhook_events` table with unique constraint, or Redis `SET key NX EX 86400`) and return 200 immediately on duplicate.

4. **Respond fast.** Most providers retry if you don't respond in 10-30s. Acknowledge the webhook (200), then process async via a queue. Doing the actual work in-handler is a recipe for missed events.

5. **Handle out-of-order delivery.** Provider may deliver `subscription.updated` before `subscription.created`. Compare timestamps or use idempotent state transitions that don't care about order.

**Common webhook bugs:**
- Trusting the `event.type` without re-fetching the resource — webhooks can be forged after secret leak.
- 500ing on a webhook the provider doesn't recognize — return 200 for unknown event types you don't handle.
- Logging the full webhook body including secrets — redact `Authorization`, `signature`, `data.object.client_secret`.

### Pagination

Offset pagination (`?page=10&limit=20`) is wrong for any list that changes (new items push older ones into your next page, causing duplicates and skips). Use cursor pagination: `?cursor=<opaque>&limit=20` returning `nextCursor`.

### Versioning

Version in the URL (`/v1/`) for breaking changes. Within a version, additions are non-breaking; removals/renames require a new version. Long-lived APIs need a deprecation policy: announce, dual-serve, sunset.

### OpenAPI / Schema-First

Generate OpenAPI from the code (NestJS `@nestjs/swagger`, or Zod via `zod-to-openapi`). The schema is consumed by the frontend (typed client generation), by tests, and by partners. Hand-maintained API docs drift; generated docs do not.

### Validation at the Boundary

Every request body, query, and path param is parsed by a Zod schema. The handler receives the validated, typed object. Never `req.body.something` directly.

```ts
const CreateInsightSchema = z.object({
  title: z.string().min(1).max(200),
  category: z.enum(['tech', 'health', 'finance']),
  evidenceCount: z.number().int().positive(),
});

@Post('insights')
async create(@Body(new ZodValidationPipe(CreateInsightSchema)) body) {
  // body is fully typed and validated
}
```

### GraphQL: When and How

Use GraphQL when (a) one API serves many clients with different needs, (b) clients fetch deeply nested data, and (c) you have the operational maturity to deal with N+1 risks. Solve N+1 with DataLoader. Limit query depth and complexity per request. Use persisted queries in production to prevent malicious queries.

### tRPC for Internal TypeScript Boundaries

If your frontend and backend are both TypeScript and share a repo, tRPC eliminates schema duplication entirely. Avoid for public APIs (no language interop, no OpenAPI).

---

## Database Architecture

### PostgreSQL as the Default

PostgreSQL is the right choice for ~95% of new applications. It handles relational, JSON (JSONB), full-text search, vector (pgvector), and time-series workloads (with TimescaleDB) in one engine. Reach for a specialized store (Elasticsearch, ClickHouse, MongoDB) only when a measured workload requires it — not by default.

### Schema Design

Normalize first, denormalize when measured. Foreign keys with `ON DELETE` policies are not optional — `RESTRICT`, `CASCADE`, or `SET NULL` is a deliberate choice every time. Use `NOT NULL` aggressively; nullable columns are a permanent open question for every reader.

### Use the Right Types

- IDs: `UUID` (v7 for time-sortable) or `BIGSERIAL`. Never `INT` — you will regret it.
- Money: `NUMERIC(precision, scale)`. Never `FLOAT` — floating point and currency do not mix.
- Timestamps: `TIMESTAMPTZ`. Never `TIMESTAMP` (which has no timezone and is a permanent trap).
- Enums: Postgres `ENUM` for stable categorical fields, `TEXT` with a `CHECK` constraint when categories evolve.
- JSON: `JSONB` (not `JSON`). Index with GIN when queried.

### Indexes Are Not Free

Every index speeds reads and slows writes. Index based on actual query patterns: `EXPLAIN ANALYZE` your top 10 queries and index what's missing. Multi-column indexes follow the leftmost-prefix rule. Partial indexes (`WHERE status = 'active'`) are powerful for skewed data.

Common patterns:
- Foreign key columns: always indexed
- `(user_id, created_at DESC)` for "user's recent items"
- `WHERE deleted_at IS NULL` partial index for soft deletes
- GIN on JSONB for flexible queries
- HNSW or IVFFlat on `vector` columns for ANN search

### Transactions Are the Only Consistency Boundary

Multi-step operations that must be all-or-nothing run in a single transaction. The rest of the system — Redis, queues, third-party APIs — is not transactional. **You cannot atomically update Postgres and send an email.** This is the source of the dual-write problem; see Outbox Pattern below.

Isolation levels matter:
- `READ COMMITTED` (default) — protects against dirty reads only.
- `REPEATABLE READ` — needed for financial calculations spanning multiple reads.
- `SERIALIZABLE` — strongest, with retry-on-conflict cost.

### Migrations Are Code

Migrations live in version control, are reviewed, and run in CI. Prisma Migrate, Drizzle, or plain SQL with `golang-migrate` — the tool matters less than the discipline. **Migrations must be backward compatible** during rolling deploys: old code still works against the new schema for the duration of the deploy.

The expand/contract pattern:
1. Expand: add new column nullable, deploy.
2. Backfill: populate the new column.
3. Switch: code reads/writes new column.
4. Contract: drop the old column in a later release.

Skipping this for a `NOT NULL` column added directly will break running pods during deploy.

### N+1 Is the Default Bug

ORMs make it easy to write `users.map(u => u.orders)` which executes N+1 queries. Detect with query logs in dev (`prisma:query`), prevent with eager loading (`include`/`select`) or DataLoader.

### Connection Pooling

Postgres handles ~100-300 connections well; beyond that, idle connections eat memory. With many app instances × many connections each, you exceed this fast. Use **PgBouncer** in transaction mode for high-instance-count deployments (Vercel, Lambda). Supabase and Neon ship with built-in pooling.

### Soft Delete vs Hard Delete

Soft delete (`deleted_at TIMESTAMPTZ`) keeps history but every query needs `WHERE deleted_at IS NULL` (use a view or a Prisma extension). Hard delete is simpler but loses audit. Choose per table: regulated data soft, ephemeral data hard.

### Outbox Pattern for Reliable Side Effects

The most important distributed-systems pattern in a single-database world. Worth understanding deeply.

**The problem (dual write):**
You want to do two things atomically:
1. Update an order's status to `paid` in Postgres
2. Publish `OrderPaid` event to a queue so email/inventory/analytics react

These cannot share a transaction — Postgres and the queue are separate systems. So you face four bad scenarios:

```
DB committed, queue published    → ✅ Happy path
DB committed, queue failed       → ❌ Other modules never know
DB failed, queue published       → ❌ Phantom event ("paid" but no record)
DB failed, queue failed          → ✅ Retry from scratch
```

**The fix — Outbox Pattern:**

```sql
CREATE TABLE outbox (
  id          UUID PRIMARY KEY,
  aggregate   TEXT NOT NULL,           -- 'Order'
  event_type  TEXT NOT NULL,           -- 'OrderPaid'
  payload     JSONB NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);
CREATE INDEX outbox_unpublished ON outbox (created_at) WHERE published_at IS NULL;
```

In the use case, write the event to `outbox` in the **same transaction** as the order update:

```ts
await prisma.$transaction([
  prisma.order.update({ where: { id }, data: { status: 'paid' } }),
  prisma.outbox.create({ data: { aggregate: 'Order', event_type: 'OrderPaid', payload: {...} } }),
]);
```

A separate **outbox publisher** process polls unpublished events and pushes to the queue:

```ts
const events = await prisma.outbox.findMany({
  where: { published_at: null },
  orderBy: { created_at: 'asc' },
  take: 100,
});
for (const e of events) {
  await queue.add(e.event_type, e.payload, { jobId: e.id }); // jobId = outbox.id ensures idempotency
  await prisma.outbox.update({ where: { id: e.id }, data: { published_at: new Date() } });
}
```

**Guarantees and trade-offs:**

| Property | Outbox provides |
|----------|----------------|
| Atomicity (DB commit ↔ event publish) | ✅ |
| Order preservation | ✅ (per aggregate, by `created_at`) |
| Exactly-once delivery | ❌ — at-least-once. Consumers must be idempotent. |
| Latency | Publishing lag = polling interval (1-5s typical) |

**Cleanup**: published events accumulate. Either soft-keep (archive after N days) or hard-delete after consumers acknowledge. Don't let the table grow forever.

**Alternatives**:
- **Change Data Capture (CDC)** with Debezium: read Postgres WAL, stream to Kafka. More infrastructure but no app-side polling.
- **Transactional Outbox + Listen/Notify**: use Postgres `NOTIFY` to wake the publisher instead of polling. Faster, still reliable.

**When you don't need this**: if losing an event is acceptable (analytics, fire-and-forget notifications), skip the outbox and just publish directly. Reserve outbox for events that drive business state in another service.

### Read Replicas

Read replicas scale read throughput, not write. Replication lag is real (typically 10-100ms). Reads that must see the most recent write (e.g., right after a write in the same request) must hit the primary. Pattern: route by query, default to replica, override to primary for read-after-write scenarios.

---

## Caching Strategy

### Cache What You Measured Slow

Caching adds invalidation complexity. Cache only after profiling shows a hotspot. Premature caching adds bugs without the gain.

### The Three Caching Patterns

1. **Cache-aside (lazy)**: Read → check cache → miss → read DB → write cache. Standard for read-heavy, slow queries.
2. **Write-through**: Every write updates cache and DB. Strong consistency, slower writes.
3. **Write-behind**: Cache absorbs writes, flushes async. Fast but can lose data on crash. Rarely worth it.

For most cases, cache-aside with TTL is the right answer.

### TTL is the First Line of Invalidation Defense

A short TTL (60-300s) hides invalidation bugs at the cost of slightly stale data. Most domains tolerate 60s of staleness; the ones that don't (financial balances, real-time presence) shouldn't be cached at all or need explicit invalidation on writes.

### Cache Stampede

When a hot key expires, every concurrent request hits the DB simultaneously. Mitigations:
- **Locking**: First request acquires a Redis lock to refill; others wait or serve stale.
- **Probabilistic early refresh**: Refresh before TTL expiration with growing probability as TTL approaches.
- **Stale-while-revalidate**: Serve expired cache while refreshing in the background.

### Cache Keys Are an API

`user:123:profile` is a contract. Versioning the key prefix (`v2:user:123:profile`) lets you ship a cache shape change without invalidating with `FLUSHDB`. Document the convention.

### Layered Caching

CDN (static assets, public API responses) → application memory (per-process LRU for hot config) → Redis (shared) → DB. Each layer is faster and smaller than the one beneath. Memory caches are per-process — invalidation across instances is hard, so use only for truly read-only data.

### Redis Patterns Beyond Caching

- **Rate limiting**: `INCR` + `EXPIRE` per `(user, window)`.
- **Distributed locks**: `SET key value NX EX 30` — but read [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) before relying on these for correctness. Prefer Redlock-aware libraries; never roll your own.
- **Pub/Sub**: lightweight event broadcast (no persistence — use Streams or a real broker for durability).
- **Streams**: durable, ordered log; good for moderate-throughput event processing.
- **Sorted sets**: leaderboards, rate-limiters, time-windowed queues.

---

## Background Jobs & Queues

### Why Queues

Some work doesn't belong in the request path: sending email, processing uploads, calling slow third-party APIs, generating reports, AI inference. Queue it; respond to the user immediately; process async.

### BullMQ Job Anatomy

```ts
@Processor('insights')
export class InsightProcessor {
  @Process('generate')
  async generate(job: Job<{ clusterId: string }>) {
    // 1. Pull dependencies fresh (don't trust process state from job creation)
    // 2. Do the work
    // 3. Be idempotent — this job may run twice
    // 4. Throw to retry, return to ack
  }
}
```

### Idempotency is Mandatory

Every queue gives at-least-once delivery — your job *will* run twice eventually. Design every handler so a second run with the same input is a no-op. Common patterns:
- Use a deterministic ID for the side effect (`INSERT ... ON CONFLICT DO NOTHING`).
- Track processed job IDs in a `processed_jobs` table or Redis `SET key NX EX 86400`.
- Check current state before acting (`if (order.status === 'paid') return`).

### Job Dependencies and Workflows

Linear chains (collect → embed → cluster → synthesize) belong in BullMQ flows. Branching, conditional logic, and human-in-the-loop steps belong in a workflow engine (Temporal, Inngest). Don't reinvent these in BullMQ — the failure modes are subtle.

### Retry Strategy

- Transient failures (network, rate limit): exponential backoff with jitter, capped at ~5 retries.
- Permanent failures (validation, 404 from upstream): fail fast to dead-letter queue.
- Distinguish via error type — `if (error.status >= 400 && error.status < 500) throw new UnrecoverableError(...)`.

### Dead-Letter Queue

Jobs that fail after max retries land here. A dead-letter queue without alerts is a black hole — every dead-letter must page or open a ticket.

### Concurrency and Rate Limiting

BullMQ's `concurrency` setting controls parallelism per worker. To respect upstream rate limits, use `Queue.rateLimit({ max, duration })` or, for finer control, a Redis-backed semaphore. **Don't rely on app-level concurrency for rate limit safety** — multiple workers exist.

### Scheduled Jobs (Cron)

Use `Queue.add(..., { repeat: { pattern: '0 */6 * * *' } })` for cron in BullMQ. For high-stakes scheduled jobs (billing, reports), consider a dedicated scheduler with leader election (Temporal cron, Kubernetes CronJob with locking) — BullMQ's repeat is great for routine work, not regulatory work.

### Job Visibility

Bull-board or BullMQ's UI shows running, failed, and stuck jobs. Production must have this dashboard accessible and metrics piped to your monitoring system.

---

## Real-time Communication

### Choosing the Right Tool

- **Server-Sent Events (SSE)**: server → client streaming. Trivial to implement (`text/event-stream`), works through HTTP/2, perfect for AI streaming and notifications.
- **WebSockets**: bidirectional, low-latency. Use when client must push frequently (chat, collaborative editing).
- **Long polling**: legacy fallback. Avoid unless required.

For most "live updates" use cases, SSE is enough and simpler than WebSockets.

### WebSocket Authentication

WebSocket upgrade requests carry the initial HTTP headers (cookies, Authorization). Authenticate at the upgrade. After the upgrade, headers don't matter — every message must trust the session established at upgrade.

### Scaling Persistent Connections

Each open WebSocket holds memory and a file descriptor. With N instances and M users, you have ~M/N connections per instance. Use a pub/sub backplane (Redis Pub/Sub, NATS) so messages from instance A reach a user connected to instance B.

### Backpressure

A slow client cannot consume messages as fast as you produce. Without backpressure, the server's send buffer grows and the process OOMs. Drop messages, disconnect slow clients, or batch — choose deliberately.

---

## Authentication & Authorization

### Authentication vs Authorization

- **Authentication**: who are you? (login, JWT, session)
- **Authorization**: what can you do? (RBAC, ABAC, RLS)

Conflating them is the most common source of permission bugs.

### Password Storage

`bcrypt` with cost factor ≥12, or `argon2id` (preferred for new systems). Never store plaintext, MD5, SHA-256 of passwords — these are not for passwords.

### Session vs JWT

- **Sessions** (server-side): revocable instantly, simple, requires session store. Default for web apps.
- **JWT**: stateless, scales without a session store, harder to revoke (need a denylist). Use for stateless APIs, mobile, and service-to-service.

JWT contains a header, payload, and signature. **The signature is the only thing standing between an attacker and admin access**.

**Algorithm choice:**
- `RS256` / `ES256` (asymmetric) — public key verifies, private key signs. Default for any token shared across services or read by clients.
- `HS256` (symmetric) — secret signs and verifies. Only for tightly-controlled internal use.
- **Never `none`** — explicit allowlist required.

**Required validations (every token, every request):**
- `iss` (issuer) — matches your token issuer
- `aud` (audience) — matches your service
- `exp` (expiration) — token not expired
- `nbf` (not before) — token already valid
- Signature — verified with the right key

**The two CVE-class JWT mistakes:**

1. **`alg: none` accepted** (CVE-2015-9235 family). Library lets the token specify `"alg": "none"` and skips verification. Defense: explicit allowlist of accepted algorithms in your verifier — never let the token's header decide.

   ```ts
   jwt.verify(token, secret, { algorithms: ['RS256'] }); // not [] or undefined
   ```

2. **Algorithm confusion** (CVE-2018-0114, etc.). Service expects `RS256` (verifies with public key); attacker sends a token with `alg: HS256` signed with the public key as HMAC secret. If the library doesn't enforce the algorithm, it verifies and the attacker controls the payload. Defense: same fix — algorithm allowlist.

3. **Trusting `kid` from the token** to fetch the verification key. Attacker points `kid` to an attacker-controlled URL or a key they generated. Defense: only resolve `kid` against a known key set (JWKS).

### Refresh Tokens

Short-lived access tokens (15 min) + long-lived refresh tokens (30 days, stored httpOnly + Secure cookie). On refresh, rotate the refresh token (invalidate the old one) — detection of reuse is your defense against stolen refresh tokens.

### OAuth / OIDC

For social login or SSO, use a library — `passport`, `next-auth`, or your platform's SDK. Implementing OAuth from scratch means implementing all of CVE history yourself.

### Authorization Models

- **RBAC** (Role-Based): user has roles, roles have permissions. Simple, scales to most apps.
- **ABAC** (Attribute-Based): policy evaluates user + resource + action attributes. Flexible but complex.
- **ReBAC** (Relationship-Based, e.g., Google Zanzibar): graph of relationships. Best for sharing/collaboration UX.
- **Row-Level Security (RLS)**: enforced in the database itself. Strong defense-in-depth.

For an indie/startup product, RBAC + RLS is the right baseline.

### RLS in Postgres

RLS policies enforce authorization at the row level inside the database. The application sets a session variable (`SET LOCAL app.user_id = '...'`) and policies use it:

```sql
CREATE POLICY user_owns_insight ON insights
  FOR SELECT USING (user_id = current_setting('app.user_id')::uuid);
```

Even if a SQL injection bug bypasses application-layer auth, RLS still protects the data. Supabase makes this trivial; with Prisma, use `$executeRaw` to set the session var per request.

### Permission Checks Belong at the Use Case

Not in controllers (too late, untested), not in domain entities (couples auth to domain). The application/use-case layer is where `assertCanEditInsight(user, insight)` runs.

---

## Security

### OWASP Top 10 as the Baseline

If you cannot articulate what each of these is and how your code prevents it, do not run a public service:
1. **Broken Access Control** — RLS + use-case-level checks.
2. **Cryptographic Failures** — TLS, strong password hashing, encrypted secrets.
3. **Injection** — parameterized queries everywhere, no string concat.
4. **Insecure Design** — threat model new features.
5. **Security Misconfiguration** — defaults reviewed, no debug in prod.
6. **Vulnerable Components** — `npm audit`, Dependabot, SBOM.
7. **Identification & Auth Failures** — MFA, rate limit login, session rotation.
8. **Software & Data Integrity Failures** — package lockfiles, signed images.
9. **Logging & Monitoring Failures** — security events logged and alerted.
10. **SSRF** — block requests to internal IPs from user-supplied URLs.

### Secrets Management

Secrets never live in:
- Git (`.env` in `.gitignore`, but `git log` still has them)
- Logs (redact `Authorization`, `password`, `token` keys)
- Error messages to users
- Frontend bundles

Secrets live in: a secret manager (AWS Secrets Manager, GCP Secret Manager, Doppler, Infisical, 1Password Connect) and are injected at runtime. Rotate quarterly; rotate immediately on compromise.

### Encryption

- **In transit**: TLS 1.3, HSTS, no plaintext anywhere internet-facing.
- **At rest**: cloud provider encryption is sufficient for most cases. Field-level encryption (PII, secrets in DB) for regulated data.
- **Application-layer**: AES-GCM for symmetric, libsodium / WebCrypto for primitives. Never roll your own cipher.

### Input Validation

Already covered in TypeScript Discipline, but for security: every input is hostile. SQL injection, XSS, SSRF, path traversal, XXE, command injection — all stem from trusting input. Validate type, length, format, and range. For URLs from users, parse, validate the scheme (`http`/`https` only), and check the resolved IP isn't internal (SSRF defense).

### Rate Limiting

Per-IP and per-user, on every public endpoint. Login endpoints get aggressive limits (5/min) to slow brute force. Use Redis with sliding window or token bucket. Global rate limits at the edge (Cloudflare, API Gateway) plus app-level for fine control.

### CORS

Set `Access-Control-Allow-Origin` to your specific frontend origin, never `*` for credentialed requests. `Access-Control-Allow-Credentials: true` only with explicit origin. Preflight caching (`Access-Control-Max-Age`) reduces overhead.

### CSRF

If you use cookie-based sessions with state-changing requests, you need CSRF protection: SameSite=Lax cookies (default in modern browsers) plus CSRF tokens on POST/PUT/DELETE. JWT in `Authorization` header is not vulnerable to CSRF (browsers don't auto-send custom headers cross-origin).

### Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: ...
```

NestJS `helmet` middleware sets sensible defaults; review and tune for your app.

### Dependency Hygiene

`npm audit` in CI, Dependabot for automated PRs, lockfile committed. Pin direct dependencies, allow flexibility for transitives. Know which dependencies have native code or postinstall scripts (supply-chain attack vector).

### Logging Sensitive Data

Authorization headers, request bodies of login endpoints, payment data — these must never reach the log aggregator. Build a redaction layer in your logger config and test it.

---

## Performance & Scaling

### Measure First

Without a baseline (p50, p95, p99 latency, RPS, error rate), every "optimization" is guessing. APM (DataDog, New Relic, Sentry Performance) or self-hosted (Prometheus + Grafana) — pick one and instrument before tuning.

### The N+1 Killer

Database round trips dominate latency for most APIs. Profile with query logs — if you see one logical operation issuing many queries, that's the fix that yields 10-100x improvements before anything else.

### Connection Pool Sizing

Postgres connections are expensive (~10MB each). Pool size = (max worker concurrency) × (instance count). Beyond 200-300 total connections, use PgBouncer in transaction mode. Misjudging this is the #1 cause of "the database is fine but my app times out."

### Index Tuning

`EXPLAIN (ANALYZE, BUFFERS)` reveals what's actually happening. Sequential scans on large tables, hash joins where merge would be cheaper, mismatched index types — these show up clearly. `pg_stat_statements` finds your top queries by total time, which is more useful than "slowest single query."

### Caching as a Last Resort, Not First

Every cache adds invalidation complexity. Faster query > smaller payload > caching. Reach for caching when profile shows a clear hotspot that's hard to make faster.

### Horizontal Scaling Prerequisites

To run multiple instances of your service, **the service must be stateless**. State lives in Postgres, Redis, or S3. In-process state (request rate counters, websocket connection lists, file-system caches) breaks horizontal scaling. The first time you hit "it works on one instance but breaks with two," it's almost always state in the wrong place.

### Vertical vs Horizontal

Scale up (bigger instance) for non-parallelizable work — a single complex query, a CPU-bound batch. Scale out (more instances) for parallelizable work — handling more concurrent requests. Cloud bills favor scale-out; engineering complexity favors scale-up. The right answer depends on the bottleneck, not preference.

### Async I/O Saturation

Even with horizontal scaling, a single slow upstream (a third-party API) can saturate your event loops. Two defenses: timeouts on every external call (5s default, never infinite), and circuit breakers that fail fast when upstream is down.

### Graceful Degradation

When a non-critical dependency is down, the service should still serve the critical path. If Redis is down, hit the DB. If the recommendation service is down, return an empty array, not a 500. The degraded response is a feature, not a bug.

### Load Testing

Synthetic load tests (k6, Artillery) before launch and before major changes. Test the realistic distribution, not just the easy path. Read latency under load (concurrent reads + writes) is the only honest measurement.

---

## AI / LLM Backend

### LLM as a Slow, Expensive, Non-deterministic External API

Treat OpenAI / Anthropic / your provider like a third-party API with poor SLA. Timeouts (30-60s), retries with backoff, fallback to cached responses or simpler models.

### Streaming as the Default UX

LLM completions are slow (5-30s for full response). Stream tokens via SSE — the user sees output starting in <1s. The endpoint:

```ts
@Get('chat')
chat(@Res() res: Response, @Query('q') q: string) {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  const stream = await openai.chat.completions.create({ ..., stream: true });
  for await (const chunk of stream) {
    res.write(`data: ${JSON.stringify(chunk)}\n\n`);
  }
  res.end();
}
```

NestJS has built-in SSE support (`@Sse()`).

### Token Accounting

Every request costs tokens × price. Without per-request token logging, you cannot answer "what is our actual cost per user." Log: input tokens, output tokens, model, request ID. Roll up to `(user, day, model)` for cost dashboards.

### Prompt Versioning

Prompts are code. Version-control them, code-review them, and tag the version on every request log so you can attribute quality regressions to a prompt change.

### Structured Output

For machine-consumed responses, use the provider's structured output mode (OpenAI `response_format: { type: "json_schema" }`, Anthropic tool use). This is far more reliable than "please respond in JSON" and asking the LLM nicely. Validate the response with Zod after parse — providers occasionally return invalid JSON.

### Vector Storage with pgvector

For semantic search and RAG, pgvector is the right default — same database as your operational data, transactional, no extra service. Specialized vector DBs (Pinecone, Weaviate, Qdrant) make sense when you have >10M vectors or specific query patterns pgvector doesn't serve.

```sql
CREATE EXTENSION vector;
ALTER TABLE documents ADD COLUMN embedding vector(1536);
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

HNSW vs IVFFlat: HNSW is faster at query time, slower to build, more memory. IVFFlat the opposite. HNSW for most online use cases.

### Embedding Cost Control

Embeddings are cheap per call but add up. Cache embeddings by content hash — recomputing the same text is waste. Batch embedding calls (OpenAI accepts up to 2048 inputs per call).

### RAG Architecture

```
User query
  → embed query
  → vector search (top K candidates)
  → optional: rerank with cross-encoder
  → context assembly with citation tracking
  → LLM call with context
  → response with citations
```

Common failures: stale embeddings (re-embed when source changes), context overflow (truncate or summarize), hallucination on missing context (instruct LLM to say "I don't know" if context insufficient).

### Agent Loops & Tool Use

An "agent" is an LLM that can call tools and react to their output. The minimal loop (OpenAI-style; Anthropic similar):

```ts
const messages: ChatMessage[] = [
  { role: 'system', content: systemPrompt },
  { role: 'user', content: userMessage },
];

for (let step = 0; step < MAX_STEPS; step++) {
  const response = await llm.chat.completions.create({
    model: 'gpt-4o-mini',
    messages,
    tools, // [{ type: 'function', function: { name, parameters, description } }, ...]
  });

  const assistantMsg = response.choices[0].message;
  messages.push(assistantMsg); // append the assistant turn (may include tool_calls)

  // Stop condition: model is done calling tools
  if (!assistantMsg.tool_calls?.length) {
    return assistantMsg.content;
  }

  // Execute each tool call and append a `tool` role message per call
  for (const call of assistantMsg.tool_calls) {
    const result = await executeTool(call.function.name, JSON.parse(call.function.arguments));
    messages.push({
      role: 'tool',
      tool_call_id: call.id,            // ← critical: links result to the call
      content: JSON.stringify(result),
    });
  }
}

throw new MaxStepsExceededError();
```

**Common bugs in agent loops:**
- Forgetting `tool_call_id` on the tool response → API returns 400.
- Pushing tool results before pushing the assistant message → API returns 400 (tool messages must follow an assistant message with `tool_calls`).
- Not checking `finish_reason === 'tool_calls'` → infinite loops on edge cases.
- No max step limit → runaway cost (one bad prompt = $$$).

**Production agents need:**
- Max-step limit (cost control, runaway loop prevention).
- Per-tool-call timeout (a slow web search shouldn't block the whole agent).
- Tool-call retries with idempotency keys.
- Full trace of every step (each LLM call, each tool input/output) for debugging.
- Human-in-the-loop checkpoints for high-stakes actions (sending email, charging cards, deleting data).
- Token budget per agent run — kill if it exceeds.

### Safety & Guardrails

LLM outputs can be wrong, biased, or harmful. For user-facing outputs: content filtering, PII redaction, prompt injection defenses (treat retrieved content as untrusted). For agent actions touching real systems: dry-run mode, confirmation steps, and audit logs. **An agent that can spend money or send messages must be reviewed by a human until you have months of clean operation data.**

### Evaluation

You cannot improve what you do not measure. Build an eval harness with curated inputs and expected behaviors, run on every prompt change, track metrics (accuracy, faithfulness, toxicity, cost, latency). Tools: Braintrust, LangSmith, OpenAI Evals, or roll your own with Vitest + JSON fixtures.

---

## Multi-tenancy

A multi-tenant SaaS serves multiple organizations from one deployment. Three isolation strategies, in increasing cost:

### Strategy 1: Shared DB, Shared Schema (tenant_id column)

Every row carries `tenant_id`; every query filters by it. Cheapest. Highest risk — one missing `WHERE tenant_id = ?` leaks data across tenants.

**Defense in depth:**
- **RLS policy**: enforce at the database level. Even an injection bug can't bypass.
- **Type-level guard**: a `TenantScoped<T>` wrapper that requires tenant context on every query.
- **Audit**: log every cross-tenant query attempt.

```sql
CREATE POLICY tenant_isolation ON insights
  FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### Strategy 2: Shared DB, Schema-per-Tenant

Each tenant gets a Postgres schema; queries set `search_path` per request. Better isolation. Migrations apply per schema (slow at high tenant counts).

### Strategy 3: Database-per-Tenant

Strongest isolation, regulatory-friendly (GDPR, residency). Operationally expensive — N databases to migrate, monitor, back up.

**Choosing**: most B2B SaaS starts with Strategy 1 + RLS. Move to 2/3 only when a customer's compliance review demands it.

### Cross-Tenant Operations

Some operations span tenants (admin dashboards, billing aggregation, support tools). Build them as a separate service/role with explicit cross-tenant permission, not as a "superuser" bypass on the regular app. Audit every cross-tenant access.

---

## File Storage

### Object Storage as the Default

S3 (or compatible: R2, B2, Spaces) for user uploads, generated artifacts, backups. Never store user files on the application server's disk — they vanish on deploy and break horizontal scaling.

### Direct Upload via Presigned URLs

Don't proxy file uploads through your API server — it costs bandwidth, RAM, and timeouts on large files. Instead:

1. Client requests presigned URL: `POST /uploads/presign`
2. Server returns a one-time URL and confirms permission/quota
3. Client uploads directly to S3 with the URL
4. Client confirms completion: `POST /uploads/:id/complete`
5. Server validates the file (size, MIME, virus scan) and links it to the user

```ts
const url = await s3.getSignedUrl('putObject', {
  Bucket: 'uploads',
  Key: `users/${userId}/${uuid()}.pdf`,
  ContentType: 'application/pdf',
  ContentLength: 10 * 1024 * 1024, // enforce max size
  Expires: 60 * 5, // 5 min
});
```

### Validate Files Server-Side

A client-claimed `Content-Type: image/png` is a lie waiting to happen. Validate by reading magic bytes (`file-type` library), not the extension. Reject if it doesn't match what you expect.

### CDN for Public Assets

S3 → CloudFront / Cloudflare R2 with custom domain. Cache headers (`Cache-Control: public, max-age=31536000, immutable` for hash-named files). Private files via signed URLs with short TTL.

### Storage Costs Compound

Lifecycle policies move cold data to cheaper tiers (S3 Glacier, R2 archive). Delete user uploads on account deletion (GDPR). Audit storage growth monthly — orphaned files are common.

---

## Email & Notifications

### Transactional vs Marketing — Separate Always

Transactional (password reset, receipts) and marketing (newsletters, drip campaigns) have different requirements:
- Transactional: must arrive, can't be unsubscribed from, low volume.
- Marketing: must respect unsubscribe (CAN-SPAM, GDPR), high volume.

Send from different domains/subdomains (`mail.yourapp.com` vs `news.yourapp.com`) so a marketing reputation problem doesn't kill password reset deliverability.

### Provider Choice

- **Resend / Postmark**: indie-friendly, great deliverability, simple API.
- **SendGrid / Mailgun**: enterprise scale.
- **AWS SES**: cheapest at scale, more setup.

For an indie product: start with Resend. Switch later if cost becomes meaningful.

### Deliverability Hygiene

DKIM, SPF, DMARC configured before first send. Without these, your emails land in spam.
- **DKIM**: cryptographic signature proving the email came from you.
- **SPF**: DNS record listing servers allowed to send for your domain.
- **DMARC**: policy telling receivers what to do when DKIM/SPF fail.

### Async Always

Email goes through a queue. Sending in-request times out under load and couples your API to a third party's availability. Outbox pattern applies.

### Idempotency

Each notification has a deterministic key (e.g., `welcome-email:user-123`). Send only if no record exists. Otherwise, a retry sends the same welcome email twice.

---

## Internationalization (i18n) and Time

### Time

- Store all timestamps in UTC with timezone (`TIMESTAMPTZ` in Postgres).
- Convert to user's timezone only at the presentation layer (frontend or formatted output).
- Never store local time without timezone — you lose information.
- Beware DST: `2026-03-09 02:30 America/New_York` may not exist (spring forward).

### Locale & Currency

- User profile stores `locale` (e.g., `en-US`, `ko-KR`) and currency preference.
- Number, date, currency formatting in the formatting layer — `Intl.NumberFormat`, `Intl.DateTimeFormat`.
- Never store currency amounts as floats. Use minor units (cents) as integers, plus an ISO 4217 currency code.

### Translation Strings

Keys in code (`order.confirmation.title`), translations in JSON / YAML files. Never hardcode user-facing strings in business logic. Tools: i18next, next-intl, fluent.

### Database Considerations

- `text_search` indexes are language-specific. Use `pg_trgm` for cross-language fuzzy search, language-tagged `tsvector` for proper full-text search.
- Sorting strings is locale-dependent — `de_DE` sorts `ä` differently than `en_US`. Use `COLLATE` clauses.

---

## Audit Logging

Audit logs are **separate from application logs**. They serve compliance, security forensics, and "who changed what when."

### What Goes In

- Authentication events (login, logout, failed attempts, password change).
- Authorization decisions on sensitive resources (admin access, data export).
- Mutations to user-controlled data (settings change, role assignment, billing change).
- Admin actions (impersonation, manual data fixes, bulk deletes).

### Schema

```sql
CREATE TABLE audit_log (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID,
  actor_id     UUID,                    -- who did it
  actor_type   TEXT,                    -- 'user', 'system', 'admin'
  action       TEXT NOT NULL,           -- 'order.canceled'
  resource_type TEXT NOT NULL,
  resource_id  TEXT NOT NULL,
  changes      JSONB,                   -- before/after for mutations
  ip_address   INET,
  user_agent   TEXT,
  request_id   TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON audit_log (tenant_id, resource_type, resource_id, created_at DESC);
```

### Properties

- **Append-only**: never UPDATE or DELETE audit rows. Use a database role that can only INSERT.
- **Tamper-evident**: hash chains or signed entries for high-stakes systems (financial, medical).
- **Retention**: years, not days. Set per regulatory requirement (GDPR: 6 years for some records).
- **Separate from operational logs**: structured logs are for debugging; audit is for compliance. Don't mix.

### Don't Log

PII beyond what's needed (full payment card numbers, social security numbers). The audit log is itself a security target — minimize sensitive data within it.

---

## Reliability & Error Handling

### Failure Categories

- **Programmer error**: a bug. The fix is in code. Crash the process if state is corrupted; a clean restart is safer than continuing.
- **Operational error**: external system failure, transient. Retry with backoff.
- **User error**: bad input. Return 4xx with a useful message.

Conflating these (returning 500 for bad input, retrying programmer errors) is the bug pattern most often seen in incident reports.

### Timeouts on Everything

No external call has an infinite timeout. Database queries (`statement_timeout`), HTTP clients (Axios, fetch), Redis operations. Default 5s, tune per endpoint. A 30-second hung query is more harmful than a fast failure.

### Retry with Exponential Backoff and Jitter

Linear retries cause thundering herds. Exponential backoff with jitter (`(2^attempt + random()) * baseDelay`) spreads retries across time. Cap total retry duration; some failures are not transient.

### Circuit Breakers

After N consecutive failures to a downstream, open the circuit — fail fast for a cooldown period — then half-open to test recovery. `opossum` is the standard Node library. Critical for protecting your service from a slow upstream cascading into total failure.

### Idempotency Everywhere

Already covered, but worth repeating: every retry-able operation must be idempotent. Without this, retries cause duplicate side effects.

### Sagas for Distributed Transactions

You cannot do a distributed `BEGIN ... COMMIT` across services. Sagas: orchestrate a series of compensatable steps, rolling back the completed steps if a later step fails. Tools: Temporal, Inngest, or hand-rolled with care.

### Graceful Degradation

Already covered in Performance. The architecture choice: which dependencies are critical (DB, auth) and which are degradable (recommendations, analytics). Document this; failure modes show up under load, not in code review.

### Chaos Engineering for Mature Systems

Once you have reliable observability, deliberately inject failures (kill pods, block network to a dependency, slow down a query) in staging or with traffic shaping. The first time this is real production fire, the cost is much higher.

---

## Observability

### The Three Pillars

- **Logs**: discrete events with context.
- **Metrics**: aggregated numerical time series.
- **Traces**: causal chain of operations across services.

You need all three. Logs answer "what happened to this request?", metrics answer "is the system healthy?", traces answer "where did this request spend time?"

### Structured Logging

Plain string logs (`console.log("user logged in")`) are unsearchable at scale. Log JSON with consistent fields:

```json
{
  "level": "info",
  "msg": "user logged in",
  "userId": "abc-123",
  "requestId": "req-456",
  "duration_ms": 45,
  "timestamp": "2026-05-08T12:00:00Z"
}
```

Pino is the standard for Node.js — fast, structured, low overhead. Always log: `requestId` (correlates a request across logs), `userId` (when authenticated), `duration_ms` for spans, `error.stack` for errors.

### Log Levels

- `fatal`: process is going to exit
- `error`: an operation failed; investigation needed
- `warn`: something unusual but handled
- `info`: high-level lifecycle events (server started, user signed up)
- `debug`: detailed flow, off in production by default
- `trace`: very fine-grained, almost never on

Production runs at `info`. `debug` and below are switchable per request via header for live debugging.

### Distributed Tracing

OpenTelemetry is the standard. Every request gets a trace ID; every operation (HTTP call, DB query, queue publish) is a span. Trace IDs propagate via headers (`traceparent`) across service boundaries. Visualize in Jaeger, Tempo, Honeycomb, or DataDog.

A trace shows: "this 2-second request spent 1.8s in a single Postgres query." Without traces, you guess.

### Metrics That Matter

The four golden signals (Google SRE):
1. **Latency**: p50, p95, p99 for every endpoint and operation.
2. **Traffic**: RPS, queue depth, active connections.
3. **Errors**: rate, by type and endpoint.
4. **Saturation**: CPU, memory, DB connections, queue lag.

Beyond these: business metrics (signups, revenue, AI tokens spent) should be in the same dashboard.

### Alerting

Alert on user-impact (error rate, latency violations, queue lag), not symptoms (CPU at 80%). Alerts must be: actionable (a runbook exists), routed (the right team gets paged), and tuned (no alert fatigue — one false page per quarter is the goal).

### Error Tracking

Sentry / Rollbar / Bugsnag captures every uncaught error with stack trace, user context, breadcrumbs, and request data. Auto-grouping deduplicates similar errors; release tagging attributes regressions to a specific deploy.

### Health Checks

- `/healthz` (liveness): "the process is alive." Returns 200 unless about to die.
- `/readyz` (readiness): "the process can serve traffic." Checks DB, Redis. Orchestrators use this for traffic routing.

Liveness should be cheap and not depend on downstream — a slow DB shouldn't kill your pod.

---

## Testing Strategy

### The Testing Pyramid (Backend Edition)

- **Unit tests** (most): pure domain logic, fast, no I/O.
- **Integration tests** (medium): real DB, real Redis, real queues — using Testcontainers. The truth-telling layer.
- **Contract tests** (medium): your API matches what consumers expect. Pact, or schema-based comparisons.
- **End-to-end tests** (few): full flows through the deployed system.

### What to Unit Test

The domain layer. If your domain is pure (no Prisma, no NestJS imports), unit tests are fast and stable. The bulk of complex logic is here.

### What Not to Mock

Database, Redis, queues. Mocked DBs lie — they pass tests that fail in production. Use Testcontainers to spin up a real Postgres for integration tests. Slower (seconds, not milliseconds) but reflects reality.

### Contract Testing

When your API has external consumers (frontend, mobile, partners), a schema change can silently break them. Contract tests fail when the response shape diverges from the contract. With OpenAPI-generated types, the frontend's TypeScript build also serves as a contract test.

### Test Data Strategy

Per-test database transactions (begin, run, rollback) for isolation. Factories (`factory-bot`-style) over fixtures — fixtures rot. Don't share state between tests.

### What Not to Test

- ORM internals (Prisma is tested; you don't need to test that `findUnique` finds).
- Trivial getters/setters.
- Framework wiring (the framework is tested).
- The third-party API's behavior.

Test your behavior, not theirs.

### Snapshot Tests Are Mostly Bad

For API responses, snapshots become "approve any change" rituals. Prefer specific assertions on the shape and values that matter. Reserve snapshots for stable, complex outputs (a generated PDF's structure).

### Load Testing

Already covered. Run before launch and after major architectural changes. k6 or Artillery; record realistic traffic distribution.

---

## Deployment & DevOps

### Containerize Everything

Docker images for every service. The image is the deployment artifact; what runs in production matches what runs locally. Multi-stage builds for small images: build stage installs dev deps and compiles, final stage copies only `dist` and prod deps.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
USER node
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### CI Pipeline

Every push runs:
1. Lint + type-check (fast, catches most issues).
2. Unit tests.
3. Integration tests (with Testcontainers).
4. Build the Docker image.
5. Security scan (Trivy, Snyk).

PRs get all of this; main pushes additionally publish the image and trigger deploy.

### Deployment Strategies

- **Rolling**: replace instances one at a time. Default for stateless services. Requires backward-compatible schema changes.
- **Blue-green**: run new version alongside, switch traffic. Fast rollback. Costs 2x during deploy.
- **Canary**: route 1% → 10% → 50% → 100% of traffic to the new version, watching metrics. Catches regressions before they hit everyone. Requires good monitoring.

For an indie product, rolling is fine. Add canary when revenue depends on uptime.

### Database Migrations in CI

Migrations run before the new code goes live, in a backward-compatible way (expand/contract). Failed migrations must roll back cleanly. Never edit a committed migration — write a new one to fix.

### Infrastructure as Code

Terraform, Pulumi, or your platform's IaC (Vercel `vercel.json`, Railway `railway.toml`). Production infrastructure is code; clicking around a cloud console is reproducibility-killing.

### Secrets in CI/CD

Encrypted in CI's secret store, injected at runtime, never logged. GitHub Actions `secrets`, masked in logs. Rotate when an engineer with access leaves the team.

### Environment Parity

Dev, staging, production differ only in scale and config — not in code or topology. A bug "only happens in production" usually means staging is missing something (real data volume, real load, real third-party endpoints). Fix the parity.

### Backup and Recovery

Daily DB snapshots, weekly off-site copies. Test the restore procedure quarterly — an untested backup is theater. Define RPO (max acceptable data loss) and RTO (max acceptable downtime); design backups to meet them.

### Cost Awareness

Cloud bills compound silently. Tag every resource by service and environment. Review monthly. The biggest wins: rightsize over-provisioned instances, delete unused resources, move cold data to cheaper storage tiers, use reserved/committed pricing for steady-state.

---

## Team Standards

### Code Review Principles

- Review for: correctness, security, observability, maintainability — in that order.
- Don't block on style (the linter does that).
- Suggest, don't dictate, on subjective choices.
- Approve when "I would maintain this" is true; request changes when there's a concrete bug or risk.
- Small PRs (<400 lines) get good reviews; large PRs get rubber stamps.

### Pull Request Structure

PR description includes:
- **What** changed (summary).
- **Why** (link to issue/spec).
- **How to verify** (tests added, manual steps).
- **Risks** (rollback plan, monitoring to watch post-deploy).

### Branch Strategy

Trunk-based development with short-lived feature branches (1-3 days). Feature flags for incomplete work that ships behind a toggle. Long-lived branches diverge from main, conflicts pile up, and the merge becomes the bug.

### Documentation Standards

- Each module has a `README.md` explaining its purpose, public API, and key invariants.
- API contracts live in OpenAPI / GraphQL schema, generated from code.
- Architecture decisions live in ADRs (Architecture Decision Records) — small docs explaining "we chose X over Y because Z." When the team forgets why, the ADR remembers.
- Runbooks for every alert: how to diagnose, how to mitigate, who owns it.

### Postmortems

Every production incident generates a postmortem within 5 days. Blameless — the goal is to find the systemic cause, not the responsible engineer. Action items have owners and dates. Track them to completion.

### On-Call Hygiene

If on-call wakes someone at 3am, the alert was either real (good — runbook helped) or noisy (bad — fix the alert before next week). Alert tuning is ongoing work, not a one-time setup.

---

## Quick Reference Checklist

### Before Shipping a New Endpoint

- [ ] Input validated with Zod at the boundary
- [ ] Authentication required (or explicitly public)
- [ ] Authorization checked at the use case
- [ ] Rate limited
- [ ] Logs include `requestId`, `userId`, key business IDs
- [ ] Errors mapped to the right HTTP status codes
- [ ] Tests: unit (domain) + integration (full path)
- [ ] OpenAPI / contract updated
- [ ] No secrets in code, logs, or error messages

### Before Shipping a New Background Job

- [ ] Idempotent (running twice = no-op)
- [ ] Bounded retry policy (max attempts, max age)
- [ ] Dead-letter queue with alerts
- [ ] Job timeout configured
- [ ] Metrics: job count, duration, failure rate
- [ ] Tested with realistic payload sizes

### Before Shipping a Schema Migration

- [ ] Backward compatible (current code works after migration)
- [ ] Rollback plan (or expand/contract for non-revertible changes)
- [ ] Tested against production-sized data (lock duration estimated)
- [ ] Indexes added if new query patterns require them

### Before Shipping AI / LLM Features

- [ ] Streaming response (SSE)
- [ ] Token usage logged per request
- [ ] Prompt versioned and tagged in logs
- [ ] Structured output validated with Zod
- [ ] Eval harness covers happy path + edge cases
- [ ] Cost ceiling and abuse protection (rate limit + max tokens)
- [ ] Fallback when LLM is down (cached response, simpler model, graceful 503)

### Before Going to Production

- [ ] Health checks (`/healthz`, `/readyz`)
- [ ] Structured logging with redaction
- [ ] Metrics dashboard (4 golden signals + business KPIs)
- [ ] Distributed tracing
- [ ] Error tracking (Sentry)
- [ ] Alerts defined and routed
- [ ] Backup + tested restore
- [ ] Runbook for top 5 alert types
- [ ] Load tested at expected peak × 2
- [ ] Security review (OWASP Top 10 walkthrough)
- [ ] Secrets rotated; CI/CD secrets least-privilege
- [ ] Dependency audit clean
- [ ] CORS, CSP, security headers configured
- [ ] Rate limiting on all public endpoints
- [ ] Graceful shutdown handles `SIGTERM`

---

*This document is a living standard. When experience exposes a gap, edit it.*
