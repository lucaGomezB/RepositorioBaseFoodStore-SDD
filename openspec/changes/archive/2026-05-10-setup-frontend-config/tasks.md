# Tasks: setup-frontend-config

## 1. Dependencies

- [x] 1.1 Update frontend/package.json with all dependencies (react, react-dom, typescript, vite, @vitejs/plugin-react, tailwindcss, postcss, autoprefixer, @tanstack/react-query)
- [x] 1.2 Run `npm install` to install dependencies

## 2. TypeScript Configuration

- [x] 2.1 Update frontend/tsconfig.json with strict: true
- [x] 2.2 Configure path aliases: "@/*" -> "src/*"
- [x] 2.3 Add jsx setting: "react-jsx"
- [x] 2.4 Test: `npx tsc --noEmit` runs without errors

## 3. Vite Configuration

- [x] 3.1 Update frontend/vite.config.ts with React plugin
- [x] 3.2 Configure resolve alias: "@" -> "./src"
- [x] 3.3 Configure server port: 5173
- [x] 3.4 Test: `npx vite --version` works

## 4. Tailwind CSS Setup

- [x] 4.1 Configure Tailwind in vite.config.ts with postcss
- [x] 4.2 Configure content paths for Tailwind
- [x] 4.3 Create frontend/src/index.css with Tailwind directives
- [x] 4.4 Test: Build produces CSS without errors

## 5. TanStack Query Setup

- [x] 5.1 Create frontend/src/app/providers.tsx with QueryClientProvider
- [x] 5.2 Configure QueryClient with default options
- [x] 5.3 Update frontend/src/App.tsx to use the provider
- [x] 5.4 Test: useQuery hook is importable

## 6. Entry Point Configuration

- [x] 6.1 Update frontend/index.html with proper root div
- [x] 6.2 Update frontend/src/index.tsx to render App
- [x] 6.3 Ensure CSS is imported in index.tsx

## 7. Verify Development Server

- [x] 7.1 Run `npm run dev` and verify server starts
- [x] 7.2 Verify http://localhost:5173 loads
- [ ] 7.3 Verify hot reload works (modify App.tsx, save, check browser)

## 8. Build Verification

- [x] 8.1 Run `npm run build`
- [x] 8.2 Verify dist/ directory is created
- [x] 8.3 Verify no TypeScript errors in build

## 9. Git Commit

- [x] 9.1 Add files: `git add frontend/package.json frontend/tsconfig.json frontend/vite.config.ts frontend/src/`
- [x] 9.2 Commit: `git commit -m "feat: setup frontend config (React, Vite, Tailwind, TanStack Query)"`

## Summary

All tasks should result in:
- React 18 with TypeScript (strict mode) configured
- Vite dev server with hot reload working at localhost:5173
- Tailwind CSS configured and working
- TanStack Query provider wrapping the app
- `npm run build` produces a production build