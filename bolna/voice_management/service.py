from sqlalchemy.orm import Session
from bolna.voice_management.models import Voice
from typing import List, Optional


class VoiceService:
    @staticmethod
    def get_voices(db: Session) -> List[Voice]:
        return db.query(Voice).all()

    @staticmethod
    def get_voice(db: Session, voice_id: str) -> Optional[Voice]:
        return db.query(Voice).filter(Voice.id == voice_id).first()