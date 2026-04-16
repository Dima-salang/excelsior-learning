import pytest
from sqlmodel import Session
from services.deck_service import DeckService
from models.deck import Deck
from models.card import Card
from models.user import User
from models.lecture import Lecture
from models.lecture_section import LectureSection
from models.lecture_step import LectureStep
from models.quiz import QuizDB
from models.llm_provider import UserLLMConfig


def test_get_decks(session: Session):
    # Setup
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    deck1 = Deck(title="Deck 1", user_id=user.id)
    deck2 = Deck(title="Deck 2", user_id=user.id)
    session.add(deck1)
    session.add(deck2)
    session.commit()

    service = DeckService(session)

    # Execute
    decks, total = service.get_decks(user_id=user.id, limit=10, offset=0)

    # Assert
    assert total == 2
    assert len(decks) == 2
    assert decks[0].title == "Deck 2"
    assert decks[1].title == "Deck 1"


def test_get_decks_with_filter(session: Session):
    # Setup
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    deck1 = Deck(title="Deck 1", user_id=user.id)
    deck2 = Deck(title="Deck 2", user_id=user.id)
    session.add(deck1)
    session.add(deck2)
    session.commit()

    service = DeckService(session)

    # Execute
    decks, total = service.get_decks(
        user_id=user.id, limit=10, offset=0, filter={"title": "Deck 1"}
    )

    # Assert
    assert total == 2
    assert len(decks) == 1
    assert decks[0].title == "Deck 1"


def test_get_decks_returns_paginated_response(session: Session):
    # Setup
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    deck1 = Deck(title="Deck 1", user_id=user.id)
    deck2 = Deck(title="Deck 2", user_id=user.id)
    deck3 = Deck(title="Deck 3", user_id=user.id)
    session.add(deck1)
    session.add(deck2)
    session.add(deck3)
    session.commit()

    service = DeckService(session)

    # Execute
    decks, total = service.get_decks(user_id=user.id, limit=2, offset=0)

    # Assert
    assert total == 3
    assert len(decks) == 2
    assert decks[0].title == "Deck 3"
    assert decks[1].title == "Deck 2"

    # Execute
    decks, total = service.get_decks(user_id=user.id, limit=2, offset=2)

    # Assert
    assert total == 3
    assert len(decks) == 1
    assert decks[0].title == "Deck 1"


def test_get_deck(session: Session):
    # Setup
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    deck = Deck(title="Individual Deck", user_id=user.id)
    session.add(deck)
    session.commit()
    session.refresh(deck)

    service = DeckService(session)

    # Execute
    fetched_deck = service.get_deck(deck.id)

    # Assert
    assert fetched_deck is not None
    assert fetched_deck.id == deck.id
    assert fetched_deck.title == "Individual Deck"


def test_get_cards(session: Session):
    # Setup
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    deck = Deck(title="Card Deck", user_id=user.id)
    session.add(deck)
    session.commit()
    session.refresh(deck)

    card1 = Card(type="multichoice", front="Question 1", deck_id=deck.id)
    card2 = Card(type="truefalse", front="Question 2", deck_id=deck.id)
    session.add(card1)
    session.add(card2)
    session.commit()

    service = DeckService(session)

    # Execute
    cards = service.get_cards(deck.id)

    # Assert
    assert len(cards) == 2
    assert cards[0].front == "Question 1"
    assert cards[1].front == "Question 2"
    assert cards[0].deck_id == deck.id
