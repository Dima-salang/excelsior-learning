from sqlmodel import Session, select
from services.llm_service import LLMService
from models.quiz import Quiz, QuizDB
from models.card import Card, CardStatus, QuizCard, QuizCardPublic
import random
from datetime import datetime, timedelta
from fastapi import HTTPException


class QuizService:
    def __init__(self, session: Session, llm_service: LLMService, quiz: Quiz = None):
        self.session = session
        self.llm_service = llm_service
        self.quiz: Quiz = quiz

    def save_quiz(self, quiz: Quiz):
        db_quiz = QuizDB(**quiz.model_dump(exclude={"cards"}))
        db_quiz.time_spent = (datetime.now() - quiz.time_started).total_seconds()
        self.session.merge(db_quiz)
        self.session.commit()
        return db_quiz

    # get quiz
    def get_quiz(self, quiz_id: int) -> Quiz:
        db_quiz = self.session.get(QuizDB, quiz_id)
        if not db_quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        cards = self.session.exec(
            select(QuizCard).where(QuizCard.quiz_id == quiz_id)
        ).all()
        quiz_model = Quiz.model_validate(db_quiz)
        quiz_model.cards = [QuizCardPublic.model_validate(qc) for qc in cards]
        return quiz_model

    # list the quizzes
    def list_quizzes(self, user_id: int) -> list[Quiz]:
        quizzes = self.session.exec(
            select(QuizDB)
            .where(QuizDB.user_id == user_id)
            .order_by(QuizDB.created_at.desc())
        ).all()
        result = []
        for q in quizzes:
            quiz_model = Quiz.model_validate(q)
            quiz_model.deck_title = q.deck.title if q.deck else "Unknown Deck"
            result.append(quiz_model)
        return result

    def start_quiz(
        self, deck_id: int, num_flashcards: int, random_order: bool = True, ignore_interval: bool = False
    ):
        # 1. Create the Quiz session record first to get an ID
        db_quiz = QuizDB(
            deck_id=deck_id, score=0.0, time_spent=0.0, time_started=datetime.now()
        )
        self.session.add(db_quiz)
        self.session.commit()
        self.session.refresh(db_quiz)

        # 2. Get cards from deck
        if ignore_interval:
            cards = self.session.exec(select(Card).where(Card.deck_id == deck_id)).all()
        else:
            cards = self.session.exec(select(Card).where(Card.deck_id == deck_id).where(Card.next_review <= datetime.now())).all()
        if random_order:
            random.shuffle(cards)

        # 3. Create and SAVE quiz card snapshots linked to this quiz
        selected_cards = cards[:num_flashcards]
        db_quiz_cards = self.create_quiz_cards(selected_cards, db_quiz.id)

        # 4. Return the full Quiz model for the frontend (clean serialization)
        quiz_model = Quiz.model_validate(db_quiz)
        quiz_model.cards = [QuizCardPublic.model_validate(qc) for qc in db_quiz_cards]
        return quiz_model

    def create_quiz_cards(
        self, cards: list[Card], quiz_id: int | None
    ) -> list[QuizCard]:
        quiz_cards = []
        for card in cards:
            # Create a snapshot object
            q_card = QuizCard(
                card_id=card.id,
                quiz_id=quiz_id,
                type=card.type,
                front=card.front,
                options=card.options,
                options_ans=card.options_ans,
                explanation=card.explanation,
                user_selected_ans=None,
                is_correct=None,
                status=card.status,
            )
            quiz_cards.append(q_card)

        self.session.add_all(quiz_cards)
        self.session.commit()
        return quiz_cards

    def submit_answer(
        self, quiz_card_id: int, user_selected_ans: int, quiz: Quiz, user_rating: int
    ) -> bool:
        if not user_rating:
            raise Exception("User must rate the card.")

        # find quiz card in the session storage (for logic)
        quiz_card = next((c for c in quiz.cards if c.id == quiz_card_id), None)
        if not quiz_card:
            raise Exception("Card not found in this quiz session")

        # get the actual QuizCard record from DB to update it
        db_quiz_card = self.session.get(QuizCard, quiz_card_id)
        if not db_quiz_card:
            raise Exception("Database record for QuizCard not found")

        # check if answer is correct using the snapshot data
        is_correct = db_quiz_card.options_ans == user_selected_ans

        # update the snapshot record
        db_quiz_card.user_selected_ans = user_selected_ans
        db_quiz_card.is_correct = is_correct
        db_quiz_card.status = (
            CardStatus.MASTERED if is_correct else CardStatus.NOT_MASTERED
        )

        if is_correct:
            quiz.score += 1

        # update the interval status for review
        self.update_card_interval(db_quiz_card.card_id, user_rating)

        # also update the original card's global status
        if db_quiz_card.card_id:
            original_card = self.session.get(Card, db_quiz_card.card_id)
            if original_card:
                original_card.status = db_quiz_card.status
                self.session.add(original_card)

        self.session.add(db_quiz_card)
        self.session.commit()

        # remove from the active queue
        quiz.cards.remove(quiz_card)

        return is_correct

    def update_card_interval(self, card_id: int, user_rating: int):
        # get the card
        card = self.session.get(Card, card_id)

        # growth of card
        ease_factor = card.ease_factor

        # streak
        repetition_count = card.repetition_count

        # card scheduling
        day_interval = card.day_interval

        # update ease factor
        ease_factor = ease_factor + (0.1 - (5 - user_rating) * (0.08 + (5 - user_rating) * 0.02))
        ease_factor = max(1.3, ease_factor)

        if user_rating >= 3:
            # correct
            if repetition_count == 0:
                day_interval = 1
            elif repetition_count == 1:
                day_interval = 3
            else:
                day_interval = round(day_interval * ease_factor)
            repetition_count += 1
        else:
            # incorrect

            # reset the rep count
            repetition_count = 0
            day_interval = 1

        card.ease_factor = ease_factor
        card.repetition_count = repetition_count
        card.day_interval = day_interval
        card.next_review = datetime.now() + timedelta(days=day_interval)

        self.session.add(card)
        self.session.commit()



        
