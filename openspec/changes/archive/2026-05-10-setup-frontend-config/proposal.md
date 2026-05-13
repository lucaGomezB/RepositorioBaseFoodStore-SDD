# Proposal: setup-frontend-config

## Why

The frontend scaffolding exists (setup-monorepo-base), but there's no actual configuration. We need React with TypeScript, Vite, Tailwind CSS, and TanStack Query properly configured before any frontend feature development can start.

## What Changes

1. **Package.json setup** — Add React 18, TypeScript, Vite, and core dependencies
2. **TypeScript configuration** — Configure tsconfig.json with strict mode
3. **Vite configuration** — Set up vite.config.ts with React plugin and aliases
4. **Tailwind CSS** — Configure tailwind.config.js and PostCSS
5. **TanStack Query** — Set up React Query provider for data fetching
6. **Project structure** — Ensure FSD structure is properly wired (app, pages, features, entities, shared)
7. **Hot reload** — Verify `npm run dev` works with hot reload

## Capabilities

### New Capabilities

- **frontend-react-setup**: React 18 with TypeScript and Vite configuration
- **frontend-styling**: Tailwind CSS with PostCSS setup
- **frontend-data-fetching**: TanStack Query provider and basic configuration

### Modified Capabilities

- (none) — This is foundational, no existing specs to modify

## Impact

- **Files created/modified**: package.json, tsconfig.json, vite.config.ts, tailwind.config.js, postcss.config.js, index.html
- **Dependencies added**: react, react-dom, typescript, vite, @vitejs/plugin-react, tailwindcss, postcss, autoprefixer, @tanstack/react-query
- **Breaking changes**: None — this is new infrastructure
- **Requires**: Node.js 18+ running