"""Live streaming dubbing routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.models import LiveStreamSession, User
from app.routers.auth import get_current_user
from app.services.live_service import LiveStreamService

router = APIRouter()
live_service = LiveStreamService()

@router.post("/start")
async def start_live_stream(
    youtube_url: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a live stream dubbing session."""
    session = LiveStreamSession(
        user_id=current_user.id,
        youtube_url=youtube_url,
        status="active"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    background_tasks.add_task(live_service.start_stream, str(session.id), youtube_url)

    return {
        "session_id": str(session.id),
        "status": "active",
        "websocket_url": f"ws://localhost:8000/ws/live/{session.id}"
    }

@router.post("/{session_id}/stop")
async def stop_live_stream(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop a live stream session."""
    result = await db.execute(
        select(LiveStreamSession).where(
            LiveStreamSession.id == uuid.UUID(session_id),
            LiveStreamSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "stopped"
    await db.commit()

    await live_service.stop_stream(session_id)

    return {"message": "Stream stopped"}

@router.get("/{session_id}/status")
async def get_stream_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get live stream status and stats."""
    result = await db.execute(
        select(LiveStreamSession).where(
            LiveStreamSession.id == uuid.UUID(session_id),
            LiveStreamSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "status": session.status,
        "total_segments": session.total_segments,
        "avg_latency_ms": session.avg_latency_ms,
        "started_at": session.created_at
    }
