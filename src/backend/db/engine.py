from sqlmodel import SQLModel, create_engine
from models.user import User
from models.lecture import Lecture
from models.lecture_section import LectureSection
from models.lecture_step import LectureStep
from models.deck import Deck
from models.card import Card
from models.llm_provider import UserLLMConfig
from models.quiz import Quiz, QuizDB
from models.chat import Chat, ChatMessage
import os
import logging

logger = logging.getLogger(__name__)

# get turso url from .env
turso_url = os.getenv("TURSO_DATABASE_URL")
turso_token = os.getenv("TURSO_AUTH_TOKEN")
supabase_url = os.getenv("SUPABASE_URL")
supabase_direct_url = os.getenv("SUPABASE_DIRECT_URL")
supabase_key = os.getenv("SUPABASE_KEY")
neon_url = os.getenv("DATABASE_URL")
DEBUG_FLAG = os.getenv("DEBUG", "False")

if turso_url and turso_token and DEBUG_FLAG == "False":
    try:
        if turso_url.startswith("libsql://"):
            engine = create_engine(turso_url, connect_args={"auth_token": turso_token})
        else:
            turso_host = turso_url.replace("https://", "").replace("http://", "")
            engine = create_engine(
                f"libsql://{turso_host}", connect_args={"auth_token": turso_token}
            )
        logger.info("Successfully connected to Turso database")
    except Exception as e:
        logger.error(f"Failed to connect to Turso database: {e}")
        raise e
elif supabase_direct_url and supabase_key and DEBUG_FLAG == "False":
    try:
        engine = create_engine(supabase_direct_url)
        logger.info("Successfully connected to Supabase database")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase database: {e}")
        raise e
elif neon_url and DEBUG_FLAG == "False":
    try:
        engine = create_engine(neon_url)
        logger.info("Successfully connected to Neon database")
    except Exception as e:
        logger.error(f"Failed to connect to Neon database: {e}")
        raise e
else:
    sqlite_file_name = "db.sqlite"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
