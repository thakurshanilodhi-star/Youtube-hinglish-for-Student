"""Dubbing job management routes."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.models import DubbingJob, JobStatus, VideoSource, User
from app.routers.auth import get_current_user
from app.services.audio_service import AudioService
from app.services.transcription_service import TranscriptionService
from app.services.diarization_service import DiarizationService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService
from app.services.pipeline_service import PipelineService

router = APIRouter()
pipeline = PipelineService()

@router.post("/create")
async def create_job(
    youtube_url: Optional[str] = None,
    source_type: VideoSource = VideoSource.YOUTUBE,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dubbing job from YouTube URL."""
    job = DubbingJob(
        user_id=current_user.id,
        source_type=source_type,
        source_url=youtube_url,
        status=JobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    if background_tasks:
        background_tasks.add_task(pipeline.process_job, str(job.id))

    return {"job_id": str(job.id), "status": job.status, "message": "Job created and queued"}

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a video file for dubbing."""
    import os
    from app.config import get_settings
    settings = get_settings()

    job = DubbingJob(
        user_id=current_user.id,
        source_type=VideoSource.UPLOAD,
        original_filename=file.filename,
        status=JobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Save uploaded file
    upload_dir = os.path.join(settings.LOCAL_STORAGE_PATH, str(job.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    job.storage_path = file_path
    await db.commit()

    background_tasks.add_task(pipeline.process_job, str(job.id))

    return {"job_id": str(job.id), "status": "pending", "filename": file.filename}

@router.get("/{job_id}")
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get job status and details."""
    result = await db.execute(
        select(DubbingJob).where(
            DubbingJob.id == uuid.UUID(job_id),
            DubbingJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": str(job.id),
        "status": job.status.value,
        "progress": job.progress_percent,
        "title": job.title,
        "source_type": job.source_type.value,
        "source_url": job.source_url,
        "duration": job.duration_seconds,
        "num_speakers": job.num_speakers,
        "error": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "download_urls": {
            "dubbed_audio": f"/api/v1/jobs/{job_id}/download/audio" if job.dubbed_audio_path else None,
            "subtitles_srt": f"/api/v1/jobs/{job_id}/download/srt" if job.subtitle_srt_path else None,
            "subtitles_vtt": f"/api/v1/jobs/{job_id}/download/vtt" if job.subtitle_vtt_path else None,
        }
    }

@router.get("/")
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """List all jobs for current user."""
    result = await db.execute(
        select(DubbingJob)
        .where(DubbingJob.user_id == current_user.id)
        .order_by(DubbingJob.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    jobs = result.scalars().all()

    return [
        {
            "id": str(j.id),
            "title": j.title,
            "status": j.status.value,
            "progress": j.progress_percent,
            "source_type": j.source_type.value,
            "created_at": j.created_at
        }
        for j in jobs
    ]

@router.get("/{job_id}/download/{file_type}")
async def download_file(
    job_id: str,
    file_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download processed files."""
    from fastapi.responses import FileResponse

    result = await db.execute(
        select(DubbingJob).where(
            DubbingJob.id == uuid.UUID(job_id),
            DubbingJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = None
    if file_type == "audio" and job.dubbed_audio_path:
        file_path = job.dubbed_audio_path
    elif file_type == "srt" and job.subtitle_srt_path:
        file_path = job.subtitle_srt_path
    elif file_type == "vtt" and job.subtitle_vtt_path:
        file_path = job.subtitle_vtt_path

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=os.path.basename(file_path))
