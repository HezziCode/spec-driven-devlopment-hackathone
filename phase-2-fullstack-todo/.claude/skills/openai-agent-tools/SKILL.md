---
name: openai-agent-tools
description: Create intelligent AI agents using OpenAI Agents SDK with function tools. Use when building conversational agents, implementing tool-calling patterns, creating multi-agent orchestration systems, or when user mentions OpenAI Agents SDK or @function_tool.
---

# OpenAI Agent Tools Skill

## Purpose
Build intelligent AI agents using OpenAI Agents SDK with @function_tool decorators for task automation and conversational interfaces.

## Context
Used for creating AI agents that can perform actions, call APIs, and manage tasks through natural language interaction.

## Pattern

### Basic Agent with Function Tools
```python
import asyncio
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city.
    
    Args:
        city: The city name to get weather for
    
    Returns:
        Weather description string
    """
    return f"The weather in {city} is sunny, 72°F"

@function_tool
def create_task(title: str, priority: str = "medium") -> dict:
    """Create a new task.
    
    Args:
        title: Task title
        priority: Priority level (low, medium, high, critical)
    
    Returns:
        Created task object
    """
    return {"id": "123", "title": title, "priority": priority}

agent = Agent(
    name="TaskAssistant",
    instructions="""You are a helpful task management assistant.
    Help users create, organize, and manage their tasks.
    Extract task details from casual conversation.""",
    model="gpt-4o-mini",
    tools=[get_weather, create_task],
)

async def main():
    result = await Runner.run(agent, input="I have a meeting tomorrow")
    print(result.final_output)

asyncio.run(main())
```

### Agent with Context Access
```python
from agents import Agent, RunContextWrapper, function_tool
from typing import Any

@function_tool
def save_to_database(
    ctx: RunContextWrapper[Any],
    data: str
) -> str:
    """Save data using context's database connection.
    
    Args:
        ctx: Run context with database access
        data: Data to save
    
    Returns:
        Confirmation message
    """
    db = ctx.context.get("database")
    # Use database connection
    return "Saved successfully"

# Context passed to runner
context = {"database": db_connection, "user_id": "abc123"}
result = await Runner.run(agent, input="Save this note", context=context)
```

### Structured Output with Pydantic
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedTask(BaseModel):
    title: str = Field(description="Task title extracted from message")
    due_date: Optional[str] = Field(description="Due date if mentioned")
    priority: str = Field(default="medium", description="Inferred priority")
    tags: List[str] = Field(default_factory=list, description="Relevant tags")

@function_tool
def extract_task(message: str) -> ExtractedTask:
    """Extract task details from natural language.
    
    Args:
        message: User's message containing task info
    
    Returns:
        Structured task data
    """
    # AI will structure the extraction
    return ExtractedTask(title="Extracted title", priority="high")
```

### Agent-as-Tool Pattern
```python
spanish_agent = Agent(
    name="SpanishTranslator",
    instructions="Translate text to Spanish",
)

french_agent = Agent(
    name="FrenchTranslator",
    instructions="Translate text to French",
)

orchestrator = Agent(
    name="Orchestrator",
    instructions="Route translation requests to appropriate agent",
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_spanish",
            tool_description="Translate to Spanish"
        ),
        french_agent.as_tool(
            tool_name="translate_french",
            tool_description="Translate to French"
        ),
    ],
)
```

### Streaming Responses
```python
async def stream_response():
    async for event in Runner.run_streamed(agent, input="Help me plan"):
        if hasattr(event, 'text'):
            print(event.text, end='', flush=True)
```

## Key Principles
1. Clear Instructions: Agent instructions define personality and capabilities
2. Typed Tools: Always use type hints for tool parameters
3. Docstrings Matter: They become the tool description for the LLM
4. Context Passing: Use RunContextWrapper for shared state
5. Structured Output: Use Pydantic models for complex returns

## References
- references/multi-agent-patterns.md - Orchestration patterns
- references/streaming-guide.md - Streaming implementation
- examples/task-manager-agent.py - Complete example
```

