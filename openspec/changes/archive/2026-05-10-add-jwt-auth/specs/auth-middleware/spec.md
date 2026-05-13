# Spec: auth-middleware

## Overview

This spec defines FastAPI dependencies for route protection.

## ADDED Requirements

### Requirement: get_current_user dependency

The system SHALL provide a dependency that extracts and validates the current user from the JWT.

#### Scenario: Valid token provides user
- **WHEN** request has valid JWT in Authorization header
- **THEN** dependency returns the user object

#### Scenario: Missing token returns 401
- **WHEN** request has no Authorization header
- **THEN** dependency raises 401 Unauthorized

#### Scenario: Invalid token returns 401
- **WHEN** request has malformed or invalid JWT
- **THEN** dependency raises 401 Unauthorized

### Requirement: require_admin dependency

The system SHALL provide a dependency that verifies the user has admin role.

#### Scenario: Admin user passes
- **WHEN** get_current_user returns an admin (rol_id <= 2)
- **THEN** request proceeds

#### Scenario: Non-admin user blocked
- **WHEN** get_current_user returns a customer (rol_id > 2)
- **THEN** dependency raises 403 Forbidden

### Requirement: get_current_active_user dependency

The system SHALL provide a dependency that also verifies the user is active.

#### Scenario: Active user passes
- **WHEN** user exists and activo=True
- **THEN** request proceeds

#### Scenario: Inactive user blocked
- **WHEN** user exists but activo=False
- **THEN** dependency raises 403 Forbidden