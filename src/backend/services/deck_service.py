from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from models.deck import Deck, DeckPublic, DeckPublicWithCards
from models.card import Card, CardPublic
from typing import List


class DeckService:
    def __init__(self, session: Session):
        self.session = session

    def get_decks(self, user_id: int) -> List[DeckPublic]:
        statement = (
            select(Deck).where(Deck.user_id == user_id).order_by(Deck.created_at.desc())
        )
        results = self.session.exec(statement)
        return results.all()

    def get_deck(self, deck_id: int) -> DeckPublicWithCards | None:
        statement = (
            select(Deck).where(Deck.id == deck_id).options(selectinload(Deck.cards))
        )
        result = self.session.exec(statement)
        return result.first()

    def get_cards(self, deck_id: int) -> List[CardPublic]:
        statement = select(Card).where(Card.deck_id == deck_id)
        results = self.session.exec(statement)
        return results.all()
