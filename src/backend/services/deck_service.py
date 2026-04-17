from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload
from models.deck import Deck, DeckPublic, DeckPublicWithCards
from models.card import Card, CardPublic
from models.lecture import Lecture
from typing import List, Optional
from datetime import datetime


class DeckService:
    def __init__(self, session: Session):
        self.session = session

    def get_decks(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        filter: Optional[dict] = None,
    ) -> tuple[list[DeckPublic], int]:
        statement = select(Deck).where(Deck.user_id == user_id)

        if filter and isinstance(filter, dict):
            title = filter.get("title")
            sort = filter.get("sort")

            if title:
                statement = statement.where(Deck.title.ilike(f"%{title}%"))

            if sort == "ascending":
                statement = statement.order_by(Deck.created_at.asc())
            else:
                statement = statement.order_by(Deck.created_at.desc())
        else:
            statement = statement.order_by(Deck.created_at.desc())

        count_statement = (
            select(func.count()).select_from(Deck).where(Deck.user_id == user_id)
        )
        total = self.session.exec(count_statement).first() or 0

        # Apply pagination
        statement = statement.limit(limit).offset(offset)
        results = self.session.exec(statement)
        decks = [DeckPublic.model_validate(deck) for deck in results.all()]

        return decks, total

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

    def get_due_cards_count(self, user_id: int) -> dict:
        now = datetime.now()
        statement = (
            select(func.count(Card.id))
            .join(Deck, Deck.id == Card.deck_id)
            .join(Lecture, Lecture.id == Deck.lecture_id)
            .where(Lecture.user_id == user_id)
            .where(Card.next_review != None)
            .where(Card.next_review <= now)
        )
        due_today = self.session.exec(statement).first() or 0

        return {"due_today": due_today, "past_due": 0}

    def update_deck(self, deck_id: int, deck_update: dict) -> Deck | None:
        deck = self.session.get(Deck, deck_id)
        if not deck:
            return None
        for key, value in deck_update.items():
            if hasattr(deck, key):
                setattr(deck, key, value)
        self.session.add(deck)
        self.session.commit()
        self.session.refresh(deck)
        return deck

    def delete_deck(self, deck_id: int) -> bool:
        deck = self.session.get(Deck, deck_id)
        if not deck:
            return False
        self.session.delete(deck)
        self.session.commit()
        return True
