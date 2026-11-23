"""Audio extraction and processing service."""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
from app.config import get_settings

settings = get_settings()

class AudioService:
    def __init__(self):
        os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)

    async def extract_from_youtube(self, url: str, job_id: str) -> Tuple[str, dict]:
        """Download audio from YouTube video/stream."""
        output_dir = os.path.join(settings.LOCAL_STORAGE_PATH, str(job_id))
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "audio.wav")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, 'audio.%(ext)s'),
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get('duration', 0)
            title = info.get('title', 'Unknown')

        return output_path, {"duration": duration, "title": title}

    async def extract_from_upload(self, file_path: str, job_id: str) -> str:
        """Extract audio from uploaded video file."""
        output_dir = os.path.join(settings.LOCAL_STORAGE_PATH, str(job_id))
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "audio.wav")

        cmd = [
            "ffmpeg", "-y", "-i", file_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path

    async def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration using ffprobe."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    async def chunk_audio(self, audio_path: str, chunk_duration: int = 10) -> list:
        """Split audio into chunks for processing."""
        output_dir = os.path.join(os.path.dirname(audio_path), "chunks")
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-f", "segment", "-segment_time", str(chunk_duration),
            "-c", "copy", os.path.join(output_dir, "chunk_%03d.wav")
        ]
        subprocess.run(cmd, capture_output=True)

        chunks = sorted([
            os.path.join(output_dir, f) 
            for f in os.listdir(output_dir) 
            if f.startswith("chunk_")
        ])
        return chunks
