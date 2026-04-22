from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from db.session import get_session
from models.deck import DeckPublic, DeckPublicWithCards, DeckUpdate, Deck, DeckDelete
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


@router.get("/stats/by-deck")
def get_due_cards_by_deck(
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    Get due cards count per deck for a user.
    """
    service = DeckService(session)
    stats = service.get_due_cards_by_deck(user_id)
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


@router.get("/{deck_id}/card-count")
def get_deck_card_count(
    deck_id: int,
    session: Session = Depends(get_session),
):
    """
    Get total card count for a specific deck.
    """
    service = DeckService(session)
    deck = service.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return {"deck_id": deck_id, "card_count": len(deck.cards)}


@router.patch("/{deck_id}", response_model=DeckPublic)
def update_deck(
    deck_id: int, deck_update: DeckUpdate, session: Session = Depends(get_session)
):
    """
    Update a deck.
    """
    service = DeckService(session)
    deck = service.update_deck(deck_id, deck_update.dict(exclude_unset=True))
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return DeckPublic.model_validate(deck)


@router.delete("/{deck_id}")
def delete_deck(deck_id: int, session: Session = Depends(get_session)):
    """
    Delete a deck.
    """
    service = DeckService(session)
    success = service.delete_deck(deck_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deck not found")
    return {"message": "Deck deleted successfully"}
