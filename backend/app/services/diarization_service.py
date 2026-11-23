"""Speaker diarization service."""
from typing import List, Dict, Any
import torch
from pyannote.audio import Pipeline
from app.config import get_settings

settings = get_settings()

class DiarizationService:
    def __init__(self):
        self.pipeline = None
        self._load_pipeline()

    def _load_pipeline(self):
        try:
            # Uses pyannote/speaker-diarization from HuggingFace
            # Requires HF_TOKEN in env for gated model
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=os.getenv("HF_TOKEN")
            )
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
        except Exception as e:
            print(f"Warning: Could not load diarization pipeline: {e}")
            self.pipeline = None

    async def diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        """Perform speaker diarization on audio."""
        if self.pipeline is None:
            return [{"speaker": "SPEAKER_00", "start": 0, "end": 0}]

        diarization = self.pipeline(audio_path)

        speakers = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })

        return speakers

    async def assign_speakers_to_segments(self, segments: List[Dict], speakers: List[Dict]) -> List[Dict]:
        """Assign speaker labels to transcript segments based on overlap."""
        for seg in segments:
            seg_start = seg["start"]
            seg_end = seg["end"]
            seg_duration = seg_end - seg_start

            best_speaker = "SPEAKER_00"
            max_overlap = 0

            for spk in speakers:
                overlap_start = max(seg_start, spk["start"])
                overlap_end = min(seg_end, spk["end"])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = spk["speaker"]

            seg["speaker"] = best_speaker

        return segments
