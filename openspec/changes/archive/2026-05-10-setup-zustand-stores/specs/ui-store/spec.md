# Spec: ui-store

## Overview

Simple state-only UI store for theme, sidebar, modals, and notifications.

## ADDED Requirements

### Requirement: Theme can be toggled

The system SHALL allow switching between light and dark themes.

#### Scenario: Toggle theme
- **WHEN** toggleTheme() is called while in light mode
- **THEN** theme switches to dark
- **AND** persists to localStorage

### Requirement: Sidebar can be toggled

The system SHALL allow opening/closing the sidebar.

#### Scenario: Sidebar toggle
- **WHEN** toggleSidebar() is called
- **THEN** sidebarOpen state inverts (open→closed, closed→open)

### Requirement: Modal management

The system SHALL allow opening and closing modals.

#### Scenario: Open modal
- **WHEN** openModal('product-detail') is called
- **AND** activeModal is set to 'product-detail'

#### Scenario: Close modal
- **WHEN** closeModal() is called
- **AND** activeModal is set to null

### Requirement: Toast notifications

The system SHALL allow adding and removing toast notifications.

#### Scenario: Add toast
- **WHEN** addToast({ id: '1', type: 'success', message: 'Saved' }) is called
- **AND** toast is added to toasts array

#### Scenario: Remove toast
- **WHEN** removeToast('1') is called
- **AND** toast with id '1' is removed from array