# Design: setup-frontend-config

## Context

The frontend scaffolding exists from setup-monorepo-base with:
- Empty directory structure (app, pages, features, entities, shared)
- Placeholder files (App.tsx, index.tsx, etc.)
- No dependencies installed
- No actual configuration

This change adds the proper configuration for React, TypeScript, Vite, Tailwind, and TanStack Query.

## Goals / Non-Goals

**Goals:**
- Configure React 18 with TypeScript (strict mode)
- Set up Vite with React plugin and path aliases
- Configure Tailwind CSS with PostCSS
- Set up TanStack Query provider
- Verify `npm run dev` works with hot reload

**Non-Goals:**
- Feature components — handled in later changes
- Routing setup — handled in frontend-auth-guards
- State management (Zustand) — handled in setup-zustand-stores

## Decisions

### 1. Vite over Create React App
**Decision**: Use Vite as the build tool.
**Rationale**: Faster dev server, instant hot module replacement (HMR), better production build times.
**Alternative considered**: CRA — deprecated, slower, no Vite features.

### 2. Tailwind CSS for styling
**Decision**: Use Tailwind CSS for utility-first styling.
**Rationale**: Rapid development, small bundle size (tree-shaking), consistent design system.
**Alternative considered**: CSS Modules — more boilerplate, less consistent.

### 3. TanStack Query for server state
**Decision**: Use TanStack Query (React Query) for data fetching.
**Rationale**: Industry standard, caching, optimistic updates, loading states built-in.
**Alternative considered**: SWR — similar features, TanStack has better TypeScript support.

### 4. TypeScript strict mode
**Decision**: Enable strict TypeScript configuration.
**Rationale**: Catches bugs at compile time, better IDE support, required by project spec.
**Alternative considered**: Loose TS config — increases runtime errors.

### 5. Path aliases
**Decision**: Configure @ alias for cleaner imports.
**Rationale**: Avoids `../../../` chains, easier refactoring.
**Alternative considered**: Relative imports — harder to maintain.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-------------|
| Node version mismatch | App fails to run | Document Node 18+ requirement |
| Tailwind not processing | Styles not applied | Verify postcss.config.js correct |
| Hot reload not working | Slow development | Test vite --host works |

## Migration Plan

1. Update package.json with all dependencies
2. Run `npm install` to install dependencies
3. Configure tsconfig.json with strict mode and paths
4. Configure vite.config.ts with React plugin
5. Configure tailwind.config.js and postcss.config.js
6. Update index.html with proper root element
7. Run `npm run dev` and verify hot reload works

## Open Questions

- Should we use JavaScript or TypeScript?
  - **Current decision**: TypeScript (required by project spec)
- Should we include eslint/prettier in this change?
  - **Current decision**: Not in this change — add later if needed