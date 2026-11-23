"""Main processing pipeline orchestrator."""
import os
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import AsyncSessionLocal
from app.models.models import DubbingJob, JobStatus, TranscriptSegment
from app.config import get_settings
from app.services.audio_service import AudioService
from app.services.transcription_service import TranscriptionService
from app.services.diarization_service import DiarizationService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService

settings = get_settings()

class PipelineService:
    def __init__(self):
        self.audio_service = AudioService()
        self.transcription_service = TranscriptionService()
        self.diarization_service = DiarizationService()
        self.translation_service = TranslationService()
        self.tts_service = TTSService()

    async def process_job(self, job_id: str):
        """Main pipeline: Extract → Transcribe → Diarize → Translate → TTS → Merge."""
        async with AsyncSessionLocal() as db:
            try:
                await self._update_job(db, job_id, JobStatus.PROCESSING, 5)

                job = await self._get_job(db, job_id)

                # 1. Extract Audio
                if job.source_type.value == "youtube":
                    audio_path, meta = await self.audio_service.extract_from_youtube(job.source_url, job_id)
                    job.title = meta.get("title", job.title)
                    job.duration_seconds = meta.get("duration", 0)
                else:
                    audio_path = await self.audio_service.extract_from_upload(job.storage_path, job_id)
                    job.duration_seconds = await self.audio_service.get_audio_duration(audio_path)

                await self._update_job(db, job_id, JobStatus.TRANSCRIBING, 20)

                # 2. Transcribe
                transcript_result = await self.transcription_service.transcribe(audio_path)
                segments = transcript_result["segments"]

                # 3. Speaker Diarization
                speakers = await self.diarization_service.diarize(audio_path)
                segments = await self.diarization_service.assign_speakers_to_segments(segments, speakers)
                job.num_speakers = len(set(s["speaker"] for s in speakers))

                await self._update_job(db, job_id, JobStatus.TRANSLATING, 40)

                # 4. Translate to Hinglish
                segments = await self.translation_service.translate_segments(segments)

                # Save transcript
                transcript_path = os.path.join(settings.LOCAL_STORAGE_PATH, job_id, "transcript.json")
                await self.transcription_service.save_transcript(segments, transcript_path)
                job.transcript_path = transcript_path

                await self._update_job(db, job_id, JobStatus.SYNTHESIZING, 60)

                # 5. Text-to-Speech
                segments = await self.tts_service.synthesize_segments(segments)

                # Save segments to DB
                for seg in segments:
                    db_seg = TranscriptSegment(
                        job_id=uuid.UUID(job_id),
                        speaker_id=seg.get("speaker", "SPEAKER_00"),
                        start_time=seg["start"],
                        end_time=seg["end"],
                        original_text=seg["text"],
                        translated_text=seg.get("translated_text", ""),
                        audio_segment_path=seg.get("audio_path")
                    )
                    db.add(db_seg)

                await self._update_job(db, job_id, JobStatus.SYNTHESIZING, 80)

                # 6. Merge audio and generate subtitles
                dubbed_path = await self._merge_audio_segments(segments, job_id)
                job.dubbed_audio_path = dubbed_path

                srt_path = os.path.join(settings.LOCAL_STORAGE_PATH, job_id, "subtitles.srt")
                vtt_path = os.path.join(settings.LOCAL_STORAGE_PATH, job_id, "subtitles.vtt")
                await self.transcription_service.generate_srt(segments, srt_path)
                await self._generate_vtt(segments, vtt_path)

                job.subtitle_srt_path = srt_path
                job.subtitle_vtt_path = vtt_path

                await self._update_job(db, job_id, JobStatus.COMPLETED, 100)

            except Exception as e:
                await self._update_job(db, job_id, JobStatus.FAILED, 0, str(e))
                raise

    async def _get_job(self, db: AsyncSession, job_id: str) -> DubbingJob:
        result = await db.execute(select(DubbingJob).where(DubbingJob.id == uuid.UUID(job_id)))
        return result.scalar_one()

    async def _update_job(self, db: AsyncSession, job_id: str, status: JobStatus, progress: float, error: Optional[str] = None):
        result = await db.execute(select(DubbingJob).where(DubbingJob.id == uuid.UUID(job_id)))
        job = result.scalar_one()
        job.status = status
        job.progress_percent = progress
        if error:
            job.error_message = error
        await db.commit()

    async def _merge_audio_segments(self, segments: list, job_id: str) -> str:
        """Merge all TTS segments into final dubbed audio."""
        from pydub import AudioSegment

        output_path = os.path.join(settings.LOCAL_STORAGE_PATH, job_id, "dubbed_audio.mp3")
        combined = AudioSegment.empty()

        current_time = 0.0
        for seg in segments:
            seg_audio_path = seg.get("audio_path")
            if seg_audio_path and os.path.exists(seg_audio_path):
                # Add silence to maintain timing
                silence_duration = int((seg["start"] - current_time) * 1000)
                if silence_duration > 0:
                    combined += AudioSegment.silent(duration=silence_duration)

                audio = AudioSegment.from_mp3(seg_audio_path)
                combined += audio
                current_time = seg["end"]

        combined.export(output_path, format="mp3")
        return output_path

    async def _generate_vtt(self, segments: list, output_path: str):
        """Generate WebVTT subtitle file."""
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for seg in segments:
                text = seg.get("translated_text") or seg["text"]
                f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
                f.write(f"{text}\n\n")
