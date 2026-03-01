from sqlmodel import SQLModel, create_engine
from models.user import User
from models.lecture import Lecture
from models.lecture_section import LectureSection
from models.lecture_step import LectureStep
from models.deck import Deck
from models.card import Card
from models.llm_provider import UserLLMConfig

sqlite_file_name = "db.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)