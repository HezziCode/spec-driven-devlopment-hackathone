---
id: 006
title: debug-delete-failure
stage: analyze
date_iso: 2026-01-16
surface: agent
model: sonnet
feature: 001-fix-delete-mcp
branch: 001-fix-delete-mcp
user: huzaifasys
command: /sp.analyze
labels: [debug, delete, title, runtime]
links:
  spec: specs/001-fix-delete-mcp/spec.md
  plan: specs/001-fix-delete-mcp/plan.md
  tasks: specs/001-fix-delete-mcp/tasks.md
files_yaml: []
tests_yaml: []
prompt_text: |
  sp.analyze debug it and make sure it should work with title the task should delete
response_text: |
  Runtime debug: Fix implemented but likely agent using old memory/instructions. Direct API test shows delete-by-name endpoint missing (404). Need to verify agent chain search+delete vs new endpoint. Root cause: Task "Cricket Match" exists, but agent may not be calling search before delete.
outcome: partial
evaluation: Specs consistent, fix deployed, runtime mismatch due to agent memory or missing endpoint.
---

**Prompt**: /sp.analyze debug delete failure

**Response Summary**: Spec analysis shows alignment, but runtime issue persists. Two possible causes:

1. **Agent memory stale**: Old instructions sending title as task_id (UUID validation fail).
2. **Delete-by-name endpoint missing**: New endpoint not registered; agent chain search+delete not executing.

**Debug steps**:
- Test direct API: `POST /api/ai/tasks/delete-by-name` (check if 404).
- Verify agent instructions loaded (`backend/chatkit/agent.py` modified?).
- Check logs for "Cricket Match" UUID validation error.

**Next**: Run debug commands to isolate failure point. Analysis confirms spec/tasks solid; runtime fix incomplete.