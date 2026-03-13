from sqlmodel import Session, select
from models.deck import Deck
from models.card import Card
from typing import List


class DeckService:
    def __init__(self, session: Session):
        self.session = session

    def get_decks(self, user_id: int) -> List[Deck]:
        statement = select(Deck).where(Deck.user_id == user_id)
        results = self.session.exec(statement)
        return results.all()

    def get_deck(self, deck_id: int) -> Deck:
        return self.session.get(Deck, deck_id)

    def get_cards(self, deck_id: int) -> List[Card]:
        statement = select(Card).where(Card.deck_id == deck_id)
        results = self.session.exec(statement)
        return results.all()
