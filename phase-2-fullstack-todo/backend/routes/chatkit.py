"""ChatKit API routes for streaming chat and thread management."""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlmodel import Session

from middleware.auth_middleware import get_current_user, get_user_id_from_token
from db import get_session
from schemas.chatkit import (
    SessionResponse,
    ThreadSyncRequest,
    ThreadItemResponse,
    ThreadListResponseV2,
)
from schemas import (
    ChatKitRequest,
    ErrorResponse,
    ThreadListResponse,
    ThreadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ChatKit"])


def get_chatkit_service(session):
    """Import and return the chatkit service."""
    from services.chatkit_service import ChatKitService

    return ChatKitService(session)


@router.post(
    "",
    summary="Send chat message with streaming response",
    description="Send a message to the AI and receive a streaming response via Server-Sent Events.",
    responses={
        200: {
            "description": "Streaming response with text/event-stream content-type",
            "content": {"text/event-stream": {}},
        },
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def send_message(
    request: Request,
    chat_request: ChatKitRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Send a message and receive streaming AI response.

    Uses Server-Sent Events (SSE) to stream response tokens as they are generated.
    Supports continuing existing threads or creating new ones.
    """
    user_id = str(user.get("id") or user.get("sub"))
    thread_id = chat_request.thread_id

    service = get_chatkit_service(session)

    async def generate_events():
        """Generate SSE events for streaming response."""
        try:
            async for event in service.process_message(
                user_id=user_id,
                thread_id=thread_id,
                message=chat_request.message,
            ):
                yield event
        except ValueError as e:
            logger.error(f"Chat error: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"
        except Exception as e:
            logger.exception(f"Unexpected chat error: {e}")
            yield f"event: error\ndata: Internal server error\n\n"

    return EventSourceResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@router.get(
    "/threads",
    response_model=ThreadListResponse,
    summary="List conversation threads",
    description="Get all conversation threads for the authenticated user.",
    responses={
        200: {"description": "List of user's threads"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_threads(
    limit: int = 50,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ThreadListResponse:
    """List all conversation threads for the user."""
    try:
        user_id = str(user.get("id") or user.get("sub"))
        service = get_chatkit_service(session)

        result = service.list_threads(user_id, limit)
        return ThreadListResponse(**result)
    except Exception as e:
        logger.exception(f"Error listing threads for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve threads",
        )


@router.get(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
    summary="Get thread with messages",
    description="Get a specific conversation thread with all its messages.",
    responses={
        200: {"description": "Thread with messages"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to access this thread"},
        404: {"model": ErrorResponse, "description": "Thread not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_thread(
    thread_id: str,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ThreadResponse:
    """Get a specific thread with all its messages."""
    try:
        user_id = str(user.get("id") or user.get("sub"))
        service = get_chatkit_service(session)

        thread_data = service.get_thread(user_id, thread_id)
        if thread_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread with ID '{thread_id}' not found",
            )

        return ThreadResponse(**thread_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving thread {thread_id} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve thread",
        )


@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a thread",
    description="Delete a conversation thread and all its messages.",
    responses={
        204: {"description": "Thread deleted successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to delete this thread"},
        404: {"model": ErrorResponse, "description": "Thread not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_thread(
    thread_id: str,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a conversation thread."""
    try:
        user_id = str(user.get("id") or user.get("sub"))
        service = get_chatkit_service(session)

        deleted = service.delete_thread(user_id, thread_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread with ID '{thread_id}' not found or not authorized",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting thread {thread_id} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete thread",
        )


# ==================== ChatKit Session Management Endpoints ====================

@router.post(
    "/chatkit/session",
    response_model=SessionResponse,
    status_code=201,
    summary="Create ChatKit session",
    description="Exchange JWT token for ChatKit client secret to establish chat session",
    responses={
        201: {"description": "Session created successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_session(
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """Create ChatKit session and return client secret."""
    from services.chatkit_service import create_chatkit_session

    try:
        result = await create_chatkit_session(UUID(current_user_id), session)
        return SessionResponse(**result)
    except Exception as e:
        logger.exception(f"Failed to create ChatKit session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get(
    "/users/{user_id}/chatkit/threads",
    response_model=ThreadListResponseV2,
    summary="List user's chat threads",
    description="Retrieve all chat threads for authenticated user with metadata",
    responses={
        200: {"description": "Thread list retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)
async def list_user_threads(
    user_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """List user's chat threads."""
    from services.chatkit_service import list_threads

    # Verify user_id matches authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        threads, total = await list_threads(user_id, session, limit, offset)

        # Convert to response format
        thread_items = [
            ThreadItemResponse(
                id=t.id,
                name=t.name,
                last_message_preview=t.last_message_preview,
                message_count=t.message_count,
                created_at=t.created_at.isoformat() + "Z",
                updated_at=t.updated_at.isoformat() + "Z",
            )
            for t in threads
        ]

        return ThreadListResponseV2(threads=thread_items, total=total)
    except Exception as e:
        logger.exception(f"Failed to list threads: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list threads: {str(e)}"
        )


@router.post(
    "/users/{user_id}/chatkit/threads/{thread_id}/sync",
    response_model=ThreadItemResponse,
    summary="Sync thread metadata",
    description="Update or create thread metadata in backend for persistence",
    responses={
        200: {"description": "Thread metadata synced successfully"},
        201: {"description": "New thread created and synced"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)
async def sync_thread_endpoint(
    user_id: UUID,
    thread_id: str,
    thread_data: ThreadSyncRequest,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """Sync thread metadata."""
    from services.chatkit_service import sync_thread

    # Verify user_id matches authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        thread = await sync_thread(user_id, thread_data.model_dump(), session)

        return ThreadItemResponse(
            id=thread.id,
            name=thread.name,
            last_message_preview=thread.last_message_preview,
            message_count=thread.message_count,
            created_at=thread.created_at.isoformat() + "Z",
            updated_at=thread.updated_at.isoformat() + "Z",
        )
    except Exception as e:
        logger.exception(f"Failed to sync thread: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync thread: {str(e)}"
        )


@router.delete(
    "/users/{user_id}/chatkit/threads/{thread_id}",
    summary="Delete chat thread",
    description="Remove chat thread and its metadata from backend storage",
    responses={
        200: {"description": "Thread deleted successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not found"},
    },
)
async def delete_user_thread(
    user_id: UUID,
    thread_id: str,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """Delete chat thread."""
    from services.chatkit_service import delete_thread

    # Verify user_id matches authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        deleted = await delete_thread(user_id, thread_id, session)
        if not deleted:
            raise HTTPException(status_code=404, detail="Thread not found")

        return {"message": "Thread deleted successfully", "thread_id": thread_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete thread: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete thread: {str(e)}"
        )
