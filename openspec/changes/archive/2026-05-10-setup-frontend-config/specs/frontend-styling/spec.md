# Spec: frontend-styling

## Overview

This spec defines the Tailwind CSS configuration for utility-first styling.

## ADDED Requirements

### Requirement: Tailwind CSS configured

The system SHALL have Tailwind CSS properly configured.

#### Scenario: tailwind.config.js exists
- **GIVEN** the frontend directory
- **WHEN** checking for tailwind.config.js
- **THEN** the file exists and is valid JavaScript

#### Scenario: Tailwind includes src files
- **GIVEN** tailwind.config.js
- **WHEN** reading the content
- **THEN** content includes "./src/**/*.{js,ts,jsx,tsx}"

#### Scenario: PostCSS configured
- **GIVEN** the frontend directory
- **WHEN** checking for postcss.config.js
- **THEN** the file exists with tailwindcss and autoprefixer plugins

---

### Requirement: Global styles use Tailwind

The system SHALL have Tailwind directives in the global CSS.

#### Scenario: index.css has Tailwind directives
- **GIVEN** the frontend/src directory
- **WHEN** checking for index.css or globals.css
- **THEN** it contains @tailwind base, @tailwind components, @tailwind utilities

#### Scenario: Tailwind is imported in app
- **GIVEN** the app entry point
- **WHEN** checking imports
- **THEN** it imports the CSS file with Tailwind directives

---

### Requirement: Styles build correctly

The system SHALL compile Tailwind styles without errors.

#### Scenario: npm run build succeeds
- **GIVEN** dependencies are installed
- **WHEN** running `npm run build`
- **THEN** it completes without errors
- **AND** produces a dist directory with CSS