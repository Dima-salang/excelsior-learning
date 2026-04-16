import pytest
from unittest.mock import patch, MagicMock
from services.chat_service import ChatService
from services.llm_service import LLMService
from sqlmodel import Session
from models.chat import Chat, ChatMessage
from models.user import User
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from api.chat.chat import get_chat_service


client = TestClient(app)


# get chat service
@pytest.fixture
def chat_service(session: Session):
    chat_service = get_chat_service(session)
    return chat_service


# SETUP DATA
@pytest.fixture
def setup_data(session: Session):
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def test_add_chat_conversation(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    assert chat.id is not None
    assert chat.user_id == user.id
    assert chat.title == "Test Chat"
    assert chat.created_at is not None
    assert chat.updated_at is not None


def test_add_chat_conversation_invalid_lectureid(
    chat_service, session: Session, setup_data
):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.add_chat_conversation(user.id, 999, "Test Chat")
    assert excinfo.value.status_code == 404


def test_add_chat_conversation_invalid_userid(
    chat_service, session: Session, setup_data
):
    response = client.post(
        "/chat/conversation", json={"user_id": 999, "title": "Test Chat"}
    )
    assert response.status_code == 422


def test_get_chat_conversation(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # get chat conversation
    chat = chat_service.get_chat_conversation(user.id, chat.id)
    assert chat.id is not None
    assert chat.user_id == user.id
    assert chat.title == "Test Chat"
    assert chat.created_at is not None
    assert chat.updated_at is not None


def test_get_chat_conversation_invalid_chatid(
    chat_service, session: Session, setup_data
):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.get_chat_conversation(user.id, 999)
    assert excinfo.value.status_code == 404


def test_get_chat_conversation_invalid_userid(
    chat_service, session: Session, setup_data
):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.get_chat_conversation(999, user.id)
    assert excinfo.value.status_code == 404


def test_get_chat_conversations(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversations
    chat1 = Chat(user_id=user.id, title="Test Chat 1")
    chat2 = Chat(user_id=user.id, title="Test Chat 2")
    session.add(chat1)
    session.add(chat2)
    session.commit()
    session.refresh(chat1)
    session.refresh(chat2)

    # get chat conversations
    chats = chat_service.get_chat_conversations(user.id)
    assert len(chats) == 2
    assert chats[0].id is not None
    assert chats[0].user_id == user.id
    assert chats[0].title == "Test Chat 2"
    assert chats[0].created_at is not None
    assert chats[0].updated_at is not None
    assert chats[1].id is not None
    assert chats[1].user_id == user.id
    assert chats[1].title == "Test Chat 1"
    assert chats[1].created_at is not None
    assert chats[1].updated_at is not None


def test_update_chat_conversation(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # update chat conversation
    chat = chat_service.update_chat_conversation(user.id, chat.id, "Test Chat Updated")
    assert chat.id is not None
    assert chat.user_id == user.id
    assert chat.title == "Test Chat Updated"
    assert chat.created_at is not None
    assert chat.updated_at is not None


def test_update_chat_conversation_invalid_chatid(
    chat_service, session: Session, setup_data
):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.update_chat_conversation(
            user_id=user.id, chat_id=999, title="Test Chat Updated"
        )
    assert excinfo.value.status_code == 404


def test_update_chat_conversation_invalid_userid(
    chat_service, session: Session, setup_data
):
    user = setup_data

    # set up
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    with pytest.raises(HTTPException) as excinfo:
        chat_service.update_chat_conversation(
            user_id=999, chat_id=chat.id, title="Test Chat Updated"
        )
    assert excinfo.value.status_code == 403


def test_delete_chat_conversation(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # delete chat conversation
    chat_service.delete_chat_conversation(user.id, chat.id)

    # check if chat is deleted
    with pytest.raises(HTTPException) as excinfo:
        chat_service.get_chat_conversation(user.id, chat.id)
    assert excinfo.value.status_code == 404


def test_delete_chat_conversation_invalid_chatid(
    chat_service, session: Session, setup_data
):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.delete_chat_conversation(user.id, 999)
    assert excinfo.value.status_code == 404


def test_delete_chat_conversation_invalid_userid(
    chat_service, session: Session, setup_data
):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.delete_chat_conversation(999, user.id)
    assert excinfo.value.status_code == 404


def test_add_chat_message(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # add chat message
    chat_message = ChatMessage(
        chat_id=chat.id, role="user", content="Test Chat Message"
    )
    session.add(chat_message)
    session.commit()
    session.refresh(chat_message)

    assert chat_message.id is not None
    assert chat_message.chat_id == chat.id
    assert chat_message.role == "user"
    assert chat_message.content == "Test Chat Message"
    assert chat_message.created_at is not None


def test_add_chat_message_invalid_chatid(chat_service, session: Session, setup_data):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.add_chat_message(
            user_id=user.id, chat_id=999, role="user", content="Test Chat Message"
        )
    assert excinfo.value.status_code == 404


def test_add_chat_message_invalid_role(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    with pytest.raises(HTTPException) as excinfo:
        chat_service.add_chat_message(
            user_id=user.id,
            chat_id=chat.id,
            role="invalid",
            content="Test Chat Message",
        )
    assert excinfo.value.status_code == 400


def test_get_chat_messages(chat_service, session: Session, setup_data):
    user = setup_data

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # add chat messages
    chat_message1 = ChatMessage(
        chat_id=chat.id, role="user", content="Test Chat Message 1"
    )
    chat_message2 = ChatMessage(
        chat_id=chat.id, role="assistant", content="Test Chat Message 2"
    )
    session.add(chat_message1)
    session.add(chat_message2)
    session.commit()
    session.refresh(chat_message1)
    session.refresh(chat_message2)

    # get chat messages
    chat_messages = chat_service.get_chat_messages(user.id, chat.id)
    assert len(chat_messages) == 2
    assert chat_messages[0].id is not None
    assert chat_messages[0].chat_id == chat.id
    assert chat_messages[0].role == "user"
    assert chat_messages[0].content == "Test Chat Message 1"
    assert chat_messages[0].created_at is not None
    assert chat_messages[1].id is not None
    assert chat_messages[1].chat_id == chat.id
    assert chat_messages[1].role == "assistant"
    assert chat_messages[1].content == "Test Chat Message 2"
    assert chat_messages[1].created_at is not None


def test_get_chat_messages_invalid_chatid(chat_service, session: Session, setup_data):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.get_chat_messages(user_id=user.id, chat_id=999)
    assert excinfo.value.status_code == 404


def test_get_chat_messages_invalid_userid(chat_service, session: Session, setup_data):
    user = setup_data
    with pytest.raises(HTTPException) as excinfo:
        chat_service.get_chat_messages(user_id=999, chat_id=user.id)
    assert excinfo.value.status_code == 404


@patch("services.llm_service.LLMService.generate_chat_message")
def test_generate_chat_message(
    mock_generate_chat_message, chat_service, session: Session, setup_data
):
    user = setup_data

    mock_generate_chat_message.return_value = "This is a test response"

    # add chat conversation
    chat = Chat(user_id=user.id, title="Test Chat")
    session.add(chat)
    session.commit()
    session.refresh(chat)

    # generate chat message
    chat_message = chat_service.generate_chat_message(
        user.id, chat.id, "Test Chat Message", 1
    )
    assert chat_message.id is not None
    assert chat_message.chat_id == chat.id
    assert chat_message.role == "assistant"
    assert chat_message.content == "This is a test response"
    assert chat_message.created_at is not None
