from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from db.session import get_session
from models.deck import DeckPublic, DeckPublicWithCards
from services.deck_service import DeckService

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=List[DeckPublic])
def get_decks(user_id: int, session: Session = Depends(get_session)):
    """
    Get all decks for a specific user.
    """
    service = DeckService(session)
    return service.get_decks(user_id)


@router.get("/{deck_id}", response_model=DeckPublicWithCards)
def get_deck(deck_id: int, session: Session = Depends(get_session)):
    """
    Get details of a specific deck, including its cards.
    """
    service = DeckService(session)
    deck = service.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck
