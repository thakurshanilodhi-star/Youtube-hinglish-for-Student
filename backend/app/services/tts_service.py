"""Text-to-Speech service with Indian accent support."""
import os
import asyncio
import tempfile
from typing import List, Dict, Optional
import requests
from app.config import get_settings

settings = get_settings()

# Voice mapping for Indian accent TTS
VOICE_MAP = {
    "male": {
        "default": "en-IN-Wavenet-C",
        "alternative": "en-IN-Wavenet-B"
    },
    "female": {
        "default": "en-IN-Wavenet-A",
        "alternative": "en-IN-Wavenet-D"
    }
}

class TTSService:
    def __init__(self):
        self.elevenlabs_key = settings.ELEVENLABS_API_KEY
        self.use_elevenlabs = bool(self.elevenlabs_key)

    async def synthesize_segment(self, text: str, voice_id: str = "en-IN-Wavenet-C", 
                                  output_path: Optional[str] = None) -> str:
        """Synthesize speech for a text segment."""
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"tts_{hash(text)}.mp3")

        if self.use_elevenlabs:
            return await self._synthesize_elevenlabs(text, voice_id, output_path)
        else:
            return await self._synthesize_gcloud(text, voice_id, output_path)

    async def _synthesize_elevenlabs(self, text: str, voice_id: str, output_path: str) -> str:
        """Use ElevenLabs for high-quality voice cloning."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = await asyncio.to_thread(
            requests.post, url, json=data, headers=headers
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            raise RuntimeError(f"ElevenLabs TTS failed: {response.text}")

    async def _synthesize_gcloud(self, text: str, voice_id: str, output_path: str) -> str:
        """Use Google Cloud TTS as fallback."""
        # This requires GOOGLE_APPLICATION_CREDENTIALS
        # For demo, we'll create a placeholder
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            name=voice_id
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )

        response = await asyncio.to_thread(
            client.synthesize_speech,
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        return output_path

    async def synthesize_segments(self, segments: List[Dict], voice_gender: str = "male") -> List[Dict]:
        """Synthesize all segments and update paths."""
        voice = VOICE_MAP.get(voice_gender, VOICE_MAP["male"])["default"]

        for seg in segments:
            if seg.get("translated_text"):
                output_path = os.path.join(
                    settings.LOCAL_STORAGE_PATH,
                    f"tts_{seg['id']}.mp3"
                )
                try:
                    await self.synthesize_segment(seg["translated_text"], voice, output_path)
                    seg["audio_path"] = output_path
                except Exception as e:
                    print(f"TTS failed for segment {seg['id']}: {e}")
                    seg["audio_path"] = None

        return segments

    async def clone_voice(self, sample_audio_path: str, name: str) -> str:
        """Clone a voice from sample audio (ElevenLabs only)."""
        if not self.use_elevenlabs:
            raise ValueError("Voice cloning requires ElevenLabs API key")

        url = "https://api.elevenlabs.io/v1/voices/add"
        headers = {"xi-api-key": self.elevenlabs_key}

        with open(sample_audio_path, "rb") as f:
            files = {"files": f}
            data = {"name": name}
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, data=data, files=files
            )

        if response.status_code == 200:
            return response.json()["voice_id"]
        else:
            raise RuntimeError(f"Voice cloning failed: {response.text}")
