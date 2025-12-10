<!-- SYNC IMPACT REPORT:
Version change: N/A → 1.0.0
Added sections: Core Principles (6), Technology Stack and Constraints, Development Workflow, Code Quality Standards, Architecture Principles, Governance
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ⚠ pending review
Follow-up TODOs: None
-->
# Evolution of Todo - Phase 1: In-Memory Python Console App Constitution

## Core Principles

### Spec-Driven Development (SDD)
All development must start with specs, plans, and tasks. No code shall be written without first creating a spec.md, then plan.md, and tasks.md. Implementation follows the spec-driven workflow using Claude Code CLI agents and skills.

### Minimal Dependencies
Use Python standard library only for core functionality (e.g., dataclasses for Task models, enum for statuses). No external dependencies except for testing (pytest). Technology stack: Python 3.13+ (strictly no lower versions).

### Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Aim for 100% coverage on core functions. Tests must be spec-driven and include edge cases. Red-Green-Refactor cycle strictly enforced.

### Clean Code and Type Safety
Functions must be small with single-responsibility (SRP). Use descriptive naming (e.g., add_task, list_tasks). Use type hints everywhere (e.g., def add_task(tasks: list[Task], title: str, description: str) -> None). Follow PEP 8 style guidelines strictly.

### In-Memory Architecture
Data management uses in-memory storage only (no persistence). Use a Task dataclass for tasks (fields: id: int, title: str, description: str, completed: bool). In-memory storage using a list of Task objects. No database or file storage in Phase 1.

### Console-First User Experience
Accessibility/Usability: Console outputs must be clear, with numbered IDs for tasks and user-friendly prompts. No web/UI components for Phase 1. Console-only implementation with clear, user-friendly interface.

## Technology Stack and Constraints

Language: Python 3.13+ (strictly no lower versions).
Libraries: Standard library only (e.g., use dataclasses for Task models, enum for statuses). No external dependencies except for testing (pytest).
Testing: Use pytest for unit tests. Aim for 100% coverage on core functions. Tests must be spec-driven and include edge cases.
Tools: Spec-Kit-Plus for SDD workflow (specs, plans, tasks, history). Claude Code CLI for agentic coding, including agents and skills. UV for project management (if needed for virtual envs).

Constraints:
No internet access or external APIs.
Code must be idempotent where applicable (e.g., task operations).
Follow PEP 8 style guidelines strictly.
All changes must be atomic, testable, and committed via git with descriptive messages including "Co-authored-by: Claude <noreply@anthropic.com>".

## Development Workflow

Workflow:
All features start with a spec.md, then plan.md, tasks.md.
Use Claude Code agents for autonomous implementation (e.g., console-feature-builder agent).
Skills for reusable patterns (e.g., console-input-skill for user prompts and validation).

Git Practices: Branch per feature (e.g., feature/add-task). Commits must reference specs/tasks.
Escalation: If ambiguities arise (e.g., spec conflicts), pause and request user input with options.

History and Records:
Prompt History Records (PHRs) in history/prompts/ for every interaction.
Architectural Decision Records (ADRs) in history/adr/ for significant decisions (suggest only; user consent required).

## Code Quality Standards

Clean Code Principles:
Functions should be small, single-responsibility (SRP).
Use descriptive naming (e.g., add_task, list_tasks).
Error handling: Use exceptions for invalid inputs (e.g., ValueError for bad task IDs).
Documentation: Docstrings for all classes/functions, following Google style.

Type Safety: Use type hints everywhere (e.g., def add_task(tasks: list[Task], title: str, description: str) -> None).
Accessibility/Usability: Console outputs must be clear, with numbered IDs for tasks and user-friendly prompts.
Performance: O(1) or O(n) operations only; no unnecessary complexity since in-memory.
Security: No secrets or user data handling in Phase 1, but follow least privilege (e.g., no global variables).

## Architecture Principles

Modular Design: Use a Task dataclass for tasks (fields: id: int, title: str, description: str, completed: bool).
Data Management: In-memory storage using a list of Task objects.
Workflow:
All features start with a spec.md, then plan.md, tasks.md.
Use Claude Code agents for autonomous implementation (e.g., console-feature-builder agent).
Skills for reusable patterns (e.g., console-component skill for input/output handling).

Non-Functional Requirements (NFRs):
Reliability: Handle invalid inputs gracefully with messages.
Maintainability: Code organized in /src (e.g., main.py, models.py, utils.py).
Testability: Each task in tasks.md must have acceptance criteria with pytest assertions.

## Governance

Spec-Driven Mandate: Refine specs until Claude Code generates correct output. No manual edits to generated code.
Reusable Intelligence:
Agents: Define agents like "console-feature-builder" for implementing features autonomously.
Skills: Use skills for patterns (e.g., "console-input-skill" for user prompts and validation).

Evaluation and Validation:
Definition of Done (DoD): Feature complete when all tasks.md items are checked, tests pass, and console demo works.
Risks: Over-specification leading to delays; mitigate by iterative refinement.
Success Metrics: App runs without errors, implements all basic features, and adheres to SDD.

This constitution is immutable unless amended via ADR. All agents/skills must reference it.

**Version**: 1.0.0 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-10
