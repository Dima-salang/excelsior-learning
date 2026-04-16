from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from db.session import get_session
from models.deck import DeckPublic, DeckPublicWithCards
from services.deck_service import DeckService
from schema.paginated_response import PaginatedResponse

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=PaginatedResponse[DeckPublic])
def get_decks(
    user_id: int, 
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0,
):
    """
    Get all decks for a specific user.
    """
    service = DeckService(session)
    decks, total = service.get_decks(user_id, limit, offset)
    return PaginatedResponse.from_sqlmodel(decks, total, limit, offset)


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
