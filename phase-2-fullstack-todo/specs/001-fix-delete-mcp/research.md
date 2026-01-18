# Research Summary: Fix Delete MCP Tool

## Findings from Codebase Exploration

**MCP Server Analysis (backend/mcp_server/)**:
- Tools (`create_task`, `update_task`, `delete_task`) all use UUID `task_id` for identification.
- `delete_task`: Validates `task_id` as UUID; queries `Task` by `id` and `user_id`; deletes if found.
- No bugs in `delete_task` implementation – identical pattern to working `update_task`.
- **Root Cause**: Chatbot/agent passes task **title** (\"Cricket Match\") as `task_id`, failing UUID validation early (pre-DB query).

**Resolution**:
- Decision: Enhance agent/chat logic to resolve title → UUID via `list_tasks` or new `search_tasks_by_title`.
- Rationale: Preserves MCP tool contract (UUID-only); fixes at agent layer (natural language → tool chain).
- Alternatives:
  | Option | Pros | Cons |
  |--------|------|------|
  | Modify MCP `delete_task` to accept title | Simple agent calls | Violates UUID contract; ambiguous duplicates; non-RESTful |
  | Add `delete_by_title` tool | Title support | Duplicates tools; title non-unique |
  | Agent chains `search_tasks` → `delete_task` | **Selected**: Maintains contracts; handles ambiguity | Slightly more complex agent prompt |

**Dependencies**:
- Existing `search_tasks` tool (handles `search` param).
- Agent must parse title from user message, search, extract first match ID, delete.

**No new tech needed** – leverages existing MCP tools/agent SDK.