# ChatKit Server Quickstart

## Running the Server

```bash
# Start the backend server (includes ChatKit)
cd backend
uv run uvicorn main:app --reload

# ChatKit endpoint is now available at POST http://localhost:8000/chatkit
```

## Testing Streaming with curl

```bash
# Send a message and receive streaming response
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"message": "Hello, I need help with my tasks"}' \
  --no-buffer

# Expected output (streaming tokens):
# data: Hello
#
# data: ! How
#
# data:  can
#
# data:  I
#
# data:  help
#
# data:  you
#
# data:  today
#
# event: done
#
```

## Example Requests/Responses

### 1. Create New Thread

**Request:**
```json
POST /chatkit
Authorization: Bearer <jwt-token>
{"message": "I need help organizing my tasks"}
```

**Response (streaming):**
```
data: I'd
data:  be
data:  happy
data:  to
data:  help
data:  you
data:  organize
data:  your
data:  tasks
event: done
data: {"thread_id": "550e8400-e29b-41d4-a716-446655440000"}
```

### 2. Continue Existing Thread

**Request:**
```json
POST /chatkit
Authorization: Bearer <jwt-token>
{"thread_id": "550e8400-e29b-41d4-a716-446655440000", "message": "What are my pending tasks?"}
```

**Response (streaming):**
```
data: Based
data:  on
data:  your
data:  task
data:  list
data: , you have:
event: tool_call
data: {"tool": "list_tasks", "arguments": {"status": "pending"}}
data: Let
data: me
data:  check
data: ...
event: done
data: {"response": "You have 3 pending tasks..."}
```

## Thread Management

### List All Threads

```bash
curl http://localhost:8000/chatkit/threads \
  -H "Authorization: Bearer <jwt-token>"
```

**Response:**
```json
{
  "threads": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Task Management Help",
      "message_count": 5,
      "created_at": "2025-12-30T10:00:00Z",
      "updated_at": "2025-12-30T10:05:00Z"
    }
  ],
  "total": 1
}
```

### Get Thread with Messages

```bash
curl http://localhost:8000/chatkit/threads/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <jwt-token>"
```

## SSE Event Format

| Event Type | Format | Description |
|------------|--------|-------------|
| Text | `data: <text>\n\n` | Streaming AI response tokens |
| Tool Call | `event: tool_call\ndata: {...}\n\n` | Agent tool invocation |
| Tool Result | `event: tool_result\ndata: {...}\n\n` | Tool output |
| Done | `event: done\ndata: {...}\n\n` | Response complete with metadata |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for agent inference |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT verification secret |

## Integration with Frontend

```javascript
// Example: Using fetch with ReadableStream
const response = await fetch('http://localhost:8000/chatkit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ message: 'Hello' })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  // Parse SSE events from chunk
  // Update UI with new tokens
}
```
