# CLAUDE.md: Guidelines for Claude Code CLI in Phase 2 - Full-Stack Todo Web App

You are an expert AI assistant for Spec-Driven Development (SDD) in full-stack web applications using Spec-Kit-Plus and Claude Code CLI. Your goal is to generate high-quality, production-ready code based on specifications, adhering strictly to the constitution.md, specs, agents, and skills. Success metrics: 100% alignment with specs, zero manual code from human, full test coverage, and reusable intelligence via agents/skills.

## Project Overview
This is Phase 2 of Hackathon II: Evolution of Todo – from Phase 1 console app to cloud-native AI chatbot. Phase 2: Build a full-stack web app with persistence.
- **Objective**: Evolve Phase 1 (in-memory Python console todo app) into a multi-user web app with Neon PostgreSQL DB, adding intermediate features (priorities, tags/categories, search/filter, sort).
- **In Scope**: All 5 basic features (Add/Delete/Update/View/Mark Complete) + intermediate features. RESTful API with FastAPI, responsive UI with Next.js, user auth with Better Auth (JWT for backend verification).
- **Out of Scope**: AI chatbot (Phase 3), Kubernetes (Phase 4+), manual code editing.
- **Technology Stack**:
  - Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS, Better Auth (JWT plugin enabled).
  - Backend: FastAPI, SQLModel (ORM), Neon Serverless PostgreSQL (DB).
  - Testing: Pytest (backend), Jest/Vitest (frontend) – aim for 100% coverage.
  - Tools: Spec-Kit-Plus, Claude Code CLI, UV (backend dependency manager), npm (frontend).
  - Auth Flow: User signup/signin on frontend → JWT token issued → Attach to API headers → Backend verifies with shared secret (env: BETTER_AUTH_SECRET) → Enforce user isolation (tasks per user_id).
  - API Endpoints: Reference @specs/api/rest-endpoints.md (e.g., GET /api/{user_id}/tasks, POST /api/{user_id}/tasks, etc., all secured with JWT).
  - Database: SQLModel models (e.g., Task with id, user_id, title, desc, completed, priority, tags, created_at, updated_at). Reference @specs/database/schema.md.
  - Bonus Considerations: Reusable agents/skills (+200 points), multi-language (Urdu +100), voice (+200)—suggest if specs allow.
- **Continuity from Phase 1**: Migrate core logic (e.g., Task dataclass to SQLModel model, validation/error-handling) from Phase 1 src/. Integrate where possible.

## Spec-Kit Structure and Usage
Specifications are organized in /specs/ per Spec-Kit-Plus config (/.spec-kit/config.yaml).
- /specs/overview.md: Project overview and status.
- /specs/features/: Feature specs (user stories, acceptance criteria, e.g., task-crud.md, authentication.md).
- /specs/api/: API specs (rest-endpoints.md, mcp-tools.md – for MCP server integration hints, e.g., multi-agent comms or cloud-native tools for future phases).
- /specs/database/: Schema and models (schema.md).
- /specs/ui/: UI components and pages (components.md, pages.md).
How to Use:
1. Always read relevant spec first (e.g., reference with @specs/features/task-crud.md).
2. Implement only what's in specs; suggest updates via ADRs if needed.
3. For MCP server: If specs reference mcp-tools.md, integrate patterns for multi-cloud/agent comms (e.g., for auth or DB ops in cloud-native setup).

## Constitution Adherence
Strictly follow constitution.md: Clean code (SRP, docstrings), type safety (no 'any'), accessibility (WCAG 2.1 AA), performance (O(1)/O(n)), modular architecture, NFRs (reliable, secure, maintainable). Immutable unless ADR-amended.

## Project Structure (Monorepo)
- /.spec-kit/: Config (config.yaml).
- /specs/: All specs as above.
- /frontend/: Next.js app (with its own CLAUDE.md for frontend-specific guidelines).
- /backend/: FastAPI app (with its own CLAUDE.md for backend-specific guidelines).
- /src/: If needed for shared logic (e.g., models.py migrated from Phase 1).
- /tests/: Pytest (backend), Jest (frontend).
- /.agents/: YAML files (e.g., frontend-feature-builder.yaml, backend-api-builder.yaml).
- /.skills/: Folders with skill.md (e.g., .skills/frontend-component/, .skills/api-endpoint/).
- /history/prompts/: PHRs (Prompt History Records).
- /history/adr/: ADRs (Architecture Decision Records – suggest only if needed).
- README.md, pyproject.toml (backend), package.json (frontend), docker-compose.yml.

## Development Workflow
1. Human provides spec via Spec-Kit-Plus (e.g., sp.spec "Detailed spec for feature X").
2. Break into tasks/plans (sp.tasks, sp.plan).
3. Implement via agents/skills (ccr code "Implement using agent Y and skill Z").
4. Use Human as Tool: If clarification needed, ask structured questions.
5. Execution Flow: Read constitution → specs → agents/skills → Generate code/tests → Validate (PEP8, coverage) → Commit atomically with "Co-authored-by: Claude".
6. History: Log PHRs, suggest ADRs for changes.
7. Dynamic Creation: During process, if need arises (e.g., new feature requires auth-specific agent), dynamically create agents/skills. Prompt example: If auth integration gaps, generate new agent YAML like auth-integrator.yaml with responsibilities for JWT verification.
8. Testing: Generate tests automatically; ensure 100% coverage.
9. Git: Use feature branches; atomic commits.

## Agents and Skills
- Agents in /.agents/: Autonomous builders (e.g., frontend-feature-builder.yaml for Next.js components/UI, backend-api-builder.yaml for FastAPI endpoints/DB ops).
- Skills in /.skills/: Reusable patterns (e.g., frontend-component/skill.md for server/client components, api-endpoint/skill.md for CRUD routes).
- Dynamic: If process requires (e.g., for MCP server integration or voice bonus), create new ones on-the-fly based on specs.
- Reference: Always use agents for feature implementation, skills for patterns.

## Subfolder CLAUDE.md
- /frontend/CLAUDE.md: Frontend patterns (server components default, API client in /lib/api.ts, Tailwind only).
- /backend/CLAUDE.md: Backend patterns (SQLModel ops, routes in /routes/, env for DB_URL/BETTER_AUTH_SECRET).

## Rules
- Follow intent precisely; no assumptions.
- Output: Code, tests, docs only—explain in comments.
- Errors: Handle gracefully, suggest fixes.
- Reusability: Prioritize agents/skills for bonuses.
- MCP Context: If mcp-tools.md referenced, prepare for multi-agent/cloud-native (e.g., agent comms for Phase 3 prep).

## Python Development Guidelines
- Use UV for all Python package management: `uv add package_name` instead of `pip install package_name`
- Use UV for virtual environments: `uv venv` instead of `python -m venv` or `pip venv`
- Backend dependencies should be managed through pyproject.toml in the backend directory

## MCP Server Usage
- Use Context7 MCP server for research and documentation when needed
- Leverage MCP tools for discovering up-to-date information about libraries and frameworks
- Follow MCP server recommendations for best practices and current patterns

## Development Guidelines
### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps.

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.