"""Speech-to-text transcription using Whisper."""
import os
import json
import tempfile
from typing import List, Dict, Any
import whisper
from whisper.utils import get_writer
from app.config import get_settings

settings = get_settings()

class TranscriptionService:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if self.model is None:
            print(f"Loading Whisper model: {settings.WHISPER_MODEL}")
            self.model = whisper.load_model(settings.WHISPER_MODEL)

    async def transcribe(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio file and return segments with timestamps."""
        result = self.model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            verbose=False,
            word_timestamps=True
        )

        segments = []
        for seg in result["segments"]:
            segments.append({
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
                "confidence": seg.get("avg_logprob", 0),
                "words": [
                    {"word": w["word"], "start": w["start"], "end": w["end"]}
                    for w in seg.get("words", [])
                ]
            })

        return {
            "text": result["text"],
            "language": result.get("language", language),
            "segments": segments,
            "duration": result.get("duration", 0)
        }

    async def transcribe_chunk(self, audio_chunk_path: str, language: str = "en") -> List[Dict]:
        """Transcribe a single audio chunk."""
        result = self.model.transcribe(
            audio_chunk_path,
            language=language,
            word_timestamps=False
        )
        return result.get("segments", [])

    async def save_transcript(self, segments: List[Dict], output_path: str):
        """Save transcript as JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

    async def generate_srt(self, segments: List[Dict], output_path: str):
        """Generate SRT subtitle file."""
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
                f.write(f"{seg['text']}\n\n")
