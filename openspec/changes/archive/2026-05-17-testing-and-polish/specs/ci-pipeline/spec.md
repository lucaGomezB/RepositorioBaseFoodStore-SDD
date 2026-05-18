## ADDED Requirements

### Requirement: Pre-commit hooks MUST be configured
The project SHALL have pre-commit hooks that run ruff linting and TypeScript type checking before each commit.

#### Scenario: Ruff lint runs on commit
- **WHEN** running `git commit`
- **THEN** ruff SHALL lint all staged Python files
- **THEN** the commit SHALL be blocked if linting fails

#### Scenario: TypeScript type check runs on commit
- **WHEN** running `git commit`
- **THEN** tsc --noEmit SHALL check all TypeScript files
- **THEN** the commit SHALL be blocked if type checking fails

### Requirement: .env.example MUST be complete
The .env.example file SHALL document all environment variables used by the project, with descriptions and example values.

#### Scenario: All env vars documented
- **WHEN** inspecting .env.example
- **THEN** every variable from backend/app/core/config.py and frontend env SHALL be listed with a description and default value
