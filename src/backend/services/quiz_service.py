from sqlmodel import Session
from services.llm_service import LLMService
from models.quiz import Quiz, QuizDB
from models.card import Card, CardStatus
import random
from datetime import datetime


class QuizService:
    def __init__(self, session: Session, llm_service: LLMService, quiz: Quiz = None):
        self.session = session
        self.llm_service = llm_service
        self.quiz: Quiz = quiz

    def save_quiz(self, quiz: Quiz):
        db_quiz = QuizDB(**quiz.dict(exclude={"cards"}))
        db_quiz.time_spent = (datetime.now() - quiz.time_started).total_seconds()
        self.session.merge(db_quiz)
        self.session.commit()
        return db_quiz

    def start_quiz(self, deck_id: int, num_flashcards: int, random_order: bool = True):
        # get cards from deck
        cards = self.session.query(Card).filter(Card.deck_id == deck_id).all()
        if random_order:
            random.shuffle(cards)
        return Quiz(
            cards=cards[:num_flashcards], deck_id=deck_id, time_spent=0, score=0.0
        )

    def submit_answer(self, card_id: int, user_selected_ans: int, quiz: Quiz) -> bool:
        # get card from session to check answer
        card = self.session.get(Card, card_id)
        if not card:
            raise Exception("Card not found")

        # find card in quiz queue
        quiz_card = next((c for c in quiz.cards if c.id == card_id), None)
        if not quiz_card:
            raise Exception("Card not in this quiz session")

        # check if answer is correct
        is_correct = card.options_ans == user_selected_ans
        if is_correct:
            quiz.score += 1

        # remove card from quiz queue
        quiz.cards.remove(quiz_card)

        # update card status
        if is_correct:
            card.status = CardStatus.MASTERED
        else:
            card.status = CardStatus.NOT_MASTERED

        # return whether answer is correct
        return is_correct
