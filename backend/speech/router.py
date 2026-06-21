"""
InterviewGPT — Speech API Router
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from backend.database.models import User
from backend.auth.dependencies import get_current_user
from backend.speech.transcriber import transcribe_audio

router = APIRouter(prefix="/speech", tags=["Speech"])


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe an audio file to text using Faster Whisper.
    
    Accepts: WAV, WebM, MP3, M4A, OGG
    Returns: Transcription with segments and confidence.
    """
    allowed = [
        "audio/wav", "audio/webm", "audio/mpeg", "audio/mp4",
        "audio/ogg", "audio/x-wav", "audio/wave", "video/webm",
    ]
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {file.content_type}",
        )

    audio_bytes = await file.read()
    
    # Max 25MB for audio
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file too large. Maximum 25MB.",
        )

    try:
        result = await transcribe_audio(audio_bytes, file.filename)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
        )
