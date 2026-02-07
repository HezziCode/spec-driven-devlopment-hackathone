"""Chat endpoint for AI agent conversations."""

from fastapi import APIRouter, Depends, HTTPException

from middleware.auth_middleware import get_current_user
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import process_message
# from middleware.rate_limiter import limit_ai_agent

router = APIRouter()


@router.post("/users/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str, request: ChatRequest, current_user=Depends(get_current_user)
):
    """
    Chat endpoint for AI agent conversations.

    Processes user messages through TaskManagerAgent and returns
    natural language responses with tool execution records.

    Args:
        user_id: UUID of the user (path parameter, must match authenticated user)
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT middleware

    Returns:
        ChatResponse with conversation_id, AI response, and tool call records

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
    """
    # Verify user owns this conversation (user isolation)
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=403, detail="You can only access your own conversations"
        )

    # Process message through agent
    try:
        result = await process_message(
            user_id=str(current_user.id),
            conversation_id=request.conversation_id,
            message=request.message,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
