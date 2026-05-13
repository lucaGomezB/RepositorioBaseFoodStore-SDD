# Spec: frontend-data-fetching

## Overview

This spec defines the TanStack Query (React Query) setup for server state management and data fetching.

## ADDED Requirements

### Requirement: TanStack Query installed

The system SHALL have TanStack Query installed as a dependency.

#### Scenario: Package has @tanstack/react-query
- **GIVEN** the frontend directory
- **WHEN** reading package.json
- **THEN** it includes "@tanstack/react-query": "^5.x.x"

---

### Requirement: QueryClientProvider configured

The system SHALL wrap the application with QueryClientProvider.

#### Scenario: App has QueryClientProvider
- **GIVEN** the app/App.tsx or index.tsx
- **WHEN** reading the component tree
- **THEN** it wraps the app with QueryClientProvider

#### Scenario: QueryClient is configured
- **GIVEN** the app has QueryClientProvider
- **WHEN** checking the configuration
- **THEN** it creates a QueryClient with default options

---

### Requirement: Query client can be used in components

The system SHALL allow components to use useQuery and useMutation hooks.

#### Scenario: useQuery is available
- **GIVEN** TanStack Query is configured
- **WHEN** importing from @tanstack/react-query
- **THEN** useQuery and useMutation are importable

#### Scenario: Provider is accessible
- **GIVEN** a component uses useQuery
- **WHEN** the component renders
- **THEN** it receives a valid QueryClient from context