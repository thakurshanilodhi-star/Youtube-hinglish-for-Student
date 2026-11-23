# HinglishDub - AI YouTube Hinglish Dubbing Platform

Full-stack AI application that translates and dubs YouTube videos and live streams into natural Hinglish.

## Quick Start

```bash
# 1. Clone and setup
cp .env.example .env
# Edit .env with your API keys

# 2. Start with Docker
docker-compose up --build

# 3. Or start manually
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Features

- **Recorded Video Dubbing**: YouTube URLs & file uploads
- **Live Stream Translation**: Real-time with <3s latency
- **Speaker Diarization**: Multi-speaker support
- **Natural Hinglish**: AI-powered translation preserving technical terms
- **Subtitle Editor**: Fine-tune translations
- **Voice Cloning**: Optional ElevenLabs integration

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Tailwind CSS, Zustand |
| Backend | Python, FastAPI, SQLAlchemy, WebSockets |
| AI | Whisper, Gemini/OpenAI, pyannote.audio, TTS |
| Storage | PostgreSQL, Redis, S3-compatible |
