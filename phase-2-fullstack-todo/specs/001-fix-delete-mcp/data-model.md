# Data Model: Fix Delete MCP Tool

No schema changes required.

**Existing Entities (Unchanged)**:
- **Task**: id (UUID PK), user_id (FK), title (used for search matching), ... (per constitution).

**Validation Rules**:
- Title matching: Exact or fuzzy (agent handles); user-owned only.

**Relationships**: Task.user_id → Users.id (CASCADE delete preserves isolation).