"""Real-time live stream dubbing service."""
import asyncio
import json
import os
import tempfile
from typing import Dict, Set
import pyaudio
import numpy as np
from fastapi import WebSocket

from app.config import get_settings
from app.services.transcription_service import TranscriptionService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService

settings = get_settings()

class LiveStreamService:
    def __init__(self):
        self.active_streams: Dict[str, dict] = {}
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.transcription = TranscriptionService()
        self.translation = TranslationService()
        self.tts = TTSService()

    async def start_stream(self, session_id: str, youtube_url: str):
        """Start capturing and processing a YouTube live stream."""
        self.active_streams[session_id] = {
            "url": youtube_url,
            "status": "active",
            "buffer": [],
            "reconnect_count": 0
        }
        self.connections[session_id] = set()

        # Start processing loop
        asyncio.create_task(self._process_stream(session_id))

    async def stop_stream(self, session_id: str):
        """Stop a live stream session."""
        if session_id in self.active_streams:
            self.active_streams[session_id]["status"] = "stopped"

    async def handle_websocket(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connections for real-time audio/subtitle delivery."""
        await websocket.accept()

        if session_id not in self.connections:
            self.connections[session_id] = set()
        self.connections[session_id].add(websocket)

        try:
            while True:
                # Keep connection alive and handle client messages
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})

        except Exception:
            pass
        finally:
            self.connections[session_id].discard(websocket)

    async def _process_stream(self, session_id: str):
        """Main live processing loop."""
        import yt_dlp

        stream = self.active_streams.get(session_id)
        if not stream:
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
        }

        while stream["status"] == "active" and stream["reconnect_count"] < settings.LIVE_RECONNECT_ATTEMPTS:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(stream["url"], download=False)
                    audio_url = info["url"]

                # Stream processing would go here
                # For production, use ffmpeg to pipe audio chunks to Whisper
                await self._process_audio_chunks(session_id, audio_url)

            except Exception as e:
                stream["reconnect_count"] += 1
                await asyncio.sleep(2)

        stream["status"] = "stopped"

    async def _process_audio_chunks(self, session_id: str, audio_url: str):
        """Process audio chunks in real-time."""
        import subprocess

        cmd = [
            "ffmpeg", "-i", audio_url,
            "-f", "s16le", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", "-"
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        chunk_size = 16000 * 2 * settings.CHUNK_DURATION  # 10 seconds of audio

        while self.active_streams.get(session_id, {}).get("status") == "active":
            raw_audio = process.stdout.read(chunk_size)
            if not raw_audio:
                break

            # Save chunk to temp file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                # Write WAV header + data
                import wave
                with wave.open(f.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    wav_file.writeframes(raw_audio)
                temp_path = f.name

            try:
                # Transcribe chunk
                result = await self.transcription_service.transcribe_chunk(temp_path)

                for seg in result:
                    # Translate to Hinglish
                    translated = await self.translation_service.translate_live(seg["text"])

                    # TTS
                    audio_path = await self.tts.synthesize_segment(translated)

                    # Broadcast to all connected clients
                    await self._broadcast(session_id, {
                        "type": "segment",
                        "original": seg["text"],
                        "translated": translated,
                        "start": seg["start"],
                        "end": seg["end"],
                        "audio_url": audio_path  # In production, stream bytes
                    })

            finally:
                os.unlink(temp_path)

    async def _broadcast(self, session_id: str, message: dict):
        """Broadcast message to all WebSocket clients."""
        if session_id not in self.connections:
            return

        disconnected = set()
        for ws in self.connections[session_id]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        self.connections[session_id] -= disconnected
