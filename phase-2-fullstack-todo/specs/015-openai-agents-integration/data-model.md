# Data Model: OpenAI Agents SDK Integration

**Feature**: 015-openai-agents-integration
**Date**: 2025-12-30

## Overview

This document defines the data models and context objects required for the OpenAI Agents SDK integration.

## Agent Context Model

### AgentContext (Runtime Context)

Used to pass user-specific information to agent tools during execution.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentContext:
    """Context passed to all agent tool invocations.

    Attributes:
        user_id: UUID of the authenticated user
        conversation_id: Optional conversation ID for context
        mcp_base_url: Base URL for MCP server (internal)
    """
    user_id: str
    conversation_id: Optional[str] = None
    mcp_base_url: str = "http://localhost:8000"
```

## Pydantic Schemas

### Chat Request/Response Schemas

Located in: `backend/schemas/chat.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation ID. Creates new if not provided."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's natural language message"
    )

class ToolCall(BaseModel):
    """Record of a tool invocation by the agent."""
    tool_name: str = Field(..., description="Name of the tool called")
    arguments: dict = Field(default_factory=dict, description="Arguments passed to tool")
    result: dict = Field(default_factory=dict, description="Result returned by tool")

class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    conversation_id: str = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant's response")
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="List of MCP tools invoked"
    )
```

### Agent Tool Input/Output Schemas

Located in: `backend/agents/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    """Task priority levels."""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class ExtractedTaskDetails(BaseModel):
    """Task details extracted from natural language."""
    title: str = Field(..., description="Task title extracted from message")
    description: Optional[str] = Field(None, description="Task description if provided")
    priority: TaskPriority = Field(
        default=TaskPriority.medium,
        description="Inferred priority level"
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date if mentioned (ISO 8601 format)"
    )

class TaskInfo(BaseModel):
    """Task information returned from tools."""
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    priority: str
    created_at: str
    updated_at: str

class TaskOperationResult(BaseModel):
    """Result of a task operation."""
    task_id: str
    status: str  # created, updated, deleted, completed
    title: str

class TaskListResult(BaseModel):
    """Result of listing tasks."""
    tasks: List[TaskInfo]
    total: int
```

## Database Models (Existing)

The following tables already exist and will be reused:

### Conversations Table
```sql
-- Already defined in constitution.md
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Messages Table
```sql
-- Already defined in constitution.md
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### SQLModel Definitions

Located in: `backend/models.py` (additions)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions."""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    """Message model for conversation history."""
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

## Agent Configuration

### TaskManagerAgent Settings

```python
AGENT_CONFIG = {
    "name": "TaskManager",
    "model": "gpt-4o-mini",  # Cost-efficient, suitable for task management
    "max_turns": 10,  # Prevent infinite loops
    "temperature": 0.7,  # Balanced creativity/consistency
}

AGENT_INSTRUCTIONS = """
You are TaskWave, a friendly and efficient task management assistant.

## Your Capabilities
- Create tasks from casual conversation (e.g., "I need to buy groceries" → task titled "Buy groceries")
- List and search through user's tasks
- Mark tasks as complete
- Update task details
- Delete tasks

## Behavior Guidelines
1. **Extract Details**: When users mention tasks casually, extract:
   - Title: The core action or task
   - Description: Additional context if provided
   - Priority: Infer from urgency words ("urgent", "important", "ASAP" = high)

2. **Ask for Clarification**: If the user's intent is unclear:
   - Ask ONE clarifying question
   - Don't guess or make assumptions

3. **Confirm Actions**: Always confirm what you did:
   - "I've created a task: 'Buy groceries'"
   - "I've marked 'Call mom' as complete"

4. **Handle Multiple Tasks**: If user mentions multiple tasks:
   - Create them separately
   - Confirm each one

5. **Natural Responses**: Be conversational but concise:
   - ✅ "Done! I've added 'Buy groceries' to your tasks."
   - ❌ "I have successfully executed the create_task function..."

## Examples
User: "I have a doctor's appointment on Friday"
→ Create task titled "Doctor's appointment" (infer Friday as context)

User: "What do I need to do?"
→ List all pending tasks

User: "I finished the report"
→ Search for task matching "report", mark as complete

User: "Remove all completed tasks"
→ List completed tasks, delete each one
"""
```

## Entity Relationships

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   User      │────<│   Conversation   │────<│   Message   │
└─────────────┘     └──────────────────┘     └─────────────┘
       │                                            │
       │                                            │
       │            ┌──────────────────┐            │
       └───────────>│      Task        │<───────────┘
                    └──────────────────┘
                    (via agent tool calls)
```

## Key Constraints

1. **User Isolation**: All operations filtered by `user_id`
2. **Message Length**: Max 4000 characters per message
3. **Role Values**: Only 'user' or 'assistant'
4. **Conversation Scope**: Messages belong to exactly one conversation
5. **Task Operations**: Go through MCP tools, not direct DB access
