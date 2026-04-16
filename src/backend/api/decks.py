from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from db.session import get_session
from models.deck import DeckPublic, DeckPublicWithCards
from services.deck_service import DeckService
from schema.paginated_response import PaginatedResponse

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/stats/due")
def get_due_cards_stats(
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    Get count of cards due for review for a user.
    """
    service = DeckService(session)
    stats = service.get_due_cards_count(user_id)
    return stats


@router.get("/", response_model=PaginatedResponse[DeckPublic])
def get_decks(
    user_id: int,
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = Query(None, description="Search by title"),
    sort: Optional[str] = Query(
        None, description="Sort order: 'ascending' or 'descending'"
    ),
):
    """
    Get all decks for a specific user.
    """
    # Build filter options
    filter_options = {}
    if search:
        filter_options["title"] = search
    if sort:
        filter_options["sort"] = sort

    service = DeckService(session)
    decks, total = service.get_decks(
        user_id, limit, offset, filter_options if filter_options else None
    )
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
