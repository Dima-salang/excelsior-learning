from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from db.session import get_session
from models.deck import DeckPublic
from services.deck_service import DeckService

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=List[DeckPublic])
def get_decks(user_id: int, session: Session = Depends(get_session)):
    """
    Get all decks for a specific user.
    """
    service = DeckService(session)
    return service.get_decks(user_id)