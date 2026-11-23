"""File upload handling."""
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from app.config import get_settings

settings = get_settings()
router = APIRouter()

ALLOWED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv'}

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Handle direct file upload."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    temp_path = os.path.join(settings.LOCAL_STORAGE_PATH, f"temp_{file.filename}")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"temp_path": temp_path, "filename": file.filename, "size": os.path.getsize(temp_path)}
