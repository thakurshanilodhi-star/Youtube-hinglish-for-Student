"""FastAPI main application."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import engine, Base
from app.routers import jobs, auth, live, subtitles, upload

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered YouTube Hinglish Dubbing Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Dubbing Jobs"])
app.include_router(live.router, prefix="/api/v1/live", tags=["Live Streaming"])
app.include_router(subtitles.router, prefix="/api/v1/subtitles", tags=["Subtitles"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["File Upload"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}

@app.websocket("/ws/live/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    from app.services.live_service import LiveStreamService
    live_service = LiveStreamService()
    await live_service.handle_websocket(websocket, session_id)
