"""Subtitle management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.models import DubbingJob, TranscriptSegment
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/{job_id}/segments")
async def get_segments(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all transcript segments for a job."""
    result = await db.execute(
        select(DubbingJob).where(
            DubbingJob.id == uuid.UUID(job_id),
            DubbingJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    segments_result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.job_id == uuid.UUID(job_id))
        .order_by(TranscriptSegment.start_time)
    )
    segments = segments_result.scalars().all()

    return [
        {
            "id": str(s.id),
            "speaker": s.speaker_id,
            "start": s.start_time,
            "end": s.end_time,
            "original": s.original_text,
            "translated": s.translated_text,
            "audio_path": s.audio_segment_path
        }
        for s in segments
    ]

@router.put("/{job_id}/segments/{segment_id}")
async def update_segment(
    job_id: str,
    segment_id: str,
    translated_text: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Edit a translated segment (subtitle editor)."""
    result = await db.execute(
        select(TranscriptSegment)
        .join(DubbingJob)
        .where(
            TranscriptSegment.id == uuid.UUID(segment_id),
            DubbingJob.user_id == current_user.id
        )
    )
    segment = result.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    segment.translated_text = translated_text
    await db.commit()

    return {"message": "Segment updated"}
