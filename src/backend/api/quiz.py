from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.session import get_session
from services.quiz_service import QuizService
from services.llm_service import LLMService
from models.quiz import Quiz
from models.user import User
from api.auth.auth import get_current_user
from pydantic import BaseModel
from typing import Annotated


router = APIRouter(prefix="/quiz", tags=["quiz"])


def get_llm_service():
    return LLMService(get_session())


@router.get("/", response_model=list[Quiz])
def list_quizzes(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    return service.list_quizzes(current_user.id)


@router.get("/{quiz_id}", response_model=Quiz)
def get_quiz(
    quiz_id: int,
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        return service.get_quiz(quiz_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/start/{deck_id}", response_model=Quiz)
def start_quiz(
    deck_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    num_flashcards: int = 10,
    random_order: bool = True,
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        quiz = service.start_quiz(deck_id, num_flashcards, random_order)
        quiz.user_id = current_user.id
        return quiz
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class SubmitAnswerRequest(BaseModel):
    card_id: int
    user_selected_ans: int
    quiz: Quiz

    # between 0-5
    user_rating: int


@router.post("/submit")
def submit_answer(
    request: SubmitAnswerRequest,
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        is_correct = service.submit_answer(
            request.card_id, request.user_selected_ans, request.quiz, request.user_rating
        )
        return {"quiz": request.quiz, "is_correct": is_correct}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/save")
def save_quiz(
    quiz: Quiz,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(get_llm_service),
):
    service = QuizService(session, llm_service)
    try:
        quiz.user_id = current_user.id
        db_quiz = service.save_quiz(quiz)
        return {"id": db_quiz.id, "message": "Quiz saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
