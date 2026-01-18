from pydantic import BaseModel
from typing import Optional


class VoiceResponse(BaseModel):
    id: str
    voice_id: str
    provider: str
    name: str
    model: str
    accent: Optional[str] = None

    class Config:
        from_attributes = True


class VoiceCreate(BaseModel):
    voice_id: str
    provider: str = "elevenlabs"
    name: str
    model: str
    accent: Optional[str] = None


class VoiceUpdate(BaseModel):
    voice_id: Optional[str] = None
    provider: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    accent: Optional[str] = None


class ErrorResponse(BaseModel):
    error: int
    message: str