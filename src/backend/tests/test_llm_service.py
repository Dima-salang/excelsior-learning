import os
import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session, select
from services.llm_service import LLMService, LLMProvider, CardList
from models.llm_provider import UserLLMConfig, UserLLMConfigCreate, UserLLMConfigUpdate
from models.lecture import Lecture
from models.lecture_section import LectureSection
from models.lecture_step import LectureStep
from models.deck import Deck
from models.card import Card, CardBase
from schema.lecture_schema_json import (
    LectureSchema,
    LectureSectionSchema,
    LectureStepSchema,
)
from models.deck import DeckWithCardsFlashcard
from cryptography.fernet import Fernet
from fastapi import HTTPException

# Constants for testing
MASTER_KEY = Fernet.generate_key().decode()


@pytest.fixture(autouse=True)
def setup_env():
    with patch.dict(os.environ, {"MASTER_KEY": MASTER_KEY}):
        yield


@pytest.fixture
def llm_service(session: Session):
    return LLMService(session)


# 1. SECRET MANAGEMENT TESTS
def test_encryption_decryption(llm_service):
    api_key = "test-api-key"
    encrypted = llm_service.encrypt_api_key(api_key)
    assert encrypted != api_key

    decrypted = llm_service.decrypt_api_key(encrypted)
    assert decrypted == api_key


def test_encryption_missing_master_key(llm_service):
    with patch.dict(os.environ, {"MASTER_KEY": ""}, clear=True):
        with pytest.raises(ValueError, match="MASTER_KEY not found"):
            llm_service.encrypt_api_key("key")


def test_decrypt_empty_key(llm_service):
    assert llm_service.decrypt_api_key(None) == ""
    assert llm_service.decrypt_api_key("") == ""


# 2. PROVIDER CRUD TESTS
def test_add_provider(llm_service, session):
    provider_data = UserLLMConfigCreate(
        provider_name="OpenAI", model_name="gpt-4", api_key="sk-123", user_id=1
    )
    db_provider = llm_service.add_provider(provider_data)

    assert db_provider.id is not None
    assert db_provider.provider_name == "OpenAI"
    # Key should be encrypted
    assert db_provider.api_key != "sk-123"
    assert llm_service.decrypt_api_key(db_provider.api_key) == "sk-123"


def test_get_providers(llm_service, session):
    p1 = UserLLMConfig(provider_name="P1", model_name="M1", api_key="K1", user_id=1)
    p2 = UserLLMConfig(provider_name="P2", model_name="M2", api_key="K2", user_id=1)
    p3 = UserLLMConfig(provider_name="P3", model_name="M3", api_key="K3", user_id=2)
    session.add_all([p1, p2, p3])
    session.commit()

    user_1_providers = llm_service.get_providers(user_id=1)
    assert len(user_1_providers) == 2


def test_get_provider_not_found(llm_service):
    with pytest.raises(HTTPException) as exc:
        llm_service.get_provider(999)
    assert exc.value.status_code == 404


def test_update_provider(llm_service, session):
    p = UserLLMConfig(provider_name="Old", model_name="Old", api_key="Old", user_id=1)
    session.add(p)
    session.commit()
    session.refresh(p)

    update_data = UserLLMConfigUpdate(
        provider_name="New",
        model_name="New",
        api_key="NewKey",
        base_url="http://new.com",
    )
    updated = llm_service.update_provider(p.id, update_data)
    assert updated.provider_name == "New"
    assert llm_service.decrypt_api_key(updated.api_key) == "NewKey"


def test_delete_provider(llm_service, session):
    p = UserLLMConfig(provider_name="ToDel", model_name="M", api_key="K", user_id=1)
    session.add(p)
    session.commit()

    llm_service.delete_provider(p.id)
    assert session.get(UserLLMConfig, p.id) is None


# 3. GENERATION TESTS (MOCKED)
@patch("services.llm_service.LLMProvider.generate")
def test_generate_lecture_success(mock_generate, llm_service, session):
    p = UserLLMConfig(
        provider_name="Gemini",
        model_name="gemini-pro",
        api_key=llm_service.encrypt_api_key("key"),
        user_id=1,
    )
    session.add(p)
    session.commit()

    mock_lecture = LectureSchema(
        title="Test Lecture",
        description="Desc",
        sections=[
            LectureSectionSchema(
                title="S1",
                order_key=1,
                steps=[LectureStepSchema(title="Step 1", order_key=1)],
            )
        ],
    )
    mock_generate.return_value = mock_lecture

    lecture = llm_service.generate_lecture("Topic", p.id, user_id=1)

    assert lecture.title == "Test Lecture"
    assert len(lecture.sections) == 1
    assert lecture.sections[0].title == "S1"
    assert len(lecture.sections[0].steps) == 1


def test_save_lecture_structure(llm_service, session):
    lecture_data = LectureSchema(
        title="Physics 101",
        description="Intro",
        sections=[
            LectureSectionSchema(
                title="Gravity",
                order_key=1,
                steps=[
                    LectureStepSchema(title="Newton", order_key=1),
                    LectureStepSchema(title="Einstein", order_key=2),
                ],
            )
        ],
    )

    db_lecture = llm_service.save_lecture(lecture_data, user_id=1)

    assert db_lecture.id is not None
    assert len(db_lecture.sections) == 1
    assert len(db_lecture.sections[0].steps) == 2
    # Verify deck creation
    assert db_lecture.deck is not None
    assert db_lecture.deck.title == "Physics 101"


@patch("services.llm_service.LLMProvider.generate")
def test_generate_cards_new_deck(mock_generate, llm_service, session):
    p = UserLLMConfig(
        provider_name="Gemini",
        model_name="gemini-pro",
        api_key=llm_service.encrypt_api_key("key"),
        user_id=1,
    )
    session.add(p)
    session.commit()

    mock_deck = DeckWithCardsFlashcard(
        title="New Deck",
        description="New Desc",
        cards=[
            CardBase(front="Q1", explanation="A1", type="basic"),
            CardBase(front="Q2", explanation="A2", type="basic"),
        ],
    )
    mock_generate.return_value = mock_deck

    deck_id = llm_service.generate_cards("Topic", p.id, user_id=1)

    db_deck = session.get(Deck, deck_id)
    assert db_deck.title == "New Deck"
    assert len(db_deck.cards) == 2


@patch("services.llm_service.LLMProvider.generate")
def test_generate_step_content(mock_generate, llm_service, session):
    p = UserLLMConfig(
        provider_name="Gemini",
        model_name="gemini-pro",
        api_key=llm_service.encrypt_api_key("key"),
        user_id=1,
    )
    lecture = Lecture(title="L", user_id=1)
    session.add_all([p, lecture])
    session.commit()

    section = LectureSection(title="S", lecture_id=lecture.id, order_key=1)
    session.add(section)
    session.commit()

    step = LectureStep(title="Step", lecture_section_id=section.id, order_key=1)
    session.add(step)
    session.commit()

    deck = Deck(title="D", user_id=1, lecture_id=lecture.id)
    session.add(deck)
    session.commit()

    class MockStepResponse:
        content = "Detailed content"
        flashcards = [CardBase(front="FQ", explanation="FA", type="basic")]

    mock_generate.return_value = MockStepResponse()

    result = llm_service.generate_step_content(lecture.id, step.id, p.id)

    assert result.content == "Detailed content"
    session.refresh(step)
    assert step.content == "Detailed content"

    cards = session.exec(select(Card).where(Card.deck_id == deck.id)).all()
    assert len(cards) == 1
    assert cards[0].front == "FQ"


def test_update_card(llm_service, session):
    card = Card(front="Old", explanation="OldExplanation", type="basic", deck_id=1)
    session.add(card)
    session.commit()
    session.refresh(card)

    update_data = {"front": "NewFront", "explanation": "NewExplanation"}
    updated = llm_service.update_card(card.id, update_data)

    assert updated.front == "NewFront"
    assert updated.explanation == "NewExplanation"


@patch("services.llm_service.genai.Client")
def test_get_model_list_success(mock_genai, llm_service):
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        mock_client = MagicMock()
        mock_genai.return_value = mock_client

        m1 = MagicMock()
        m1.name = "models/gemini-pro"
        m1.display_name = "Gemini Pro"
        m1.supported_generation_methods = ["generateContent"]

        m2 = MagicMock()
        m2.name = "models/embedding-001"
        m2.display_name = "Embedding 001"
        m2.supported_generation_methods = ["embedContent"]

        mock_client.models.list.return_value = [m1, m2]

        models = llm_service.get_model_list("gemini")
        assert len(models) == 1
        assert models[0]["name"] == "models/gemini-pro"


@patch("services.llm_service.LLMProvider.generate")
def test_generate_cards_existing_deck(mock_generate, llm_service, session):
    p = UserLLMConfig(
        provider_name="Gemini",
        model_name="gemini-pro",
        api_key=llm_service.encrypt_api_key("key"),
        user_id=1,
    )
    deck = Deck(title="Existing", user_id=1)
    session.add_all([p, deck])
    session.commit()

    mock_cards = CardList(cards=[CardBase(front="Q", explanation="A", type="basic")])
    mock_generate.return_value = mock_cards

    llm_service.generate_cards("Topic", p.id, user_id=1, deck_id=deck.id)

    session.refresh(deck)
    assert len(deck.cards) == 1


# 4. LLM PROVIDER LOGIC TESTS
def test_llm_provider_resolution():
    config = UserLLMConfig(
        provider_name="OpenAI", model_name="gpt-4", api_key="k", user_id=1
    )
    provider = LLMProvider(config, "k", MagicMock())

    schema = provider.resolve_json_schema("lecture")
    assert schema == LectureSchema

    with pytest.raises(HTTPException):
        provider.resolve_json_schema("invalid")


# 5. ERROR HANDLING TESTS
def test_get_model_list_missing_api_key(llm_service):
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
        with pytest.raises(HTTPException) as exc:
            llm_service.get_model_list("gemini")
        assert exc.value.status_code == 400


@patch("services.llm_service.LLMProvider.generate")
def test_generate_lecture_llm_failure(mock_generate, llm_service, session):
    p = UserLLMConfig(
        provider_name="Gemini",
        model_name="gemini-pro",
        api_key=llm_service.encrypt_api_key("key"),
        user_id=1,
    )
    session.add(p)
    session.commit()

    mock_generate.side_effect = Exception("LLM Down")

    with pytest.raises(HTTPException) as exc:
        llm_service.generate_lecture("Topic", p.id, user_id=1)
    assert exc.value.status_code == 500
    assert "Generation failed" in exc.value.detail
