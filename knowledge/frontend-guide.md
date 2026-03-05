# Indie Maker Frontend Guide

Next.js App Router + TypeScript + Tailwind CSS + shadcn/ui patterns for indie MVPs.
Provide this document as context to Claude Code for consistent, high-quality code generation.

---

## Non-Negotiable Rules

Rules that senior React/Next.js engineers enforce on every codebase.
Sources: Vercel Engineering Blog, Airbnb React Style Guide, React Docs, WCAG 2.1, Google Core Web Vitals.

### React Server Components (RSC)
1. **Server Components by default** — Every component starts as a Server Component (RSC). Only add `'use client'` when the component requires browser APIs, event handlers (onClick, onChange), or React hooks (useState, useEffect). RSCs have zero JavaScript bundle impact on the client.
2. **Push `'use client'` to leaf nodes** — If only a button inside a large component needs interactivity, extract just that button as a Client Component. Never mark a layout, page, or section as `'use client'` to avoid composition complexity.
3. **Data fetching belongs in Server Components** — Fetch data directly in RSCs using `async/await`. Never fetch in Client Components when the data is needed on initial render. This eliminates loading waterfalls.

### TypeScript
4. **Strict mode is mandatory** — `"strict": true` in `tsconfig.json`. No exceptions. Strict mode enables null checking, strict function types, and class property initialization checks. Disabling it hides bugs that will appear in production.
5. **Zero `any` types** — Every use of `any` disables TypeScript's type checking for that value. Use `unknown` when the type is truly unknown (then narrow it). Use proper generics when types are dynamic. `any` is a bug deferred to runtime.
6. **Explicit types for props and returns** — Create TypeScript interfaces for all component props. Function return types are explicit for non-trivial functions. `React.FC` is avoided — use `function ComponentName({ prop }: Props)` syntax.
7. **Zod for all external data** — Forms, API responses, environment variables, URL parameters — all validated with Zod schemas. Runtime validation where TypeScript's static analysis cannot reach.

### Error Handling & Loading States
8. **Error boundaries at page and section level** — Every page has an `error.tsx` file (Next.js App Router built-in error boundary). Sections fetching independent data have their own error boundary. An unhandled error must never crash the entire application.
9. **Loading states are not optional** — Every async operation must show feedback: skeleton, spinner, or progress indicator. "Waiting silently" is a broken user experience. Use `loading.tsx` for route-level loading and `<Skeleton>` for component-level.
10. **Empty states for every data-driven component** — Lists, tables, dashboards, and feeds must have an explicit empty state UI. Never render a blank space when data is empty. The empty state guides users toward action.

### Accessibility (WCAG 2.1 AA)
11. **Semantic HTML over `<div>` soup** — `<button>` for clickable actions, `<a>` for navigation, `<nav>` for navigation sections, `<main>` for main content, `<header>`/`<footer>` for layout landmarks. Semantic elements provide accessibility for free; `<div>` provides none.
12. **No `<div onClick>`** — A `<div>` with an onClick handler is inaccessible to keyboard users and screen readers. Use `<button>` for actions (automatically focusable, keyboard-activatable, announced as "button").
13. **`next/image` for all images** — Never use raw `<img>` tags for product images. `next/image` provides automatic optimization, lazy loading, responsive sizing, and prevents layout shift (CLS). Use `<img>` only for dynamic/user-uploaded content.
14. **ARIA only when semantic HTML is insufficient** — `aria-label`, `aria-labelledby`, `aria-describedby` supplement semantics where HTML alone is inadequate. Never use ARIA to override correct semantics or as a substitute for proper HTML.
15. **Keyboard navigation for all interactive elements** — Custom interactive components (date pickers, dropdowns, modals) must support: Tab to focus, Enter/Space to activate, Escape to dismiss, arrow keys for navigation within compound widgets.

### Code Quality
16. **One component, one concern** — Split components when they exceed ~150 lines or handle more than one responsibility. A component that fetches data, formats it, AND renders complex UI is three components.
17. **Naming conventions** — Components: PascalCase. Functions/variables: camelCase. Files: kebab-case for non-component files, PascalCase.tsx for component files. Event handlers: `handleEventName` (handleSubmit, handleClick).
18. **No prop drilling beyond 2 levels** — If a prop is passed through 3+ components without being used, extract to context or co-locate state closer to where it's needed.

### Performance
19. **Core Web Vitals are shipping criteria** — LCP (Largest Contentful Paint) ≤ 2.5s. INP (Interaction to Next Paint) ≤ 200ms. CLS (Cumulative Layout Shift) ≤ 0.1. Check with Vercel Speed Insights or Lighthouse. These metrics affect SEO and user retention.
20. **Dynamic imports for heavy components** — Large charts, rich text editors, video players: use `next/dynamic` with `{ ssr: false }` for client-only or `loading: () => <Skeleton />` for lazy loading. Reduces initial bundle size.

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
```

### tsconfig.json (strict mode)

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

### Folder Structure

```
src/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   ├── page.tsx       ← Server Component (renders form)
│   │   │   └── loading.tsx    ← Loading UI
│   │   └── signup/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx         ← Auth guard + sidebar layout
│   │   ├── dashboard/
│   │   │   ├── page.tsx       ← Data fetching RSC
│   │   │   ├── loading.tsx
│   │   │   └── error.tsx      ← Error boundary
│   │   └── [feature]/
│   │       └── page.tsx
│   ├── api/
│   │   └── [resource]/
│   │       └── route.ts       ← API Route Handler
│   ├── layout.tsx             ← Root layout
│   ├── page.tsx               ← Landing page (public)
│   ├── error.tsx              ← Root error boundary
│   └── not-found.tsx
├── components/
│   ├── ui/                    ← shadcn components (auto-generated)
│   ├── layout/
│   │   ├── navbar.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── features/              ← Domain-specific components
│       └── [feature-name]/
├── lib/
│   ├── supabase/
│   │   ├── client.ts          ← Browser client
│   │   └── server.ts          ← Server client (cookies)
│   └── utils.ts               ← cn(), formatDate(), etc.
├── hooks/                     ← Custom React hooks
└── types/                     ← Shared TypeScript types
    └── index.ts
```

---

## Supabase Client Setup

```typescript
// src/lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

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
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        },
      },
    }
  )
}
```

## Auth Middleware

```typescript
// src/middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return request.cookies.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  if (!user && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return supabaseResponse
}

export const config = {
  matcher: ['/dashboard/:path*'],
}
```

---

## Core Component Patterns

### Server Component: Data Fetching

```typescript
// src/app/(dashboard)/dashboard/page.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { ItemList } from '@/components/features/items/item-list'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  const { data: items, error } = await supabase
    .from('items')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error  // caught by error.tsx

  return <ItemList items={items ?? []} userId={user.id} />
}
```

### Client Component: Form with Validation

```typescript
'use client'
// src/components/features/items/create-item-form.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Form, FormControl, FormField, FormItem, FormLabel, FormMessage,
} from '@/components/ui/form'

const createItemSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title is too long'),
})

type CreateItemFormValues = z.infer<typeof createItemSchema>

export function CreateItemForm() {
  const router = useRouter()
  const supabase = createClient()

  const form = useForm<CreateItemFormValues>({
    resolver: zodResolver(createItemSchema),
    defaultValues: { title: '' },
  })

  async function onSubmit(values: CreateItemFormValues) {
    const { error } = await supabase.from('items').insert(values)

    if (error) {
      toast.error('Failed to create item: ' + error.message)
      return
    }

    toast.success('Item created!')
    router.refresh()
    form.reset()
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="flex gap-2">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem className="flex-1">
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input placeholder="Enter title..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          disabled={form.formState.isSubmitting}
          className="mt-6"
        >
          {form.formState.isSubmitting ? 'Creating...' : 'Add Item'}
        </Button>
      </form>
    </Form>
  )
}
```

### Empty State Component (required pattern)

```typescript
// src/components/ui/empty-state.tsx
import { LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-slate-100 p-4 mb-4">
        <Icon className="h-8 w-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm text-slate-500 max-w-sm">{description}</p>
      {action && (
        <Button onClick={action.onClick} className="mt-4">
          {action.label}
        </Button>
      )}
    </div>
  )
}
```

### Dashboard Layout with Auth Guard

```typescript
// src/app/(dashboard)/layout.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { Sidebar } from '@/components/layout/sidebar'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar user={user} />
      <main className="flex-1 overflow-auto">
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  )
}
```

### Error Boundary (required in every route segment)

```typescript
// src/app/(dashboard)/dashboard/error.tsx
'use client'
import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)  // Sentry will capture this automatically
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <h2 className="text-lg font-semibold text-slate-900">Something went wrong</h2>
      <p className="mt-2 text-sm text-slate-500">
        {error.message || 'An unexpected error occurred.'}
      </p>
      <Button onClick={reset} className="mt-4">Try again</Button>
    </div>
  )
}
```

---

## Utility Functions

```typescript
// src/lib/utils.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format date for display */
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

/** Format relative time ("2 hours ago") */
export function formatRelativeTime(date: string | Date): string {
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  const diff = (new Date(date).getTime() - Date.now()) / 1000
  if (Math.abs(diff) < 60) return rtf.format(Math.round(diff), 'second')
  if (Math.abs(diff) < 3600) return rtf.format(Math.round(diff / 60), 'minute')
  if (Math.abs(diff) < 86400) return rtf.format(Math.round(diff / 3600), 'hour')
  return rtf.format(Math.round(diff / 86400), 'day')
}

/** Format USD price */
export function formatPrice(cents: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(cents / 100)
}
```

---

## Environment Variables

```bash
# .env.local (git-ignored, never commit)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Server-only — never NEXT_PUBLIC_ prefix
SUPABASE_SERVICE_ROLE_KEY=eyJ...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_PRICE_ID=price_...
RESEND_API_KEY=re_...

# Public
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## Required Dependencies

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@supabase/ssr": "latest",
    "@supabase/supabase-js": "latest",
    "stripe": "latest",
    "@stripe/stripe-js": "latest",
    "lucide-react": "latest",
    "clsx": "latest",
    "tailwind-merge": "latest",
    "sonner": "latest",
    "react-hook-form": "latest",
    "@hookform/resolvers": "latest",
    "zod": "latest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "latest",
    "@types/react": "latest",
    "@types/react-dom": "latest"
  }
}
```

---

## Architecture Decision Guide

| Scenario | Decision | Reason |
|----------|---------|--------|
| Initial page data | Server Component fetch | No client JS, faster TTFB |
| User interaction triggers data change | `useTransition` + Server Action | No separate API route needed |
| Real-time data (chat, notifications) | Supabase Realtime + Client Component | SSR cannot push updates |
| Heavy component (chart, editor) | `next/dynamic` with loading skeleton | Reduce initial bundle |
| Auth state | Middleware + RSC check | Most secure; no client-side flash |
| Form submission | React Hook Form + Zod + API Route | Validation both sides |
| Global state | React Context or Zustand | Context for simple, Zustand for complex |

---

## Server Actions

Prefer Server Actions over API Routes for mutations that originate from a form or button in a Server/Client Component. No separate `route.ts` needed; revalidation is co-located with the action.

### Basic Server Action (inline)

```typescript
// src/app/(dashboard)/items/page.tsx
import { revalidatePath } from 'next/cache'
import { createClient } from '@/lib/supabase/server'
import { Button } from '@/components/ui/button'

export default async function ItemsPage() {
  const supabase = await createClient()
  const { data: items } = await supabase.from('items').select('*')

  async function deleteItem(formData: FormData) {
    'use server'
    const id = formData.get('id') as string
    const supabase = await createClient()
    const { error } = await supabase.from('items').delete().eq('id', id)
    if (error) throw error
    revalidatePath('/items')
  }

  return (
    <ul>
      {(items ?? []).map((item) => (
        <li key={item.id} className="flex items-center justify-between gap-4 p-3 border rounded">
          <span>{item.title}</span>
          <form action={deleteItem}>
            <input type="hidden" name="id" value={item.id} />
            <Button type="submit" variant="destructive" size="sm">Delete</Button>
          </form>
        </li>
      ))}
    </ul>
  )
}
```

### Server Action with useTransition (Client Component)

Use `useTransition` to show pending state without blocking navigation.

```typescript
'use client'
import { useTransition } from 'react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

// actions/items.ts (separate file — reusable across components)
// 'use server'
// export async function deleteItemAction(id: string) { ... }

interface DeleteButtonProps {
  itemId: string
  deleteAction: (id: string) => Promise<void>
}

export function DeleteItemButton({ itemId, deleteAction }: DeleteButtonProps) {
  const [isPending, startTransition] = useTransition()

  function handleDelete() {
    startTransition(async () => {
      try {
        await deleteAction(itemId)
        toast.success('Item deleted')
      } catch {
        toast.error('Failed to delete item')
      }
    })
  }

  return (
    <Button
      variant="destructive"
      size="sm"
      disabled={isPending}
      onClick={handleDelete}
    >
      {isPending ? 'Deleting...' : 'Delete'}
    </Button>
  )
}
```

### Extracted Server Action file

```typescript
// src/actions/items.ts
'use server'
import { revalidatePath } from 'next/cache'
import { createClient } from '@/lib/supabase/server'
import { z } from 'zod'

const createItemSchema = z.object({
  title: z.string().min(1).max(200),
})

export async function createItemAction(data: z.infer<typeof createItemSchema>) {
  const parsed = createItemSchema.safeParse(data)
  if (!parsed.success) throw new Error('Invalid input')

  const supabase = await createClient()
  const { error } = await supabase.from('items').insert(parsed.data)
  if (error) throw error

  revalidatePath('/items')
}

export async function deleteItemAction(id: string) {
  const supabase = await createClient()
  const { error } = await supabase.from('items').delete().eq('id', id)
  if (error) throw error
  revalidatePath('/items')
}
```

---

## Streaming & Suspense

Use `<Suspense>` to stream slow data sections without blocking the entire page render. The page shell renders immediately; slow components stream in as data resolves.

### Page-level Streaming

```typescript
// src/app/(dashboard)/dashboard/page.tsx
import { Suspense } from 'react'
import { StatsCards } from '@/components/features/dashboard/stats-cards'
import { RecentActivity } from '@/components/features/dashboard/recent-activity'
import { StatsSkeleton } from '@/components/ui/skeletons'

export default function DashboardPage() {
  // Do NOT await here — let Suspense boundaries handle timing
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Fast section — no Suspense needed */}
      <WelcomeBanner />

      {/* Slow section — streams in independently */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsCards />
      </Suspense>

      {/* Another independent slow section */}
      <Suspense fallback={<div className="h-48 rounded-lg bg-slate-100 animate-pulse" />}>
        <RecentActivity />
      </Suspense>
    </div>
  )
}
```

```typescript
// src/components/features/dashboard/stats-cards.tsx
// This is an async Server Component — it fetches its own data
import { createClient } from '@/lib/supabase/server'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export async function StatsCards() {
  const supabase = await createClient()
  const { data: items } = await supabase.from('items').select('id', { count: 'exact' })

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-slate-500">Total Items</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{items?.length ?? 0}</p>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Dynamic rendering (opt out of static)

```typescript
// Force dynamic rendering for pages with real-time or user-specific data
export const dynamic = 'force-dynamic'

// Or use unstable_noStore inside a component
import { unstable_noStore as noStore } from 'next/cache'

export async function LiveStats() {
  noStore()
  const supabase = await createClient()
  // ...
}
```

---

## Skeleton Loading Components

Define skeleton components co-located with the real component, or in `src/components/ui/skeletons.tsx` for shared ones. Always match the visual shape of the real content to prevent layout shift.

### Shared Skeleton Primitives

```typescript
// src/components/ui/skeletons.tsx
import { Skeleton } from '@/components/ui/skeleton'  // shadcn skeleton

// Stats cards skeleton (mirrors StatsCards layout)
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

// List row skeleton (mirrors list items)
export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-lg border bg-white p-4">
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

// Table skeleton
export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-lg border">
      <div className="border-b bg-slate-50 p-4">
        <div className="flex gap-4">
          {Array.from({ length: cols }).map((_, i) => (
            <Skeleton key={i} className="h-4 flex-1" />
          ))}
        </div>
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 border-b p-4 last:border-0">
          {Array.from({ length: cols }).map((_, j) => (
            <Skeleton key={j} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

// Form skeleton (mirrors form layout)
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

### Route-level loading.tsx

```typescript
// src/app/(dashboard)/items/loading.tsx
import { ListSkeleton } from '@/components/ui/skeletons'

export default function ItemsLoading() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="h-7 w-32 bg-slate-200 rounded animate-pulse" />
        <div className="h-9 w-24 bg-slate-200 rounded animate-pulse" />
      </div>
      <ListSkeleton rows={8} />
    </div>
  )
}
```

---

## SEO & Metadata

Use Next.js `generateMetadata` for dynamic SEO. Static pages use `export const metadata`. Both are Server-only — never import in Client Components.

### Static metadata (landing page)

```typescript
// src/app/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ProductName — One-line value proposition',
  description: 'Two-sentence description under 160 chars. Focus on the user benefit.',
  openGraph: {
    title: 'ProductName — One-line value proposition',
    description: 'Two-sentence description under 160 chars.',
    url: process.env.NEXT_PUBLIC_APP_URL,
    siteName: 'ProductName',
    images: [
      {
        url: `${process.env.NEXT_PUBLIC_APP_URL}/og-image.png`,  // 1200×630px
        width: 1200,
        height: 630,
        alt: 'ProductName screenshot',
      },
    ],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ProductName — One-line value proposition',
    description: 'Two-sentence description.',
    images: [`${process.env.NEXT_PUBLIC_APP_URL}/og-image.png`],
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL!),
}
```

### Root layout metadata (defaults + icons)

```typescript
// src/app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL!),
  title: {
    template: '%s | ProductName',   // page title + site name
    default: 'ProductName',
  },
  description: 'Default description for pages without their own.',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
}
```

### Dynamic metadata (blog post, product detail)

```typescript
// src/app/blog/[slug]/page.tsx
import type { Metadata } from 'next'
import { createClient } from '@/lib/supabase/server'
import { notFound } from 'next/navigation'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const supabase = await createClient()
  const { data: post } = await supabase
    .from('posts')
    .select('title, excerpt, cover_image_url')
    .eq('slug', slug)
    .single()

  if (!post) return { title: 'Not Found' }

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: post.cover_image_url ? [{ url: post.cover_image_url }] : [],
    },
  }
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params
  const supabase = await createClient()
  const { data: post } = await supabase.from('posts').select('*').eq('slug', slug).single()
  if (!post) notFound()
  // ...
}
```

### Structured data (JSON-LD, optional for articles/products)

```typescript
// src/components/seo/json-ld.tsx
interface ArticleJsonLdProps {
  title: string
  description: string
  publishedAt: string
  authorName: string
  url: string
}

export function ArticleJsonLd({ title, description, publishedAt, authorName, url }: ArticleJsonLdProps) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description,
    datePublished: publishedAt,
    author: { '@type': 'Person', name: authorName },
    url,
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}
```

---

## Stripe Checkout UI

Two patterns: **Stripe Checkout** (redirect to Stripe-hosted page — simplest) and **Payment Element** (embedded form — more control). For indie MVPs, use Checkout redirect unless custom branding is required.

### Pattern A: Checkout redirect (recommended for MVPs)

```typescript
// src/actions/stripe.ts
'use server'
import Stripe from 'stripe'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function createCheckoutSession(priceId: string) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const session = await stripe.checkout.sessions.create({
    customer_email: user.email,
    client_reference_id: user.id,
    line_items: [{ price: priceId, quantity: 1 }],
    mode: 'subscription',
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?checkout=success`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    metadata: { userId: user.id },
  })

  redirect(session.url!)
}
```

```typescript
// src/components/features/pricing/upgrade-button.tsx
'use client'
import { useTransition } from 'react'
import { Button } from '@/components/ui/button'
import { createCheckoutSession } from '@/actions/stripe'

interface UpgradeButtonProps {
  priceId: string
  label?: string
}

export function UpgradeButton({ priceId, label = 'Upgrade to Pro' }: UpgradeButtonProps) {
  const [isPending, startTransition] = useTransition()

  function handleUpgrade() {
    startTransition(async () => {
      await createCheckoutSession(priceId)
    })
  }

  return (
    <Button onClick={handleUpgrade} disabled={isPending} size="lg">
      {isPending ? 'Redirecting to checkout...' : label}
    </Button>
  )
}
```

### Pricing card with upgrade button

```typescript
// src/components/features/pricing/pricing-card.tsx
import { Check } from 'lucide-react'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { UpgradeButton } from './upgrade-button'

interface PricingCardProps {
  name: string
  price: number           // in dollars
  description: string
  features: string[]
  priceId: string
  isPopular?: boolean
  isCurrent?: boolean
}

export function PricingCard({
  name, price, description, features, priceId, isPopular, isCurrent,
}: PricingCardProps) {
  return (
    <Card className={isPopular ? 'ring-2 ring-slate-900' : ''}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{name}</CardTitle>
          {isPopular && <Badge>Most Popular</Badge>}
        </div>
        <div className="mt-2">
          <span className="text-4xl font-bold">${price}</span>
          <span className="text-slate-500 text-sm">/month</span>
        </div>
        <p className="text-sm text-slate-600">{description}</p>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {features.map((feature) => (
            <li key={feature} className="flex items-center gap-2 text-sm">
              <Check className="h-4 w-4 text-green-600 shrink-0" aria-hidden="true" />
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
      <CardFooter>
        {isCurrent ? (
          <p className="text-sm text-slate-500 text-center w-full">Current plan</p>
        ) : (
          <UpgradeButton priceId={priceId} label={`Get ${name}`} />
        )}
      </CardFooter>
    </Card>
  )
}
```

### Customer portal (manage / cancel subscription)

```typescript
// src/actions/stripe.ts — add to existing file
export async function createPortalSession() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  // Fetch Stripe customer ID stored in your DB after first checkout
  const { data: profile } = await supabase
    .from('profiles')
    .select('stripe_customer_id')
    .eq('id', user.id)
    .single()

  if (!profile?.stripe_customer_id) redirect('/pricing')

  const session = await stripe.billingPortal.sessions.create({
    customer: profile.stripe_customer_id,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/settings`,
  })

  redirect(session.url)
}
```

```typescript
// src/components/features/settings/manage-subscription-button.tsx
'use client'
import { useTransition } from 'react'
import { Button } from '@/components/ui/button'
import { createPortalSession } from '@/actions/stripe'

export function ManageSubscriptionButton() {
  const [isPending, startTransition] = useTransition()

  return (
    <Button
      variant="outline"
      disabled={isPending}
      onClick={() => startTransition(async () => { await createPortalSession() })}
    >
      {isPending ? 'Opening portal...' : 'Manage subscription'}
    </Button>
  )
}
```

### Post-checkout success banner

```typescript
// Detect ?checkout=success in dashboard and show a one-time toast
// src/app/(dashboard)/dashboard/page.tsx
import { CheckoutSuccessBanner } from '@/components/features/dashboard/checkout-success-banner'

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ checkout?: string }>
}) {
  const { checkout } = await searchParams
  return (
    <div className="space-y-6">
      {checkout === 'success' && <CheckoutSuccessBanner />}
      {/* ...rest of dashboard */}
    </div>
  )
}
```

```typescript
// src/components/features/dashboard/checkout-success-banner.tsx
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

export function CheckoutSuccessBanner() {
  const router = useRouter()

  useEffect(() => {
    toast.success('Subscription activated! Welcome to Pro.')
    // Remove ?checkout=success from URL without reloading
    router.replace('/dashboard')
  }, [router])

  return null
}
```

---

## Optimistic UI

Use `useOptimistic` (React 19) for instant feedback on mutations — list item toggles, likes, deletes. Pair with a Server Action; the UI rolls back automatically if the action throws.

### Toggle with useOptimistic

```typescript
'use client'
import { useOptimistic, useTransition } from 'react'
import { toggleItemAction } from '@/actions/items'
import { Button } from '@/components/ui/button'
import { Check, Circle } from 'lucide-react'

interface Item {
  id: string
  title: string
  completed: boolean
}

export function ItemList({ initialItems }: { initialItems: Item[] }) {
  const [isPending, startTransition] = useTransition()
  const [optimisticItems, updateOptimistic] = useOptimistic(
    initialItems,
    (state, { id, completed }: { id: string; completed: boolean }) =>
      state.map((item) => (item.id === id ? { ...item, completed } : item))
  )

  function handleToggle(item: Item) {
    startTransition(async () => {
      // Optimistic update fires immediately
      updateOptimistic({ id: item.id, completed: !item.completed })
      // Server action runs; if it throws, optimistic state rolls back
      await toggleItemAction(item.id, !item.completed)
    })
  }

  return (
    <ul className="space-y-2">
      {optimisticItems.map((item) => (
        <li key={item.id} className="flex items-center gap-3 rounded-lg border bg-white p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleToggle(item)}
            aria-label={item.completed ? 'Mark incomplete' : 'Mark complete'}
          >
            {item.completed
              ? <Check className="h-4 w-4 text-green-600" />
              : <Circle className="h-4 w-4 text-slate-400" />
            }
          </Button>
          <span className={item.completed ? 'line-through text-slate-400' : ''}>
            {item.title}
          </span>
        </li>
      ))}
    </ul>
  )
}
```

### Optimistic delete

```typescript
'use client'
import { useOptimistic, useTransition } from 'react'
import { deleteItemAction } from '@/actions/items'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-react'
import { toast } from 'sonner'

interface Item { id: string; title: string }

export function DeletableItemList({ initialItems }: { initialItems: Item[] }) {
  const [, startTransition] = useTransition()
  const [optimisticItems, removeOptimistic] = useOptimistic(
    initialItems,
    (state, idToRemove: string) => state.filter((item) => item.id !== idToRemove)
  )

  function handleDelete(id: string) {
    startTransition(async () => {
      removeOptimistic(id)
      try {
        await deleteItemAction(id)
      } catch {
        toast.error('Delete failed — item restored')
        // useOptimistic auto-restores state on throw
      }
    })
  }

  return (
    <ul className="space-y-2">
      {optimisticItems.map((item) => (
        <li key={item.id} className="flex items-center justify-between rounded-lg border bg-white p-4">
          <span className="text-sm">{item.title}</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleDelete(item.id)}
            aria-label={`Delete ${item.title}`}
          >
            <Trash2 className="h-4 w-4 text-slate-400 hover:text-red-500" />
          </Button>
        </li>
      ))}
    </ul>
  )
}
```

---

## Quick Reference Checklist

Before delivering any code output:

- [ ] No `any` TypeScript types
- [ ] No raw `<img>` tags — `next/image` used
- [ ] No `<div onClick>` — semantic `<button>` or `<a>` used
- [ ] Loading state present for every async operation
- [ ] Error boundary (`error.tsx`) at page level
- [ ] Empty state for all data-driven lists/dashboards
- [ ] All form inputs validated with Zod schema
- [ ] `'use client'` only at leaf nodes needing interactivity
- [ ] No secrets in client-accessible code (no `NEXT_PUBLIC_` for private keys)

---

## Claude Code Prompt Template

Provide this context when asking Claude Code to implement a feature:

```
Context:
- Product: [idea-canvas.md summary]
- Feature: [prd-lean.md feature name + description]
- Stack: Next.js 15 App Router + TypeScript strict + Tailwind + shadcn/ui + Supabase

Guidelines (from frontend-guide.md):
- Server Components by default; 'use client' only at leaf nodes
- Zod validation for all inputs
- Loading + error + empty states required
- Semantic HTML only (no div onClick)
- No `any` types

Request: Implement [specific feature] following these guidelines.
```
