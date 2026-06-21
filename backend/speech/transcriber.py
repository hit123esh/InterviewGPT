"""
InterviewGPT — Speech Transcription (Faster Whisper)

Handles audio transcription using the faster-whisper library.
Model is loaded once at startup for performance.
"""

import os
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

_model = None


def get_whisper_model():
    """Lazy-load the Faster Whisper model."""
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel
            from backend.config import get_settings
            settings = get_settings()
            _model = WhisperModel(
                settings.WHISPER_MODEL_SIZE,
                device=settings.WHISPER_DEVICE,
                compute_type=settings.WHISPER_COMPUTE_TYPE,
            )
            logger.info(f"Whisper model loaded: {settings.WHISPER_MODEL_SIZE}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    return _model


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> dict:
    """
    Transcribe audio bytes to text using Faster Whisper.
    
    Args:
        audio_bytes: Raw audio file bytes
        filename: Original filename for format detection
        
    Returns:
        {
            "text": str,           # Full transcription
            "segments": list,      # Individual segments with timestamps
            "language": str,       # Detected language
            "confidence": float,   # Average confidence score
        }
    """
    model = get_whisper_model()
    
    # Save to temp file (faster-whisper needs file path)
    suffix = os.path.splitext(filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments_gen, info = model.transcribe(
            tmp_path,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
        )

        segments = []
        full_text_parts = []
        total_confidence = 0.0
        segment_count = 0

        for segment in segments_gen:
            seg_data = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
                "confidence": round(segment.avg_log_prob, 3) if hasattr(segment, 'avg_log_prob') else 0.0,
            }
            segments.append(seg_data)
            full_text_parts.append(segment.text.strip())
            total_confidence += abs(seg_data["confidence"])
            segment_count += 1

        avg_confidence = (total_confidence / segment_count) if segment_count > 0 else 0.0

        return {
            "text": " ".join(full_text_parts),
            "segments": segments,
            "language": info.language,
            "confidence": round(min(avg_confidence * 100, 100), 1),
        }

    finally:
        os.unlink(tmp_path)
