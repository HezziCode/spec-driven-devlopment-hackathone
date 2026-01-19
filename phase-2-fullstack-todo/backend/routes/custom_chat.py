"""Custom chat API routes without ChatKit dependencies."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from db import get_session
from middleware.auth_middleware import get_current_user
from schemas import (
    ChatKitRequest,
    ErrorResponse,
    ThreadResponse,
)
from schemas.chatkit import (
    ThreadItemResponse,
    ThreadListResponseV2,
    ThreadSyncRequest,
)

# Import the service functions at the top to avoid import issues in async context
from services.chatkit_service import (
    delete_thread as delete_thread_service,
)
from services.chatkit_service import (
    list_threads as list_threads_service,
)
from services.chatkit_service import (
    sync_thread,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Custom Chat"])


@router.post(
    "/users/{user_id}/chat/messages",
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
    user_id: UUID,
    request: Request,
    chat_request: ChatKitRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Send a message and receive streaming AI response.

    Uses Server-Sent Events (SSE) to stream response tokens as they are generated.
    Supports continuing existing threads or creating new ones.
    """
    # Verify user_id matches authenticated user
    if str(user_id) != str(current_user.get("id") or current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized")

    user_id_str = str(user_id)
    thread_id = chat_request.thread_id

    # Extract JWT token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    jwt_token = (
        auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    )

    if not jwt_token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    from services.chatkit_service import ChatKitService

    service = ChatKitService(session)

    async def generate_events():
        """Generate SSE events for streaming response."""
        try:
            async for event in service.process_message(
                user_id=user_id_str,
                thread_id=thread_id,
                message=chat_request.message,
                jwt_token=jwt_token,
            ):
                # Add a small delay after thread creation event to ensure database visibility
                if '"threadId"' in event and thread_id is None:
                    import asyncio

                    await asyncio.sleep(0.1)  # Small delay after new thread creation
                yield event
        except ValueError as e:
            logger.error(f"Chat error: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"
        except Exception as e:
            logger.exception(f"Unexpected chat error: {e}")
            yield "event: error\ndata: Internal server error\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/users/{user_id}/chat/threads",
    response_model=ThreadListResponseV2,
    summary="List conversation threads",
    description="Get all conversation threads for the authenticated user.",
    responses={
        200: {"description": "List of user's threads"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def list_threads_endpoint(
    user_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ThreadListResponseV2:
    """List all conversation threads for the user."""
    # Verify user_id matches authenticated user
    if str(user_id) != str(current_user.get("id") or current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        threads, total = await list_threads_service(user_id, session, limit, offset)

        # Convert to response format
        thread_items = [
            ThreadItemResponse(
                id=str(t.id),
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
        raise HTTPException(status_code=500, detail=f"Failed to list threads: {str(e)}")


@router.get(
    "/users/{user_id}/chat/threads/{thread_id}",
    response_model=ThreadResponse,
    summary="Get thread with messages",
    description="Get a specific conversation thread with all its messages.",
    responses={
        200: {"description": "Thread with messages"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {
            "model": ErrorResponse,
            "description": "Not authorized to access this thread",
        },
        404: {"model": ErrorResponse, "description": "Thread not found"},
    },
)
async def get_thread(
    user_id: UUID,
    thread_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ThreadResponse:
    """Get a specific thread with all its messages."""
    # Verify user_id matches authenticated user
    if str(user_id) != str(current_user.get("id") or current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized")

    from services.chatkit_service import ChatKitService

    service = ChatKitService(session)

    try:
        thread_data = service.get_thread(str(user_id), thread_id)
        if thread_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            )

        return ThreadResponse(**thread_data)
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.exception(f"Failed to get thread: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get thread: {str(e)}")


@router.delete(
    "/users/{user_id}/chat/threads/{thread_id}",
    summary="Delete a thread",
    description="Delete a conversation thread and all its messages.",
    responses={
        200: {"description": "Thread deleted successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {
            "model": ErrorResponse,
            "description": "Not authorized to delete this thread",
        },
        404: {"model": ErrorResponse, "description": "Thread not found"},
    },
)
async def delete_thread_endpoint(
    user_id: UUID,
    thread_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a conversation thread."""
    # Verify user_id matches authenticated user
    if str(user_id) != str(current_user.get("id") or current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        deleted = await delete_thread_service(user_id, thread_id, session)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            )

        return {"message": "Thread deleted successfully", "thread_id": thread_id}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Failed to delete thread: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete thread: {str(e)}"
        )


@router.post(
    "/users/{user_id}/chat/threads/{thread_id}/sync",
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
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Sync thread metadata."""
    # sync_thread is already imported at the top

    # Verify user_id matches authenticated user
    if str(user_id) != str(current_user.get("id") or current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        thread = await sync_thread(user_id, thread_data.model_dump(), session)

        return ThreadItemResponse(
            id=str(thread.id),
            name=thread.name,
            last_message_preview=thread.last_message_preview,
            message_count=thread.message_count,
            created_at=thread.created_at.isoformat() + "Z",
            updated_at=thread.updated_at.isoformat() + "Z",
        )
    except Exception as e:
        logger.exception(f"Failed to sync thread: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync thread: {str(e)}")
