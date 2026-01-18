# specs/001-fix-delete-mcp/plan.md

## 1. Scope and Dependencies

### In Scope
- Enhance the MCP agent's delete functionality to support natural language deletion requests using task titles (e.g., \"Delete the call mom task\") by resolving titles to task_ids via search.
- Modify agent logic (likely in `backend/chatkit/agent.py` or equivalent OpenAI Agents SDK integration) to detect delete intent with title reference, perform a `search_tasks` or `list_tasks` call first, match the title, retrieve task_id, then invoke `delete_task`.
- Ensure user isolation is maintained throughout (user_id filtering in all tool calls).
- Update relevant tests to cover the new resolution flow (e.g., `backend/tests/test_agent_tools.py`, `backend/tests/test_mcp_tools.py`).
- No changes to `backend/mcp_server/tools.py` (existing `delete_task` and `search_tasks` tools are sufficient and unchanged).
- Frontend ChatKit integration unchanged (handles SSE streaming but agent logic is backend).

### Out of Scope
- Changes to MCP server tools (`backend/mcp_server/tools.py`) or schemas (`backend/mcp_server/schemas.py`).
- New database schema/migrations (uses existing Task model with title field).
- Frontend modifications (ChatInterface.tsx, etc., already streams agent responses).
- Support for partial title matching ambiguities (assume first/exact match; clarify if multiple).
- Non-delete operations (create/update/list already functional).
- Deployment/K8s changes.

### External Dependencies
- Neon PostgreSQL (existing DB_URL): Relies on indexed `title` and `user_id` for fast searches.
- OpenAI Agents SDK (via `backend/chatkit/` or `backend/agents/`): Agent instructions and tool calling.
- FastMCP server (mounted at `/mcp`): Unchanged tools for search/delete.
- Ownership: Backend team owns agent logic; DB ops via task_service.py (indirect).

## 2. Key Decisions and Rationale

### Options Considered
1. **Add title param to delete_task tool**: Simple but violates tool contract (breaks existing callers), non-reversible, increases tool complexity.
2. **Agent-side resolution (selected)**: Agent detects intent, calls search_tasks → delete_task chain. Trade-offs: Adds orchestration logic (minimal, ~20 LOC); reversible; follows agent autonomy principle; no tool changes.
3. **Client-side resolution**: Frontend resolves before agent call (poor UX, violates separation of concerns).

### Trade-offs and Rationale
- **Agent autonomy**: Agents should handle natural language → structured actions (per constitution: modular, intelligent).
- **Smallest viable change**: Modify only agent instructions/tools wrapper (~1 file), leverage existing search/delete.
- **Reversible**: No schema/API changes; test-only impact if rolled back.
- **Principles**: SRP (agent orchestrates), type-safe (Pydantic), performant (single search + delete tx).

## 3. Interfaces and API Contracts

### Public APIs (Unchanged)
- Agent tools remain identical:
  - `search_tasks(user_id: str, query: str) → {\"tasks\": [...], \"total\": int}`
  - `delete_task(user_id: str, task_id: str) → {\"task_id\": str, \"status\": \"deleted\", \"title\": str}`
- Chat endpoint (`POST /api/users/{user_id}/chat`): Streams agent response with tool_calls array including chained search+delete.

### Versioning Strategy
- No API changes; internal agent logic only (semver patch if tagged).

### Idempotency, Timeouts, Retries
- Existing: DB ops idempotent (UUID checks); agent retries on transient errors via OpenAI SDK.
- Timeouts: MCP calls <500ms (indexed queries); agent total <5s.

### Error Taxonomy
| Code | Status | Example |
|------|--------|---------|
| NOT_FOUND | 404 | No task matches title |
| VALIDATION_ERROR | 422 | Invalid title/query |
| DATABASE_ERROR | 500 | Tx failure |
| AMBIGUOUS_MATCH | 400 | Multiple tasks match (agent returns clarification) |

## 4. Non-Functional Requirements (NFRs) and Budgets

- **Performance**: p95 <200ms end-to-end (search O(log n) + delete O(1)); cap queries at 50 tasks.
- **Reliability**: 99.9% uptime (leverage existing MCP); error budget 0.1%.
- **Security**: User_id isolation (verified in every tool); no title-based injection (Pydantic validated).
- **Cost**: Negligible (1-2 OpenAI tokens extra per delete; DB reads cheap).

## 5. Data Management and Migration

- **Source of Truth**: Existing Task table (`backend/models.py`); no schema changes.
- **Schema Evolution**: None needed (title field indexed? Verify/add if absent).
- **Migration/Rollback**: N/A (code-only).
- **Data Retention**: Deleted tasks hard-deleted (per spec); audit via logs.

## 6. Operational Readiness

- **Observability**: Log agent tool chains (e.g., \"search→delete\" flow) with user_id anonymized; metrics: delete_success_rate.
- **Alerting**: >5% delete failures → page on-call.
- **Runbooks**: \"Agent delete fail\" → check logs for ambiguous titles.
- **Deployment/Rollback**: Atomic commit/PR to branch `001-fix-delete-mcp`; FF via env var `AGENT_ENHANCED_DELETE=true`.
- **Feature Flags**: Optional env toggle for new logic.

## 7. Risk Analysis and Mitigation

1. **Risk: Ambiguous titles** (blast: low, user confusion). Mitigate: Agent asks \"Which one?\" if >1 match; cap at first exact.
2. **Risk: Perf regression** (blast: medium). Mitigate: Index `title`; test p95 <200ms.
3. **Risk: Breaks existing delete by ID** (blast: high). Mitigate: Tests cover both flows; no tool changes.

## 8. Evaluation and Validation

- **Definition of Done**:
  - [ ] Agent handles \"Delete [title]\" → search → delete.
  - [ ] Tests: `test_agent_delete_by_title_success`, `test_agent_delete_ambiguous`.
  - [ ] 100% coverage on new logic (pytest).
  - [ ] Manual: Chat \"Delete test task\" succeeds.
  - [ ] Scans: mypy, black, no new lint errors.
- **Output Validation**: JSON tool responses match schemas; error if no match.

## 9. Architectural Decision Record (ADR)
No significant decisions (agent orchestration is tactical, follows existing patterns). If multi-tool chaining becomes common, suggest future ADR.

## Step-by-Step Implementation Strategy

1. **Explore/Verify (Current)**: Confirmed `delete_task` needs task_id; agent examples imply intent detection but no resolution.
2. **Update Agent Instructions** (`backend/chatkit/agent.py` or `backend/agents/agent.py`):
   - Enhance AGENT_INSTRUCTIONS: \"For delete requests with titles, search first, then delete matching task_id.\"
3. **Modify Tool Wrapper** (if delete_tool in agent layer):
   - Override `delete_task`: If title provided, search_tasks → extract id → call MCP delete.
4. **Add Tests** (`backend/tests/test_agent_tools.py`):
   - Success: Title → delete.
   - Edge: No match, ambiguous, exact ID.
5. **Integrate/Validate**: Test chat endpoint with delete message.
6. **Commit**: Atomic, Co-Authored-By.

### Files to Modify/Create
- `backend/chatkit/agent.py` (or `backend/agents/agent.py`): Update instructions/tool logic for resolution.
- `backend/services/chatkit_service.py` (if orchestration): Chain tool calls.
- `backend/tests/test_agent_tools.py`: New test suite for delete-by-title.
- `backend/tests/test_chatkit.py`: Integration tests.
- `backend/mcp_server/tools.py`: Reference: Existing search/delete tools (no changes).
- `backend/routes/chatkit.py`: Chat endpoint exposing agent (minor validation).