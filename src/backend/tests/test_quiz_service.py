import pytest
from sqlmodel import Session
from services.quiz_service import QuizService
from services.llm_service import LLMService
from models.card import Card, CardStatus, QuizCard
from models.deck import Deck
from models.user import User
from models.quiz import Quiz, QuizDB
from datetime import datetime


@pytest.fixture
def quiz_service(session: Session):
    llm_service = LLMService(session)
    return QuizService(session, llm_service)


@pytest.fixture
def setup_data(session: Session, quiz_service: QuizService):
    # Setup test user
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Setup test deck
    deck = Deck(title="Test Deck", user_id=user.id)
    session.add(deck)
    session.commit()
    session.refresh(deck)

    # Setup test cards
    cards = [
        Card(
            front=f"Front {i}",
            type="multiple-choice",
            options=["A", "B", "C", "D"],
            options_ans=0,
            deck_id=deck.id,
        )
        for i in range(5)
    ]
    session.add_all(cards)
    session.commit()

    # create quiz
    quiz_model = quiz_service.start_quiz(deck.id, num_flashcards=3)

    return user, deck, cards, quiz_model


def test_start_quiz(quiz_service: QuizService, setup_data, session: Session):
    user, deck, cards, _ = setup_data

    # Start quiz with 3 cards
    quiz_model = quiz_service.start_quiz(deck.id, num_flashcards=3)

    # 1. Verify QuizDB record
    assert quiz_model.id is not None
    db_quiz = session.get(QuizDB, quiz_model.id)
    assert db_quiz is not None
    assert db_quiz.deck_id == deck.id

    # 2. Verify QuizCard snapshots
    assert len(quiz_model.cards) == 3
    for q_card in quiz_model.cards:
        assert q_card.quiz_id == quiz_model.id
        assert q_card.card_id is not None
        # Verify content snapshot
        assert q_card.front.startswith("Front")
        assert q_card.options == ["A", "B", "C", "D"]
        assert q_card.options_ans == 0
        assert q_card.user_selected_ans is None


def test_submit_answer_correct(quiz_service: QuizService, setup_data, session: Session):
    user, deck, cards, _ = setup_data
    quiz_model = quiz_service.start_quiz(deck.id, num_flashcards=1)
    quiz_card = quiz_model.cards[0]
    user_rating = 3

    # Submit correct answer (idx 0 based on setup_data)
    is_correct = quiz_service.submit_answer(quiz_card.id, 0, quiz_model, user_rating)

    assert is_correct is True
    assert quiz_model.score == 1

    # Verify DB update in snapshot
    db_quiz_card = session.get(QuizCard, quiz_card.id)
    assert db_quiz_card.user_selected_ans == 0
    assert db_quiz_card.is_correct is True
    assert db_quiz_card.status == CardStatus.MASTERED

    # Verify global card update
    original_card = session.get(Card, db_quiz_card.card_id)
    assert original_card.status == CardStatus.MASTERED


def test_submit_answer_incorrect(
    quiz_service: QuizService, setup_data, session: Session
):
    user, deck, cards, _ = setup_data
    quiz_model = quiz_service.start_quiz(deck.id, num_flashcards=1)
    quiz_card = quiz_model.cards[0]
    user_rating = 1

    # Submit incorrect answer (expected 0, giving 1)
    is_correct = quiz_service.submit_answer(quiz_card.id, 1, quiz_model, user_rating)

    assert is_correct is False
    assert quiz_model.score == 0

    # Verify DB update in snapshot
    db_quiz_card = session.get(QuizCard, quiz_card.id)
    assert db_quiz_card.is_correct is False
    assert db_quiz_card.status == CardStatus.NOT_MASTERED

    # Verify global card update
    original_card = session.get(Card, db_quiz_card.card_id)
    assert original_card.status == CardStatus.NOT_MASTERED


def test_get_quiz_persistence(quiz_service: QuizService, setup_data, session: Session):
    user, deck, cards, _ = setup_data
    start_model = quiz_service.start_quiz(deck.id, num_flashcards=1)
    quiz_card_id = start_model.cards[0].id
    user_rating = 3

    # Answer and then retrieve
    quiz_service.submit_answer(quiz_card_id, 0, start_model, user_rating)

    # Retrieve from DB using the service
    retrieved_quiz = quiz_service.get_quiz(start_model.id)

    assert retrieved_quiz.id == start_model.id
    assert len(retrieved_quiz.cards) == 1
    assert retrieved_quiz.cards[0].user_selected_ans == 0
    assert retrieved_quiz.cards[0].is_correct is True


def test_list_quizzes(quiz_service: QuizService, setup_data, session: Session):
    user, deck, cards, _ = setup_data

    # Create two quizzes for this user
    q1 = quiz_service.start_quiz(deck.id, 1)
    q1.user_id = user.id
    quiz_service.save_quiz(q1)

    q2 = quiz_service.start_quiz(deck.id, 1)
    q2.user_id = user.id
    quiz_service.save_quiz(q2)

    # Create one for another user
    other_user = User(username="other", password="p")
    session.add(other_user)
    session.commit()
    q3 = quiz_service.start_quiz(deck.id, 1)
    q3.user_id = other_user.id
    quiz_service.save_quiz(q3)

    user_quizzes = quiz_service.list_quizzes(user.id)
    assert len(user_quizzes) == 2
    # Verify ordering (newest first)
    assert user_quizzes[0].id == q2.id
    assert user_quizzes[1].id == q1.id


def test_create_quiz_cards(quiz_service: QuizService, setup_data, session: Session):
    user, deck, cards, quiz_model = setup_data
    quiz_model.cards = quiz_service.create_quiz_cards(
        cards=quiz_model.cards, quiz_id=quiz_model.id
    )

    # verify that the quiz model has 3 cards
    assert len(quiz_model.cards) == 3

    # verify that the cards are QuizCards
    assert all([isinstance(card, QuizCard) for card in quiz_model.cards])

    # verify that the cards are linked to the quiz
    assert all([card.quiz_id == quiz_model.id for card in quiz_model.cards])


def test_update_card_interval(quiz_service: QuizService, setup_data, session: Session):
    user, deck, cards, quiz_model = setup_data
    quiz_card = quiz_model.cards[0]
    original_card = session.get(Card, quiz_card.card_id)
    user_rating = 5

    # get ease factor
    ease_factor = original_card.ease_factor

    # compute ease factor
    ease_factor = ease_factor + (
        0.1 - (5 - user_rating) * (0.08 + (5 - user_rating) * 0.02)
    )
    ease_factor = max(1.3, ease_factor)

    # update the interval status for review
    quiz_service.update_card_interval(quiz_card.card_id, user_rating)

    # verify the card's interval status
    assert original_card.ease_factor == ease_factor
    assert original_card.repetition_count == 1
    assert original_card.day_interval == 1
