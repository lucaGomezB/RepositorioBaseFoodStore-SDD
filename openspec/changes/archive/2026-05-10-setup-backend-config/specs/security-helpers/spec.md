# Spec: security-helpers

## Overview

This spec defines the basic security helper utilities including password hashing and JWT configuration structures.

## ADDED Requirements

### Requirement: Password hashing utilities available

The system SHALL provide password hashing functionality using bcrypt.

#### Scenario: Hash function exists
- **GIVEN** the security module is imported
- **WHEN** calling `hash_password("mypassword")`
- **THEN** a bcrypt hash string is returned
- **AND** the hash is different each time (salt is random)

#### Scenario: Verify function works
- **GIVEN** a password and its hash
- **WHEN** calling `verify_password("mypassword", hash)`
- **THEN** True is returned

#### Scenario: Verify returns False for wrong password
- **GIVEN** a password and its hash
- **WHEN** calling `verify_password("wrongpassword", hash)`
- **THEN** False is returned

---

### Requirement: JWT configuration exists

The system SHALL provide JWT configuration structures.

#### Scenario: JWT settings can be imported
- **GIVEN** the security module is imported
- **WHEN** accessing JWT configuration
- **THEN** settings include: SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

#### Scenario: JWT config uses environment variables
- **GIVEN** environment variables are set for JWT
- **WHEN** the security module is loaded
- **THEN** the configuration values come from the environment

---

### Requirement: Security module is modular

The system SHALL keep security utilities separate from business logic.

#### Scenario: Security module exists independently
- **GIVEN** the app/core/ directory exists
- **WHEN** checking for security.py
- **THEN** the file exists and can be imported independently

#### Scenario: No security logic in main.py
- **GIVEN** the app/main.py file
- **WHEN** reading its contents
- **THEN** it does not contain password hashing or JWT creation logic
- **AND** security utilities are imported from app.core.security