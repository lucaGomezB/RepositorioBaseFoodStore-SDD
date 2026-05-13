# Spec: jwt-authentication

## Overview

This spec defines JWT token generation, validation, and refresh logic.

## ADDED Requirements

### Requirement: User can login with email/password

The system SHALL validate credentials and return JWT tokens on successful login.

#### Scenario: Successful login
- **WHEN** user sends POST /api/v1/auth/login with valid email and password
- **THEN** system returns access_token and refresh_token

#### Scenario: Invalid credentials
- **WHEN** user sends POST /api/v1/auth/login with wrong password
- **THEN** system returns 401 Unauthorized

### Requirement: Access token has expiration

The system SHALL generate access tokens that expire after 15 minutes.

#### Scenario: Expired access token
- **WHEN** using an expired access token
- **THEN** system returns 401 with "token expired" message

### Requirement: Refresh token provides new access token

The system SHALL allow exchanging a valid refresh token for a new access token.

#### Scenario: Refresh access token
- **WHEN** sending POST /api/v1/auth/refresh with valid refresh_token
- **THEN** system returns new access_token

#### Scenario: Invalid refresh token
- **WHEN** sending POST /api/v1/auth/refresh with invalid/expired refresh_token
- **THEN** system returns 401 Unauthorized

### Requirement: User can logout

The system SHALL invalidate the refresh token on logout.

#### Scenario: Logout invalidates token
- **WHEN** user sends POST /api/v1/auth/logout with valid refresh_token
- **THEN** refresh_token is deleted from database

### Requirement: Tokens contain user info

The system SHALL include user_id and role in JWT payload.

#### Scenario: Token payload
- **WHEN** decoding access token
- **THEN** payload contains user_id, email, rol_id, and exp