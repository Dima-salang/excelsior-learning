from sqlmodel import Session
from services.llm_service import LLMService
from models.quiz import Quiz


class QuizService:
    def __init__(self, session: Session, llm_service: LLMService):
        self.session = session
        self.llm_service = llm_service

    def save_quiz(self, quiz: Quiz):
        pass

    def start_quiz(self, deck_id: int, num_flashcards: int):
        pass

    def submit_answer(self, card_id: int, user_selected_ans: int):
        pass