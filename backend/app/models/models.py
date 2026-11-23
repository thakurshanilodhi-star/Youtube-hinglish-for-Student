"""SQLAlchemy database models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoSource(str, enum.Enum):
    YOUTUBE = "youtube"
    YOUTUBE_LIVE = "youtube_live"
    UPLOAD = "upload"

class DubbingJob(Base):
    __tablename__ = "dubbing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=True)
    source_type = Column(Enum(VideoSource), nullable=False)
    source_url = Column(Text, nullable=True)
    original_filename = Column(String(500), nullable=True)
    storage_path = Column(Text, nullable=True)

    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress_percent = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)

    original_language = Column(String(10), default="en")
    target_language = Column(String(10), default="hinglish")

    # Results
    transcript_path = Column(Text, nullable=True)
    translated_transcript_path = Column(Text, nullable=True)
    dubbed_audio_path = Column(Text, nullable=True)
    subtitle_srt_path = Column(Text, nullable=True)
    subtitle_vtt_path = Column(Text, nullable=True)

    # Metadata
    duration_seconds = Column(Float, nullable=True)
    num_speakers = Column(Integer, default=1)
    speaker_mapping = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="jobs")
    segments = relationship("TranscriptSegment", back_populates="job", cascade="all, delete-orphan")

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("dubbing_jobs.id"), nullable=False)

    speaker_id = Column(String(50), nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)

    # TTS
    audio_segment_path = Column(Text, nullable=True)
    voice_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("DubbingJob", back_populates="segments")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("DubbingJob", back_populates="user")

class LiveStreamSession(Base):
    __tablename__ = "live_stream_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    youtube_url = Column(Text, nullable=False)
    status = Column(String(50), default="active")  # active, paused, stopped, error

    # Real-time stats
    total_segments = Column(Integer, default=0)
    avg_latency_ms = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
