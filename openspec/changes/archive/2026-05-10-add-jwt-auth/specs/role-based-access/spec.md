# Spec: role-based-access

## Overview

This spec defines role-based access control for endpoints.

## ADDED Requirements

### Requirement: Public endpoints require no auth

The system SHALL allow access to certain endpoints without authentication.

#### Scenario: Public endpoint accessible
- **WHEN** accessing GET /api/v1/productos (public read)
- **THEN** request proceeds without token

### Requirement: Admin endpoints require admin role

The system SHALL restrict certain endpoints to admin users only.

#### Scenario: Admin can access protected endpoint
- **WHEN** admin user accesses POST /api/v1/productos
- **THEN** request proceeds

#### Scenario: Customer blocked from admin endpoint
- **WHEN** customer user accesses POST /api/v1/productos
- **THEN** request returns 403 Forbidden

### Requirement: User can only access own data

The system SHALL restrict users to access only their own resources.

#### Scenario: User accesses own profile
- **WHEN** user accesses GET /api/v1/users/me
- **THEN** request proceeds

#### Scenario: User blocked from other user data
- **WHEN** user accesses GET /api/v1/users/123 (not their own)
- **THEN** request returns 403 Forbidden

### Requirement: Roles defined

The system SHALL define the following roles:
- **Admin** (rol_id 1-2): Full access to all resources
- **Employee** (rol_id 3): Limited management access
- **Customer** (rol_id 4): Own data only
- **Guest** (rol_id 5): Public read-only access