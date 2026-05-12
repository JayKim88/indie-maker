# Senior Frontend Developer Guide

> Next.js 15 App Router · TypeScript strict · Tailwind CSS · shadcn/ui

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Quick Decision Guide](#quick-decision-guide)
3. [Project Setup](#project-setup)
4. [Architecture](#architecture)
5. [Non-Negotiable Rules](#non-negotiable-rules)
6. [Core Patterns](#core-patterns)
7. [Advanced Patterns](#advanced-patterns)
8. [Performance Optimization](#performance-optimization)
9. [App-Wide Concerns](#app-wide-concerns)
10. [UI Components](#ui-components)
11. [Testing](#testing)
12. [Observability](#observability)
13. [Quick Reference Checklist](#quick-reference-checklist)
14. [Prompt Template](#prompt-template)

---

## Philosophy

Five principles that override all other preferences:

1. **Server-first** — Every component starts as a Server Component. `'use client'` is an escape hatch, not a default.
2. **Type safety everywhere** — `strict: true` is mandatory. Every `any` is a deferred bug. External data is validated with Zod at runtime.
3. **Explicit over implicit** — State lives where it's used. URLs encode shareable state. Nothing "just works" — it's wired deliberately.
4. **Performance is a feature** — LCP, INP, CLS are shipping criteria, not post-launch cleanup.
5. **Accessibility is non-negotiable** — Semantic HTML, keyboard navigation, and WCAG 2.1 AA are enforced on every component, not audited at the end.

---

## Quick Decision Guide

### Data Fetching

```
Does the data change after initial load?
├── No → Static generation (generateStaticParams + revalidate)
└── Yes → Is it user-specific?
    ├── Yes → Server Component fetch (async/await in RSC, per-request)
    └── Real-time / very frequent → Client Component + subscription
```

### State Management

```
Where does the state live?
├── Single component → useState
├── 2–3 siblings → lift to parent
├── Subtree (< 5 levels) → React Context
├── Cross-cutting UI (modals, sidebar, theme) → Zustand
├── URL-driven (filters, pagination, search) → nuqs
└── Server data on client → TanStack Query (if real-time needed)

Never:
- Put server data in Zustand (stale data bugs)
- Use URL state for ephemeral UI (flash on reload)
- Use Context for high-frequency updates (renders everything)
```

### Form Approach

| Factor | `useActionState` | `react-hook-form` |
|--------|-----------------|-------------------|
| Default choice | ✅ | — |
| Works without JS | ✅ | ❌ |
| Real-time validation | ❌ | ✅ |
| Multi-step wizard | Awkward | Natural |
| Bundle cost | Zero | +13KB |
| Best for | CRUD, login, settings | Onboarding, checkout, complex forms |

**Rule: default to `useActionState`. Switch to RHF only when real-time per-field validation or multi-step partial validation is required.**

### Data Mutation

| Origin | Pattern |
|--------|---------|
| Form submission | Server Action + `useActionState` |
| Button / event handler | Server Action + `useTransition` |
| Immediate feedback needed | `useOptimistic` + Server Action |
| Client state only | `useState` / Zustand |

---

## Project Setup

### Initialization

```bash
npx create-next-app@latest my-app \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

cd my-app
npx shadcn@latest init
# Style: Default | Base color: Slate | CSS variables: Yes

npm install nuqs zustand zod react-hook-form @hookform/resolvers sonner next-themes framer-motion
npm install -D @next/bundle-analyzer eslint-plugin-import
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "lib": ["dom", "dom.iterable", "esnext"],
    "target": "ES2017",
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  }
}
```

### `next.config.ts` (canonical)

Security headers, image optimization, and bundle analysis in one file — never split across sections:

```typescript
import type { NextConfig } from 'next'
import bundleAnalyzer from '@next/bundle-analyzer'

const withBundleAnalyzer = bundleAnalyzer({ enabled: process.env.ANALYZE === 'true' })

const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' blob: data: https:",
      "font-src 'self'",
      "connect-src 'self' https:",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests",
    ].join('; '),
  },
]

const nextConfig: NextConfig = {
  compress: true,
  poweredByHeader: false,
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }]
  },
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons', 'date-fns'],
  },
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60 * 60 * 24 * 30,
  },
}

export default withBundleAnalyzer(nextConfig)
```

Verify security headers at launch with [securityheaders.com](https://securityheaders.com).

### `.eslintrc.json`

```json
{
  "extends": [
    "next/core-web-vitals",
    "next/typescript",
    "plugin:import/recommended",
    "plugin:import/typescript"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "import/no-cycle": "error"
  }
}
```

### `.prettierrc`

```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
```

### Husky + lint-staged

```bash
npm install -D husky lint-staged
npx husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,css}": "prettier --write"
  }
}
```

```bash
# .husky/pre-commit
npx lint-staged
```

### Environment Variables

```bash
# .env.local — never commit
DATABASE_URL=
SECRET_API_KEY=
SERVICE_ROLE_KEY=

NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

```typescript
// src/lib/env.ts — validate at startup, fail fast on missing vars
import { z } from 'zod'

const serverSchema = z.object({
  DATABASE_URL: z.string().url(),
  SECRET_API_KEY: z.string().min(1),
  NODE_ENV: z.enum(['development', 'test', 'production']),
})

const clientSchema = z.object({
  NEXT_PUBLIC_APP_URL: z.string().url(),
})

export const env = {
  ...serverSchema.parse(process.env),
  ...clientSchema.parse(process.env),
}
```

### Canonical Root Layout

All layout-level concerns in one place — never have multiple conflicting `layout.tsx` snippets:

```typescript
// src/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import { Providers } from './providers'
import { WebVitalsReporter } from '@/components/web-vitals-reporter'
import './globals.css'

const inter = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-inter' })

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL!),
  title: { default: 'My App', template: '%s | My App' },
  description: 'App description under 160 characters.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
      </head>
      <body>
        <Providers>
          <WebVitalsReporter />
          {children}
          <Toaster position="bottom-right" richColors closeButton />
        </Providers>
      </body>
    </html>
  )
}
```

```typescript
// src/app/providers.tsx
'use client'
import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      {children}
    </ThemeProvider>
  )
}
```

---

## Architecture

### Folder Structure by Scale

**Small (< 10 routes, 1 developer)**
```
src/
├── app/
├── components/
│   ├── ui/                 ← shadcn primitives
│   └── [feature-name].tsx
├── lib/
│   ├── db/                 ← server-only data access
│   └── utils.ts
└── types/index.ts
```

**Medium (10–30 routes, 2–5 developers)**
```
src/
├── app/
├── components/
│   ├── ui/
│   ├── layout/             ← navbar, sidebar, footer
│   └── features/
│       └── [domain]/
├── actions/                ← server actions by domain
├── lib/
│   ├── db/
│   ├── validations/
│   └── utils.ts
├── hooks/
└── types/index.ts
```

**Large (30+ routes, 5+ developers)**
```
src/
├── app/
├── features/               ← vertical slices
│   └── [domain]/
│       ├── components/
│       ├── actions/
│       ├── queries/
│       ├── hooks/
│       ├── schemas/
│       └── types.ts
├── components/
│   ├── ui/
│   └── layout/
├── lib/
│   ├── db/
│   └── utils.ts
└── types/index.ts
```

### Module Boundary Rules

1. **One-way dependency** — `app/` → `features/` → `lib/`. Never invert.
2. **No cross-feature imports** — shared logic goes to `lib/`. Cross-feature imports are a coupling smell.
3. **Data access is server-only** — `lib/db/` and `actions/` use `import 'server-only'`. Build fails if imported in a Client Component.
4. **Barrel exports are opt-in** — only at feature public API boundaries. Never inside a feature (circular dep risk, impedes tree-shaking).

### URL State (nuqs)

```typescript
// src/lib/search-params.ts — define parsers once, share across components
import { createSearchParamsCache, parseAsInteger, parseAsString } from 'nuqs/server'

export const searchParamsCache = createSearchParamsCache({
  page: parseAsInteger.withDefault(1),
  q: parseAsString.withDefault(''),
  status: parseAsString.withDefault('all'),
})
```

```typescript
// Server Component: read
const { page, q, status } = searchParamsCache.parse(await searchParams)

// Client Component: write
'use client'
import { useQueryState } from 'nuqs'
const [q, setQ] = useQueryState('q', { shallow: false })
```

---

## Non-Negotiable Rules

### RSC

1. **Server Components by default** — `'use client'` only when the component needs browser APIs, event handlers, or React hooks.
2. **Push `'use client'` to leaf nodes** — never mark layouts, pages, or sections as client.
3. **Data fetching in RSC** — `async/await` directly. Never fetch in Client Components for data needed on initial render — eliminates loading waterfalls.
4. **`'server-only'` for data access** — marks DB files, env secrets, privileged logic. Build-time failure on accidental client import.

### TypeScript

5. **Strict mode mandatory** — `"strict": true`, `"noUncheckedIndexedAccess": true`, `"exactOptionalPropertyTypes": true`.
6. **Zero `any`** — use `unknown` + narrowing, or generics for dynamic types. Every `any` is a bug deferred to runtime.
7. **Explicit component props** — `interface Props`, `function Component({ prop }: Props)`. Never `React.FC`.
8. **Zod for all external data** — forms, API responses, env vars, URL params, webhook payloads. TypeScript checks compile time only.

### React 19

9. **`useActionState` for server-bound forms** — replaces the `useState` + `useTransition` pattern. Provides `state`, `action`, `isPending` in one hook.
10. **`useFormStatus` for submit button** — must live in a child component of the `<form>` element.
11. **`use()` for conditional reads** — `use(SomeContext)` works inside conditionals and loops unlike `useContext`. `use(promise)` suspends until resolved — pair with `<Suspense>`.
12. **React Compiler awareness** — if `babel-plugin-react-compiler` is enabled, do NOT add `useMemo`/`useCallback` — the compiler inserts them automatically.

### Next.js 15

13. **`params` / `searchParams` are Promises** — always `await` before destructuring.

```typescript
// ✅ Next.js 15
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
}

// ❌ Next.js 14 pattern — breaks silently in production
export default async function Page({ params }: { params: { id: string } }) {
  const { id } = params
}
```

14. **`cookies()` / `headers()` are async** — `await cookies()`, `await headers()`.

### Security

15. **No secrets in `NEXT_PUBLIC_`** — prefix bakes the value into the client bundle. Payment keys, service role keys: server-only env vars.
16. **Sanitize `dangerouslySetInnerHTML`** — DOMPurify before any user-supplied HTML. Never `{ __html: userInput }`.
17. **Validate redirect targets** — relative paths only, or an explicit allowlist.

```typescript
// ❌ Open redirect
redirect(searchParams.get('next')!)

// ✅ Safe
const next = searchParams.get('next')
const safeNext = next?.startsWith('/') ? next : '/dashboard'
redirect(safeNext)
```

18. **Server Actions have built-in CSRF protection** — do not expose them as public API routes.
19. **CSP in `next.config.ts`** — see canonical config in Project Setup.
20. **`npm audit` in CI** — fail the build on high/critical severity.

### Error Handling

21. **Error boundaries at every route** — `error.tsx` per route segment. Sections with independent data get their own `<ErrorBoundary>`. An unhandled error must never crash the full app.
22. **Loading states are mandatory** — `loading.tsx` for route-level, `<Suspense fallback={<Skeleton />}>` for component-level. No async operation is silent.
23. **Empty states for all data views** — never blank space. Every list, table, and dashboard has explicit empty UI that guides the user toward action.

### Accessibility (WCAG 2.1 AA)

24. **Semantic HTML** — `<button>` for actions, `<a>` for navigation, `<nav>`, `<main>`, `<header>`, `<footer>`. Never `<div onClick>`.
25. **`next/image` for all images** — handles lazy loading, CLS prevention, format optimization. Raw `<img>` only for truly dynamic/user-uploaded content.
26. **Keyboard navigation** — all custom widgets support Tab/Enter/Space/Escape and arrow keys within compound widgets (date pickers, dropdowns, menus).
27. **Color contrast ≥ 4.5:1** — normal text: 4.5:1, large text (18px+): 3:1. Never convey information by color alone.
28. **Focus management in modals** — trap focus inside, return focus to trigger on close. Test with keyboard only.
29. **Reduced motion** — `prefers-reduced-motion` / `useReducedMotion()` for all animations. No motion without an opt-out.

### Code Quality

30. **One component, one concern** — split at ~150 lines or when handling more than one responsibility. A component that fetches, formats, and renders complex UI is three components.
31. **No prop drilling > 2 levels** — if a prop passes through 3+ components unused, extract to context or co-locate state.
32. **Naming** — Components: PascalCase. Functions/vars: camelCase. Files: kebab-case (non-components), PascalCase.tsx (components). Handlers: `handleEventName`.
33. **Custom hooks return data, not JSX** — `useAuth()` returns `{ user, signOut }`. If it returns JSX, it's a component.

### Performance

34. **CWV are shipping criteria** — LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1. Verify with Vercel Speed Insights or Lighthouse before launch.
35. **`next/dynamic` for heavy components** — charts, rich text editors, video players: dynamic import with loading skeleton.
36. **Measure before optimizing** — React DevTools Profiler first. `useMemo` for expensive computations, `useCallback` for callbacks passed to memoized children. Never premature-optimize.
37. **Bundle analysis before launch** — target < 100KB First Load JS per route. No moment.js (use date-fns), no full lodash (use lodash-es or individual imports).
38. **`next/font` for all fonts** — `display: 'swap'`. Load only used weights and subsets.

### Testing

39. **Test behavior, not implementation** — query by role/label/text, never by CSS class or test ID. A test that breaks on internal refactoring is a wrong test.
40. **Test pyramid** — 60% unit (Vitest), 30% integration (Testing Library), 10% e2e (Playwright).
41. **Every form has an integration test** — valid submission, invalid input errors, pending state, server error display.
42. **No snapshot tests** — break on every UI change, provide zero behavioral confidence, teach blind `toMatchSnapshot` updates.

### Observability

43. **Sentry in every `error.tsx`** — `Sentry.captureException(error)`. Tag with `user_id` and route.
44. **Web Vitals in production** — track LCP, INP, CLS per route. Alert on regressions (LCP > 3s, CLS > 0.15).
45. **Structured logging** — no raw `console.log` in components. Use a logging utility. Strip debug logs in production.

---

## Core Patterns

### Server Component: Data Fetching

```typescript
// src/app/(dashboard)/items/page.tsx
export default async function ItemsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string>>
}) {
  const user = await requireUser()
  const { page, q } = searchParamsCache.parse(await searchParams)
  const { items, total } = await getItems({ userId: user.id, page, q })
  return <ItemsView items={items} total={total} />
}
```

### Form with Server Action

```typescript
// src/components/features/items/create-item-form.tsx
'use client'
import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'
import { createItemAction } from '@/actions/items'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <Button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Item'}
    </Button>
  )
}

export function CreateItemForm() {
  const [state, action] = useActionState(createItemAction, null)
  return (
    <form action={action} className="space-y-4">
      <div className="space-y-1">
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          name="title"
          aria-invalid={!!state?.errors?.title}
          aria-describedby={state?.errors?.title ? 'title-error' : undefined}
        />
        {state?.errors?.title && (
          <p id="title-error" role="alert" className="text-sm text-red-500">
            {state.errors.title[0]}
          </p>
        )}
      </div>
      {state?.error && (
        <p role="alert" className="text-sm text-red-500">{state.error}</p>
      )}
      <SubmitButton />
    </form>
  )
}
```

### Server Action with Validation

```typescript
// src/actions/items.ts
'use server'
import { revalidatePath } from 'next/cache'
import { z } from 'zod'
import { requireUser } from '@/lib/auth'
import { db } from '@/lib/db'

const schema = z.object({
  title: z.string().min(1, 'Required').max(200, 'Too long'),
})

type ActionState = { error?: string; errors?: Record<string, string[]> } | null

export async function createItemAction(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const user = await requireUser()
  const parsed = schema.safeParse({ title: formData.get('title') })
  if (!parsed.success) return { errors: parsed.error.flatten().fieldErrors }
  try {
    await db.items.create({ data: { ...parsed.data, userId: user.id } })
    revalidatePath('/items')
    return null
  } catch {
    return { error: 'Failed to create item. Please try again.' }
  }
}
```

### Streaming with Suspense

```typescript
// src/app/(dashboard)/dashboard/page.tsx
import { Suspense } from 'react'
import { StatsSkeleton, ListSkeleton } from '@/components/ui/skeletons'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <Suspense fallback={<StatsSkeleton />}>
        <StatsCards />
      </Suspense>
      <Suspense fallback={<ListSkeleton rows={5} />}>
        <RecentActivity />
      </Suspense>
    </div>
  )
}

// Each is an async Server Component — fetches its own data independently
async function StatsCards() {
  const stats = await getStats()
  return <div className="grid gap-4 md:grid-cols-3">{/* render stats */}</div>
}
```

### Optimistic UI

```typescript
'use client'
import { useOptimistic, useTransition } from 'react'
import { toggleItemAction } from '@/actions/items'

interface Item { id: string; title: string; completed: boolean }

export function ItemList({ initialItems }: { initialItems: Item[] }) {
  const [, startTransition] = useTransition()
  const [items, updateOptimistic] = useOptimistic(
    initialItems,
    (state, { id, completed }: { id: string; completed: boolean }) =>
      state.map((item) => (item.id === id ? { ...item, completed } : item))
  )

  function handleToggle(item: Item) {
    startTransition(async () => {
      updateOptimistic({ id: item.id, completed: !item.completed })
      await toggleItemAction(item.id, !item.completed)
    })
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.id} className="flex items-center gap-3 p-4 border rounded-lg">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleToggle(item)}
            aria-label={item.completed ? 'Mark incomplete' : 'Mark complete'}
          >
            {item.completed ? <Check className="h-4 w-4 text-green-600" /> : <Circle className="h-4 w-4 text-slate-400" />}
          </Button>
          <span className={item.completed ? 'line-through text-slate-400' : ''}>{item.title}</span>
        </li>
      ))}
    </ul>
  )
}
```

---

## Advanced Patterns

### Pagination

```typescript
// src/lib/db/items.ts
export async function getItems({
  userId, page = 1, pageSize = 20, q,
}: {
  userId: string; page?: number; pageSize?: number; q?: string
}) {
  const offset = (page - 1) * pageSize
  const [items, total] = await Promise.all([
    db.items.findMany({
      where: { userId, ...(q && { title: { contains: q } }) },
      skip: offset,
      take: pageSize,
    }),
    db.items.count({ where: { userId, ...(q && { title: { contains: q } }) } }),
  ])
  return { items, total, pageCount: Math.ceil(total / pageSize) }
}
```

```typescript
// src/components/ui/pagination.tsx
'use client'
import { useQueryState, parseAsInteger } from 'nuqs'

export function Pagination({ pageCount }: { pageCount: number }) {
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1))
  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-slate-500">Page {page} of {pageCount}</p>
      <div className="flex gap-1">
        <Button variant="outline" size="icon" disabled={page <= 1} onClick={() => setPage(page - 1)} aria-label="Previous page">
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" disabled={page >= pageCount} onClick={() => setPage(page + 1)} aria-label="Next page">
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
```

### Infinite Scroll

```typescript
// src/hooks/use-intersection-observer.ts
import { useEffect, useRef } from 'react'

export function useIntersectionObserver(callback: () => void) {
  const ref = useRef<HTMLElement>(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) callback() },
      { threshold: 0.1 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [callback])
  return ref
}
```

```typescript
'use client'
import { useState, useCallback } from 'react'

export function InfiniteItemList({ initialItems }: { initialItems: Item[] }) {
  const [items, setItems] = useState(initialItems)
  const [cursor, setCursor] = useState(initialItems.at(-1)?.id ?? null)
  const [hasMore, setHasMore] = useState(initialItems.length >= 20)
  const [loading, setLoading] = useState(false)

  const loadMore = useCallback(async () => {
    if (!cursor || loading || !hasMore) return
    setLoading(true)
    const result = await fetchMoreItemsAction(cursor)
    if (result.length === 0 || result.length < 20) setHasMore(false)
    if (result.length > 0) {
      setItems((prev) => [...prev, ...result])
      setCursor(result.at(-1)!.id)
    }
    setLoading(false)
  }, [cursor, loading, hasMore])

  const sentinelRef = useIntersectionObserver(loadMore)

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.id} className="p-4 border rounded-lg">{item.title}</li>
      ))}
      <li ref={sentinelRef} className="py-2 text-center text-sm text-slate-400" aria-live="polite">
        {loading && 'Loading...'}
        {!hasMore && items.length > 0 && 'All items loaded'}
      </li>
    </ul>
  )
}
```

### File Upload

```typescript
// src/actions/upload.ts
'use server'
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const
const MAX_SIZE = 5 * 1024 * 1024

export async function uploadFileAction(formData: FormData) {
  const user = await requireUser()
  const file = formData.get('file')
  if (!(file instanceof File)) return { error: 'No file provided' }
  if (!ALLOWED_TYPES.includes(file.type as typeof ALLOWED_TYPES[number]))
    return { error: 'Invalid file type. Allowed: JPEG, PNG, WebP' }
  if (file.size > MAX_SIZE) return { error: 'File too large. Max 5MB.' }
  const url = await uploadToStorage(file, `users/${user.id}/${Date.now()}-${file.name}`)
  return { url }
}
```

### Multi-Step Form (Wizard)

```typescript
'use client'
// Per-step schemas enable partial validation on each step
const step1Schema = z.object({ name: z.string().min(1), role: z.string().min(1) })
const step2Schema = z.object({ companyName: z.string().min(1), teamSize: z.string() })
const fullSchema = step1Schema.merge(step2Schema)
type FormValues = z.infer<typeof fullSchema>

const STEPS = [
  { title: 'About you', schema: step1Schema },
  { title: 'Your company', schema: step2Schema },
]

export function OnboardingWizard() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)

  const form = useForm<FormValues>({
    resolver: zodResolver(
      step === STEPS.length - 1 ? fullSchema : STEPS[step].schema as z.ZodType<Partial<FormValues>>
    ),
    defaultValues: { name: '', role: '', companyName: '', teamSize: '' },
    mode: 'onBlur',
  })

  async function handleNext() {
    const fields = Object.keys(STEPS[step].schema.shape) as (keyof FormValues)[]
    if (await form.trigger(fields)) setStep((s) => s + 1)
  }

  async function handleSubmit(values: FormValues) {
    setSubmitting(true)
    const result = await completeOnboardingAction(values)
    if (result.error) {
      form.setError('root', { message: result.error })
      setSubmitting(false)
    } else {
      router.push('/dashboard')
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="flex gap-2 mb-8" role="list" aria-label="Progress">
        {STEPS.map((s, i) => (
          <div
            key={s.title}
            role="listitem"
            aria-current={i === step ? 'step' : undefined}
            className={`flex-1 h-1 rounded ${i <= step ? 'bg-slate-900' : 'bg-slate-200'}`}
          />
        ))}
      </div>
      <h2 className="text-xl font-semibold mb-6">{STEPS[step].title}</h2>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        {step === 0 && <Step1Fields form={form} />}
        {step === 1 && <Step2Fields form={form} />}
        {form.formState.errors.root && (
          <p role="alert" className="text-sm text-red-500">{form.formState.errors.root.message}</p>
        )}
        <div className="flex gap-3 pt-4">
          {step > 0 && (
            <Button type="button" variant="outline" onClick={() => setStep((s) => s - 1)}>Back</Button>
          )}
          {step < STEPS.length - 1 ? (
            <Button type="button" onClick={handleNext} className="flex-1">Continue</Button>
          ) : (
            <Button type="submit" disabled={submitting} className="flex-1">
              {submitting ? 'Finishing...' : 'Get started'}
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}
```

### Data Table (TanStack Table)

```bash
npm install @tanstack/react-table
```

```typescript
'use client'
import {
  useReactTable, getCoreRowModel, getSortedRowModel,
  flexRender, type ColumnDef, type SortingState,
} from '@tanstack/react-table'
import { useState } from 'react'

interface Item { id: string; title: string; status: string; createdAt: string }

const columns: ColumnDef<Item>[] = [
  {
    accessorKey: 'title',
    header: ({ column }) => (
      <Button variant="ghost" onClick={() => column.toggleSorting()}>
        Title
        {column.getIsSorted() === 'asc' ? <ArrowUp className="ml-2 h-4 w-4" />
          : column.getIsSorted() === 'desc' ? <ArrowDown className="ml-2 h-4 w-4" />
          : <ArrowUpDown className="ml-2 h-4 w-4" />}
      </Button>
    ),
  },
  { accessorKey: 'status', header: 'Status' },
  {
    accessorKey: 'createdAt',
    header: 'Created',
    cell: ({ row }) => new Intl.DateTimeFormat('en-US').format(new Date(row.getValue('createdAt'))),
  },
]

export function ItemsTable({ data }: { data: Item[] }) {
  const [sorting, setSorting] = useState<SortingState>([])
  const table = useReactTable({
    data, columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((hg) => (
            <TableRow key={hg.id}>
              {hg.headers.map((h) => (
                <TableHead key={h.id}>{flexRender(h.column.columnDef.header, h.getContext())}</TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={columns.length} className="text-center py-8 text-slate-500">
                No items found
              </TableCell>
            </TableRow>
          ) : (
            table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
```

### Real-Time (Supabase)

```typescript
'use client'
import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

export function useRealtimeItems(initialItems: Item[]) {
  const [items, setItems] = useState(initialItems)

  useEffect(() => {
    const supabase = createClient()
    const sub = supabase
      .channel('items')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'items' }, (payload) => {
        if (payload.eventType === 'INSERT') setItems((prev) => [payload.new as Item, ...prev])
        if (payload.eventType === 'DELETE') setItems((prev) => prev.filter((i) => i.id !== payload.old.id))
        if (payload.eventType === 'UPDATE') setItems((prev) => prev.map((i) => i.id === payload.new.id ? payload.new as Item : i))
      })
      .subscribe()
    return () => { sub.unsubscribe() }
  }, [])

  return items
}
```

---

## Performance Optimization

### LCP (Largest Contentful Paint) — Target: ≤ 2.5s

**Priority loading for LCP element**

```tsx
// next/image priority: disables lazy loading + injects <link rel="preload">
<Image src="/hero.jpg" alt="Hero" width={1200} height={600} priority />

// Non-Next.js image: explicit format fallback
<picture>
  <source srcset="hero.avif" type="image/avif" />
  <source srcset="hero.webp" type="image/webp" />
  <img src="hero.jpg" alt="Hero" loading="eager" width="1200" height="600" />
</picture>
```

**Font display swap — FOUT > FOIT**

```typescript
const inter = Inter({ subsets: ['latin'], display: 'swap', preload: true, variable: '--font-inter' })
```

**Reduce FOUT layout shift with `size-adjust`**

```css
@font-face {
  font-family: 'Inter Fallback';
  src: local('Arial');
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}
```

---

### CLS (Cumulative Layout Shift) — Target: ≤ 0.1

```tsx
// ✅ explicit dimensions — reserves layout space before load
<Image src="/product.jpg" alt="Product" width={400} height={300} />

// ✅ unknown dimensions — aspect-ratio container
<div className="relative aspect-video w-full overflow-hidden">
  <Image src="/thumb.jpg" alt="Thumbnail" fill className="object-cover" />
</div>

// ✅ reserve space for dynamic content
<div className="min-h-[56px]">{isLoaded && <Banner />}</div>
```

---

### INP (Interaction to Next Paint) — Target: ≤ 200ms

INP replaced FID as a Core Web Vital in 2024. Measures worst interaction latency across the page lifetime.

**`startTransition` — defer non-urgent updates**

```typescript
'use client'
import { startTransition, useState } from 'react'

function handleInput(value: string) {
  setQuery(value)                        // urgent: update input immediately
  startTransition(() => {
    setResults(expensiveFilter(value))   // non-urgent: can yield to browser
  })
}
```

**`useDeferredValue` — expensive render trails fast input**

```typescript
'use client'
import { useState, useDeferredValue, memo } from 'react'

function SearchPage({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <ResultList items={items} query={deferredQuery} />
    </>
  )
}

// memo: only re-renders when deferred value settles
const ResultList = memo(function ResultList({ items, query }: { items: Item[]; query: string }) {
  return <ul>{items.filter((i) => i.title.includes(query)).map((i) => <li key={i.id}>{i.title}</li>)}</ul>
})
```

**Yield to browser for tasks > 50ms**

```typescript
async function processLargeDataset(items: Item[]) {
  const CHUNK = 100
  const results: ProcessedItem[] = []
  for (let i = 0; i < items.length; i += CHUNK) {
    results.push(...items.slice(i, i + CHUNK).map(processItem))
    await new Promise((resolve) => setTimeout(resolve, 0))
  }
  return results
}
```

---

### FCP (First Contentful Paint) — Target: ≤ 1.8s

- Server Components eliminate JS waterfall on first paint
- `<Suspense>` streaming flushes shell HTML before data resolves
- Avoid synchronously loading third-party CSS above the fold

---

### Rendering Optimization

**List virtualization (500+ items)**

```bash
npm install @tanstack/react-virtual
```

```typescript
'use client'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

export function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null)
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 64,
    overscan: 5,
  })

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((v) => (
          <div
            key={v.key}
            style={{
              position: 'absolute', top: 0, left: 0, width: '100%',
              height: `${v.size}px`, transform: `translateY(${v.start}px)`,
            }}
          >
            {items[v.index].title}
          </div>
        ))}
      </div>
    </div>
  )
}
```

**`React.memo` — measure before adding**

```typescript
// ✅ parent re-renders often + child is expensive + props are stable
const ExpensiveChart = memo(function ExpensiveChart({ data }: { data: ChartData }) {
  return <Chart data={data} />
})

// Stabilize callback props so memo isn't bypassed
const handleSelect = useCallback((id: string) => selectItem(id), [])

// ❌ Don't memo everything — overhead is real; profile first
```

**`content-visibility: auto` for below-fold sections**

```css
/* globals.css */
.section-lazy {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px; /* estimated height prevents CLS while hidden */
}
```

---

### Image Optimization

```tsx
// sizes: tell browser actual rendered width per breakpoint
<Image
  src="/product.jpg"
  alt="Product"
  width={800}
  height={600}
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 400px"
/>

// blur placeholder — static import auto-generates blurDataURL
import productImage from '@/public/product.jpg'
<Image src={productImage} alt="Product" placeholder="blur" />

// fill: container controls size
<div className="relative w-full aspect-square overflow-hidden rounded-lg">
  <Image src={src} alt={alt} fill className="object-cover" sizes="(max-width: 768px) 100vw, 50vw" />
</div>
```

---

### Caching Strategy

```typescript
// cache() — deduplicate within a single request tree
import { cache } from 'react'

export const getPostBySlug = cache(async (slug: string) => {
  return db.posts.findUnique({ where: { slug } })
})
```

```typescript
// unstable_cache — persist across requests with tag-based revalidation
import { unstable_cache } from 'next/cache'

export const getItemsByUser = unstable_cache(
  async (userId: string) => db.items.findMany({ where: { userId } }),
  ['items-by-user'],
  { tags: ['items'], revalidate: 60 }
)

// Invalidate after mutation
import { revalidateTag } from 'next/cache'
revalidateTag('items')
```

**Route segment config:**

```typescript
// Marketing / blog — static, rebuilt hourly
export const revalidate = 3600
export const dynamic = 'force-static'

// Dashboard / auth — always server-render
export const dynamic = 'force-dynamic'
```

**`fetch` cache options:**

```typescript
const data = await fetch('/api/items', { next: { tags: ['items'], revalidate: 60 } })
const userData = await fetch('/api/me', { cache: 'no-store' })
```

---

### Resource Hints

```typescript
// In layout.tsx <head> — early connection to third-party origins
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://cdn.your-cdn.com" crossOrigin="anonymous" />
<link rel="dns-prefetch" href="https://analytics.example.com" />

// Preload LCP image (when not using next/image priority)
<link rel="preload" href="/hero.jpg" as="image" type="image/jpeg" fetchPriority="high" />
```

---

### Web Vitals Measurement

```typescript
// src/components/web-vitals-reporter.tsx
'use client'
import { useReportWebVitals } from 'next/web-vitals'

const THRESHOLDS: Record<string, number> = {
  LCP: 2500, INP: 200, CLS: 0.1, FCP: 1800, TTFB: 800,
}

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {
    const threshold = THRESHOLDS[metric.name]
    if (threshold && metric.value > threshold) {
      console.warn(`[Web Vitals] ${metric.name}: ${metric.value} > ${threshold}`)
    }
    fetch('/api/vitals', {
      method: 'POST',
      keepalive: true,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        url: window.location.pathname,
      }),
    })
  })
  return null
}
```

---

### Build Optimization

```bash
ANALYZE=true npm run build
```

Act on:
- Route First Load JS > 100KB → `next/dynamic` for heavy components
- Single dependency > 30KB → find lighter alternative (date-fns vs moment, lodash-es vs lodash)
- Same chunk duplicated across routes → extract to shared layout or `lib/`

---

## App-Wide Concerns

### Authentication

**Middleware auth guard:**

```typescript
// src/middleware.ts
import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_PATHS = new Set(['/', '/login', '/signup', '/about', '/pricing'])

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublic = PUBLIC_PATHS.has(pathname) || pathname.startsWith('/api/auth')
  if (isPublic) return NextResponse.next()

  const session = request.cookies.get('session')?.value
  if (!session) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('next', pathname)
    return NextResponse.redirect(loginUrl)
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)'],
}
```

**Server-side auth helpers:**

```typescript
// src/lib/auth.ts
import { cache } from 'react'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export const getCurrentUser = cache(async () => {
  const cookieStore = await cookies()
  const token = cookieStore.get('session')?.value
  if (!token) return null
  return validateSession(token)
})

export async function requireUser() {
  const user = await getCurrentUser()
  if (!user) redirect('/login')
  return user
}
```

**Supabase SSR:**

```typescript
// src/lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (s) => s.forEach(({ name, value, options }) => cookieStore.set(name, value, options)),
      },
    }
  )
}

// src/lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**Supabase middleware (session refresh on every request):**

```typescript
// src/middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (s) => {
          s.forEach(({ name, value }) => request.cookies.set(name, value))
          response = NextResponse.next({ request })
          s.forEach(({ name, value, options }) => response.cookies.set(name, value, options))
        },
      },
    }
  )
  const { data: { user } } = await supabase.auth.getUser()
  if (!user && !request.nextUrl.pathname.startsWith('/login')) {
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    return NextResponse.redirect(url)
  }
  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)'],
}
```

---

### SEO & Metadata

```typescript
// Root metadata with template
export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL!),
  title: { default: 'My App', template: '%s | My App' },
  description: 'Description under 160 characters.',
  openGraph: {
    siteName: 'My App',
    type: 'website',
    images: [{ url: '/og.png', width: 1200, height: 630 }],
  },
  twitter: { card: 'summary_large_image' },
  robots: { index: true, follow: true },
}

// Dynamic metadata per content page
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = await getPostBySlug(slug)
  if (!post) return {}
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      type: 'article',
      publishedTime: post.publishedAt,
      images: [{ url: post.coverImage, width: 1200, height: 630 }],
    },
  }
}
```

**Dynamic OG image:**

```typescript
// src/app/og/route.tsx
import { ImageResponse } from 'next/og'

export async function GET(request: Request) {
  const title = new URL(request.url).searchParams.get('title') ?? 'My App'
  return new ImageResponse(
    (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', background: '#1e1e2e', padding: 80 }}>
        <p style={{ color: 'white', fontSize: 60, fontWeight: 700, textAlign: 'center' }}>{title}</p>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}

// Usage: openGraph: { images: [`/og?title=${encodeURIComponent(post.title)}`] }
```

**Sitemap + Robots:**

```typescript
// src/app/sitemap.ts
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getAllPosts()
  return [
    { url: 'https://myapp.com', lastModified: new Date(), priority: 1 },
    ...posts.map((p) => ({ url: `https://myapp.com/blog/${p.slug}`, lastModified: p.updatedAt, priority: 0.6 })),
  ]
}

// src/app/robots.ts
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/dashboard/', '/api/'] },
    sitemap: 'https://myapp.com/sitemap.xml',
  }
}
```

**JSON-LD:**

```typescript
export function ArticleJsonLd({ title, description, publishedAt, author, url }: {
  title: string; description: string; publishedAt: string; author: string; url: string
}) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Article',
          headline: title, description,
          datePublished: publishedAt,
          author: { '@type': 'Person', name: author },
          url,
        }),
      }}
    />
  )
}
```

---

### Dark Mode & Theming

```typescript
// src/components/ui/theme-toggle.tsx
'use client'
import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      aria-label="Toggle theme"
    >
      <Sun className="h-4 w-4 dark:hidden" aria-hidden="true" />
      <Moon className="h-4 w-4 hidden dark:block" aria-hidden="true" />
    </Button>
  )
}
```

```css
/* globals.css — CSS variable tokens */
:root { --background: 0 0% 100%; --foreground: 240 10% 3.9%; }
.dark { --background: 240 10% 3.9%; --foreground: 0 0% 98%; }
```

---

### Notifications (Sonner)

```typescript
import { toast } from 'sonner'

// Variants
toast.success('Item created')
toast.error('Failed to save', { description: error.message })
toast.warning('Draft saved — publish when ready')

// With action
toast.error('Upload failed', { action: { label: 'Retry', onClick: retry } })

// Loading → resolve
const id = toast.loading('Uploading...')
const result = await upload()
if (result.ok) toast.success('Done', { id })
else toast.error('Failed', { id, description: result.error })

// Promise shorthand
toast.promise(deleteItem(id), { loading: 'Deleting...', success: 'Deleted', error: 'Failed' })
```

---

### Animation (Framer Motion)

```typescript
// Always pair with useReducedMotion — no motion without opt-out
'use client'
import { motion, useReducedMotion, AnimatePresence } from 'framer-motion'

export function FadeIn({ children, className }: { children: React.ReactNode; className?: string }) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      initial={{ opacity: 0, y: reduce ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduce ? 0 : 0.2, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Staggered list with exit animation
const container = { show: { transition: { staggerChildren: 0.05 } } }
const item = { hidden: { opacity: 0, x: -16 }, show: { opacity: 1, x: 0 } }

export function AnimatedList({ items }: { items: Item[] }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      <AnimatePresence mode="popLayout">
        {items.map((i) => (
          <motion.li key={i.id} variants={item} exit={{ opacity: 0, x: 16 }} layout>
            {i.title}
          </motion.li>
        ))}
      </AnimatePresence>
    </motion.ul>
  )
}

// Page transition — app/template.tsx (re-runs on every navigation)
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.15 }}>
      {children}
    </motion.div>
  )
}
```

---

## UI Components

### Skeleton Loading

```typescript
// src/components/ui/skeletons.tsx
import { Skeleton } from '@/components/ui/skeleton'

export function StatsSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="rounded-lg border bg-white p-6">
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-8 w-16" />
        </div>
      ))}
    </div>
  )
}

export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-lg border p-4">
          <Skeleton className="h-10 w-10 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-lg border">
      <div className="border-b bg-slate-50 p-4">
        <div className="flex gap-4">
          {Array.from({ length: cols }).map((_, i) => <Skeleton key={i} className="h-4 flex-1" />)}
        </div>
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 border-b p-4 last:border-0">
          {Array.from({ length: cols }).map((_, j) => <Skeleton key={j} className="h-4 flex-1" />)}
        </div>
      ))}
    </div>
  )
}

export function FormSkeleton() {
  return (
    <div className="space-y-4 max-w-md">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-10 w-full" />
        </div>
      ))}
      <Skeleton className="h-10 w-28" />
    </div>
  )
}
```

### Empty State

```typescript
// src/components/ui/empty-state.tsx
import { type LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: { label: string; onClick: () => void }
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-slate-100 p-4 mb-4">
        <Icon className="h-8 w-8 text-slate-400" aria-hidden="true" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm text-slate-500 max-w-sm">{description}</p>
      {action && (
        <Button onClick={action.onClick} className="mt-4">{action.label}</Button>
      )}
    </div>
  )
}
```

### Error Boundary

```typescript
// src/app/(dashboard)/items/error.tsx
'use client'
import { useEffect } from 'react'
import * as Sentry from '@sentry/nextjs'
import { Button } from '@/components/ui/button'

export default function ItemsError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => { Sentry.captureException(error) }, [error])
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="mt-2 text-sm text-slate-500">
        {error.message || 'An unexpected error occurred.'}
      </p>
      <Button onClick={reset} className="mt-4">Try again</Button>
    </div>
  )
}
```

### Confirm Dialog

```typescript
'use client'
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useState, useTransition } from 'react'
import { toast } from 'sonner'

export function ConfirmDialog({
  title, description, onConfirm, trigger, destructive,
}: {
  title: string
  description: string
  onConfirm: () => Promise<void>
  trigger: React.ReactNode
  destructive?: boolean
}) {
  const [open, setOpen] = useState(false)
  const [isPending, startTransition] = useTransition()

  function handleConfirm() {
    startTransition(async () => {
      try {
        await onConfirm()
        setOpen(false)
      } catch {
        toast.error('Action failed. Please try again.')
      }
    })
  }

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <span onClick={() => setOpen(true)}>{trigger}</span>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isPending}
            className={destructive ? 'bg-red-600 hover:bg-red-700' : ''}
          >
            {isPending ? 'Processing...' : 'Confirm'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

### Utility Functions

```typescript
// src/lib/utils.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs))

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  }).format(new Date(date))
}

export function formatRelativeTime(date: string | Date): string {
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  const diff = (new Date(date).getTime() - Date.now()) / 1000
  if (Math.abs(diff) < 60) return rtf.format(Math.round(diff), 'second')
  if (Math.abs(diff) < 3600) return rtf.format(Math.round(diff / 60), 'minute')
  if (Math.abs(diff) < 86400) return rtf.format(Math.round(diff / 3600), 'hour')
  return rtf.format(Math.round(diff / 86400), 'day')
}

export function formatCurrency(cents: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(cents / 100)
}

export function slugify(str: string): string {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]+/g, '')
}

export function truncate(str: string, maxLength: number): string {
  return str.length <= maxLength ? str : str.slice(0, maxLength - 3) + '...'
}
```

---

## Testing

### Setup

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event @vitejs/plugin-react jsdom msw
npm install -D @playwright/test && npx playwright install
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'], globals: true },
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
})
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'
afterEach(() => cleanup())
```

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'html',
  use: { baseURL: 'http://localhost:3000', trace: 'on-first-retry', screenshot: 'only-on-failure' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['iPhone 14'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### Patterns

```typescript
// Integration: query by role/label/text — never CSS class
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

it('shows validation error on empty submit', async () => {
  render(<CreateItemForm />)
  await userEvent.click(screen.getByRole('button', { name: /create item/i }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Required')
})

it('calls action with valid data', async () => {
  render(<CreateItemForm />)
  await userEvent.type(screen.getByLabelText(/title/i), 'My Item')
  await userEvent.click(screen.getByRole('button', { name: /create item/i }))
  expect(screen.getByRole('button', { name: /creating/i })).toBeDisabled()
})
```

```typescript
// E2e: critical flows only
test('user can create and view item', async ({ page }) => {
  await page.goto('/dashboard')
  await page.getByRole('button', { name: 'New Item' }).click()
  await page.getByLabel('Title').fill('Test Item')
  await page.getByRole('button', { name: 'Create Item' }).click()
  await expect(page.getByText('Test Item')).toBeVisible()
})
```

---

## Observability

### Sentry

```typescript
// src/instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('../sentry.server.config')
  }
  if (process.env.NEXT_RUNTIME === 'edge') {
    await import('../sentry.edge.config')
  }
}
```

Every `error.tsx` calls `Sentry.captureException(error)` — see Error Boundary pattern above.

### Structured Logging

```typescript
// src/lib/logger.ts
type Level = 'debug' | 'info' | 'warn' | 'error'
type LogData = Record<string, unknown>

function log(level: Level, message: string, data?: LogData) {
  if (level === 'debug' && process.env.NODE_ENV === 'production') return

  const entry = JSON.stringify({
    level, message,
    timestamp: new Date().toISOString(),
    ...data,
  })

  if (level === 'error') console.error(entry)
  else if (level === 'warn') console.warn(entry)
  else console.log(entry)
}

export const logger = {
  debug: (msg: string, data?: LogData) => log('debug', msg, data),
  info:  (msg: string, data?: LogData) => log('info',  msg, data),
  warn:  (msg: string, data?: LogData) => log('warn',  msg, data),
  error: (msg: string, data?: LogData) => log('error', msg, data),
}
```

---

## Quick Reference Checklist

**Architecture**
- [ ] Data access files have `import 'server-only'`
- [ ] No cross-feature imports (shared logic → `lib/`)
- [ ] URL-driven state uses nuqs, not useState
- [ ] No server data in Zustand

**TypeScript & Validation**
- [ ] `strict: true`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`
- [ ] Zero `any` types
- [ ] All external data validated with Zod (forms, API responses, env vars, URL params)
- [ ] `params` / `searchParams` awaited (Next.js 15)

**Security**
- [ ] No secrets in `NEXT_PUBLIC_` vars
- [ ] Redirect targets validated (relative path or allowlist)
- [ ] No raw user input in `dangerouslySetInnerHTML`
- [ ] Auth check via `requireUser()` in Server Components, never client-side
- [ ] Security headers in `next.config.ts` — verified at securityheaders.com
- [ ] `npm audit` passing in CI

**React / Next.js**
- [ ] `'use client'` only at leaf nodes
- [ ] Forms use `useActionState` + `useFormStatus` (default)
- [ ] Heavy components use `next/dynamic`
- [ ] `requireUser()` in every protected Server Component

**UI Quality**
- [ ] Loading state for every async operation (`loading.tsx` or `<Suspense>`)
- [ ] `error.tsx` at every route level
- [ ] Empty state for every list / table / dashboard
- [ ] No `<div onClick>` — semantic `<button>` or `<a>`
- [ ] No raw `<img>` — `next/image` with `width`/`height` or `fill`

**Accessibility**
- [ ] Keyboard navigation for all interactive elements
- [ ] Color contrast ≥ 4.5:1
- [ ] Animations respect `prefers-reduced-motion` (`useReducedMotion()`)
- [ ] Error messages linked via `aria-describedby`

**Performance**
- [ ] LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 (verified with Lighthouse)
- [ ] LCP element has `priority` prop
- [ ] `sizes` attribute on responsive images
- [ ] Bundle size < 100KB First Load JS per route (`ANALYZE=true npm run build`)
- [ ] Fonts via `next/font` with `display: 'swap'`

**SEO (public-facing pages)**
- [ ] `metadata` on every page (title, description, OG image)
- [ ] Dynamic OG image for content pages
- [ ] `sitemap.ts` + `robots.ts` at app root
- [ ] JSON-LD for articles / products

**Setup**
- [ ] `suppressHydrationWarning` on `<html>` tag
- [ ] `<Toaster />` mounted once at root layout
- [ ] `<WebVitalsReporter />` mounted once at root layout
- [ ] Theme toggle keyboard-accessible

**Testing**
- [ ] Every form has integration tests (valid, invalid, pending, server error)
- [ ] Critical flows have e2e tests
- [ ] No snapshot tests

**Observability**
- [ ] Every `error.tsx` calls `Sentry.captureException`
- [ ] Web Vitals tracked in production
- [ ] No raw `console.log` — use `logger`

---

## Prompt Template

```
Context:
- Feature: [name + description]
- Stack: Next.js 15 · TypeScript strict · Tailwind · shadcn/ui · Supabase

Rules (this guide):
- Server Components by default; 'use client' only at leaf nodes
- Forms: useActionState + useFormStatus (default)
         react-hook-form only for multi-step / real-time field validation
- URL state: nuqs · Mutations: Server Actions
- Zod for all external data (forms, API, env vars, URL params)
- Auth: requireUser() in every protected Server Component
- Loading + error + empty states required on every async view
- Semantic HTML · no div onClick · next/image only (no raw img)
- No `any` · no NEXT_PUBLIC_ secrets · await params/searchParams
- Animations: useReducedMotion() always · Notifications: toast() not alert()
- CWV: LCP ≤ 2.5s · INP ≤ 200ms · CLS ≤ 0.1

Request: [specific implementation request]
```
