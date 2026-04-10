from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.session import get_session
from services.quiz_service import QuizService
from services.llm_service import LLMService
from models.quiz import Quiz
from pydantic import BaseModel


router = APIRouter(prefix="/quiz", tags=["quiz"])


def get_llm_service():
    return LLMService(get_session())


@router.post("/start/{deck_id}", response_model=Quiz)
def start_quiz(
    deck_id: int,
    num_flashcards: int = 10,
    random_order: bool = True,
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        quiz = service.start_quiz(deck_id, num_flashcards, random_order)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class SubmitAnswerRequest(BaseModel):
    card_id: int
    user_selected_ans: int
    quiz: Quiz


@router.post("/submit")
def submit_answer(
    request: SubmitAnswerRequest,
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        is_correct = service.submit_answer(
            request.card_id, request.user_selected_ans, request.quiz
        )
        return {"quiz": request.quiz, "is_correct": is_correct}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/save")
def save_quiz(
    quiz: Quiz,
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        db_quiz = service.save_quiz(quiz)
        return {"id": db_quiz.id, "message": "Quiz saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
