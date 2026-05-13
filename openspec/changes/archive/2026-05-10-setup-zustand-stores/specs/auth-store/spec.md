# Spec: auth-store

## Overview

Hybrid auth store that holds state but delegates API logic to React Query.

## ADDED Requirements

### Requirement: Store holds authentication state

The system SHALL provide an auth store with token, user, and login status.

#### Scenario: Initial state on app load
- **WHEN** app loads and user has valid stored token
- **THEN** authStore.token is populated, isLoggedIn is true

#### Scenario: No stored token
- **WHEN** app loads and no token in localStorage
- **THEN** authStore.token is null, isLoggedIn is false

### Requirement: Auth state can be set programmatically

The system SHALL allow setting auth state from external source (React Query).

#### Scenario: Inject login result into store
- **WHEN** React Query mutation returns { access_token, refresh_token, user }
- **THEN** store.setAuth() is called with these values
- **AND** token is persisted to localStorage

#### Scenario: Logout clears all auth state
- **WHEN** store.logout() is called
- **THEN** token, refreshToken, user are all set to null
- **AND** localStorage is cleared

### Requirement: User can be updated

The system SHALL allow updating user data in the store.

#### Scenario: Update user profile in store
- **WHEN** store.updateUser(newUserData) is called
- **AND** user object in store is replaced with new data