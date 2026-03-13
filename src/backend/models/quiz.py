from pydantic import BaseModel
from models.card import Card

class Quiz(BaseModel):
    cards: list[Card]
    deck_id: int
    time_spent: int
    score: float
    
