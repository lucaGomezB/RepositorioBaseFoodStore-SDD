## ADDED Requirements

### Requirement: Backend MUST have coverage reporting
The project SHALL use pytest-cov to generate coverage reports. Minimum coverage threshold SHALL be 70%.

#### Scenario: Coverage report generates
- **WHEN** running `pytest --cov=app --cov-report=term --cov-report=html`
- **THEN** a coverage report SHALL be displayed in terminal
- **THEN** an HTML report SHALL be generated in htmlcov/

#### Scenario: Coverage threshold enforced
- **WHEN** running `pytest --cov=app --cov-fail-under=70`
- **THEN** the command SHALL fail if coverage is below 70%

### Requirement: Frontend MUST have coverage reporting
The project SHALL configure Vitest with coverage via v8/istanbul.

#### Scenario: Frontend coverage report generates
- **WHEN** running `npx vitest --coverage`
- **THEN** a coverage report SHALL be generated
