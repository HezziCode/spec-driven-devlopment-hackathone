---
id: 095
title: Fix all MCP agent tools by adding AI endpoints
stage: general
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-fix-chat-errors
user: huzaifa
command: direct fix (not /sp command)
labels: ["bugfix", "mcp", "chatbot", "api", "agent-tools"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/routes/ai_tools.py
 - backend/ai_agents/tools.py
tests:
 - None (manual testing required)
---

## Prompt

now investigate why the task list and other mcp isn't work just create task mcp is working fine just check create task mcp implementation and code and then made other mcp same

maybe there is an issue that doesn't resolve yet see  Can u provide task list?
It seems there was an error while trying to retrieve your task list. Let me try again.I'm still unable to retrieve your task list due to a technical issue. Please let me know if there's a specific task you'd like to manage or create, and I can assist you with that!

## Response snapshot

### Root Cause Analysis:

I investigated why `create_task` was working but all other MCP agent tools (list, update, delete, mark_complete, search) were failing.

**Key Finding:**
- `create_task` calls `/api/ai/tasks` which bypasses authentication (designed for AI agents)
- Other tools were calling REST API endpoints at `/api/users/{user_id}/tasks` which REQUIRE JWT authentication
- The `AgentContext` in `chat_service.py` was NOT passing JWT token (it doesn't have access to it)
- Only `/api/ai/tasks` (POST create) endpoint existed - missing AI endpoints for other operations

### Solution Implemented:

1. **Added Missing AI Tool Endpoints** in `backend/routes/ai_tools.py`:
   - `POST /api/ai/tasks/list` - List tasks (with status filter)
   - `POST /api/ai/tasks/{task_id}/get` - Get specific task
   - `POST /api/ai/tasks/{task_id}/complete` - Mark task complete
   - `POST /api/ai/tasks/search` - Search tasks by query
   - Existing: `PUT /api/ai/tasks/{task_id}` - Update task (already existed)
   - Existing: `DELETE /api/ai/tasks/{task_id}` - Delete task (already existed)

2. **Updated All Agent Tools** in `backend/ai_agents/tools.py`:
   - Changed `list_tasks` to call `POST /api/ai/tasks/list`
   - Changed `get_task` to call `POST /api/ai/tasks/{task_id}/get`
   - Changed `mark_complete` to call `POST /api/ai/tasks/{task_id}/complete`
   - Changed `update_task` to call `PUT /api/ai/tasks/{task_id}` (changed from PATCH)
   - Changed `delete_task` to call `DELETE /api/ai/tasks/{task_id}` (with JSON body)
   - Changed `search_tasks` to call `POST /api/ai/tasks/search`

3. **Key Design Pattern:**
   - All `/api/ai/*` endpoints bypass authentication
   - They accept `user_id` in the request body
   - They use the same underlying `task_service` functions
   - They enforce user isolation at the service layer
   - No JWT token required - perfect for AI agent tools

### Files Modified:

**backend/routes/ai_tools.py:**
- Added 4 new endpoint functions with request models:
  - `list_tasks_for_ai()` with `ListTasksRequest`
  - `mark_task_complete_for_ai()` with `MarkCompleteRequest`
  - `get_task_for_ai()` with `GetTaskRequest`
  - `search_tasks_for_ai()` with `SearchTasksRequest`

**backend/ai_agents/tools.py:**
- Updated 6 function tools to use AI endpoints:
  - `list_tasks` - Changed from GET with auth to POST without auth
  - `get_task` - Changed from GET with auth to POST without auth
  - `mark_complete` - Changed from PATCH with auth to POST without auth
  - `update_task` - Changed from PATCH with auth to PUT without auth
  - `delete_task` - Changed from DELETE with auth to DELETE without auth (but with JSON body)
  - `search_tasks` - Changed from GET with auth to POST without auth

## Outcome

- ✅ Impact: Fixed all MCP agent tools by creating matching AI endpoints that bypass authentication
- 🧪 Tests: Manual testing required - user should test chatbot for list, update, delete, mark complete, and search operations
- 📁 Files: Modified `backend/routes/ai_tools.py` (added 4 endpoints) and `backend/ai_agents/tools.py` (updated 6 tools)
- 🔁 Next prompts: Test chatbot with "show task list", "delete task", "update task", "mark complete", "search tasks"
- 🧠 Reflection: The issue was architectural - agent tools need auth-free endpoints. The `/api/ai/*` endpoints follow the same pattern as `create_task` which was already working

## Evaluation notes (flywheel)

- Failure modes observed: Missing AI endpoints for list/get/mark_complete/search operations, JWT token not available in agent context
- Graders run and results (PASS/FAIL): N/A - manual testing required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test all chatbot operations (list, update, delete, complete, search) to verify they work
