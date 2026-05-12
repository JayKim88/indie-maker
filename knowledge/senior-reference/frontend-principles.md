# Senior Frontend Developer Principles

> Stack: Next.js · React · React Native · TypeScript · TailwindCSS · Apollo Client · Supabase · Vitest · Storybook

---

## Table of Contents

**Foundation**
1. [Core Philosophy](#core-philosophy)
2. [JavaScript Fundamentals](#javascript-fundamentals)
   — Execution Context · Hoisting · `this` Binding · Closures · Prototype Chain
3. [TypeScript Discipline](#typescript-discipline)
   — Strict Mode · Generics · Utility Types · Type Narrowing · Mapped Types · Conditional Types
4. [Project Architecture](#project-architecture)
   — Folder Structure · Module Boundaries · File Naming · Import Discipline

**Build Layer**
5. [Component Design](#component-design)
   — Server/Client Boundary · Error Boundaries · Custom Hook Pattern · Side Effect Lifecycle · Imperative DOM Access · Event Propagation · React Portals · Styling with TailwindCSS
6. [Rendering Strategy](#rendering-strategy)
   — SSR · SSG · ISR · CSR · Streaming · RSC · JSX Transform · Virtual DOM · Fiber · Concurrent Mode
7. [State Architecture](#state-architecture)
   — Four Categories · Decision Tree · React 19 APIs (`use`, `useOptimistic`, `ref` as prop)
8. [Data Layer & Apollo Client](#data-layer--apollo-client)
   — Cache Normalization · Fetch Policies · Optimistic Updates · Route Handlers · Supabase Direct Access
9. [Form Handling](#form-handling)
   — Server Actions · react-hook-form · Validation · Pending States · Error Display

**UX Quality**
10. [Performance Mindset](#performance-mindset)
    — Core Web Vitals · Browser Rendering Pipeline · FCP · LCP · CLS · Stacking Context · INP · Bundle Size · Build Pipeline · HTTP Caching · Memory Leaks · React DevTools Profiling
11. [Accessibility Standards](#accessibility-standards)
    — Semantic HTML · Keyboard Navigation · Color/Contrast · ARIA · Motion Accessibility

**Security**
12. [Authentication & Security](#authentication--security)
    — Network Fundamentals · TLS · JWT · Web Storage · Protected Routes · CORS · XSS Prevention

**Platform Extensions**
13. [AI Feature Development](#ai-feature-development)
14. [React Native & Cross-Platform](#react-native--cross-platform)

**Operations**
15. [Testing Philosophy](#testing-philosophy)
    — Testing Pyramid · AAA Pattern · Storybook · MSW · Coverage Strategy
16. [Observability](#observability)
17. [Deployment & CI/CD](#deployment--cicd)
    — Vercel · GitHub Actions · Next.js Metadata API
18. [Team Standards](#team-standards)

19. [Quick Reference Checklist](#quick-reference-checklist)

---

## Core Philosophy

### Five Principles That Override Everything Else

**Server-first rendering.** Every component is a Server Component until there is a concrete reason it cannot be. Interactivity, browser APIs, and subscriptions are the only valid reasons to move to the client. "I'm used to writing client components" is not a reason. The default stance eliminates unnecessary JavaScript bundles, improves initial load performance, and keeps sensitive data server-side.

**Type safety as correctness guarantee.** TypeScript strict mode is not a linting preference — it is the primary tool for making refactors safe and catching errors before runtime. Every `any`, every type assertion without justification, and every ignored compiler error is a deferred production incident. The goal is a codebase where changing an interface causes every affected call site to surface a type error immediately.

**Explicit state ownership.** Ambiguous state is the root cause of most frontend bugs. Before writing any state, answer: who owns this, who reads it, and when does it change? State that should be in a URL is often put in component memory. State that should be on the server is often duplicated on the client. Getting this decision right at the start is faster than debugging stale state later.

**Performance is a launch criterion.** Core Web Vitals — LCP, INP, CLS — are part of the definition of "done" for every feature, not a post-launch concern. A feature that renders correctly but degrades user experience metrics is not finished. Budget these targets into design and architecture decisions, not as an afterthought.

**Accessibility is non-negotiable.** Semantic HTML, keyboard navigation, and WCAG 2.1 AA compliance are baseline requirements for every component. These are not audited at the end of a project — they are enforced in design review and code review. Retrofitting accessibility is significantly more expensive than building it in.

---

## TypeScript Discipline

TypeScript rules apply to everything that follows. Component design, state management, data fetching, and form handling are all downstream of type discipline. Establish this foundation before anything else.

### Strict Mode is the Minimum

Enable every strict TypeScript check: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`. These catch entire categories of runtime errors at compile time. Array index access returning `T | undefined` rather than `T` prevents the most common null pointer class of bugs. Exact optional properties prevent the accidental passing of `undefined` where a property simply should not exist.

### Where Types Come From

Types are generated, not hand-written, wherever possible. GraphQL schema → TypeScript types via code generation (GraphQL Code Generator). Database schema → TypeScript types via Supabase type generation. External API responses → Zod schemas that parse and validate at the boundary, producing TypeScript types as a byproduct. Hand-writing types for external data sources creates a second source of truth that diverges from reality.

### The Boundary Rule

Validate external data at every entry point. HTTP responses from FastAPI, data from Supabase queries, URL parameters, environment variables, and user form inputs are all external. Validate them with Zod at the exact point they enter the application. Once validated, treat the data as typed throughout the application. Never validate in the middle of a function — validate at the boundary, trust internally.

### The `any` Prohibition

`any` disables the type checker for everything it touches and every value derived from it. Every `any` must be justified with a comment explaining why it cannot be typed correctly. "It's complex" and "I'll fix it later" are not justifications. If a third-party library lacks types, create a declaration file with minimal but accurate typings. If a type is genuinely dynamic, use `unknown` and narrow it explicitly.

### Type Assertions

Type assertions (`as Type`) override the compiler's judgment. They are appropriate when you have information the compiler cannot infer — typically after a type guard, or when a library returns a weaker type than you know is actually present. They are not appropriate for "making the error go away." A type assertion without a comment explaining the invariant it is asserting is always wrong.

### Discriminated Unions for State

Represent UI states as discriminated unions rather than multiple nullable fields. A request that can be idle, loading, successful, or failed is four distinct states, not one state with four nullable fields. Discriminated unions make invalid states unrepresentable and exhaustive switch statements make missed cases compile errors.

### Generic Types

A generic type accepts type parameters, allowing a function, hook, or component to work with any type while preserving type relationships. A function that takes an array and returns its first element should type its return as `T | undefined` given input `T[]` — not `any`. Generics are how you write abstractions that remain fully type-safe regardless of what type they operate on.

Generics are not advanced TypeScript — they are the mechanism behind almost every utility type, every reusable hook, and every component abstraction. Avoiding them forces one of two bad alternatives: duplicating typed functions for each concrete type, or using `any` to accept all types at the cost of type safety.

**Generic constraints.** A type parameter can be constrained with `extends`. A function that accesses `.id` on its argument constrains the parameter to `T extends { id: string }` rather than accepting anything. This narrows what types a generic accepts while still allowing variation within that constraint.

**When to reach for a generic.** The signal: a function, hook, or type operates identically regardless of the specific type, and the return type depends on the input type. Common cases: `useLocalStorage<T>`, a `Result<T, E>` discriminated union for success/failure, a generic table component `DataTable<TRow>` that preserves row type through sorting and filtering.

### Utility Types

TypeScript ships built-in utility types that transform existing types. These are not shortcuts — they are the mechanism for expressing types derived from other types. Hand-writing transformed types is a maintenance problem: a change to the base type must be manually propagated to every derived type.

| Utility | What it produces | When to use |
|---|---|---|
| `Partial<T>` | All properties optional | Form state before validation, patch payloads |
| `Required<T>` | All properties required | After defaults are applied, after validation |
| `Pick<T, K>` | Only specified keys | DTO subsets, component prop projections |
| `Omit<T, K>` | All keys except specified | Removing server-generated fields (id, createdAt) from creation payloads |
| `Record<K, V>` | Object with specific key/value types | Lookup tables, enum-to-display-string maps |
| `ReturnType<F>` | Return type of a function | Typing variables that hold function results without duplicating the type |
| `NonNullable<T>` | Removes null and undefined | Downstream of a null check to narrow the type |
| `Awaited<T>` | Resolved type of a Promise | Typing async results; common in Server Component data patterns |
| `Parameters<F>` | Tuple of parameter types | Typing wrappers around existing functions |

### Type Narrowing

Type narrowing makes TypeScript aware that a value's type is more specific than its declared type, based on runtime checks. After narrowing, TypeScript treats the value as the narrower type in that branch, enabling safe access to properties that would otherwise be unsafe.

The built-in narrowing mechanisms: `typeof` for primitives, `instanceof` for class instances, `in` for property existence, and equality checks against `null` or `undefined`. These are statically analyzed — the compiler understands what each check implies about the type.

**Custom type guards** extend narrowing to conditions TypeScript cannot infer. A function with return type `value is User` tells the compiler that when the function returns true, `value` is narrowed to `User` in the calling scope. This is the correct pattern for validation functions that check the shape of unknown data.

**`unknown` pairs with narrowing.** External data should enter as `unknown`, not `any`. The difference: `unknown` requires narrowing before any property access; `any` disables all checks. Casting directly with `as User` skips the check and reintroduces the risks `unknown` was designed to prevent. Validate with Zod at the boundary — Zod's output is a narrowed, typed value. For simpler cases without Zod, narrow manually with type guards.

### Mapped Types

A mapped type transforms the properties of an existing type according to a rule: `{ [K in keyof T]: SomeTransformation }`. This is how most built-in utility types are implemented, and the right tool when a type must mirror another type's structure with modified properties — staying automatically in sync when the source type changes.

In application code, mapped types appear for: creating per-field validation states that mirror a form type, building typed permission objects that enumerate exactly the actions available on a resource, and typing event handler maps where every event variant must be handled. The principle: when structure must mirror another type and stay synchronized, a mapped type guarantees that.

### Conditional Types and `infer`

A conditional type selects between two types based on a condition: `T extends U ? X : Y`. The practical use is writing types whose output depends on the input type — a utility that extracts a nested type only when the structure matches a pattern.

The `infer` keyword captures a type variable from within the matched pattern. `ReturnType<F>` is implemented as `F extends (...args: any[]) => infer R ? R : never` — it matches any function and captures its return type as `R`. Understanding this is necessary for reading library source types and building utilities when built-in ones do not compose into what you need. In application code, the most common need is typing wrapper functions around generics whose return types TypeScript cannot automatically infer.

---

## JavaScript Fundamentals

JavaScript's runtime behavior — how code executes, how scope works, how values are inherited — is the foundation everything else builds on. These concepts explain why React hooks work the way they do, what causes stale closure bugs, and how to reason about async execution order.

### Execution Context and the Call Stack

Every piece of JavaScript code runs inside an execution context — an internal object that holds the variable environment (all identifiers declared in this scope and their current values), the lexical environment (a reference chain to outer scopes for identifier lookup), and the `this` binding. When the engine begins running a script, it creates the global execution context. Each function call creates a new function execution context and pushes it onto the call stack. When the function returns, its context is popped. The engine always runs the context at the top of the stack.

### Hoisting and the Temporal Dead Zone

Before any code in a scope runs, the engine performs an evaluation phase that registers all declarations. Function declarations are fully hoisted — registered with their complete implementation and available anywhere in the scope, even before the line where they are written. `var` declarations are hoisted and initialized to `undefined`. `let` and `const` declarations are hoisted but left in an uninitialized state called the Temporal Dead Zone — accessing them before their declaration line throws a ReferenceError. This distinction explains why `var` can appear to run in unexpected order, and why `let` and `const` provide safer scoping semantics. Always use `const` by default and `let` when reassignment is needed. `var` has no valid use case in modern JavaScript.

### `this` Binding Rules

`this` is not a variable — it is a keyword whose value is determined at call time, not at definition time. The value of `this` inside a function depends on how that function is invoked, not where it was written.

Four binding rules determine `this` in order of precedence. Default binding: a regular function called as a standalone call has `this` set to the global object in non-strict mode, or `undefined` in strict mode. Implicit binding: when a function is called as a method (`obj.method()`), `this` is the calling object. Explicit binding: `call`, `apply`, and `bind` set `this` explicitly. Constructor binding: when a function is called with `new`, `this` is a newly created empty object that the function populates.

Arrow functions do not have their own `this` — they capture it lexically from the enclosing scope at definition time, and no binding rule can change it. In React function components, `this` is not used at all — hooks replace the class lifecycle model entirely. In class components (now rare), passing an unbound method as a prop loses its `this` binding when the caller invokes it; the standard fixes are binding in the constructor or writing the method as an arrow function class property.

### Closures

Every execution context has a lexical environment — a data structure that maps identifier names to their current values. When a function is defined, it captures a reference to the lexical environment of the scope it was defined in, not the scope it is called from. This captured reference is a closure. The function retains access to the outer scope's variables even after the outer function has returned and its context has been popped from the call stack.

Closures are the mechanism behind React hooks. When a component renders, each hook call captures the current state values in a closure. This creates a specific class of bug: stale closures. A `useEffect` callback captures the values of its dependencies at the time the effect was created. If those values change in a subsequent render, the effect's closure still references the old values unless the dependency array is updated. A missing dependency in a `useEffect` dependency array is a stale closure bug — the effect runs with outdated data. `useCallback` exists for the same reason: without memoization, a new function is created on every render with a fresh closure, making referential equality checks for child component props always fail.

### Prototype Chain

JavaScript objects are linked through a chain of prototype references. When the engine looks up a property, it checks the object itself first, then its prototype, then the prototype's prototype, continuing until it reaches `null`. Arrays inherit `map`, `filter`, and `reduce` from `Array.prototype`. Plain objects inherit `hasOwnProperty` and `toString` from `Object.prototype`. The `class` keyword is syntactic sugar over this mechanism: `class User extends Person` sets `User.prototype`'s prototype to `Person.prototype`.

In React function components, direct prototype manipulation is never appropriate. Understanding the chain matters for: reasoning about `instanceof` checks, knowing why spreading an object copies only its own enumerable properties (not inherited ones), reading third-party library code that uses constructor patterns, and explaining `typeof null === 'object'` (a historical specification bug that cannot be fixed without breaking the web).

---

## Project Architecture

### Folder Structure Strategy

Feature-based organization scales better than layer-based organization. In layer-based organization, all components live in `/components`, all hooks in `/hooks`, all utilities in `/utils` — regardless of what feature they belong to. This means understanding one feature requires jumping across the codebase. In feature-based organization, everything belonging to a feature lives together: its components, hooks, types, utilities, and server actions.

The practical structure has three layers:

The **app layer** contains only Next.js routing concerns — `page.tsx`, `layout.tsx`, `error.tsx`, `loading.tsx`, and `route.ts`. Pages are thin orchestrators that import from the feature layer. Business logic does not live in page files.

The **features layer** contains self-contained feature modules. Each feature directory owns its components, hooks, types, server actions, and utilities. Features do not import from each other — if two features share something, that shared thing moves to the shared layer.

The **shared layer** contains genuinely cross-cutting concerns: the design system components, shared types, global utilities, API clients, and configuration. Code earns its place in the shared layer by being referenced from three or more distinct features, not by being "general enough."

### Module Boundary Rules

A feature may import from the shared layer. A feature must not import from another feature. A page may import from any feature. If a page needs to combine outputs from two features, it orchestrates them — it does not create a dependency between the features themselves.

Circular imports are always a symptom of a boundary violation. When a circular import appears, the solution is not a workaround — it is a boundary redesign. Either the shared dependency needs to move to the shared layer, or the features need to be merged because they were never truly separate concerns.

### File Naming Conventions

Component files and their default exports match exactly: `UserProfileCard.tsx` exports `UserProfileCard`. Server Actions live in `actions.ts` within the relevant feature or route directory. Hooks start with `use` and are named after what they return, not how they work: `useCurrentUser` rather than `useAuthFetch`. Types and interfaces for a module live in `types.ts` in the same directory. Shared types that span multiple features live in `lib/types/`.

### Import Discipline

Absolute imports using path aliases (`@/features/user`) are always preferred over relative imports that navigate upward (`../../components/user`). Relative imports are acceptable only within the same directory. Import order: external packages first, then internal absolute imports, then relative imports. A consistent import order makes diffs easier to read and merge conflicts easier to resolve.

---

## Component Design

### The Single Responsibility Boundary

A component does one thing well. The question to ask is: if this component changes, what else might break? If the answer involves more than one concern — data fetching, display logic, interaction handling, and layout — the component should be split. Splitting early is almost always cheaper than splitting after business logic has entangled itself with rendering logic.

### The Server/Client Boundary

Server Components have access to server resources — databases, environment secrets, file system — and produce no JavaScript bundle cost. Client Components run in the browser and support state, event handlers, and browser APIs. These are not interchangeable: the boundary between them is an architectural decision, not a performance tweak.

The `'use client'` directive marks the boundary. Everything below it in the component tree becomes client-side JavaScript. The architectural goal is to push this boundary as deep into the tree as possible — ideally to the leaf nodes that genuinely need interactivity. A page that fetches data should be a Server Component. The interactive button within that page is a Client Component. The layout wrapping the page is a Server Component.

Server Components cannot be imported into Client Components and used as children that receive props — but they can be passed as `children` from a Server Component parent. This pattern allows a Client Component to handle interaction while a Server Component handles the data-heavy subtree within it. Understanding this composition model is the prerequisite for avoiding unnecessary client-side bundles.

**Directive clarification: `'use client'` vs `'use server'`.** In Next.js App Router, Server Components are the default — they require no directive. `'use client'` marks the boundary where a component and everything it imports becomes client-side JavaScript. `'use server'` is a different concept entirely: it marks Server Actions — async functions that can be called from Client Components but execute on the server (form submissions, mutations, server-side validation). Applying `'use server'` to a component file does not make it a Server Component; it is not a valid directive for that purpose. A common misconception in the ecosystem is treating `'use server'` as the counterpart to `'use client'` for components — it is not. The correct mental model: no directive = Server Component (default), `'use client'` = Client Component, `'use server'` = Server Action function.

See [Rendering Strategy](#rendering-strategy) for how the Server/Client distinction maps to page-level rendering decisions.

### Composition Over Configuration

Prefer composing multiple focused components over a single component with many configuration props. A component that accepts fifteen props is doing too much. When you find yourself adding another boolean prop to change rendering behavior, that is a signal to extract a variant or a separate component. The shadcn/ui pattern — exporting primitive subcomponents like `Card`, `CardHeader`, `CardContent` — is the right model: maximum flexibility with minimal complexity at any individual level.

### Separation of Data and Presentation

The Container/Presentational pattern is the naming convention for a principle already implicit in well-structured components: data-handling logic belongs in one place, rendering belongs in another. A container component manages state, fetches data, handles events, and passes results down as props. A presentational component receives props and renders markup — it has no opinion about where the data came from or how events are handled. The presentational component is easy to test, easy to reuse, and easy to render in Storybook in isolation.

In the Next.js App Router model, the Server/Client boundary already enforces this separation at the page level: a Server Component fetches data and passes it to a Client Component child that owns interactivity. Inside a feature's Client Component subtree, the same principle applies manually. A component that both fetches order data, manages a selected-order state, and renders the list is doing too much. Splitting it into a container (state and data) and a presentational component (rendering given props) makes each unit testable and replaceable independently.

The pattern does not require creating files with "Container" in the name — what matters is the structural rule: components that own state and data should not own rendering details, and components that own rendering should not own state.

### Error Boundaries

React renders component trees synchronously. If any component throws an error during rendering, the entire tree unmounts by default — the user sees a blank page. Error Boundaries are class components that implement `componentDidCatch` and `getDerivedStateFromError` to intercept render errors and display a fallback UI instead of crashing the application.

The scope of an Error Boundary is its subtree: it catches errors thrown during rendering, in lifecycle methods, and in constructors of components below it. It cannot catch errors in event handlers (use try/catch there), asynchronous code like `setTimeout` or Promise rejections, or server-side rendering errors. A single application-level boundary is insufficient — place boundaries strategically around sections of the UI that can fail independently without taking down the rest of the application.

Practical placement: wrap major page sections (sidebar, main content area, data widgets) in separate boundaries so a failing widget does not blank the entire page. Pair Error Boundaries with Sentry capture in `componentDidCatch` to record the error in production monitoring before showing the fallback. The fallback UI should be informative — "This section failed to load" with a retry button is better than a generic error message that gives users no path forward.

### Custom Hook Pattern

A custom hook is a function whose name starts with `use` and that calls one or more built-in hooks. Custom hooks are the primary mechanism for separating behavior logic from rendering logic in function components. A component that mixes data fetching state, polling logic, and render markup in one function body is doing too much. Extracting the behavior into a custom hook produces two units: a hook that owns the behavior (stateful, testable in isolation), and a component that owns the rendering (receives the hook's return values as its working data).

**When to extract.** The signal is cognitive load, not file length. Extract when: a group of state variables and effects always change together and represent a unified concern (a `useWebSocket` that manages connection, reconnection, and message state); a behavioral pattern repeats across multiple components with slight variations (a `usePagination` used by three different list components); or when testing the behavior independently from rendering is valuable.

**Design the API for the consumer, not the implementation.** A custom hook's return value is its public interface. `useCurrentUser()` returning `{ user, isLoading, error }` is a clear API. A hook returning `[userData, setUserData, userLoading, userError, refetchUser, clearUser]` is exposing implementation details as an interface — group related values into objects and name them by what they represent, not how they are stored.

**Hooks are not components.** A custom hook cannot be rendered, cannot return JSX, and must only call hooks, run synchronous logic, and produce return values. If you find yourself wanting to return markup from a custom hook, you have a component, not a hook.

**`renderHook` for isolated testing.** React Testing Library's `renderHook` mounts a hook in a minimal host component, allowing assertions on returned values and state changes without rendering any UI. Test the hook's behavior directly when the logic is complex enough to warrant it, rather than testing it indirectly through a component that uses it.

### Co-location

Keep related things close together. A component's types and its immediate helpers should live in the same file or the same directory. Reaching across the project to find a type used by one component is a maintenance overhead that compounds with project size. The exception is shared types that are genuinely referenced across many parts of the application — those belong in the shared types directory.

### Side Effect Lifecycle

`useEffect` cleanup is not the reverse of the effect itself — it is the preparation for the next effect cycle. Before React runs the next effect (because a dependency changed) or before the component unmounts, it executes the cleanup function returned from the current effect. This ordering guarantees that the side effects from one effect cycle do not interfere with the next.

**Three categories that always require cleanup.** Any `useEffect` that creates one of the following must return a cleanup function with no exceptions:

Timers and intervals — each time the component renders with changed dependencies, the effect body runs again and creates a new timer. Without cleanup, the previous timer continues firing alongside the new one. The cleanup must cancel the previous timer before the new one is created. The pattern applies equally to `setTimeout` and `setInterval`.

DOM event listeners and subscriptions — `addEventListener` accumulates listeners; it does not replace. If an effect adds a scroll listener and the component re-renders without cleanup removing the previous listener, the handler fires multiple times per event by the next render cycle. The same applies to WebSocket subscriptions, message channels, and any pub-sub pattern. The cleanup removes exactly the listener instance created in that effect's closure — not a generic reference.

Asynchronous requests — when a user changes a search query faster than responses arrive, each effect run fires a new request. Without cancellation, responses arrive out of order and each one updates state, causing visual flicker or incorrect final state. The pattern is to create an `AbortController` inside the effect, pass its signal to the fetch call, and call `controller.abort()` in the cleanup. The aborted request's rejection is ignored rather than updating state.

**Simple data fetching without cleanup.** A one-time fetch with an empty dependency array does not technically require cleanup in React 18 because React suppresses the "can't perform state update on unmounted component" warning. However, under Concurrent Mode, React can render a component twice in development before committing — and in production, a component can mount, unmount, and remount. Any fetch inside `useEffect` should cancel via `AbortController` in the cleanup to be safe in concurrent rendering contexts. The `isMounted` boolean flag — setting a local `let isMounted = true` and checking it before calling `setState` in the response handler — is the legacy pattern for this problem. It prevents the state update but does not cancel the in-flight network request, which continues consuming bandwidth unnecessarily. `AbortController` supersedes it: the request is actually terminated, no response is processed, and no guard check is needed.

**Cleanup captures its render's values.** The cleanup function is a closure over the values from the render that created the effect. When `count` is 3 and an effect fires, the cleanup for that effect will see `count` as 3 — regardless of what `count` is when the cleanup runs. This is the intended behavior: the cleanup is cleaning up that specific effect invocation. It is also the source of stale closure bugs when the dependency array is incomplete. If the effect reads `userId` but `userId` is absent from the dependency array, the cleanup will always capture the initial value of `userId`, which is wrong when `userId` changes.

**The `exhaustive-deps` ESLint rule is authoritative.** Treat every `react-hooks/exhaustive-deps` warning as a probable bug, not a suggestion. The most common "fix" of suppressing the warning with a disable comment is almost always wrong — it hides a real synchronization problem. The legitimate exceptions (intentionally running an effect only on mount with values that should not re-trigger it) require explicit reasoning and a comment explaining why the omission is safe.

**React.StrictMode double-invocation is a validator.** In development, React.StrictMode runs each effect twice — mount → cleanup → mount — to surface cleanup bugs. If a component behaves incorrectly when its effect runs twice, its cleanup is incomplete. This is not a quirk to work around; it is a deliberate mechanism that makes cleanup bugs visible before production. Any effect that cannot tolerate being run a second time after its cleanup has a defect.

**`useLayoutEffect` for pre-paint DOM work.** `useEffect` fires asynchronously after the browser has already painted the committed DOM. `useLayoutEffect` fires synchronously after React's commit phase but before the browser paints — the user never sees the intermediate state. Both hooks run after React has written changes to the DOM; the only difference is whether the browser is allowed to paint between the commit and the effect.

This timing difference matters precisely when you read a DOM measurement and use it to immediately alter what is displayed. If you read an element's `getBoundingClientRect()` inside a regular `useEffect` and then update state to reposition a tooltip, a popover, or a virtualized list row based on the measurement, the browser has already painted once with the wrong position. The user sees a flash. `useLayoutEffect` prevents this: the state update happens inside the same synchronous block as the measurement, so the browser paints only the corrected result.

The canonical cases for `useLayoutEffect`: reading element dimensions to position a floating element (tooltip, dropdown, context menu), reading scroll height to initialize a virtualized list, synchronizing sibling element heights, and initializing an animation at the exact position of a DOM element. If none of these patterns apply — if the effect does not read layout measurements to drive an immediate DOM correction — use `useEffect`.

`useLayoutEffect` does not run on the server. In a Next.js App Router project, this means it is only valid inside Client Components — React will warn if a Server Component uses it. If a shared component needs layout measurements and might be rendered in a server context, the safe pattern is to initialize with a null or zero measurement value, render with that initial value on the server, and update via `useLayoutEffect` on the client after the first commit. The user sees a layout adjustment on first client render, which is acceptable because the server cannot know DOM dimensions anyway.

Because `useLayoutEffect` runs synchronously and blocks paint, an expensive operation inside it degrades FCP and INP directly. If the effect takes more than a few milliseconds, the layout-blocking behavior becomes the performance problem. Keep `useLayoutEffect` bodies to DOM reads and immediate state sets — no network requests, no timers, no complex computations.

### Imperative DOM Access

React's rendering model is declarative: you describe what the UI should look like given current state, and React handles translating that description into actual DOM nodes. Direct DOM manipulation via `document.querySelector` or `document.getElementById` breaks this contract. When React next renders the component, it reconciles based on the Virtual DOM tree it controls — and it will overwrite any mutations you made directly to the real DOM. The result is UI inconsistency: your change disappears, or worse, the reconciler produces incorrect output because its internal representation no longer matches the real DOM.

**The `ref` prop is React's approved escape hatch.** When you attach a `ref` to a JSX element — `<input ref={inputRef} />` — React sets `ref.current` to the underlying DOM node after the component mounts and commits to the DOM. You access this node through `ref.current` inside a `useEffect` or an event handler, after the render is complete. This is safe because you are not modifying content that React's reconciler is managing; you are performing imperative operations on a node that React created and tracks.

**When imperative DOM access is legitimate.** There are operations that have no declarative React equivalent and must be performed imperatively: programmatic focus management (placing focus on an input after a modal opens, or returning focus to a trigger element when it closes), reading layout measurements (an element's width, height, or scroll position before React can know them), triggering scroll behavior (`scrollIntoView`, scroll position restoration), and integrating third-party libraries that require a DOM node to initialize (chart libraries, rich text editors, map embeds). These are the canonical cases for DOM refs.

**What refs must not do.** Do not use a DOM ref to modify content, attributes, or styles on elements that React is rendering. If you set `ref.current.textContent = "..."` on an element whose text is also controlled by JSX, React's next render will overwrite your change — and the behavior depends on render timing in a way that is not deterministic. Imperative DOM access through refs is an escape hatch from the declarative model, not an alternative to it. If you find yourself reaching for a DOM ref to change visible content, that is a signal to model the change as state instead.

**Component refs and the forwarding pattern.** Native DOM elements accept the `ref` prop by default. Custom components do not — passing `ref` to a custom component does nothing unless the component explicitly forwards it using `React.forwardRef`. When building a shared component (a custom input, a modal container, a scroll region) that consuming code may need to imperatively control, expose the underlying DOM node via `forwardRef` so callers can attach their own refs. Without this, the DOM node is inaccessible, and callers fall back to `document.querySelector` — the pattern this is meant to avoid.

### Event Propagation Model

Events in the DOM do not only fire on the element that was clicked or focused — they travel through the document in two phases. The capture phase starts at the document root and propagates down the tree to the target element. The bubble phase starts at the target element and propagates back up to the document root. React's synthetic event system uses the bubble phase by default, which is why a click on a child element triggers `onClick` handlers on its parent elements unless stopped explicitly.

`event.target` is the element that originally received the event — the specific button or input that was clicked. `event.currentTarget` is the element on which the current event handler is registered. These are different when an event has bubbled up from a child: `event.target` is the child that was clicked, `event.currentTarget` is the ancestor with the handler.

`event.stopPropagation()` halts the event from continuing its bubble phase, preventing parent handlers from firing. Use this deliberately — accidentally stopping propagation hides events from ancestor components that may legitimately need them. A common mistake is calling `stopPropagation` to prevent a modal backdrop from closing when clicking inside the modal; the correct approach is to check whether `event.target` is the backdrop element before calling the close handler, not to stop propagation from the content.

Event delegation leverages bubbling intentionally: a single listener on a list container handles clicks on all its children by inspecting `event.target`, rather than attaching per-item listeners. React uses this pattern internally — all synthetic event listeners are attached to the root, not to individual DOM nodes. This is why React's event handling scales well even across very large component trees.

### React Portals

React renders its component tree into the DOM container specified at `createRoot`. Portals render a component's output into a different DOM node — typically `document.body` — while keeping the component in its original position in the React tree for context propagation and event bubbling.

**The two problems portals solve.** Overflow clipping: a modal rendered inside a container with `overflow: hidden` is visually clipped to the container's bounds. Stacking context: a tooltip inside an element that creates a stacking context (via `transform`, `opacity < 1`, `will-change`, or `z-index` combined with `position`) cannot appear above sibling elements regardless of its own `z-index`. Portaling to `document.body` removes both constraints — the modal or tooltip renders outside any clipping or stacking context.

**The React tree is preserved even when the DOM tree is not.** A portaled component still receives its parent's Context values, still participates in event bubbling through the React component tree (not the DOM tree), and still unmounts when its React parent unmounts. A click inside a portaled modal bubbles up through React to the portal's parent component handlers — this is often surprising but is intentional and correct.

**Canonical uses.** Modals and dialogs (must overlay the entire page), tooltips and popovers (must appear above overflow-clipped containers), toast notifications (fixed position relative to the viewport), and right-click context menus. The shadcn/ui `Dialog`, `Popover`, `DropdownMenu`, `Tooltip`, and `Sheet` components all use Radix UI's portal primitive internally — understanding this mechanism explains why they work correctly in deeply nested layouts.

### Styling with TailwindCSS

TailwindCSS applies styles by composing atomic utility classes directly on elements. The principles below prevent the class-string chaos that gives Tailwind a poor reputation when used without discipline.

**`cn()` is mandatory for any component that accepts a `className` prop.** Tailwind classes can conflict: if a component applies `text-red-500` and a consumer passes `text-blue-500`, both classes exist in the DOM and the winner is determined by CSS order in the generated stylesheet — not by which class appeared last. This produces unintuitive visual bugs. The solution is `cn()` — a thin wrapper around `clsx` (conditional class composition) and `tailwind-merge` (deduplicates conflicting utilities, keeping the last winner). Every component that accepts external class names must merge them through `cn()`. This is non-optional.

**Component variants belong in `cva`.** When a component has multiple visual variants — primary/secondary/destructive buttons, sm/md/lg sizes — the naive approach is string concatenation with ternaries. This becomes unreadable at three variants and unmaintainable at five. `class-variance-authority` (cva) defines variant mappings as structured data: each variant name maps to the Tailwind classes that implement it. The result is a typed API where an invalid variant name is a TypeScript error, and all class strings for a variant are co-located and easy to change.

**Arbitrary values signal a design system gap.** Tailwind's arbitrary value syntax (`w-[347px]`, `text-[#1a2b3c]`) is appropriate for genuine one-offs — matching a fixed third-party element dimension, integrating a legacy layout. It is not a shortcut around the design system. Frequent arbitrary values for spacing, color, or typography indicate the Tailwind config needs extending with proper design tokens, not circumventing.

**Responsive design is mobile-first.** Breakpoint prefixes (`md:`, `lg:`) apply at and above the specified breakpoint. The unprefixed class applies at all breakpoints — write mobile layout without a prefix, then override for larger screens. Writing desktop styles without a prefix and attempting to override for mobile does not work cleanly in Tailwind.

**Extract into components, not `@apply`.** When the same class combination appears in many places, the reflex is `@apply` inside a CSS class. This is almost always wrong: it creates opaque class names, undermines Tailwind's purging, and reintroduces cascade problems Tailwind was designed to avoid. The correct extraction is a React component. If a card with specific padding, border radius, and shadow is used in fifteen places, make a `<Card>` component. `@apply` is appropriate only for global base styles that cannot reasonably be a component — link styles in MDX content, form element resets in a markdown renderer.

---

## Rendering Strategy

### Rendering Architecture Concepts

Before choosing a rendering strategy, the terminology must be clear — these terms are frequently conflated, and conflating them leads to wrong architectural decisions.

**SPA vs CSR: architecture vs rendering method.** SPA (Single Page Application) is an architectural pattern: the application loads once and navigates without full-page reloads, updating the DOM in place. CSR (Client-Side Rendering) is a rendering method: the browser receives a minimal HTML shell and JavaScript generates the full UI on the client. Most early SPAs used CSR, which is why the terms are often used interchangeably — but they are distinct. A Next.js application is an SPA in the architectural sense (client-side navigation, no full reloads after initial load), yet it uses SSR or SSG for most of its rendering. SPA describes the navigation model; CSR describes who renders the HTML.

**Why SSR re-emerged.** The original web was entirely SSR: servers generated complete HTML on every request. When JavaScript frameworks matured, the industry shifted toward CSR because it enabled app-like experiences without page reloads. CSR introduced two problems that became unacceptable at scale: slow initial load (the browser receives an empty shell and waits for JavaScript to run before showing any content) and poor SEO (crawlers saw empty pages). SSR returned not as a regression but as a deliberate hybrid strategy — use the server for initial rendering to get fast first paint and crawler-readable content, then hand off to the client for subsequent interactions.

**Hydration: how SSR hands off to the client.** In traditional SSR, the server renders a complete HTML page and sends it with a JavaScript bundle. The browser displays the HTML immediately — users see content before any JavaScript runs. But this HTML is inert: buttons do not respond, state does not exist, React has not executed. Hydration is the process of React executing on the client over the already-rendered HTML, matching the client-rendered Virtual DOM tree against the server-rendered DOM, and "wiring up" the event handlers and state that make the page interactive. Until hydration completes, the page is visible but not interactive — this gap is the Time to Interactive (TTI) concern. Hydration requires the client to download, parse, and execute the full JavaScript bundle for every hydrated component. For content-heavy pages with little interactivity, this is pure overhead.

**SSR vs React Server Components: what gets sent to the client.** SSR and React Server Components (RSC) are often confused because both render on the server. The difference is in what the client receives. Traditional SSR sends HTML and a JavaScript bundle containing the component code; the client must execute this bundle to hydrate the page. RSC sends only HTML and serialized props — no component JavaScript at all for Server Components. A Server Component has zero bundle contribution; it cannot maintain state, handle events, or use browser APIs, and in return it sends nothing to the JavaScript bundle. This is why RSC is the correct choice for data-heavy, non-interactive components: a product page that renders 500 items from a database query contributes nothing to the client bundle if those item components are Server Components. The JS bundle cost scales only with interactive Client Components, not with total application complexity.

**The five rendering strategies and when each applies.**

| Strategy | What happens | When to use |
|----------|-------------|-------------|
| SSR (Server-Side Rendering) | Server renders full HTML on every request | User-specific, real-time, or frequently-changing content |
| SSG (Static Site Generation) | HTML generated once at build time | Content identical for all users, rarely changes |
| ISR (Incremental Static Regeneration) | Static pages regenerated in the background at a set interval | Content that changes occasionally; SSG staleness is unacceptable but full SSR cost is unnecessary |
| CSR (Client-Side Rendering) | Browser renders HTML from JavaScript | Real-time subscriptions, browser-only APIs, highly interactive widgets |
| Streaming SSR | Server sends HTML in chunks as each section resolves | Pages with multiple independent data sources of varying latency |

**Next.js App Router is a hybrid model by default.** The framework does not force a global rendering strategy — each route segment independently declares its strategy via export configuration or implicitly through how it fetches data. A marketing page uses SSG. A dashboard page uses SSR. A real-time notification widget uses CSR. A product page with occasionally-updated pricing uses ISR with an appropriate revalidation window. The routing model is SPA-style (client-side navigation after first load), while individual page rendering can be any of the five strategies above.

### The Four Rendering Modes

**Static generation** is the default for content that does not change per request: marketing pages, blog posts, documentation, product listings that update infrequently. Generate these at build time. If the content changes occasionally, use Incremental Static Regeneration with a revalidation interval that matches the acceptable staleness window. Minutes for news, hours for documentation, days for rarely-changed pages.

**Dynamic server rendering** is for content that is user-specific or must be fresh on every request: dashboards, account settings, personalized feeds. This renders on the server per request but still sends no unnecessary JavaScript to the browser. It is faster than client-side rendering because the browser receives pre-rendered HTML rather than a loading state followed by a data fetch.

**Client-side rendering** is for genuinely interactive experiences where the data cannot be fetched on the server, or where real-time updates are required. Subscription-based data — live chat, presence indicators, real-time dashboards — belongs here. So does anything that requires browser APIs unavailable on the server.

**Streaming** allows a Server Component to send parts of the page incrementally as they resolve, rather than waiting for all data to be ready. Use streaming for pages with multiple independent data sources where one slow source should not block the rest of the page from rendering. Wrap each independent section in a Suspense boundary with a skeleton placeholder. The user sees content progressively rather than a blank page followed by everything at once.

### Choosing the Right Mode

Ask these questions in order. Is this content identical for all users and does it not change frequently? Static generation. Is it user-specific but can be resolved on the server? Dynamic server rendering. Does it need real-time updates or browser-only APIs? Client rendering. Does it have multiple independent async sections? Streaming with Suspense.

### Route Segment Configuration

Next.js lets you opt routes into specific rendering behaviors at the segment level — force static, force dynamic, set revalidation intervals, specify runtime (Node.js vs. Edge). These decisions belong close to the route definition, not scattered through component logic. Make these decisions explicitly and document why: a route opted into dynamic rendering should have a comment explaining what makes it incompatible with static generation.

In App Router, the `fetch` cache option is the primary mechanism for selecting rendering behavior per data call. The concrete mapping: `fetch(url)` with no options or `{ cache: 'force-cache' }` caches at build time (SSG behavior). `{ next: { revalidate: N } }` caches for N seconds and regenerates in the background when the window expires (ISR behavior). `{ cache: 'no-store' }` bypasses the cache entirely and re-runs on every request (SSR behavior). A route that mixes fetch calls with different cache policies will render dynamically if any call opts out of caching — Next.js uses the most restrictive policy on the route. Segment-level exports (`export const dynamic = 'force-dynamic'`) override fetch-level settings and apply to the entire route segment.

### Every Async View Has Three States

Any view that fetches data must explicitly handle three states: loading (show a skeleton that matches the dimensions of the expected content), error (show a recoverable message, not a blank page), and empty (show a prompt that guides the user toward useful action, not an empty list). A view that only handles the success state is incomplete. These three states are not edge cases — they are experienced by real users on slow connections, failed requests, and new accounts.

### React's Rendering Model: Virtual DOM, Fiber, and Concurrency

Understanding how React renders client-side UI is prerequisite to reasoning about performance, key prop semantics, and when to reach for Concurrent Mode APIs.

**JSX is syntactic sugar, not a separate language.** JSX syntax (`<Button onClick={handleClick}>Save</Button>`) is not valid JavaScript. Before any code runs, a transpiler (Babel or esbuild) transforms every JSX expression into a call to `React.createElement`. The transformed version is `React.createElement(Button, { onClick: handleClick }, "Save")` — a regular JavaScript function call that returns a plain object describing the element: its type, its props, and its children. This object tree is what React works with; JSX is only a notation convenience that disappears before the browser ever runs the code.

The practical consequence: `import React from 'react'` was required in older codebases because `React.createElement` needed to be in scope for JSX to compile. With the modern JSX transform (React 17+), the runtime import is injected automatically by the transpiler, so explicit React imports for JSX are no longer needed. The underlying mechanism — objects representing element descriptors — has not changed.

**Virtual DOM as a reconciliation layer.** React does not write directly to the DOM on every state change. Instead, when state or props change, React builds a new Virtual DOM tree — a lightweight JavaScript object graph representing the current UI. Each node in this tree is a plain object describing a component's type, props, and children. React then compares this new tree against the previous snapshot (diffing), calculates the minimal set of changes, and commits only those changes to the real DOM. This is reconciliation. Its purpose is to minimize expensive DOM operations: every real DOM change risks triggering Reflow and Repaint; by batching and minimizing DOM writes, React reduces main thread layout work.

**Diffing assumptions.** React's diffing algorithm operates under two assumptions that make it O(n) rather than the theoretical O(n³) for tree comparison. First, elements of different types produce entirely different trees — React does not attempt to partially match a `<div>` against a `<section>`, it replaces the entire subtree. Second, the `key` prop provides explicit identity for list items. If `key` is stable across renders, React assumes the element at that key is the same item and updates its props; the underlying DOM node is reused. If `key` changes — or is absent and React falls back to index — React cannot make this assumption. Using array index as key causes subtle bugs in sorted or filtered lists: React sees the same key at position 0 and reuses the DOM node, updating only the props, when it should have destroyed and recreated it. Every list that can be reordered, filtered, or have items removed needs a stable, unique key derived from the item's identity, not its position.

**Batching.** React batches multiple state updates that occur within the same event handler into a single re-render. The component function runs once, a single new Virtual DOM tree is produced, and one diff-and-commit cycle executes. Without batching, three `setState` calls would trigger three render cycles and three DOM commit passes. React 18 extends automatic batching to asynchronous contexts (promises, setTimeout) that previously required manual batching.

**React Fiber: making reconciliation interruptible.** Before React 16, reconciliation was synchronous and recursive. Once a render started, it ran to completion before the browser could do anything else — handle input events, run animations, repaint the screen. On complex component trees this blocking could last 50–100ms, making the application feel unresponsive. Fiber rewrote the reconciliation engine to make work incremental and interruptible. Each component in the tree corresponds to a Fiber node — a unit of work with fields for the component type, props, state, and a priority level. The reconciler processes these nodes one at a time and can pause between them to check whether higher-priority work is waiting.

Fiber separates rendering into two phases. The work phase — traversing the component tree, running component functions, and building the new Fiber tree — can be interrupted and resumed. The commit phase — actually writing changes to the DOM — is always synchronous and uninterrupted, because a half-applied DOM update would leave the UI in an inconsistent visual state. This separation is what makes Concurrent Mode possible.

**Concurrent Mode.** Concurrent Mode is the scheduling layer built on top of Fiber's interruptibility. React can pause a low-priority render in the middle of the work phase, hand the main thread back to the browser to process a user input event or run an animation frame, then resume the deferred work. From the user's perspective, the application stays responsive even while expensive renders are in progress.

Two APIs expose this scheduling to application code. `startTransition` marks a state update as non-urgent — React will complete it in the background and yield to higher-priority work if needed. This is the primary tool for INP: if updating a complex list, chart, or data grid in response to a filter input is causing Long Tasks, wrapping the list state update in `startTransition` keeps the input field responsive while the expensive re-render runs in background. `useDeferredValue` provides a "lagging" version of a value — the UI renders immediately with the old value while the expensive derived computation catches up. Next.js uses Concurrent Mode (`createRoot`) by default since React 18, so these APIs are available without configuration.

**Memoization is caching, not magic.** Fiber and Concurrent Mode do not eliminate the cost of reconciliation — they schedule it better. Unnecessary re-renders still execute component functions, generate new Virtual DOM trees, and run diffing. But memoization is not the solution to all re-render problems — it is a caching mechanism with its own costs, and applying it carelessly makes things slower and harder to maintain.

Every memoized value occupies memory for as long as the component is mounted. On each render, React evaluates the dependency array — comparing each entry against the previous value using shallow equality. For primitive deps this comparison is trivial, but for objects, arrays, or functions defined inline, the comparison itself is O(n) in the size of the structure. A `useMemo` wrapping a one-line string concatenation costs more than it saves — the overhead of dependency tracking exceeds the cost of the computation. `React.memo` performs a shallow comparison of all props on every parent render; a component with fifteen props of complex types pays the comparison cost unconditionally, even when the parent renders for unrelated reasons.

**The three-piece memoization trio and when it applies.** `React.memo`, `useCallback`, and `useMemo` are most effective as a coordinated system, not individually. `React.memo` wraps a child component and skips its re-render when all props pass shallow equality. For this to work, every callback prop passed to it must have a stable reference — otherwise the memo check fails on every render because a new function object is created. `useCallback` provides that stable reference; it preserves a function across renders as long as its own dependencies are unchanged. `useMemo` does the same for computed values and objects passed as props. The trio is warranted when: the parent re-renders frequently, the child is measurably expensive to re-render, and the props genuinely do not change on most parent renders. Absent all three conditions, the trio adds complexity without benefit.

**Decision criteria by hook.**

`React.memo` — apply when a child component renders frequently due to parent state changes unrelated to the child's own props, and the child's render function is non-trivial. Avoid wrapping components that receive object or array props constructed inline at the call site — the shallow comparison will always fail, making `React.memo` a pure overhead.

`useCallback` — apply when the function is passed as a prop to a `React.memo`-wrapped child, or when the function appears in another hook's dependency array (e.g., a `useEffect` that should run only when the handler changes). Do not apply to event handlers that go directly to native DOM elements (`onClick`, `onChange` on `<button>`, `<input>`) — the DOM does not use referential equality.

`useMemo` — apply when the computation is measurably expensive (sorting or filtering large datasets, complex graph calculations, cryptographic operations) and the inputs change less often than the parent renders. The threshold is roughly: if the computation takes more than 1ms, profiling is warranted; if it takes less than 0.1ms, `useMemo` is almost certainly unnecessary overhead. Do not apply to simple derivations like concatenating strings, formatting dates, or computing a boolean from two state values.

`useRef` — for values that must persist across renders without triggering re-renders. The canonical uses are: storing a DOM element reference, persisting a timer or interval ID so it can be cleared in cleanup, and keeping a mutable accumulator (like a previous value or a scroll position) that component logic reads but should not cause a re-render when updated.

`useDeferredValue` and `useTransition` — for scheduling, not for caching. Their purpose is to separate urgent updates (what the user typed) from non-urgent ones (re-rendering a large filtered list). They are covered in the Concurrent Mode and INP sections above.

**Profile before optimizing.** The React DevTools Profiler is the authoritative source for re-render costs. It shows which component re-rendered, why it re-rendered (which props changed), and how long the render took. Applying `React.memo` or `useMemo` without profiling is a guess. It may fix a problem that did not exist at measurable cost; it may introduce a new problem (stale closure bugs from an incorrect dependency array, or memory pressure from caching large values). Optimize what the profiler identifies as the bottleneck, not what looks expensive in the source code.

---

## State Architecture

### The Four Categories of State

**Server state** is data that lives on the server and is fetched into the UI. This is the most common kind of state in a data-driven application. It is not owned by the frontend — the frontend only holds a cached copy. Apollo Client manages server state for GraphQL APIs. The key discipline here is never duplicating server state into local component state unless you have an explicit reason (like optimistic updates). Duplication causes synchronization bugs.

**URL state** is state encoded in the URL — search parameters, filters, pagination, selected tabs, modal open/closed. This state is shareable, bookmarkable, and survives page refreshes. It belongs in the URL, not in `useState`. A user who filters a table and shares the link should send the recipient to the same filtered view. Use `nuqs` to synchronize URL parameters with typed values. URL state is often the right answer to the question "should this be in component state?"

**Client state** is UI-only state that does not need to be shared widely: the open/closed state of a dropdown, form field values before submission, the selected item in a local list. This belongs in `useState` at the lowest component that needs it. If it needs to be shared across siblings, lift it to their nearest common ancestor. If it needs to be accessed globally, consider whether it is actually URL state or server state dressed as client state.

When local state involves multiple distinct actions that transition the state in different ways — a multi-step form, an accordion with expand/collapse/reset actions, a fetch cycle with idle/loading/success/error states — `useReducer` is more appropriate than `useState`. The reducer function makes each state transition explicit and testable in isolation. The rule of thumb: if you find yourself managing several related `useState` calls that change together, or writing complex `setState` callbacks to derive the next state from the current state, that is the signal to move to `useReducer`. For simple values that change independently, `useState` remains the right choice.

**Global client state** is client-side state that genuinely needs to be accessed across many disconnected parts of the application: the current user's theme preference (before it is persisted), a multi-step form wizard's progress, notification counts. Zustand is the right tool for this category. Redux is almost never the right answer for a modern application at this scale.

React's Context API is sometimes the right tool for global state, but its performance characteristic must be understood before choosing it. When a Context value changes, every component that consumes that context re-renders — regardless of whether the specific part of the value that component reads actually changed. This makes Context appropriate for state that changes infrequently: the current authenticated user, the active locale, the selected theme. These values rarely change and the re-render cost is negligible. Context is a poor fit for state that changes on user interaction — a search query, a selected filter, an active tab index — because every consumer re-renders on every keystroke or click. Zustand solves this via selector subscriptions: a component subscribes to a specific slice of the store, and re-renders only when that slice changes.

For feature-scoped shared state — state that needs to be shared across several components within a single feature, but does not need to be globally accessible — `useContext` combined with `useReducer` is a clean middle ground. The `useReducer` hook provides structured state transitions with named actions; wrapping it in a Context Provider scopes it to the feature subtree without installing an external library. This pattern is appropriate when a feature has complex internal state that multiple sibling components read and modify, but the state has no meaning outside the feature boundary. When that boundary is crossed — when the state genuinely needs to be accessed from unrelated parts of the application — move it to Zustand.

### The Decision Tree for State

When adding state to an application, apply this filter in order:

- Can it be derived from existing data at render time? Then it is not state — compute it.
- Should it survive a page refresh and be shareable via URL? Use URL parameters.
- Is it server data being temporarily cached? Let Apollo Client own it.
- Is it local to one component? Use `useState`.
- Is it local to a small subtree of components? Lift to the nearest common ancestor.
- Is it needed across the entire application? Use Zustand.

State that violates this hierarchy — global state holding what should be URL state, component state holding what should be server state — is the most common source of synchronization bugs and stale UI.

### React 19 State and Data APIs

React 19 (stable late 2024) introduces APIs that change how certain state and data patterns are expressed. These are available in the current stack.

**`use()` for reading resources in Client Components.** The `use()` hook reads a value from a Promise or Context. Unlike `useContext`, it can be called inside conditional branches. Unlike `await`, it suspends the component while the Promise resolves and resumes when it completes — composing naturally with Suspense boundaries. `use(promise)` is the primary mechanism for reading data in Client Components that receive a Promise prop from a Server Component parent, without `useEffect`-based data fetching.

**`useOptimistic` for pre-confirmation state.** `useOptimistic` manages the optimistic (pre-server-confirmation) representation of state. It takes the current server-confirmed state and a reducer, and returns an optimistic copy that can be updated immediately while the server request is in flight. When the server responds, the optimistic state reconciles with the confirmed state automatically. This supersedes hand-rolling optimistic update logic with paired `useState` variables for non-GraphQL mutations. For GraphQL, Apollo's `optimisticResponse` option remains appropriate.

**`ref` as a prop.** React 19 removes the need for `forwardRef`. A custom component can accept `ref` as a regular prop alongside other props. The `forwardRef` wrapper is no longer required for new code. Existing `forwardRef` usage continues to work but can be migrated to the simpler prop pattern as components are updated.

**`useActionState` replaces `useFormState`.** The hook (renamed stable in React 19) manages the state cycle of a Server Action: the pending state, the previous action result, and the action function to pass to a form. `useFormStatus` reads the pending state of the nearest form's action from any child component, enabling submit button pending states without prop drilling. These are covered in the Form Handling section.

---

## Data Layer & Apollo Client

### Apollo Client as the Truth for GraphQL Data

Apollo Client is not just a fetching library — it is a client-side cache for your GraphQL data. Treat it as the authoritative source of server state. Do not fetch GraphQL data and then copy it into `useState`. Do not re-fetch data that is already in the cache unless you have a specific reason to bypass caching. Understanding Apollo's normalized cache is foundational to using it correctly.

### Cache Normalization

Apollo normalizes its cache by type and ID. An object returned from any query is stored once and referenced from all queries that include it. When a mutation updates a `User` with a specific ID, every query that includes that user reflects the update immediately — no manual cache invalidation. This only works if your GraphQL schema returns objects with consistent `id` fields and proper `__typename`. Never strip `__typename` from responses. Never return non-unique IDs within the same type.

### Fetch Policies

Apollo's fetch policy controls how queries interact with the cache:

| Policy | Behavior | When to use |
|--------|----------|-------------|
| `cache-first` | Read cache; skip network if data exists | Data that changes infrequently; slight staleness is acceptable |
| `cache-and-network` | Return cached data immediately, also fetch to update | Dashboards, feeds — must show fast and stay fresh |
| `network-only` | Always fetch; do not read cache first | Payment confirmations, critical status checks — staleness is never acceptable |
| `no-cache` | Fetch fresh; do not write to cache | Sensitive data that must not persist in cache |

Choosing the wrong fetch policy is a common source of either stale UI or unnecessary network load. Make the decision explicitly.

### Mutations and Cache Updates

After a mutation, Apollo does not automatically know which parts of the cache are affected. There are two strategies: refetch affected queries by name (simple, always correct, slightly inefficient), or update the cache directly using the mutation result (efficient, requires understanding the cache structure). For mutations that add items to a list, direct cache updates are preferred. For mutations that affect complex, nested data, refetching is safer.

### Optimistic Updates

Optimistic updates show the expected result of a mutation before the server confirms it, then reconcile with the real server response. They make applications feel instant. Use them for actions where failure is unlikely and user feedback is critical — liking a post, completing a task, adding an item to a cart. Do not use optimistic updates for destructive actions (deletes) or financial transactions where you must confirm server success before updating UI.

### Error Handling in GraphQL

GraphQL returns errors in two distinct ways: network errors (the request failed entirely) and GraphQL errors (the request succeeded but the operation returned errors in the response). Handle both. Network errors typically indicate connectivity or authentication problems. GraphQL errors represent business logic failures — validation errors, permission denials, resource not found. A query can return partial data alongside errors; handle both in your UI rather than treating any error as a complete failure.

### Route Handlers

Route Handlers are the App Router equivalent of API routes. A `route.ts` file in any directory within `app/` defines HTTP endpoint handlers for the methods it exports (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`). They run on the server with full access to environment secrets, the Supabase server client, and the Node.js runtime.

**When to use Route Handlers instead of Server Actions.** Server Actions are the correct choice for form submissions, mutations, and data operations originating from your own frontend — they handle CSRF automatically, integrate with `useActionState`, and do not require a stable URL. Route Handlers are appropriate for: webhook endpoints (Stripe, GitHub, email providers — external services calling your application), file download/streaming endpoints (generating PDFs, CSVs, or streaming large binary responses that cannot go through a Server Action), third-party OAuth callback handlers, and any endpoint that must be callable from non-browser clients (mobile apps, other services, CLI tools).

**Request and response interface.** Route Handlers receive a `NextRequest` (extends the standard Web API `Request`) and must return a `NextResponse` or a standard Web API `Response`. No framework-specific req/res objects — the interface is the Web Platform API. This makes Route Handlers portable and straightforward to test without Next.js-specific mocking.

**Caching behavior.** `GET` Route Handlers participate in Next.js's caching model — they can use `{ cache: 'force-cache' }` or `{ next: { revalidate: N } }` on fetch calls inside them. Non-GET handlers and any handler that uses dynamic APIs (cookies, headers, reading the request body) are always dynamic and never cached.

### Supabase Direct Access

Apollo Client handles GraphQL operations against the FastAPI backend. The Supabase client (`@supabase/ssr` server-side, `@supabase/supabase-js` client-side) handles direct database access, storage, and realtime subscriptions. These two data layers are not interchangeable — use Apollo for GraphQL, use the Supabase client for operations against Supabase directly.

**TypeScript and query results.** The Supabase client returns data with types that are often broader than necessary. Generate types from your schema using `supabase gen types typescript` and import them — never hand-write Supabase types, which creates a second source of truth that diverges from the actual schema. The generated types feed into properly typed query results without manual casting.

**Server vs. browser client.** The `@supabase/ssr` package provides separate client creation functions for server-side contexts (Server Components, Server Actions, Route Handlers) and browser contexts. The server client reads session cookies from the request. The browser client manages session state in browser storage. Never use the browser client in Server Components — it does not have access to the request's cookie store and always produces an unauthenticated context.

**Error handling.** Every Supabase query returns `{ data, error }`. A non-null `error` means the query failed — always check it before accessing `data`. The error object contains `message`, `code`, and `details`. For operations where specific failures require specific handling (RLS violation, unique constraint, network timeout), check the error code rather than just its presence. A silently null `data` value from an unhandled Supabase error is one of the most common sources of blank UI in production.

**Realtime subscriptions.** Supabase Realtime provides WebSocket-based subscriptions to database changes via PostgreSQL logical replication. A subscription is created with `supabase.channel()`, specifying the table, event type (INSERT/UPDATE/DELETE), and an optional row filter. Subscriptions are stateful resources — every channel must be explicitly removed (`supabase.removeChannel(channel)`) when the component unmounts, in a `useEffect` cleanup function. Failing to unsubscribe leaves the WebSocket channel active, the callback firing on every change, and potentially calling `setState` on an unmounted component. Subscriptions are client-side only — they cannot be created in Server Components or Server Actions.

---

## Form Handling

Forms are one of the most common user interaction patterns and one of the most frequently under-engineered. A form is not complete until it handles submission, loading, success, and every error case correctly.

### Choosing the Right Approach

Two approaches cover almost all cases. The decision depends on the form's complexity and interaction requirements.

**React 19 Server Actions with `useActionState`** is the default for forms that submit data to the server. This approach keeps mutation logic server-side, eliminates the need for a client-side API call, and integrates naturally with Next.js App Router. The form submits, the server action runs, and the result — either a success redirect or an error object — flows back to the component. Use this for: login forms, signup forms, settings pages, and any single-step form where real-time field feedback is not required.

**react-hook-form** is appropriate when the form has requirements that exceed what `useActionState` handles well: multi-step wizards that maintain state across steps, real-time per-field validation as the user types, complex conditional field logic where one field's value changes what other fields appear, or forms that are entirely client-side with no server round-trip. The library's registration model and watch system handle these cases efficiently. Do not use react-hook-form for simple server-side forms — it adds dependency weight and complexity where the native approach is sufficient.

### Validation Strategy

Validation logic lives in Zod schemas, not in component code. Define the schema once and use it in both places: on the server to validate incoming form data before processing, and on the client to validate before submission. This eliminates the class of bug where client-side and server-side validation rules diverge. The Zod schema is the single source of truth for what constitutes valid input.

Field-level errors are returned from the server action as structured data and displayed adjacent to the field they describe. A generic "something went wrong" message at the top of a form is not acceptable for validation failures — users need to know which field failed and why. Network errors and unexpected server failures display a generic message, but input validation errors must be specific.

### Pending and Loading States

Every form has two interactive states beyond the default: pending (submission in progress) and disabled (submission not allowed, typically due to invalid input). The submit button reflects both states visually. During submission, the button shows a loading indicator and becomes non-interactive — duplicate submission is prevented at the UI level, not just the server level.

`useFormStatus` reports the pending state of the nearest parent form's Server Action. This allows child components — including the submit button — to respond to submission state without prop drilling. The submit button component can read `pending` from `useFormStatus` independently of where it is placed in the component tree.

### Error Display Hierarchy

Form errors exist at two levels. Field errors are adjacent to the input they describe and appear as soon as that field's validation state is known — either on blur or after the first submission attempt. Form-level errors appear at the top of the form and cover conditions that are not attributable to a single field: duplicate email on signup, insufficient permissions, rate limiting. Both levels are required. A form that only shows field errors misses server-side business logic failures. A form that only shows form-level errors makes it impossible for users to find which input to fix.

### Accessibility in Forms

Every input has a programmatically associated label. Placeholder text is not a label substitute — it disappears when the user types and is not reliably announced by screen readers. Error messages are associated with their input via `aria-describedby` so screen readers announce them when focus moves to the field. Required fields are marked with `aria-required`. The form can be fully completed and submitted using only the keyboard.

---

## Performance Mindset

### Core Web Vitals as Acceptance Criteria

Treat Core Web Vitals as part of the definition of done for every feature:

| Metric | Target | What it measures |
|--------|--------|-----------------|
| LCP (Largest Contentful Paint) | ≤ 2.5 seconds | How fast the main content appears |
| INP (Interaction to Next Paint) | ≤ 200ms | How responsive the page is to input |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | How much content moves unexpectedly |
| FCP (First Contentful Paint) | ≤ 1.8 seconds | How fast anything appears |

A feature that ships with degraded CWV has shipped a regression.

### Browser Architecture

A browser is not a single program — it is a system of specialized components that coordinate to turn network responses into interactive pages. Understanding which component is responsible for what helps diagnose problems in the right layer.

| Component | Responsibility |
|-----------|---------------|
| User Interface | Address bar, navigation buttons, bookmarks — everything except the rendered page content itself |
| Browser Engine | Coordinates between the UI and the rendering engine; manages navigation state |
| Rendering Engine | Parses HTML and CSS, constructs DOM and CSSOM, performs layout and paint (Blink in Chrome/Edge, WebKit in Safari, Gecko in Firefox) |
| Networking | Handles HTTP requests and responses, DNS resolution, caching, and connection management |
| UI Backend | Renders native OS-level UI widgets (buttons, dropdowns, scrollbars) using the operating system's primitives |
| JavaScript Engine | Parses, compiles, and executes JavaScript (V8 in Chrome/Node.js, SpiderMonkey in Firefox, JavaScriptCore in Safari) |
| Data Storage | Manages client-side persistence: cookies, Web Storage (localStorage/sessionStorage), IndexedDB, Cache API |

These components run in separate processes or threads. The rendering engine and JavaScript engine share the main thread, which is why JavaScript execution can block rendering and vice versa. Networking and data storage operate on background threads. This architecture is why the "main thread" is so central to performance discussions — it is the single shared resource between rendering and script execution.

### Browser Rendering Pipeline

Understanding how browsers convert network responses into pixels is a prerequisite for diagnosing rendering performance problems and for understanding what metrics like LCP and CLS actually measure.

**The parsing pipeline.** The browser does not receive HTML as a structured object — it receives raw bytes over the network. The parsing pipeline transforms those bytes in stages: bytes are decoded into characters using the document's character encoding, characters are tokenized into syntactically meaningful units (opening tags, attributes, text content, closing tags), tokens are converted into nodes, and nodes are assembled into the tree structure of the DOM. CSS goes through the same pipeline to produce the CSSOM. This staged process is why the browser can begin constructing the DOM before the entire HTML document has arrived — it processes the stream incrementally.

**JavaScript parsing and execution cost.** JavaScript goes through its own compilation pipeline before running: the engine tokenizes the source, parses tokens into an Abstract Syntax Tree (AST), compiles the AST to bytecode, and executes. Modern engines also JIT-compile hot code paths to machine code. This pipeline has real cost — a large JavaScript bundle takes measurable time to parse and compile, separate from network download time. A 500KB JavaScript file that downloads quickly on a fast network still imposes parse and compile overhead, particularly on mobile devices with constrained CPUs. This is why code splitting and lazy loading JavaScript matters beyond just download size.

**JavaScript blocking behavior.** A `<script>` tag without `defer` or `async` halts HTML parsing entirely while the script downloads and executes. The parser cannot proceed until the script finishes because the script might call `document.write`, which would invalidate already-parsed content. `defer` downloads the script in parallel with parsing and executes it after the DOM is complete. `async` downloads in parallel but executes immediately when ready, interrupting parsing if the download finishes before parsing completes. In Next.js, the framework handles script loading strategy automatically — third-party scripts added via `next/script` accept a `strategy` prop that maps to these behaviors.

The JavaScript language fundamentals — execution context, hoisting, `this` binding, closures, and prototype chain — are covered in the [JavaScript Fundamentals](#javascript-fundamentals) section. The sections below focus on browser-level performance behavior.

**From HTML to pixels.** The DOM and CSSOM are combined into the Render Tree, which contains only visible elements — elements with `display: none` are excluded entirely. The Layout stage (also called Reflow) calculates the exact position and size of every element in the viewport. Paint converts layout instructions into pixels organized into layers. Compositing combines those layers into the final frame the user sees.

**Reflow and Repaint costs.** Reflow is expensive: changing one element's geometry can cascade to affect its siblings, ancestors, and descendants. Repaint is cheaper — it recalculates visual properties like color and shadow without changing layout. The most expensive case is triggering Reflow on every animation frame. CSS `transform` and `opacity` are composited directly on the GPU and skip both Reflow and Repaint entirely — always prefer these for animations over properties like `top`, `left`, `width`, or `margin`.

**Minimizing Reflow and Repaint in practice.** Batch DOM mutations rather than applying them one at a time. Reading a layout property (offsetWidth, getBoundingClientRect) after a write forces the browser to flush pending layout calculations synchronously — this is called layout thrashing. The pattern to avoid is alternating reads and writes in a loop. Group all reads together, then group all writes. Apply style changes via CSS class toggles rather than setting individual inline style properties — class changes are batched and applied in a single recalculation. When building lists or tables dynamically, construct the complete structure off-screen before inserting it into the document in a single operation, rather than appending nodes one by one.

**Lazy Loading and the initial load.** Images and iframes below the initial viewport should load lazily: the browser fetches them only as they approach the viewport. This reduces the number of network requests competing at page load time. LCP candidate images — those visible immediately on load — must never use lazy loading, because deferring them directly delays the metric that most represents perceived load speed.

### FCP Optimization

FCP (First Contentful Paint) measures when the browser first renders any text, image, or SVG — the moment the user gets confirmation that the page is alive. Target ≤ 1.8 seconds. FCP is distinct from LCP: FCP fires on the first piece of content, even a small header; LCP fires when the main content element is ready.

**Render-blocking resources are the primary FCP bottleneck.** The browser cannot render anything until it has processed all CSS that applies to the above-the-fold content, and any synchronous JavaScript that appears before the content in the HTML. Every external stylesheet in the `<head>` is render-blocking by default. Every `<script>` without `defer` or `async` is render-blocking. A page that links five CSS files and three synchronous scripts before any visible content will not paint until all eight files are downloaded and processed.

**Critical CSS.** The technique that directly addresses this is inlining the minimum CSS required to render above-the-fold content directly in the `<head>`. The browser can immediately apply inline styles without a network round-trip. The full stylesheet then loads asynchronously — using `media="print"` with an `onload` handler to switch to `media="all"` is the classic pattern, though Next.js handles this automatically for its built-in CSS pipeline. The discipline is keeping the inlined CSS genuinely minimal: only the styles visible in the initial viewport, nothing more.

**TTFB (Time to First Byte) is the upstream constraint.** FCP cannot be faster than TTFB — the time from request to the first byte of the HTML response. A slow server, unoptimized database queries, or missing edge caching will floor FCP regardless of front-end optimizations. For Next.js on Vercel, static pages served from edge CDN nodes typically achieve TTFB under 50ms globally. Dynamic Server-Rendered pages that hit a database on every request will have TTFB measured in hundreds of milliseconds. Cache static pages where possible; for dynamic pages, ensure the server-side data queries are indexed and fast.

**TTI (Time To Interactive)** is a related Lighthouse metric measuring how long before the page reliably responds to user input — not just painted but fully functional. In the field, INP has largely replaced TTI as the interaction quality signal. The techniques that improve TTI are the same ones that improve INP and bundle size: defer non-critical JavaScript with `defer`, split large bundles with dynamic imports, and avoid long synchronous JavaScript execution during page load. A page can have a fast FCP and LCP but poor TTI if a large JavaScript bundle parses and executes synchronously before the event loop is free to handle user input.

### LCP Optimization Principles

The LCP element is almost always the hero image or the main heading on a page. Identify it explicitly and treat it as a special concern. Images that are LCP candidates must be preloaded — either via the `priority` attribute on the image component or via a preload hint in the document head. They must be sized correctly, served in modern formats (AVIF first, WebP fallback), and their rendered dimensions must closely match the source dimensions. Oversized images that browsers scale down are the most common LCP bottleneck.

Fonts are the second most common LCP bottleneck. Use `next/font` to self-host fonts, which eliminates the external network fetch and allows preloading. The `font-display` descriptor controls what the browser shows while a web font is loading:

- `block` — the browser renders invisible text (FOIT: Flash of Invisible Text) for up to 3 seconds, then falls back to a system font. This is the worst option: the user sees no text at all until the font arrives.
- `swap` — the browser shows a system font immediately (FOUT: Flash of Unstyled Text), then swaps in the web font when it arrives. Text is always visible, though it may reflow when the font swaps. `font-display: swap` is the minimum acceptable setting.
- `optional` — the browser gives the font a very short loading window (100ms); if it does not arrive, the system font is used for the entire session with no swap. This produces zero FOUT and zero layout shift, but requires the font to either be cached or fast enough to arrive within the window. Use `optional` when the visual difference between the web font and the system fallback is small enough to be acceptable.

`next/font` applies `optional` by default, which is why Next.js font loading produces no CLS. If your design depends strongly on a specific web font, use `swap` and define a size-adjusted system font fallback via `font-family` that minimizes the layout shift when the swap occurs.

### CLS Elimination

Layout shift happens when elements move after the page has already rendered. The causes are predictable: images without explicit dimensions, late-loading content that pushes other content down, web fonts causing text reflow, and dynamically injected content above existing content.

Every image must have width and height attributes set. Every skeleton placeholder must match the exact dimensions of the content it replaces. Every font must have a size-adjusted fallback that minimizes reflow. Dynamically injected banners or notification bars must reserve their space in the layout before injecting their content.

### Stacking Context and CSS Containment

A stacking context is the three-dimensional rendering context in which `z-index` values are evaluated. Z-index only controls stacking order relative to elements that share the same stacking context — not globally. An element with `z-index: 9999` inside a stacking context whose parent has `z-index: 1` cannot appear above a sibling element with `z-index: 2` at the parent level, regardless of the child's own z-index value. This is the most common source of z-index bugs.

Properties that create a new stacking context include: any non-`auto` `z-index` combined with a non-`static` position, `opacity` less than 1, `transform`, `filter`, `will-change`, and `isolation: isolate`. The last one — `isolation: isolate` — is the explicit way to create a stacking context without any visual side effect. Use it deliberately on container elements when you need to limit the z-index scope of their children, such as a widget that uses high z-index values internally but should not compete with the application-level modal layer.

**CSS `contain` as a performance hint.** The `contain` property tells the browser that a subtree is independent from the rest of the page. `contain: layout` prevents a subtree's layout changes from triggering document-wide reflow. `contain: paint` creates a new paint layer and clips overflow to the element's border box. `contain: strict` enables all containment modes simultaneously. These hints are appropriate for isolated, self-contained widgets — complex charts, virtualized lists, web components — that should not cause document-wide recalculations when their internal layout changes. Browser support is complete across modern browsers.

### INP Optimization

INP measures the delay from user interaction to visual feedback. Long JavaScript tasks on the main thread are the primary cause of poor INP.

**The Event Loop and why it matters for INP.** JavaScript is single-threaded: only one task runs on the main thread at a time. The call stack holds the execution contexts described earlier — when a function is called, its context is pushed; when it returns, it is popped. Objects referenced by those contexts live in the heap, a separate memory region that the garbage collector manages. The Event Loop's job is to coordinate what gets pushed onto the call stack next.

When the call stack is empty, the Event Loop follows a strict priority cycle: first, it drains the Microtask Queue completely — executing every queued microtask, including any new ones added during that draining pass — before moving on. Only after the Microtask Queue is fully empty does it pick a single task from the Macrotask Queue, push it onto the call stack, and run it. After that task completes, the cycle repeats: drain all microtasks, then pick one macrotask.

**What belongs in each queue** determines execution order in async code:

| Queue | Contains |
|-------|---------|
| Microtask Queue | `Promise.then` / `.catch` / `.finally` callbacks, `queueMicrotask()`, `MutationObserver` callbacks |
| Macrotask Queue | `setTimeout`, `setInterval`, DOM event handlers (click, input, scroll), network response handlers, `requestAnimationFrame` |

**Why the distinction exists.** Microtasks are language-level async — Promise resolution is a JavaScript primitive that should complete before the browser touches anything else. Macrotasks are environment-level async — timers, events, and I/O come from the browser or OS and are allowed to wait until after rendering. This separation gives Promise chains guaranteed immediate-next-tick behavior, which is what makes patterns like `.then().then().then()` predictably sequential.

`requestAnimationFrame` is a macrotask, but the browser schedules it immediately before the next paint — it does not wait in a long queue behind other macrotasks. This makes it the correct tool for visual updates that must sync with the display refresh cycle. Using `setTimeout(fn, 0)` for animations is a common mistake: zero-delay timeouts still wait their turn in the macrotask queue and can fire at unpredictable intervals relative to paint.

A task that runs for more than 50ms is classified as a Long Task — it blocks the browser from processing input events or rendering frames until it finishes. This is the direct mechanical cause of poor INP. A click handler that triggers a 200ms synchronous computation will feel sluggish even if the visual result is correct. The rule is: keep every task short, break long work across multiple tasks using `scheduler.yield()` or chunked `setTimeout`, and push genuinely expensive computation off the main thread using Web Workers.

Break expensive computations off the main thread using Web Workers, which run in a separate thread with no access to the DOM. In React, a Worker is created inside `useEffect`, receives input via `postMessage`, and sends results back via `onmessage` which calls `setState`. The cleanup function calls `worker.terminate()` to prevent the Worker from posting messages to a stale state setter after the component unmounts or the input changes. This is the correct separation: Worker handles the CPU-bound computation; React handles the state update and re-render once the result arrives. The distinction between Workers and `startTransition` is important — Workers are for genuinely parallel CPU computation; `startTransition` is for deprioritizing React's own reconciliation work. Use `startTransition` to mark non-urgent state updates — React yields the main thread between render chunks rather than blocking it for the entire update. Use `useDeferredValue` to keep UI responsive while a derived computation runs as a low-priority background task. Virtualize long lists — rendering thousands of DOM nodes is a continuous main thread cost that compounds until interaction latency becomes perceptible.

**Debounce and throttle for high-frequency events.** Some events fire at very high rates: `resize`, `scroll`, `mousemove`, and `input` can fire dozens of times per second. Running an expensive handler on every firing creates a continuous stream of Long Tasks. Debouncing delays the handler execution until the event stream has been quiet for a specified time — appropriate when only the final value matters (search input that triggers an API call, a resize handler that recalculates layout). Throttling limits handler execution to at most once per specified interval — appropriate when you need periodic updates during a continuous event (scroll position tracking, real-time chart updates). In a React context, debouncing is commonly applied to search inputs to avoid firing a query on every keystroke, and to validation that calls a server endpoint. Use a utility like `lodash.debounce` or implement with `useRef` holding a timeout ID and clearing it on each new invocation. Always cancel pending debounced or throttled callbacks in the cleanup function of `useEffect` to prevent stale executions after component unmount.

### Bundle Size Discipline

Every dependency added to the frontend bundle is a cost paid on every page load. Before adding a package, ask: does this need to run on the client, or can it run on the server? Is there a lighter-weight alternative? Is it tree-shakeable? Use the bundle analyzer to track bundle composition. Set a size budget for the main bundle and treat budget overruns as regressions.

Dynamic imports defer loading a module until it is actually needed. Use dynamic imports for large components that are not visible on initial load — modals, heavy visualizations, editor components. This keeps the initial bundle small and pushes non-critical code to separate chunks that load on demand. `React.lazy` is the React API for this pattern: wrap a dynamic import in `React.lazy`, then render the lazily-loaded component inside a `Suspense` boundary that provides a fallback during the load. The component's JavaScript chunk is only fetched from the network when React first attempts to render that `Suspense` boundary, not at application startup.

### Build Pipeline and Module System

Understanding the build pipeline is prerequisite to reasoning about bundle size, tree-shaking, and development speed. What runs in development and what runs in production are different tools with different goals.

**ESM vs CommonJS.** JavaScript modules come in two formats. CommonJS (CJS) uses `require()` and `module.exports`. It is dynamic — the module graph can only be determined at runtime because `require()` can appear inside `if` statements or function calls. ES Modules (ESM) use `import` and `export`. They are static — the import graph is known at parse time before any code executes. This distinction is the entire reason tree-shaking is possible: a bundler can only eliminate unused exports when it can statically trace what each module exports and what each consumer actually uses. CJS modules cannot be tree-shaken. Any package that ships only CJS will be included in full, regardless of how little of it you use.

**What tree-shaking requires.** For the bundler to eliminate a dead export, three conditions must hold simultaneously: the dependency must be published as ESM (not CJS), your import must use named imports rather than a namespace import (`import { formatDate }` rather than `import * as utils`), and the module must not have side effects — if a module runs code when it is imported (modifying globals, registering event listeners), the bundler cannot safely remove it even if none of its exports are consumed. Package authors signal this with `"sideEffects": false` in `package.json`. Most modern libraries follow this convention; older utilities often do not.

**Vite's development model.** Vite solves slow HMR in large projects by changing the fundamental premise of the dev server. Traditional bundlers (Webpack) rebuild the entire module graph on startup and re-bundle affected chunks on every file change — work that grows linearly with project size. Vite instead serves source files over native ESM directly to the browser, with no bundling step. The browser handles module resolution. When a file changes, only that file is invalidated; the browser re-fetches only the changed module. HMR stays fast regardless of application size because invalidation scope is bounded to what actually changed.

Vite uses esbuild for language transformation — stripping TypeScript types and transforming JSX — because esbuild is written in Go and operates roughly 10–100× faster than Babel for these operations. esbuild does not perform type-checking; that remains a separate step (`tsc --noEmit`).

**Vite's production build.** Vite uses Rollup for production builds rather than serving raw ESM. Browsers cannot efficiently handle thousands of individual module files in production — HTTP/2 parallelism has limits, and the round-trip cost of module resolution across a deep import graph adds up. Rollup bundles and tree-shakes the module graph into optimized output chunks, applies code splitting at dynamic import boundaries, and produces content-hashed filenames for long-term caching. The development and production pipelines use fundamentally different mechanisms — this is by design.

**Next.js and Turbopack.** Next.js has historically used Webpack for both development and production builds. Turbopack (Rust-based) is the long-term replacement, currently stable for development (`next dev --turbo`) with production support in progress. For this stack, Turbopack is an implementation detail managed by Next.js — you get faster dev server HMR without configuration changes. The module system principles remain the same.

**Barrel files and tree-shaking.** A barrel file is an `index.ts` that re-exports from many modules in a directory (`export * from './Button'; export * from './Input'; ...`). They create a convenient import path (`import { Button } from '@/components/ui'`) but collapse module boundaries. When a bundler encounters a barrel re-exporting 50 components and you import one, it must evaluate whether any of the other 49 have side effects before it can eliminate them. In practice, barrel files in `node_modules` (like component libraries) frequently defeat tree-shaking. In application code, barrel files under `features/` are an acceptable convenience if all exports are side-effect-free — but adding a barrel to `shared/components/` that re-exports every component is a reliable way to inflate the bundle.

### Image Handling

All images go through `next/image`, never raw `<img>` tags. This enforces correct sizing attributes (preventing CLS), automatic format negotiation (AVIF/WebP), lazy loading by default for below-the-fold images, and priority loading for LCP candidates. The image component is not optional — it is how images work in this stack.

### HTTP Caching Strategy

HTTP caching is the most effective way to eliminate unnecessary network requests. Every resource served over HTTP can carry cache control headers that instruct browsers and CDN edge nodes how long to store the response and when to revalidate it.

**Cache-Control directives.** The `Cache-Control` response header is the authoritative instruction for caching behavior:

| Directive | Meaning | Typical use |
|-----------|---------|-------------|
| `public, max-age=N` | Cache for N seconds; CDNs and proxies may store it | Static assets with content-hash filenames |
| `private, max-age=N` | Browser cache only; CDNs must not store it | User-specific pages (dashboard, settings) |
| `no-cache` | Cache may store but must revalidate before serving | Frequently updated content where staleness is unacceptable |
| `no-store` | Never cache anywhere | Authentication responses, payment pages, personal data |
| `immutable` | Content will never change; skip revalidation even on reload | Versioned assets whose filename includes a content hash |

**ETag and conditional requests.** When a cached response expires or `no-cache` is set, the browser does not immediately re-download the resource — it first asks whether the content changed. The `ETag` header is a version identifier for the resource: a hash of the file content, a row's updated-at timestamp, or any value that changes when the content changes. On subsequent requests, the browser sends `If-None-Match: <etag-value>`. If the content is unchanged, the server replies `304 Not Modified` with no body — the cache lifetime refreshes without transmitting the resource again. If the content changed, the server replies `200 OK` with new content and a new ETag.

The ETag is regenerated based on the content itself, not the request: the same resource URL requested by different users at different times returns the same ETag if the content has not changed.

**Caching strategy by resource type.** Static assets whose filenames contain a content hash can use `immutable` with a very long max-age — the filename changes whenever the content changes, so the old URL is simply no longer referenced. HTML documents must use `no-cache` or a short max-age because they reference the versioned filenames; if a browser caches an HTML file for too long, users receive old references to assets that no longer exist. API responses with user-specific data use `private` with a max-age matching acceptable staleness. API responses containing sensitive data use `no-store`.

**Memory cache vs disk cache.** The browser maintains two cache layers. Memory cache holds recently used resources in RAM and clears when the tab closes — it produces the "from memory cache" result in DevTools. Disk cache persists across sessions and survives browser restarts. The browser decides placement based on resource type, size, and memory pressure; this is not directly controllable, but understanding it explains why the same resource appears in different cache locations across page reloads.

### Memory Leak Patterns

A memory leak means memory that is no longer needed has not been garbage collected — because a reference to it is still held somewhere. In React, leaks manifest most commonly as components that have unmounted but are still referenced by pending async operations, active intervals, or live subscriptions.

**The three patterns that reliably leak.** Event listeners on `window` or `document` without cleanup, intervals not cleared in cleanup, and WebSocket or observable subscriptions not explicitly closed. Each of these is caught by the `useEffect` cleanup discipline covered in the [Side Effect Lifecycle](#component-design) section — which is precisely why that discipline exists. The consequence of skipping cleanup is not just a React warning: the component's closure (including its state and props) is retained in memory because the live reference prevents garbage collection.

**Retained references in state.** A distinct but related problem: holding large objects in state that are no longer needed — accumulated event logs, replaced fetch results, growing arrays from pagination. This is not a traditional leak (the reference is live, so GC is correct), but it inflates memory in long-running sessions. Clear or null out large state values in `useEffect` cleanup when navigating away from a feature.

**How to identify leaks.** Chrome DevTools Memory tab: take a baseline heap snapshot, navigate away from the suspected component, force a garbage collection, take a second snapshot. Objects that should have been released but appear in the second snapshot are candidates. Filter for "Detached" DOM nodes — nodes removed from the document but still referenced by JavaScript. A React component that remains in the DevTools Components panel after its route is unmounted indicates a reference leak, not just a memory issue.

### React DevTools Profiling Workflow

The React DevTools Profiler is the authoritative tool for diagnosing re-render performance. It records which components rendered, why they rendered, and how long each render took — information that cannot be inferred from reading code.

**The workflow.** Enable profiling in DevTools, reproduce the slow interaction (a filter input that causes jank, a list that takes time to update), then stop recording. The flame chart shows every component that rendered during the interaction with its duration. Components highlighted unexpectedly — rendered when they should not have — are the starting point.

**"Why did this render?" tooltip.** Clicking any component in the Profiler shows the reason: a prop change (which prop), a state change (which hook), or a parent re-render (the component did not bail out). "Re-rendered because parent re-rendered" with no prop or state change is the signal that `React.memo` may be warranted — the child is rendering purely because the parent did, even though nothing it cares about changed.

**The commit timeline.** The bars at the top of the Profiler represent individual commit phases. Tall bars that take tens of milliseconds are Long Task candidates. Click a commit bar to see the component tree as it was during that specific render — identify the root components of expensive commits and trace downward.

---

## Accessibility Standards

### Why It Is Non-Negotiable

Accessibility is both a legal requirement in many jurisdictions and a quality bar that indicates thoughtful engineering. A component that cannot be navigated with a keyboard is broken in the same way that a button that does not respond to clicks is broken. WCAG 2.1 AA compliance is the minimum standard.

### Semantic HTML First

The first question for any UI element is: what is the correct HTML element for this? A button that performs an action is a `<button>`. A link that navigates is an `<a>`. A list of items is a `<ul>` or `<ol>`. Heading levels establish document hierarchy and must be sequential — never skip from `h1` to `h3`. Form inputs must have associated labels — not placeholder text, not adjacent div text, but properly associated labels. Using the right element gives you keyboard behavior, screen reader announcements, and focus management for free.

Using a `<div>` with an `onClick` handler instead of a `<button>` is always wrong. Divs have no implicit role, no keyboard interaction, and no focus behavior. Custom interactive elements require extensive ARIA to match the behavior a correct element provides automatically — and ARIA is difficult to implement correctly. Prefer the right element over ARIA workarounds.

### Keyboard Navigation

Every interactive element must be reachable and operable by keyboard. Tab moves focus forward. Shift-Tab moves it backward. Enter and Space activate buttons. Arrow keys navigate within composite widgets (menus, tabs, radio groups, listboxes). Focus must be visible — the browser's default focus ring is often styled away by CSS resets and must be replaced with a clearly visible alternative.

When a modal opens, focus moves into it. When a modal closes, focus returns to the element that opened it. When a navigation event occurs in a single-page application, focus is placed on the new page's main heading or the top of the main content area. These behaviors do not happen automatically — they require deliberate implementation.

### Color and Contrast

Text must meet WCAG AA contrast ratios: 4.5:1 for body text, 3:1 for large text (18px+ regular or 14px+ bold). Contrast must be checked for all theme variants, including dark mode. Never convey meaning through color alone — error states require both color and an icon or text label.

### ARIA

ARIA attributes supplement semantic HTML — they do not replace it. The rules of ARIA use: prefer no ARIA over incorrect ARIA, prefer native HTML semantics, do not override implicit roles without reason. `aria-label` describes an element when its visual label cannot be associated programmatically. `aria-expanded` and `aria-haspopup` communicate control states. `aria-live` regions announce dynamic content changes to screen readers. `aria-describedby` connects inputs to their error messages. Learn the handful of ARIA patterns that are genuinely necessary and use them correctly.

### Motion and Animation Accessibility

The `prefers-reduced-motion` media query reflects the user's OS-level setting to minimize non-essential motion. Users who enable "Reduce Motion" — typically those with vestibular disorders, migraine sensitivity, or photosensitivity — have indicated that motion-heavy interfaces cause discomfort or harm. Respecting this preference is an accessibility requirement, not a nicety.

In practice: any transition or animation that is not functionally necessary — decorative entry animations, continuous background motion, parallax effects — must be disabled or significantly reduced when `prefers-reduced-motion: reduce` is active. Tailwind provides a `motion-reduce:` variant for this purpose. CSS animations and transitions can be globally reduced in a base stylesheet with a `prefers-reduced-motion: reduce` media query that sets `animation-duration` and `transition-duration` to near-zero. JavaScript-driven animations must check this preference explicitly — Framer Motion's `useReducedMotion()` hook reads the media query and returns a boolean for conditional logic.

Functionally necessary motion — a progress indicator that indicates a task is running, a spinner that communicates loading state — is acceptable even when reduced motion is preferred, because it conveys information the user cannot otherwise perceive. Decorative motion with no informational value is the target for reduction.

---

## Authentication & Security

### Network Fundamentals

A senior frontend developer does not need to implement network protocols, but must understand them well enough to diagnose performance problems, interpret browser DevTools correctly, and make informed decisions about connection management and API design.

**The TCP/IP model and why layers matter.** Internet communication is organized into four layers, each with a distinct responsibility:

| Layer | Responsibility | Protocols |
|-------|---------------|-----------|
| Application | Define service-level rules and message format | HTTP, HTTPS, DNS, WebSocket |
| Transport | Reliable delivery, ordering, flow control | TCP, UDP |
| Internet | Routing packets to the correct destination | IP, ARP, ICMP |
| Link | Physical transmission over the local network | Ethernet, Wi-Fi |

The layered design means each layer is independently replaceable. Switching from HTTP/1.1 to HTTP/2 happens at the Application layer without changing TCP below it. Switching from TCP to QUIC (as HTTP/3 does) changes the Transport layer without touching the Application layer. Understanding which layer a problem belongs to narrows the debugging surface significantly.

**TCP vs UDP: the reliability tradeoff.** TCP guarantees that every byte arrives in order and intact, by numbering packets, requiring acknowledgment of receipt, and retransmitting lost ones. This reliability has a cost: the TCP three-way handshake (SYN → SYN-ACK → ACK) adds a round-trip before any data can flow, and TCP slow start means throughput ramps up gradually on new connections rather than using full bandwidth immediately. UDP delivers packets with no ordering or reliability guarantees, which makes it unsuitable for most web APIs but ideal where low latency matters more than completeness — video calls, games, and DNS queries.

The frontend implication is concrete: every new HTTPS connection costs at least two round-trips before the first byte of application data arrives — one for the TCP handshake, one for the TLS handshake. Reusing connections (HTTP keep-alive, connection pooling) and multiplexing multiple requests over one connection (HTTP/2, HTTP/3) directly reduce this overhead. When diagnosing slow API response times in DevTools, always check the "Timing" breakdown to distinguish DNS resolution, TCP connection, TLS negotiation, and actual server response time.

**Packets, not streams.** Data travels in discrete packets, not as a continuous stream. A large HTTP response is split into many packets, each potentially taking a different network path, arriving out of order, and reassembled by TCP at the destination. This explains why streaming (sending data as it is generated rather than buffering until complete) produces a better user experience: the browser renders the first packets while the rest are still in transit.

**DNS resolution: the first step of every connection.** Before a TCP connection can begin, the browser must resolve the domain name to an IP address. This resolution follows a hierarchical chain: browser DNS cache → operating system DNS cache → local router → ISP resolver → root DNS servers → TLD (top-level domain) nameservers → the authoritative nameserver that holds the actual record. Each uncached step requires a network round-trip. Most lookups are served from the ISP resolver's cache, but a cold lookup for a domain the user has never visited can add 100–500ms of latency before the first TCP packet is sent. HSTS ensures the browser uses HTTPS directly without an HTTP redirect, but the DNS lookup itself is unavoidable.

**Frontend performance implications.** Understanding the network stack reframes several performance decisions:

- DNS resolution adds latency before the TCP handshake can even begin. `dns-prefetch` and `preconnect` resource hints instruct the browser to resolve DNS and establish TCP/TLS connections for anticipated origins during idle time, before those resources are requested.
- CDNs reduce latency not by making servers faster, but by placing servers physically closer to users, shortening the physical distance packets must travel and reducing the number of routing hops.
- HTTP/2 multiplexes multiple requests over a single TCP connection, eliminating the per-request connection overhead. HTTP/3 moves to QUIC (UDP-based), which removes TCP's head-of-line blocking entirely — a lost packet stalls only the stream it belongs to, not all requests sharing the connection.
- TCP slow start means the first request on a new connection is intentionally slower while the protocol probes available bandwidth. Connection reuse is therefore not just a nicety — it directly determines whether subsequent requests benefit from already-warmed connections.

### Transport Security and TLS

HTTPS is not just about encrypting data — it provides three distinct guarantees that every frontend developer must understand: confidentiality (data cannot be read in transit), integrity (data cannot be modified in transit), and authentication (the server is who it claims to be). Each guarantee is enforced by a different mechanism within TLS.

**How the TLS handshake establishes trust.** Before any application data is exchanged, the client and server perform a handshake to agree on an encryption method and establish a shared secret. The server presents a certificate signed by a Certificate Authority (CA). The client verifies this certificate against the CAs it trusts, confirming the server's identity. If verification fails, the browser blocks the connection entirely — this is the first line of defense against man-in-the-middle attacks.

**Why the handshake uses two types of encryption.** Asymmetric encryption (public/private key pairs) is secure but computationally expensive. Symmetric encryption (a single shared key) is fast but requires both parties to already share the key securely. TLS combines both: it uses asymmetric encryption during the handshake to safely exchange a pre-master secret, then derives a symmetric session key from it. All subsequent data is encrypted with this session key. This is why TLS connections have a small upfront cost but fast ongoing throughput.

**What this means for frontend decisions.** Several common frontend mistakes become obviously wrong once the TLS model is understood. Mixed content — loading HTTP resources (scripts, images, fonts) on an HTTPS page — breaks the confidentiality and integrity guarantees because those resources travel unencrypted and unverified. Browsers block or warn on mixed content; treat any mixed content warning as a blocking issue. API calls from the frontend must always use HTTPS endpoints, including in development against local or staging servers. Self-signed certificates in development environments are acceptable only when the implications are understood.

**HSTS (HTTP Strict Transport Security).** HSTS instructs browsers to always use HTTPS for a domain, even if the user types a plain HTTP URL. Once a browser receives an HSTS header, it will refuse HTTP connections to that domain for the specified duration and will not allow users to bypass certificate errors. Set `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` in your response headers. This eliminates the window of vulnerability on the first connection before HSTS is established — but commit to it only when you are certain HTTPS is stable, because HSTS cannot be easily undone within its max-age window.

**Certificate validation is automatic but not unconditional.** The browser validates the server's certificate against trusted CAs automatically. Your responsibility as a frontend developer is to not disable or bypass certificate validation in tooling, to keep dependencies updated so known compromised CA roots are removed promptly, and to monitor certificate expiry. A production certificate that expires silently takes down the application for all users simultaneously.

### Supabase Auth as the Foundation

Supabase Auth handles email/password, magic links, OAuth providers, and session management. The `@supabase/ssr` package is the correct integration for Next.js — it handles cookie-based session storage in a way that works with Server Components, API routes, and middleware. Never use the browser client in Server Components; the server and browser clients are distinct and serve different purposes.

Authentication state propagation in Next.js App Router requires middleware to refresh sessions on every request. Without this, sessions expire silently and users are logged out unexpectedly. The middleware pattern reads the session cookie, refreshes the token if needed, and sets updated cookies before the request reaches any page.

### JWT and Token Security

Supabase Auth issues JWTs internally to represent authenticated sessions. Understanding how JWTs work is not optional — it directly affects storage decisions, session management choices, and the security surface of the application.

**JWT structure.** A JWT is three Base64Url-encoded segments separated by dots: header, payload, and signature. The header declares the token type and signing algorithm. The payload carries claims — structured data about the subject, such as user ID, role, expiry time, and issuer. The signature is computed from the header and payload using a secret key, and it allows any party with the key to verify that the token has not been tampered with. The critical point: Base64Url encoding is not encryption. Anyone who holds a JWT can decode the header and payload and read every claim in plain text. Never include sensitive data — passwords, payment information, personal health data — in a JWT payload.

**Stateless verification.** The server does not need a database lookup to validate a JWT. It verifies the signature using its secret key, checks that the token has not expired, and trusts the claims in the payload. This is why JWTs are efficient at scale: authentication becomes a local cryptographic operation rather than a round-trip to a session store. The trade-off is that claims baked into the token at issue time reflect the state of the world at that moment. If a user's role changes after a JWT is issued, the token continues to carry the old role until it expires.

**The invalidation problem.** Because JWT validation is stateless, there is no built-in revocation mechanism. A token that has been issued is valid until it expires, even if the user logs out, changes their password, or their account is suspended. Two strategies mitigate this: keep access token lifetimes short (15 minutes is common), and use a separate refresh token stored server-side that can be revoked. When a user logs out, invalidate the refresh token — the access token will expire on its own within its short window. Supabase handles this pattern automatically. Do not attempt to build JWT issuance and refresh logic manually on top of Supabase.

**Storage: the XSS vs. CSRF tradeoff.** Where a token lives determines what attacks can steal it.

| Storage | XSS exposure | CSRF exposure | Notes |
|---------|-------------|---------------|-------|
| `localStorage` | High — any script on the page can read it | None — not sent automatically | Readable by injected scripts |
| `sessionStorage` | High — same as localStorage, cleared on tab close | None | Slightly less persistent, same XSS risk |
| HttpOnly cookie | None — JavaScript cannot access it at all | Possible — sent automatically with every request | Mitigated by `SameSite=Strict` or `SameSite=Lax` |

The recommendation is unambiguous for security-sensitive applications: HttpOnly cookies with `Secure` and `SameSite=Lax` (or `Strict`). `SameSite=Lax` blocks the cookie from cross-origin POST requests while allowing top-level navigations (clicking a link). `SameSite=Strict` blocks the cookie on all cross-origin requests, including navigations, which breaks OAuth redirect flows. Supabase's `@supabase/ssr` uses HttpOnly cookies by default — do not override this to use localStorage for convenience.

**When to read JWT claims vs. when to query the database.** JWT claims reflect state at token issue time. For data that changes infrequently and where a brief window of staleness is acceptable — the user's ID, basic role, subscription tier — reading from the token avoids a database round-trip. For data that must be current — whether a specific feature flag is enabled, whether a payment is in good standing, whether an account has been suspended — query the database. Never make security-critical authorization decisions based solely on JWT claims for a long-lived token.

### Web Storage API

The browser's Data Storage layer provides several mechanisms for client-side persistence. Each has a distinct lifetime, scope, and appropriate use case.

**localStorage** persists indefinitely — data survives browser restarts and remains until explicitly cleared or the user purges browser data. All tabs sharing the same origin access the same localStorage namespace. Storage capacity is approximately 5–10MB per origin depending on the browser. Use localStorage for data that should outlive the session: user interface preferences (theme, language, layout density), non-sensitive application state that would be jarring to lose on refresh (a partially expanded sidebar, a column sort order). Do not use localStorage for sensitive data, authentication tokens, or anything that should be cleared on logout — localStorage is synchronous, blocking the main thread, and its contents are fully readable by any JavaScript running on the page, including injected scripts.

**sessionStorage** is scoped to the browser tab and cleared when the tab closes. Unlike localStorage, each tab has its own independent sessionStorage even for the same origin — data written in one tab is not visible in another. Storage capacity is approximately 5MB. Use sessionStorage for state that is meaningful only within the current session: multi-step form data where losing progress on tab close is acceptable, scroll position within a long document, tab-specific UI state that should not bleed across sessions. The tab-isolation property makes sessionStorage useful for scenarios where the same user might have the same application open in multiple tabs with different in-progress states.

**The storage decision hierarchy.** The correct question is not "should I use localStorage or sessionStorage" but "should this data be in client storage at all?"

| Data type | Appropriate storage |
|-----------|-------------------|
| Authentication tokens | HttpOnly cookie (never Web Storage) |
| User preferences (theme, language) | localStorage |
| Multi-step form progress | sessionStorage |
| Server-fetched data (user profile, content) | Apollo cache or React Query — not Web Storage |
| Application state that affects all tabs | Zustand (in-memory) or localStorage with a storage event listener for cross-tab sync |
| Large structured data (offline content, file data) | IndexedDB |

**IndexedDB for complex storage needs.** When localStorage's limitations become apparent — its synchronous API blocks the main thread, its 5–10MB cap is insufficient, it stores only strings — IndexedDB is the appropriate tool. IndexedDB is an asynchronous, transactional, key-value database built into the browser with storage measured in hundreds of megabytes. Use it for offline-capable applications, large dataset caching, and structured data that requires querying. Direct IndexedDB usage is verbose; libraries like `idb` (a small Promise wrapper) or Dexie.js make it practical.

**Storage events for cross-tab synchronization.** When localStorage changes in one tab, the browser fires a `storage` event in all other tabs from the same origin. This allows state that lives in localStorage to stay synchronized across tabs without a server. A common use case is logout synchronization: when the user logs out in one tab (clearing auth state from localStorage), other open tabs listen for the storage event and redirect to the login page. This pattern requires deliberate implementation — it does not happen automatically.

### Protected Routes

Every page or API route that requires authentication enforces it at the earliest possible point. In Next.js App Router, this means a server-side check — either in middleware for broad route groups, or explicitly at the top of a Server Component for individual pages. Client-side authentication checks (a `useEffect` that redirects when no user is found) are insufficient — they cause a flash of protected content before redirect and do not prevent direct API access.

The correct pattern is a `requireUser()` function that reads the session server-side, returns the authenticated user if valid, and redirects to the login page if no session exists. Call this at the top of every protected Server Component before rendering any content. Never render sensitive content before this check completes.

### Row Level Security

Supabase's Row Level Security enforces data access at the database level. A user can only read or write rows where the policy permits. RLS is not optional — it is the last line of defense against data exposure even if application-level authorization has a bug. Every table that contains user-specific data must have RLS enabled and appropriate policies defined. Never disable RLS on a table with sensitive data for convenience or speed.

### Secrets and Environment Variables

The `NEXT_PUBLIC_` prefix makes an environment variable available in the browser bundle — it is visible to anyone who inspects the page source. Never put secrets (API keys, database credentials, signing secrets) in `NEXT_PUBLIC_` variables. Server-side secrets are accessible only in Server Components, API routes, and server-side utility functions. Validate all environment variables at application startup using Zod, so a missing or malformed secret fails immediately at deploy time rather than silently in production.

### Content Security Policy

CSP headers restrict what resources the browser will load and execute on a page. A properly configured CSP prevents cross-site scripting attacks from injected content. Set CSP headers in `next.config.ts` for static headers. At minimum: restrict `script-src` to trusted origins, set `object-src 'none'`, and set `frame-ancestors 'self'`. Test CSP in report-only mode before enforcing to avoid breaking legitimate functionality.

### CORS

CORS (Cross-Origin Resource Sharing) is a browser security mechanism — not a server bug, not a misconfiguration to circumvent. The correct mental model is: CORS is the browser asking the server for permission on the user's behalf. Understanding this model resolves most CORS confusion.

**What "origin" means.** An origin is the combination of three components: scheme (http vs https), host (including subdomains), and port. All three must be identical for two URLs to share an origin. `https://app.example.com` and `https://api.example.com` are different origins despite sharing the same root domain. `http://localhost:3000` and `http://localhost:4000` are different origins despite running on the same machine. This strictness is intentional.

**Why CORS exists and why it is browser-only.** CORS enforces the Same-Origin Policy: a script running on one origin cannot read responses from a different origin unless that origin explicitly permits it. This protects users from malicious pages that silently make requests to other services (a bank, an email provider) using the user's stored credentials. The browser intercepts the response before JavaScript can access it. This is why Postman, `curl`, and server-to-server requests are unaffected by CORS — they run outside the browser's security context and are not protecting user credentials.

**The Preflight mechanism.** The browser splits cross-origin requests into two categories. Simple requests (GET or POST with only basic headers and a limited set of MIME types) are sent directly. Non-simple requests — PUT, DELETE, PATCH, or any request with custom headers like `Authorization` or `Content-Type: application/json` — trigger a Preflight: the browser first sends an OPTIONS request to ask whether the actual request is permitted. The server must respond to this OPTIONS request with the correct CORS headers before the browser sends the real request. A server that ignores OPTIONS requests will break all non-simple cross-origin API calls.

**Required server headers.** A server that receives a cross-origin request must respond with `Access-Control-Allow-Origin` set to the requesting origin (or `*` for public APIs). For Preflight responses, it must also include `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` listing what the actual request is permitted to use. On a FastAPI backend, this is configured via the `CORSMiddleware`. The allowed origins list must be maintained explicitly — never hardcode development URLs into production configuration.

**Credentials require explicit opt-in from both sides.** Sending cookies or Authorization headers in a cross-origin request requires the client to set `credentials: 'include'` (or `withCredentials: true` in axios) and the server to respond with `Access-Control-Allow-Credentials: true`. There is one firm constraint: when credentials are involved, the server cannot use a wildcard (`*`) for `Access-Control-Allow-Origin` — it must specify the exact origin. A wildcard with credentials is rejected by the browser unconditionally.

**The proxy pattern.** A reverse proxy at the same origin as the frontend eliminates CORS entirely for API calls. When the frontend at `https://app.example.com` sends requests to `/api/*` and the web server forwards those to the FastAPI backend at `https://api.example.com`, the browser sees only requests to `app.example.com` — same origin, no CORS check. This is the recommended production architecture for same-domain API routing. Next.js `rewrites` accomplish the same pattern in development: a rewrite rule maps `/api/*` to the backend URL server-side, so browser requests hit Next.js (same origin) and Next.js forwards them to the backend.

**What to check when CORS errors occur.** The browser's error message identifies the missing header. Check the actual response headers in DevTools Network tab — not the error message alone, which is often vague. Confirm whether the request is triggering a Preflight (look for an OPTIONS request immediately before the failing request). Verify that the server's allowed origins list includes the exact requesting origin with the correct scheme and port. Verify that environment-specific backend URLs are correctly configured — a common mistake is configuring CORS for the production domain but forgetting the preview deployment domain.

### CORS vs. CSRF

CORS and CSRF are often confused because both involve cross-origin requests, but they protect against opposite threats. CORS prevents a malicious site from reading responses from another origin using the victim's credentials. CSRF prevents a malicious site from performing state-changing actions on another origin using the victim's credentials — but does not prevent the action from reaching the server, only from the attacker reading the result. A CSRF attack against a form submission does not need to read the response; it only needs the request to execute. CSRF protection requires server-side measures (CSRF tokens, `SameSite` cookie attributes) independent of CORS headers.

### XSS Prevention

Cross-site scripting (XSS) injects malicious scripts into a page that execute in the context of the victim's browser session — with access to cookies, localStorage, the DOM, and the ability to make authenticated requests on the user's behalf. Frontend developers are the last line of defense because the attack surface is the UI layer.

**How React prevents XSS by default.** React's JSX escapes all values before rendering them into the DOM. Any string rendered as a child or attribute value — even one containing `<script>` tags or JavaScript — is treated as text, not markup. This protection covers every standard JSX render path and is why React applications are significantly more resistant to XSS than raw DOM manipulation or template string HTML.

**`dangerouslySetInnerHTML` bypasses this protection entirely.** The prop's name is a deliberate warning: passing `{ __html: someString }` tells React to inject the string as raw HTML, skipping all escaping. If that string contains attacker-controlled content, injected scripts execute. The only safe use of `dangerouslySetInnerHTML` is with content that has been sanitized through a library that removes script tags, event handler attributes, and other executable markup before injection. DOMPurify is the standard choice. Never pass user-submitted content to `dangerouslySetInnerHTML` without sanitization, regardless of how the content was stored or where it originated.

**Third-party content rendering.** Markdown renderers, rich text editors, and HTML email renderers produce raw HTML that gets injected into the DOM. Any component that renders user-provided HTML must sanitize before injection — sanitization must run client-side, not only server-side, because content may arrive through multiple paths and client-side sanitization is the last gate before it reaches the DOM.

**`eval` and dynamic code execution.** `eval`, `new Function(string)`, and `setTimeout(string)` execute strings as code. Never pass user-controlled data to any of these. This class of vulnerability is less common in React applications but appears in template engines, dynamic configuration, and older utility code.

**CSP as defense in depth.** A Content Security Policy header that restricts `script-src` to trusted origins prevents injected scripts from executing even if sanitization fails. CSP does not replace proper escaping and sanitization — it limits the blast radius when they fail. The document's existing CSP section covers header configuration.

---

## AI Feature Development

### Streaming as the Default

AI API responses from OpenAI and Anthropic are streamed — the model generates tokens progressively, and the API can deliver them incrementally rather than waiting for the complete response. Streaming is not an optimization; it is the expected user experience for AI features. A blank screen waiting for a complete response before showing anything is always worse than progressive text appearance. Implement streaming responses from the start, not as a later enhancement.

On the Next.js side, this means using Server Actions or API route handlers that stream responses, and Suspense or manual state management on the client to render the stream progressively. The client shows text as it arrives. Never buffer the entire AI response before showing it.

### Error States and Uncertainty

AI responses can fail, be empty, be cut off mid-sentence, or produce content that requires clarification. Every AI-powered feature must have explicit handling for: request failure (network or API error), rate limiting, empty or very short responses, and responses that the user may want to regenerate. The UI must make it clear when content is AI-generated, when it is loading, and when it has failed. Never present AI output without giving the user the ability to regenerate or dismiss it.

### AI Response UX Patterns

**Progressive disclosure**: Show AI output as it streams. Do not show a spinner until the full response is ready.

**Regeneration**: Always provide a way to regenerate a response. The user's first result is often not what they wanted.

**Copy and use**: Provide explicit actions (copy to clipboard, insert into form, apply changes) rather than requiring users to manually select and copy text.

**Confidence signals**: Where AI output is used to populate structured data or make a recommendation, show the reasoning or source rather than just the conclusion.

**Graceful degradation**: AI features must degrade gracefully when the API is unavailable. If an AI feature augments an existing workflow, the workflow must remain functional without the AI component.

### pgvector and Semantic Search

Semantic search with pgvector works by embedding a search query into a vector and finding database entries whose stored embeddings are nearest to it. The quality of results depends entirely on the embedding model, the content that was embedded, and the similarity threshold. From a frontend perspective, treat semantic search like any other search — but be aware that result relevance may surprise users accustomed to exact keyword matching. Provide feedback mechanisms so users can indicate when results are not useful.

---

## React Native & Cross-Platform

### Shared Logic, Platform-Specific UI

The correct model for a React + React Native codebase is: maximize sharing of business logic, state management, types, and utility functions; accept that UI components are largely separate. Attempting to share UI components between web and native through abstraction layers adds complexity that rarely pays off. The platforms have fundamentally different layout systems, interaction models, and component primitives.

Share across platforms: TypeScript types, Apollo Client configuration and fragments, Zod schemas, business logic utilities (date formatting, currency, validation rules), Zustand stores, and authentication logic.

Keep separate per platform: all UI components, navigation, platform-specific hooks, styling, and assets.

### Navigation Architecture

React Navigation is the standard for React Native. Its APIs — especially for deep linking and typed navigation — require explicit configuration. Define navigation parameter types centrally and share them across all screens that reference them. Deep links from push notifications, email, and web URLs must be handled from cold launch and be testable in isolation.

### Platform-Specific Behavior

Some behaviors diverge fundamentally between platforms: text input behavior, scroll performance, gesture handling, keyboard avoidance, and safe area handling on mobile. Do not try to abstract these into a unified component — write platform-appropriate implementations. Use `.ios.tsx`, `.android.tsx`, and `.native.tsx` file extensions to split implementations cleanly when the divergence is significant.

Performance on React Native is more sensitive than on web because the bridge between JavaScript and native has a cost. Avoid passing large objects across the bridge. Avoid expensive computations in the render path. Virtualize all long lists — rendering thousands of DOM nodes produces visible jank on mobile hardware. Animations must use the native driver; JavaScript-driven animations that cross the bridge produce jank on the main thread.

---

## Testing Philosophy

### The Testing Pyramid

The testing strategy follows a pyramid: many unit tests, fewer integration tests, fewer end-to-end tests. Each layer tests different things and has different costs.

**Unit tests with Vitest** verify isolated logic: utility functions, data transformations, custom hooks (tested via React Testing Library's `renderHook`), Zod schema validation, and business logic modules. These run in milliseconds and provide immediate feedback during development. Every pure function has tests. Every edge case in business logic has a test.

Vitest is fast for two structural reasons. First, it runs on Vite's build pipeline — it reads the same `vite.config.ts` as the application, so TypeScript compilation, path alias resolution (`@/features/...`), and Vite plugins are all applied identically in tests and in the running app. There is no separate Babel or `ts-jest` config to maintain and drift. Second, Vitest is ESM-native: it executes modules directly without a CommonJS transformation step, which eliminates the transpiling overhead that makes Jest slow on ESM-heavy codebases. In watch mode, Vitest uses Vite's module graph to identify exactly which test files are affected by a source change, and re-runs only those — not the entire test suite.

For component tests that require DOM APIs, configure Vitest with `environment: 'jsdom'` in `vite.config.ts`. This gives each test file a simulated browser environment that React Testing Library can render into. Component tests live next to their source files (co-location) and use `@testing-library/user-event` rather than `fireEvent` for interactions — user-event simulates full browser event sequences (pointer events, focus, keyboard) rather than dispatching a single synthetic event.

**Integration tests** verify that components work correctly with realistic data and interactions, without requiring a real browser or a live backend. A form integration test renders the form, fills in values, submits it, and verifies the loading state, success state, and error state all render correctly. Use React Testing Library's user-event API to simulate real user interactions. Mock only what you must: network requests and external services, not internal application code.

**Structure every test with Arrange, Act, Assert.** Every test has three phases. Arrange: set up the preconditions — render the component, initialize state, configure mocks, define the input. Act: trigger the behavior under test — call the function, simulate a user interaction, fire an event. Assert: verify the outcome — check the return value, inspect the DOM, confirm a mock was called with expected arguments. Keeping these phases explicit makes tests readable at a glance: a reader can immediately identify what the test sets up, what it does, and what it verifies. A test that interleaves all three phases throughout its body is hard to reason about and harder to diagnose when it fails.

**End-to-end tests with Playwright** verify complete user flows in a real browser against a real (or staging) environment. These are expensive to write and maintain, so they cover only critical paths: authentication flow, core conversion flow, and the most common user journey. Not every feature needs an e2e test — integration tests cover most scenarios more efficiently.

### Storybook as the Component Contract

Storybook serves two purposes. First, it is the development environment for UI components — build in isolation, see all variants, test edge cases with props, without running the full application. Second, it is living documentation of the design system — every variant, every state, every prop combination is visible and interactive.

Every component in the design system has a Storybook story. At minimum: the default state, a loading state, an empty/no-data state, and an error state. Accessibility testing runs in Storybook using the a11y addon — every story passes automated accessibility checks before the component is considered done.

Stories serve as the specifications that integration tests reference. The same mock data used in stories can power integration tests, keeping the two in sync.

### What Not to Test

Do not test implementation details. An implementation detail is anything the user or consumer of a component does not know about and should not care about: internal state variable names, private helper functions, how exactly child components are structured, or which specific DOM method was called. A test that breaks when you rename an internal variable, extract a helper function, or restructure state — without changing any externally observable behavior — is a fragile test. It creates maintenance overhead without adding confidence. Tests should be written from the perspective of the user: render the component, interact with it the way a real user would (click a button, type in a field), and assert on what the user can observe (text content, visible elements, navigation). If a component shows a count that increments when a button is clicked, test that behavior — not the `useState` variable that holds the count. This principle is why React Testing Library queries by visible text, role, and label rather than by component name or CSS class.

Do not use snapshot tests for UI components — they break on every visual change, including intentional ones, and fail silently when snapshots become stale. Do not test framework behavior (Next.js routing, Apollo caching internals, Supabase auth) — trust the library and test your code.

### MSW (Mock Service Worker)

Mock Service Worker intercepts HTTP requests at the network layer — in the browser via a Service Worker, and in Node.js via `msw/node` for Vitest. Unlike mocking `fetch` or `axios` directly, MSW intercepts at the transport level, which means the application code under test runs without any modification. The actual fetching logic, error handling, and retry behavior are all exercised; only the server's response is controlled.

**The advantage over client-level mocks.** When you mock the fetch client directly, you test whether your component handles the mock correctly — but you do not test whether your component makes the right request in the first place. MSW tests the full request lifecycle: the component fires a fetch, MSW intercepts the request (allowing assertions on its URL, method, and body), and returns a controlled response. This is the closest you can get to testing real network behavior without a running backend.

**Test server setup.** A single MSW server instance is initialized before the test suite, with handlers for the API endpoints that tested components use. Each test can override specific handlers for the scenario it requires — happy path, error response, empty data, timeout simulation. Call `server.resetHandlers()` between tests to ensure isolation. The server's `use()` method adds a one-time handler override for a single test.

**Development workflow.** MSW can also run in the browser during development, serving as a development API before the real backend is ready. The same handler definitions power both development mocking and test mocking, keeping the two in sync. When the real API changes, a single handler update propagates to both.

### Test Coverage Strategy

A coverage percentage can be gamed. 100% line coverage does not mean the code is correct — it means every line was executed during tests, which is achievable without a single meaningful assertion. Coverage numbers are a floor, not a ceiling: they show what was not tested at all, not whether what was tested was tested well.

**What coverage numbers are useful for.** They surface code paths that have never been executed: functions with 0% coverage are candidates for either testing or deletion. Branches that have never taken their false path may hide bugs that only manifest when the condition fails. Use coverage as a signal for where tests are missing — not as the measure of quality.

**Coverage targets by layer.** Unit tests for pure functions should achieve high branch coverage — every logical branch is reachable and should be tested. Integration tests for components cover critical paths and primary error cases; exhaustive branch coverage at the integration level is expensive to maintain. End-to-end tests cover flows, not branches — their coverage numbers are intentionally low.

**The assertion quality problem.** A test that calls every function but only checks `expect(result).toBeDefined()` achieves 100% coverage while verifying almost nothing. Coverage is a proxy for thoroughness, not a substitute for it. When reviewing coverage gaps, ask whether the uncovered path matters — some error branches only execute under conditions that cannot fail in practice. Cover what matters; skip what cannot meaningfully break.

---

## Observability

### Error Tracking with Sentry

Sentry captures unhandled exceptions and promise rejections in production. Every `error.tsx` boundary explicitly captures the error with Sentry before rendering the user-facing error message. Every Server Action catches errors it cannot handle and logs them to Sentry with enough context to reproduce the issue. Never swallow errors silently — log or rethrow.

Error context matters. When capturing an error, include: the user's ID (anonymized if necessary), the route, and any relevant input that caused the failure. An error log with only a stack trace often does not have enough information to diagnose the issue.

### Web Vitals Monitoring

Core Web Vitals must be measured in production, not just in Lighthouse. Lighthouse measures one synthetic run from one machine. Production RUM (Real User Monitoring) shows the actual distribution of user experiences across all devices, network conditions, and geographic locations. The `useReportWebVitals` hook in Next.js fires when CWV data is available — pipe this to your analytics or monitoring service. Alert when p75 metrics degrade from baseline.

### Structured Logging

`console.log` is not a logging strategy. In production, logs need to be searchable, filterable, and parseable. Use a structured logging utility that emits JSON-formatted logs with consistent fields: level, message, timestamp, route, user context, and any relevant data. On Vercel, structured logs appear in the log viewer with filtering capabilities. On self-hosted infrastructure (Koyeb, GCP), structured logs integrate with log aggregation services.

Log at the right level: debug for development-only detail, info for significant events (user created, payment completed), warn for recoverable unexpected states, error for failures that require attention.

---

## Deployment & CI/CD

### Vercel as the Frontend Deployment Platform

Vercel provides automatic preview deployments for every pull request. Every PR has a live, shareable URL at the exact state of that branch. Stakeholders review features before merge. QA runs tests against the real deployment. This eliminates the "works on my machine" class of deployment bugs.

Environment variables are managed per environment in Vercel: development, preview, and production are distinct. Secrets for staging environments must not be the same as production secrets. Preview deployments must not connect to production databases.

Production deployments are triggered by merges to the main branch. The deployment pipeline runs type checking, linting, and the build before deploying. A failed type check or lint error blocks deployment — the pipeline is not advisory.

### GitHub Actions for CI

Every pull request triggers the CI pipeline. The pipeline runs in order: install dependencies, type check, lint, run unit and integration tests, build. Any failure blocks merge. The pipeline must complete in under ten minutes or it becomes a bottleneck that developers route around.

Type checking and linting run in parallel. Tests run in parallel across multiple workers when the test suite grows large. Cache dependencies and Next.js build artifacts between runs — this reduces pipeline time significantly.

The CI pipeline is the canonical definition of "this code works." If something is not verified in CI, it is not reliably enforced.

### FastAPI Backend on Koyeb

The FastAPI backend deploys separately from the Next.js frontend. API changes that affect the frontend must be coordinated — a deployed frontend calling a changed or removed API endpoint is a production incident. Version APIs where breaking changes are necessary. Use generated TypeScript types from the OpenAPI spec to enforce the contract at compile time.

Koyeb deployments trigger on main branch pushes via GitHub Actions. Health checks on the backend must be configured — a deployed but unhealthy backend receiving traffic silently breaks the frontend.

### Web Server Layer

A web server (Nginx, Caddy, Apache) sits between the internet and the application server, handling concerns that the application should not be responsible for. Understanding this layer is essential for debugging production behavior, configuring deployments, and recognizing what Vercel does automatically on the frontend.

**The web server as the first contact point.** Every HTTP request from a browser hits the web server before reaching the application. The web server inspects the request — path, host, headers — and decides what to do with it: serve a static file directly, forward it to an application server, block it, or redirect it. Because it sits in front of everything, the web server is the right place for cross-cutting concerns that apply uniformly across all requests, not just those handled by a specific application route.

**SSL/TLS termination.** The web server handles the TLS handshake and decrypts incoming HTTPS traffic. The application server (FastAPI, Node.js) receives plain HTTP on the internal network, which is simpler and faster. This separation means the application does not need TLS configuration — the web server owns that concern entirely. Certificate renewal, cipher suite selection, and HSTS headers are all configured at the web server, not the application. On Vercel, TLS termination is managed automatically. On Koyeb hosting FastAPI, an Nginx or Caddy layer in front of the application handles this.

**Reverse proxy and path-based routing.** The reverse proxy pattern allows a single domain to front multiple services. A request to `/api/*` can be forwarded to the FastAPI backend, while all other paths serve the Next.js frontend. The browser communicates only with one origin, which eliminates CORS complexity for same-domain API calls. The internal routing is invisible to the client. This architecture also means the application server's address and port are never exposed directly to the internet — the web server is the only public-facing endpoint.

**Static file serving.** The web server serves static files — HTML, CSS, JS, images, fonts — directly from disk, without involving the application server. Serving a static file is an order of magnitude faster than routing a request through an application: no process spawning, no business logic, no database access. For a Next.js deployment on Vercel, the built static assets are served by Vercel's CDN edge nodes, not by a Node.js process. Understanding this separation explains why `.next/static/` assets can have very long cache lifetimes — they are served at the edge, independently of the application.

**Compression.** The web server compresses responses before sending them to the browser. Gzip reduces most text-based assets (HTML, CSS, JS, JSON) to 20–30% of their original size. Brotli achieves better compression ratios than gzip for the same CPU cost. Compression happens once at the network boundary; the application server never sees compressed data, and the browser decompresses transparently. On Vercel, compression is applied automatically. For self-hosted deployments, compression must be configured explicitly at the web server — an uncompressed Next.js bundle is 3–5× larger than a compressed one.

**Load balancing.** When multiple instances of an application server run behind a web server, the load balancer distributes incoming requests across them. This provides both horizontal scalability (handling more traffic by adding instances) and fault tolerance (if one instance fails, others continue serving). The distribution strategy matters: round-robin distributes evenly by default, but sticky sessions (routing the same client to the same instance) are needed for applications that store session state in process memory rather than a shared store like Redis. Applications using Supabase or a shared database for session storage can use stateless load balancing — which is the correct architecture.

**Access control and rate limiting.** The web server can enforce IP-based access restrictions, request rate limits, and bot filtering before requests reach the application. Blocking at the web server layer is cheaper than blocking in application code because the application server never needs to process blocked requests at all. Rate limiting at this layer prevents brute-force attacks on authentication endpoints, API abuse, and DDoS amplification.

**What Vercel provides automatically.** Vercel functions as a fully managed web server, CDN, and load balancer for the Next.js frontend. TLS termination, compression, static file serving at the edge, HTTP/2 and HTTP/3, caching headers, and global load distribution are all handled without any configuration. This is the primary reason Vercel is the right deployment target for Next.js: the infrastructure concerns that require significant Nginx configuration on self-hosted deployments are resolved by the platform. The trade-off is vendor lock-in and cost at scale.

### Next.js Metadata API

The Metadata API is the App Router system for managing document metadata — page titles, meta descriptions, Open Graph tags, Twitter card data, robots directives, and canonical URLs. It replaces the legacy `<Head>` component with a typed, co-located, server-friendly approach. Metadata is critical for SEO and social sharing: a page without correct metadata is poorly ranked in search and renders without preview images or titles when shared.

**Static metadata** is exported as a typed `Metadata` object from any `page.tsx` or `layout.tsx`. This is the correct approach for pages whose metadata does not depend on data — marketing pages, documentation, static landing pages.

**`generateMetadata` for dynamic metadata.** Export an async `generateMetadata` function from any page that needs data-driven titles or descriptions — product pages, blog posts, user profiles, any page whose identity comes from a URL parameter. The function receives the same `params` and `searchParams` as the page component and returns a `Metadata` object. Data fetches inside `generateMetadata` are automatically deduplicated with matching fetches in the page component — you do not pay a second round-trip.

**Layout-level metadata with title templates.** Define a title template in a layout's metadata: `title: { template: '%s | App Name', default: 'App Name' }`. Child pages set only the page-specific portion. The template applies automatically. This ensures every page has the app name in its title without every page repeating it.

**Robots and canonical.** Pages that must not be indexed — admin panels, settings, confirmation pages, auth callbacks — should set `robots: { index: false }`. The canonical URL field prevents duplicate content penalties for pages accessible via multiple URL variants (with/without trailing slash, pagination, filter parameters). Set the canonical explicitly on any page that has URL variants.

---

## Team Standards

### Code Review Principles

Code review is a quality gate, not a style debate. Reviewers check for: correctness (does it do what it claims?), security (are there injection, exposure, or auth issues?), performance (does this degrade CWV or add unnecessary bundle cost?), accessibility (does this meet the baseline standard?), and testability (can this be verified?). Style issues are handled by linters and formatters — they do not belong in code review comments.

Every review comment should be actionable. "This could be better" is not actionable. "This pattern leaks server state to the client — consider moving the query to a Server Component" is actionable. Non-blocking suggestions must be labeled as such.

### Pull Request Structure

A PR is easier to review when it is focused. One PR per logical change: one feature, one bugfix, one refactor. PR description includes: what changed, why it changed, how to test it manually, and a link to the relevant ticket or design. Screenshots or video for UI changes.

Breaking changes — API changes, schema migrations, removed exports — are flagged explicitly in the PR description and coordinated with consuming systems before merge.

### Branch Strategy

`main` is always deployable. Feature branches are created from `main` and merged back via PR. Long-lived feature branches diverge and become painful to merge — keep branches short-lived and merge frequently. If a feature is large, use feature flags to merge incomplete work to main without exposing it to users.

### Documentation Standards

Comments in code explain why, not what. What the code does is readable from the code itself. Why — the constraint it was written to satisfy, the edge case it handles, the non-obvious invariant it depends on — is not visible from the code and belongs in a comment. Every non-obvious architectural decision belongs in an ADR. These do not need to be formal — a markdown file with "We chose X over Y because of Z constraint" is sufficient.

---

## Quick Reference Checklist

**Before starting a feature:**
- [ ] Rendering strategy decided (static / dynamic / streaming)
- [ ] State ownership decided (server / URL / client / global)
- [ ] Data fetching strategy decided (Apollo query / Supabase client / RSC fetch / subscription)
- [ ] Form approach decided (useActionState / react-hook-form)
- [ ] Auth requirements identified (public / authenticated / role-specific)
- [ ] Accessibility requirements reviewed with design (including motion)
- [ ] Page metadata planned (title, description, og:image, robots) for new routes

**During implementation:**
- [ ] Server Components used by default; `'use client'` only at leaf nodes
- [ ] All external data (API responses, URL params, env vars) validated with Zod at the boundary
- [ ] No `any` types without justification comment; generics used for reusable abstractions
- [ ] Images through `next/image` with explicit dimensions
- [ ] Semantic HTML elements used correctly; no `div onClick`
- [ ] Keyboard navigation implemented and tested manually
- [ ] Loading, error, and empty states handled for every async view
- [ ] Form errors shown at both field level and form level
- [ ] Submit button shows pending state; duplicate submission prevented
- [ ] Animations respect `prefers-reduced-motion` (`motion-reduce:` variant or JS check)
- [ ] `dangerouslySetInnerHTML` — only with sanitized content (DOMPurify); never raw user input
- [ ] Supabase `{ data, error }` — error checked before accessing data
- [ ] useEffect cleanup returns cleanup function for all subscriptions, listeners, intervals

**Before opening a PR:**
- [ ] Type check passes with no errors
- [ ] Linting passes with no warnings
- [ ] Unit tests written for new logic
- [ ] Integration test covers the critical path
- [ ] Storybook story added for new components (a11y addon passes)
- [ ] LCP element identified and optimized if applicable
- [ ] No layout shift introduced (images have explicit dimensions, skeletons match content)
- [ ] No secrets in `NEXT_PUBLIC_` variables
- [ ] No `console.log` left in production code
- [ ] Sentry error capture added to new error boundaries
- [ ] Page metadata exported from new route segments

**Before merge:**
- [ ] CI pipeline passes
- [ ] Preview deployment tested on mobile viewport
- [ ] Accessibility tested with keyboard navigation
- [ ] API changes coordinated with backend if applicable
- [ ] Supabase realtime channels removed on unmount if subscriptions added
