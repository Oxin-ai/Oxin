from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from bolna.auth.database import get_db
from bolna.voice_management.schemas import VoiceResponse
from bolna.voice_management.service import VoiceService

router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("/", response_model=List[VoiceResponse])
async def get_voices(db: Session = Depends(get_db)):
    """Get all voices."""
    voices = VoiceService.get_voices(db)
    return voices


@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(voice_id: str, db: Session = Depends(get_db)):
    """Get a specific voice by ID."""
    voice = VoiceService.get_voice(db, voice_id)
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice not found"
        )
    return voice