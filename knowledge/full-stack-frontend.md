# Indie Maker Full-Stack Frontend

Extended pattern library for Rex (Indie SaaS Frontend Specialist).
Covers patterns NOT in `frontend-guide.md`: animation, URL state, multi-step forms, Zustand, dark mode, data tables, landing sections, v0.dev prompts.

> Read `frontend-guide.md` first — these patterns build on top of those foundations.

---

## Section 1: Product Type UI Matrix

Choose UI personality based on product type. Affects layout density, animation intensity, color mode default.

| Product Type | Layout | Animation | Color Mode | Density |
|-------------|--------|-----------|-----------|---------|
| B2B SaaS | Sidebar + table-heavy | Subtle (0.15s ease) | Light default | High |
| Consumer App | Tab bar / card feed | Expressive (0.3s spring) | Both | Medium |
| Dev Tool | Command palette + code pane | Minimal | Dark default | High |
| Marketplace | Grid discovery | Medium (0.2s) | Light | Medium |
| Creator Tool | Canvas / full-bleed | Expressive | Both | Low |
| Productivity | Clean list / focus mode | Micro-only | System default | High |

**Decision rule**: When in doubt, start with B2B SaaS defaults. Override when prd-lean.md indicates consumer audience.

---

## Section 2: Animation Patterns (Framer Motion)

### Install

```bash
npm install framer-motion
```

### Rule: Always respect reduced motion

```typescript
import { useReducedMotion } from 'framer-motion'

export function AnimatedCard({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      initial={reduce ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduce ? 0 : 0.2 }}
    >
      {children}
    </motion.div>
  )
}
```

### Page transition (fade in on mount)

```typescript
// src/components/ui/page-transition.tsx
'use client'
import { motion } from 'framer-motion'

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )
}
```

### List item stagger (cards, feeds)

```typescript
'use client'
import { motion } from 'framer-motion'

const container = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.06 },
  },
}

const item = {
  hidden: { opacity: 0, y: 8 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.2 } },
}

interface StaggerListProps<T> {
  items: T[]
  renderItem: (item: T) => React.ReactNode
  keyExtractor: (item: T) => string
}

export function StaggerList<T>({ items, renderItem, keyExtractor }: StaggerListProps<T>) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show" className="space-y-3">
      {items.map((i) => (
        <motion.li key={keyExtractor(i)} variants={item}>
          {renderItem(i)}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### Slide-in sheet / panel

```typescript
'use client'
import { motion, AnimatePresence } from 'framer-motion'

interface SlideInPanelProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
}

export function SlideInPanel({ open, onClose, children }: SlideInPanelProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/40 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed right-0 top-0 h-full w-96 bg-white z-50 shadow-xl overflow-auto"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### Micro-interaction: button press

```typescript
// Wrap any button for tactile feedback
<motion.button
  whileTap={{ scale: 0.97 }}
  transition={{ duration: 0.1 }}
  className="..."
>
  Click me
</motion.button>
```

### Number counter animation

```typescript
'use client'
import { useSpring, useTransform, motion } from 'framer-motion'
import { useEffect } from 'react'

export function AnimatedNumber({ value }: { value: number }) {
  const spring = useSpring(0, { stiffness: 100, damping: 20 })
  const display = useTransform(spring, (v) => Math.round(v).toLocaleString())

  useEffect(() => { spring.set(value) }, [spring, value])

  return <motion.span>{display}</motion.span>
}
```

---

## Section 3: URL State Management (nuqs)

URL state is the correct place for filter, sort, search, and page parameters in SSR apps. `nuqs` provides type-safe URL state with Next.js App Router integration.

### Install

```bash
npm install nuqs
```

### Root layout setup

```typescript
// src/app/layout.tsx
import { NuqsAdapter } from 'nuqs/adapters/next/app'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <NuqsAdapter>{children}</NuqsAdapter>
      </body>
    </html>
  )
}
```

### Search + filter bar (Client Component)

```typescript
'use client'
import { useQueryState } from 'nuqs'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'

export function SearchFilterBar() {
  const [search, setSearch] = useQueryState('q', { defaultValue: '' })
  const [status, setStatus] = useQueryState('status', { defaultValue: 'all' })

  return (
    <div className="flex gap-3">
      <Input
        placeholder="Search..."
        value={search}
        onChange={(e) => setSearch(e.target.value || null)}
        className="max-w-sm"
      />
      <Select value={status} onValueChange={setStatus}>
        <SelectTrigger className="w-36">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All</SelectItem>
          <SelectItem value="active">Active</SelectItem>
          <SelectItem value="archived">Archived</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
```

### Read URL state in Server Component (for DB queries)

```typescript
// src/app/(dashboard)/items/page.tsx
import { createSearchParamsCache, parseAsString, parseAsInteger } from 'nuqs/server'

const searchParamsCache = createSearchParamsCache({
  q:      parseAsString.withDefault(''),
  status: parseAsString.withDefault('all'),
  page:   parseAsInteger.withDefault(1),
})

export default async function ItemsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string>>
}) {
  const { q, status, page } = searchParamsCache.parse(await searchParams)

  const supabase = await createClient()
  let query = supabase.from('items').select('*').order('created_at', { ascending: false })

  if (q) query = query.ilike('title', `%${q}%`)
  if (status !== 'all') query = query.eq('status', status)

  const from = (page - 1) * 10
  const { data: items } = await query.range(from, from + 9)

  return <ItemsView items={items ?? []} />
}
```

### Pagination with URL state

```typescript
'use client'
import { useQueryState, parseAsInteger } from 'nuqs'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  totalPages: number
}

export function UrlPagination({ totalPages }: PaginationProps) {
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1))

  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="icon"
        disabled={page <= 1}
        onClick={() => setPage(page - 1)}
        aria-label="Previous page"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <span className="text-sm text-slate-600">
        Page {page} of {totalPages}
      </span>
      <Button
        variant="outline"
        size="icon"
        disabled={page >= totalPages}
        onClick={() => setPage(page + 1)}
        aria-label="Next page"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  )
}
```

---

## Section 4: Multi-Step Form Pattern

Use when onboarding or complex creation flows exceed 3 fields. Keep each step focused on one decision.

### State machine approach (no external library)

```typescript
// src/components/features/onboarding/onboarding-wizard.tsx
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import {
  Form, FormControl, FormField, FormItem, FormLabel, FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { completeOnboardingAction } from '@/actions/onboarding'

// --- Schemas per step ---
const step1Schema = z.object({
  displayName: z.string().min(1, 'Name is required').max(50),
})

const step2Schema = z.object({
  role: z.enum(['founder', 'developer', 'designer', 'other']),
})

type Step1Values = z.infer<typeof step1Schema>
type Step2Values = z.infer<typeof step2Schema>
type AllValues = Step1Values & Step2Values

const TOTAL_STEPS = 2

export function OnboardingWizard() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [collected, setCollected] = useState<Partial<AllValues>>({})

  const progress = Math.round((step / TOTAL_STEPS) * 100)

  async function handleStep1(values: Step1Values) {
    setCollected((prev) => ({ ...prev, ...values }))
    setStep(2)
  }

  async function handleStep2(values: Step2Values) {
    const final = { ...collected, ...values } as AllValues
    await completeOnboardingAction(final)
    router.push('/dashboard')
    router.refresh()
  }

  return (
    <div className="max-w-md mx-auto space-y-8 py-16 px-4">
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-slate-500">
          <span>Step {step} of {TOTAL_STEPS}</span>
          <span>{progress}%</span>
        </div>
        <Progress value={progress} />
      </div>

      {step === 1 && <Step1Form defaultValues={collected} onNext={handleStep1} />}
      {step === 2 && (
        <Step2Form
          defaultValues={collected}
          onBack={() => setStep(1)}
          onSubmit={handleStep2}
        />
      )}
    </div>
  )
}

// --- Step components ---
function Step1Form({
  defaultValues,
  onNext,
}: {
  defaultValues: Partial<Step1Values>
  onNext: (v: Step1Values) => void
}) {
  const form = useForm<Step1Values>({
    resolver: zodResolver(step1Schema),
    defaultValues: { displayName: defaultValues.displayName ?? '' },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onNext)} className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold">What's your name?</h2>
          <p className="text-sm text-slate-500 mt-1">This is how you'll appear to your team.</p>
        </div>
        <FormField control={form.control} name="displayName" render={({ field }) => (
          <FormItem>
            <FormLabel>Display Name</FormLabel>
            <FormControl><Input {...field} autoFocus /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Continue →</Button>
      </form>
    </Form>
  )
}

function Step2Form({
  defaultValues,
  onBack,
  onSubmit,
}: {
  defaultValues: Partial<Step2Values>
  onBack: () => void
  onSubmit: (v: Step2Values) => Promise<void>
}) {
  const form = useForm<Step2Values>({
    resolver: zodResolver(step2Schema),
    defaultValues: { role: defaultValues.role },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold">What's your role?</h2>
        </div>
        <FormField control={form.control} name="role" render={({ field }) => (
          <FormItem>
            <FormLabel>Role</FormLabel>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {(['founder', 'developer', 'designer', 'other'] as const).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => field.onChange(r)}
                  className={`rounded-lg border p-3 text-sm capitalize text-left transition-colors ${
                    field.value === r
                      ? 'border-slate-900 bg-slate-900 text-white'
                      : 'border-slate-200 hover:border-slate-400'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
            <FormMessage />
          </FormItem>
        )} />
        <div className="flex gap-3">
          <Button type="button" variant="outline" onClick={onBack} className="flex-1">← Back</Button>
          <Button type="submit" disabled={form.formState.isSubmitting} className="flex-1">
            {form.formState.isSubmitting ? 'Finishing...' : 'Get started'}
          </Button>
        </div>
      </form>
    </Form>
  )
}
```

---

## Section 5: Zustand State Management

Use Zustand when 3+ components share state, or when state persists across route navigations. Default: React `useState`. Upgrade: Zustand.

### Install

```bash
npm install zustand
```

### Store pattern (with TypeScript)

```typescript
// src/stores/sidebar-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SidebarStore {
  isCollapsed: boolean
  toggle: () => void
  setCollapsed: (v: boolean) => void
}

// persist saves to localStorage automatically
export const useSidebarStore = create<SidebarStore>()(
  persist(
    (set) => ({
      isCollapsed: false,
      toggle: () => set((s) => ({ isCollapsed: !s.isCollapsed })),
      setCollapsed: (v) => set({ isCollapsed: v }),
    }),
    { name: 'sidebar-state' }
  )
)
```

### Usage in components

```typescript
// Server Component renders without Zustand — pass as prop or use in client only
'use client'
import { useSidebarStore } from '@/stores/sidebar-store'

export function Sidebar() {
  const { isCollapsed, toggle } = useSidebarStore()

  return (
    <aside className={`transition-all ${isCollapsed ? 'w-16' : 'w-64'}`}>
      <button onClick={toggle} aria-label="Toggle sidebar">...</button>
    </aside>
  )
}
```

### Notification store (global toast queue)

```typescript
// src/stores/notification-store.ts
import { create } from 'zustand'

interface Notification {
  id: string
  type: 'success' | 'error' | 'info'
  message: string
}

interface NotificationStore {
  notifications: Notification[]
  add: (n: Omit<Notification, 'id'>) => void
  remove: (id: string) => void
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],
  add: (n) => set((s) => ({
    notifications: [...s.notifications, { ...n, id: crypto.randomUUID() }],
  })),
  remove: (id) => set((s) => ({
    notifications: s.notifications.filter((n) => n.id !== id),
  })),
}))
```

---

## Section 6: Dark Mode (next-themes)

### Install

```bash
npm install next-themes
```

### Root layout setup

```typescript
// src/app/layout.tsx
import { ThemeProvider } from 'next-themes'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Theme toggle button

```typescript
'use client'
import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch — render only after mount
  useEffect(() => setMounted(true), [])
  if (!mounted) return <Button variant="ghost" size="icon" aria-hidden className="w-9 h-9" />

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
      aria-label="Toggle theme"
    >
      {resolvedTheme === 'dark'
        ? <Sun className="h-4 w-4" />
        : <Moon className="h-4 w-4" />
      }
    </Button>
  )
}
```

### Tailwind dark mode tokens

```css
/* In globals.css — shadcn/ui CSS variables handle this automatically */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}
```

---

## Section 7: Data Table Pattern (TanStack Table)

For tables with sorting, filtering, and column visibility. Use shadcn/ui's DataTable recipe as base.

### Install

```bash
npm install @tanstack/react-table
npx shadcn@latest add table
```

### Column definition pattern

```typescript
// src/components/features/items/columns.tsx
'use client'
import { ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowUpDown } from 'lucide-react'
import { formatDate } from '@/lib/utils'

export type Item = {
  id: string
  title: string
  status: 'active' | 'archived'
  created_at: string
}

export const columns: ColumnDef<Item>[] = [
  {
    accessorKey: 'title',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Title <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => (
      <Badge variant={row.original.status === 'active' ? 'default' : 'secondary'}>
        {row.original.status}
      </Badge>
    ),
  },
  {
    accessorKey: 'created_at',
    header: 'Created',
    cell: ({ row }) => formatDate(row.original.created_at),
  },
]
```

### DataTable component

```typescript
// src/components/ui/data-table.tsx
'use client'
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table'
import { useState } from 'react'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import { Input } from '@/components/ui/input'

interface DataTableProps<TData> {
  columns: ColumnDef<TData>[]
  data: TData[]
  searchKey?: string
  searchPlaceholder?: string
}

export function DataTable<TData>({
  columns,
  data,
  searchKey,
  searchPlaceholder = 'Search...',
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    state: { sorting, globalFilter },
    onGlobalFilterChange: setGlobalFilter,
  })

  return (
    <div className="space-y-4">
      {searchKey && (
        <Input
          placeholder={searchPlaceholder}
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="max-w-sm"
        />
      )}
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center text-slate-500">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
```

---

## Section 8: Image Upload UI

### Client-side preview + upload to Supabase Storage

```typescript
// src/components/features/profile/avatar-upload.tsx
'use client'
import { useState, useRef } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { toast } from 'sonner'
import { Upload } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface AvatarUploadProps {
  currentUrl?: string | null
  userId: string
}

const MAX_SIZE = 2 * 1024 * 1024  // 2MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export function AvatarUpload({ currentUrl, userId }: AvatarUploadProps) {
  const router = useRouter()
  const supabase = createClient()
  const inputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    if (!ALLOWED_TYPES.includes(file.type)) {
      toast.error('Only JPEG, PNG, or WebP files are allowed')
      return
    }
    if (file.size > MAX_SIZE) {
      toast.error('Image must be smaller than 2MB')
      return
    }

    // Local preview
    setPreview(URL.createObjectURL(file))
    handleUpload(file)
  }

  async function handleUpload(file: File) {
    setUploading(true)
    try {
      const ext = file.name.split('.').pop()
      const path = `avatars/${userId}.${ext}`

      const { error: uploadError } = await supabase.storage
        .from('public-assets')
        .upload(path, file, { upsert: true, contentType: file.type })

      if (uploadError) throw uploadError

      const { data: { publicUrl } } = supabase.storage
        .from('public-assets')
        .getPublicUrl(path)

      await supabase.from('profile').update({ avatar_url: publicUrl }).eq('id', userId)

      toast.success('Avatar updated')
      router.refresh()
    } catch {
      toast.error('Upload failed — try again')
      setPreview(null)
    } finally {
      setUploading(false)
    }
  }

  const displayUrl = preview ?? currentUrl

  return (
    <div className="flex items-center gap-4">
      <div className="relative h-16 w-16 rounded-full overflow-hidden bg-slate-100">
        {displayUrl ? (
          <Image src={displayUrl} alt="Avatar" fill className="object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-400 text-2xl font-semibold">
            ?
          </div>
        )}
      </div>
      <div>
        <Button
          variant="outline"
          size="sm"
          disabled={uploading}
          onClick={() => inputRef.current?.click()}
        >
          <Upload className="h-4 w-4 mr-2" />
          {uploading ? 'Uploading...' : 'Change avatar'}
        </Button>
        <p className="text-xs text-slate-500 mt-1">JPEG, PNG, WebP — max 2MB</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(',')}
        onChange={handleFileSelect}
        className="sr-only"
        aria-label="Upload avatar"
      />
    </div>
  )
}
```

---

## Section 9: Landing Page Section Patterns

### Feature grid (3-column)

```typescript
// src/components/sections/features-section.tsx
import { LucideIcon } from 'lucide-react'

interface Feature {
  icon: LucideIcon
  title: string
  description: string
}

export function FeaturesSection({ features }: { features: Feature[] }) {
  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-slate-900 mb-4">
          Everything you need
        </h2>
        <p className="text-center text-slate-600 max-w-xl mx-auto mb-16">
          Built for indie makers who ship fast and need tools that work.
        </p>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((f) => (
            <div key={f.title} className="space-y-3">
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900">
                <f.icon className="h-5 w-5 text-white" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-slate-900">{f.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### Social proof / testimonials

```typescript
interface Testimonial {
  quote: string
  author: string
  role: string
  avatarUrl?: string
}

export function TestimonialsSection({ testimonials }: { testimonials: Testimonial[] }) {
  return (
    <section className="py-24 bg-slate-50 px-4">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-16">Loved by indie makers</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((t) => (
            <blockquote
              key={t.author}
              className="rounded-xl border bg-white p-6 shadow-sm"
            >
              <p className="text-sm text-slate-700 leading-relaxed">"{t.quote}"</p>
              <footer className="mt-4 flex items-center gap-3">
                {t.avatarUrl && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={t.avatarUrl}
                    alt={t.author}
                    className="h-8 w-8 rounded-full object-cover"
                  />
                )}
                <div>
                  <cite className="not-italic text-sm font-semibold text-slate-900">{t.author}</cite>
                  <p className="text-xs text-slate-500">{t.role}</p>
                </div>
              </footer>
            </blockquote>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### FAQ Accordion

```typescript
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from '@/components/ui/accordion'

interface FaqItem {
  question: string
  answer: string
}

export function FaqSection({ items }: { items: FaqItem[] }) {
  return (
    <section className="py-24 px-4">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">Frequently asked questions</h2>
        <Accordion type="single" collapsible className="w-full">
          {items.map((item, i) => (
            <AccordionItem key={i} value={`item-${i}`}>
              <AccordionTrigger className="text-left font-medium">
                {item.question}
              </AccordionTrigger>
              <AccordionContent className="text-slate-600 leading-relaxed">
                {item.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  )
}
```

---

## Section 10: v0.dev Prompt Templates

Generate components faster with structured prompts. Copy, fill in `[]`, paste into v0.dev.

### SaaS Dashboard prompt

```
Create a Next.js dashboard page using shadcn/ui components.

Stack: Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui, Lucide icons.

Layout:
- Fixed left sidebar (w-64) with navigation links and user avatar
- Main content area with top header (title + action button)
- Responsive: sidebar collapses to Sheet on mobile

Stats row: 3 Cards showing [metric 1], [metric 2], [metric 3]. Each Card has a title, large number, and trend badge (green up / red down).

Below stats: a DataTable with columns [col1], [col2], [col3], [col4]. Include a search input above the table.

Colors: slate-900 primary, white background, slate-50 surface.
Typography: font-semibold headings, text-sm table rows.
```

### Pricing page prompt

```
Create a pricing page using shadcn/ui.

Stack: Next.js, TypeScript, Tailwind, shadcn/ui, Lucide.

Two pricing cards side by side (md:grid-cols-2):
- Free: $0/month — features: [f1], [f2], [f3]. Button: "Get started"
- Pro: $[X]/month — highlighted with ring-2 ring-slate-900 — features: [f1], [f2], [f3], [f4]. Badge: "Most Popular". Button: "Upgrade to Pro" (filled, dark).

Below cards: FAQ Accordion with 5 items.
Above cards: headline "[Product] pricing" and subtitle "Simple, transparent pricing."
```

### Auth form prompt (login + signup tabs)

```
Create an auth page with login and signup tabs using shadcn/ui Tabs.

Stack: Next.js App Router, TypeScript, Tailwind, shadcn/ui, React Hook Form.

Centered card (max-w-sm, mx-auto, mt-24).
Tabs: "Log in" | "Sign up"

Log in tab: email input + password input + "Sign in" button (full width) + "Forgot password?" link below.
Sign up tab: name input + email input + password input + "Create account" button (full width) + terms disclaimer text.

Show loading state (disabled + spinner) on submit.
Error messages below each invalid field.
```

### Settings page prompt

```
Create a settings page using shadcn/ui.

Stack: Next.js, TypeScript, Tailwind, shadcn/ui.

Layout: left nav with sections (Profile, Account, Notifications, Billing). Right content area renders selected section.

Profile section:
- Avatar upload (circular, 80px, with "Change" button overlay)
- Display name Input
- Bio Textarea (max 160 chars, char counter)
- Save button

Account section:
- Email display (read-only) + "Change email" link
- Password change form (current + new + confirm)
- Danger zone card (red border): "Delete account" button with confirmation Dialog.
```

---

*Generated by indie-frontend / Rex — Indie SaaS Frontend Specialist*
