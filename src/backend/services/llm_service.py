from models.llm_provider import (
    UserLLMConfig,
    UserLLMConfigBase,
    UserLLMConfigCreate,
    UserLLMConfigUpdate,
    UserLLMConfigPublic,
)
from models.lecture import Lecture
from models.lecture_section import LectureSection
from models.lecture_step import LectureStep
from models.deck import Deck, DeckWithCardsFlashcard, DeckPublicWithCards
from pydantic import BaseModel
from schema.lecture_schema_json import LectureSchema, LectureStepSchema
from sqlmodel import Session
from cryptography.fernet import Fernet
import os
from fastapi import HTTPException
from google import genai
from datetime import datetime
from models.card import Card, CardBase
from models.llm_provider import PromptManager
from models.lecture import LectureStepPublic
import requests
import litellm

# url for openrouter model api
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


import logging

logger = logging.getLogger("excelsior.llm")


class CardList(BaseModel):
    cards: list[CardBase]


class LLMService:
    prompt_manager: PromptManager
    PROVIDER_NOT_FOUND = "Provider not found"

    def __init__(self, session: Session):
        self.session = session
        self.prompt_manager = PromptManager()

    def get_model_list(self):
        # get the model list from openrouter
        response = requests.get(OPENROUTER_MODELS_URL)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=response.text)

        # extract id and name
        model_list = []
        for model in response.json()["data"]:
            model_list.append({"name": model["id"], "display_name": model["name"]})

        return model_list

    def add_provider(self, provider: UserLLMConfigCreate):
        db_provider = UserLLMConfig(**provider.model_dump())
        db_provider.api_key = self.encrypt_api_key(provider.api_key)
        self.session.add(db_provider)
        self.session.commit()
        self.session.refresh(db_provider)
        return db_provider

    def get_provider(self, provider_id: int) -> UserLLMConfigPublic:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)
        return provider

    def get_providers(self, user_id: int) -> list[UserLLMConfigPublic]:
        from sqlmodel import select

        providers = self.session.exec(
            select(UserLLMConfig)
            .filter(UserLLMConfig.user_id == user_id)
            .order_by(UserLLMConfig.created_at.desc())
        ).all()
        return [UserLLMConfigPublic.model_validate(provider) for provider in providers]

    def update_provider(
        self, provider_id: int, provider_update: UserLLMConfigUpdate
    ) -> UserLLMConfigPublic:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)
        provider.provider_name = provider_update.provider_name
        provider.model_name = provider_update.model_name
        provider.api_key = self.encrypt_api_key(provider_update.api_key)
        provider.base_url = provider_update.base_url
        self.session.add(provider)
        self.session.commit()
        self.session.refresh(provider)
        return provider

    def delete_provider(self, provider_id: int) -> UserLLMConfigPublic:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)
        self.session.delete(provider)
        self.session.commit()
        return provider

    # get api key by provider for reuse
    def get_api_key(self, provider_id: int) -> str:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)
        return self.decrypt_api_key(provider.api_key)

    def encrypt_api_key(self, api_key: str) -> str:
        # get the master key
        master_key = os.getenv("MASTER_KEY")
        if not master_key:
            raise ValueError("MASTER_KEY not found in environment variables")

        f = Fernet(master_key)
        return f.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self, api_key: str | None) -> str:
        if not api_key:
            return ""
        # get the master key
        master_key = os.getenv("MASTER_KEY")
        if not master_key:
            raise ValueError("MASTER_KEY not found in environment variables")

        f = Fernet(master_key)
        return f.decrypt(api_key.encode()).decode()

    # LECTURES
    def generate_lecture(self, prompt: str, provider_id: int, user_id: int) -> Lecture:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)

        # decrypt the api key
        api_key = self.decrypt_api_key(provider.api_key)

        # create llm provider
        llm_provider = LLMProvider(
            provider, api_key, prompt_manager=self.prompt_manager
        )

        try:
            # generate lecture
            lecture = llm_provider.generate(prompt, type="lecture")
            if not lecture or not hasattr(lecture, "title"):
                raise HTTPException(
                    status_code=500,
                    detail="LLM failed to generate valid lecture structure",
                )

            # save and return lecture
            return self.save_lecture(lecture, user_id)
        except Exception as e:
            logger.error(f"Error generating lecture: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    def save_lecture(self, lecture: LectureSchema, user_id: int) -> Lecture:
        # create lecture
        db_lecture = Lecture(
            title=lecture.title,
            description=lecture.description,
            user_id=user_id,
            completion_percentage=0.0,
        )
        self.session.add(db_lecture)
        self.session.commit()
        self.session.refresh(db_lecture)

        for section_schema in lecture.sections:
            db_section = LectureSection(
                title=section_schema.title,
                order_key=section_schema.order_key,
                lecture_id=db_lecture.id,
            )
            self.session.add(db_section)
            self.session.commit()
            self.session.refresh(db_section)

            for step_schema in section_schema.steps:
                db_step = LectureStep(
                    title=step_schema.title,
                    order_key=step_schema.order_key,
                    lecture_section_id=db_section.id,
                )
                self.session.add(db_step)

            self.session.commit()

        # create a deck for the lecture
        db_deck = Deck(
            title=lecture.title,
            description=lecture.description,
            user_id=user_id,
            lecture_id=db_lecture.id,
            lecture=db_lecture,
        )
        self.session.add(db_deck)
        self.session.commit()
        self.session.refresh(db_deck)

        self.session.refresh(db_lecture)
        return db_lecture

    # FLASHCARDS
    def generate_cards(
        self,
        prompt: str,
        provider_id: int,
        user_id: int,
        deck_id: int = None,
        num_flashcards: int = 10,
        difficulty: str = "normal",
    ) -> int:
        logger.info(
            f"Initiating card generation for user {user_id} (Deck: {deck_id or 'New'})"
        )
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)

        # decrypt the api key
        api_key = self.decrypt_api_key(provider.api_key)

        # create llm provider
        llm_provider = LLMProvider(
            provider, api_key, prompt_manager=self.prompt_manager
        )

        # generate flashcards
        data = llm_provider.generate(
            prompt,
            type="flashcard" if deck_id else "deck",
            num_flashcards=num_flashcards,
            difficulty=difficulty,
        )

        # save and return flashcards
        return self.save_cards(data, user_id, deck_id)

    def save_cards(
        self,
        data: DeckWithCardsFlashcard | CardList,
        user_id: int,
        deck_id: int = None,
    ) -> int:
        # create a deck for the flashcards if it does not exist
        if not deck_id:
            db_deck = Deck(
                title=data.title,
                description=data.description,
                user_id=user_id,
            )
            self.session.add(db_deck)
            self.session.commit()
            self.session.refresh(db_deck)
        else:
            # get the deck
            db_deck = self.session.get(Deck, deck_id)
            if not db_deck:
                raise HTTPException(status_code=404, detail="Deck not found")

        # create cards
        for card_schema in data.cards:
            db_card = Card(
                **card_schema.model_dump(),
                deck_id=db_deck.id,
            )
            self.session.add(db_card)

        self.session.commit()
        self.session.refresh(db_deck)
        return db_deck.id

    # CHAT
    def generate_chat(self, prompt: str, provider_id: int) -> str:
        pass

    def generate_step_content(self, lecture_id: int, step_id: int, provider_id: int):

        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=self.PROVIDER_NOT_FOUND)

        lecture = self.session.get(Lecture, lecture_id)
        step = self.session.get(LectureStep, step_id)

        if not lecture or not step:
            raise HTTPException(status_code=404, detail="Lecture or Step not found")

        # decrypt the api key
        api_key = self.decrypt_api_key(provider.api_key)

        llm_provider = LLMProvider(
            provider, api_key, prompt_manager=self.prompt_manager
        )

        # We need context for the generation
        section = self.session.get(LectureSection, step.lecture_section_id)
        prompt = (
            f"Lecture: {lecture.title}\nSection: {section.title}\nStep: {step.title}"
        )

        try:
            # generate content
            data = llm_provider.generate(prompt, type="step")

            if not data or not hasattr(data, "content"):
                raise HTTPException(
                    status_code=500, detail="LLM failed to generate valid content"
                )

            # save the step to the db
            step.content = data.content
            step.updated_at = datetime.now()
            self.session.add(step)
            self.session.commit()
            self.session.refresh(step)

            if hasattr(data, "flashcards") and data.flashcards:
                self.save_step_cards(step_id, data.flashcards)

            return LectureStepPublic.model_validate(step)
        except Exception as e:
            logger.error(f"Error generating step content: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    def update_card(self, card_id: int, card_update: dict) -> Card:
        card = self.session.get(Card, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        for key, value in card_update.items():
            setattr(card, key, value)

        card.updated_at = datetime.now()
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card

    def save_step_cards(self, step_id: int, cards: list) -> None:
        # get the deck associated with the lecture
        step = self.session.get(LectureStep, step_id)
        lecture = step.lecture_section.lecture
        deck = lecture.deck

        to_save = []
        for card_data in cards:
            to_save.append(
                Card(
                    type=card_data.type,
                    front=card_data.front,
                    options=card_data.options,
                    options_ans=card_data.options_ans,
                    explanation=card_data.explanation,
                    step_id=step_id,
                    deck_id=deck.id,
                )
            )
        self.session.add_all(to_save)
        self.session.commit()


class LLMProvider:
    def __init__(
        self, config: UserLLMConfigBase, api_key: str, prompt_manager: PromptManager
    ):
        self.config = config
        self.api_key = api_key
        self.prompt_manager = prompt_manager

    def generate(
        self,
        user_prompt: str,
        type: str,
        num_flashcards: int | None = None,
        difficulty: str | None = None,
    ) -> str:
        # resolve the type
        json_schema = self.resolve_json_schema(type)
        prompt = self.resolve_prompt(
            type,
            topic=user_prompt,
            num_flashcards=num_flashcards,
            difficulty=difficulty,
        )
        provider = self.config.provider_name.lower()

        # load api key into environment
        os.environ[f"{provider.upper()}_API_KEY"] = self.api_key

        model_name = self.config.model_name
        # litellm expects "openrouter/" prefix for OpenRouter models
        if provider == "openrouter" and not model_name.startswith("openrouter/"):
            model_name = f"openrouter/{model_name}"

            # Setup litellm completion kwargs
            litellm_kwargs = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt
                        + f"Return as JSON matching this schema: {json_schema.model_json_schema()}",
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                "response_format": {"type": "json_object"},
            }

            # apply custom api_base if configured
            if getattr(self.config, "base_url", None):
                litellm_kwargs["api_base"] = self.config.base_url

            # litellm completion
            response = litellm.completion(**litellm_kwargs)
            content = response["choices"][0]["message"]["content"]
            return json_schema.model_validate_json(content)

        if provider == "gemini":
            os.environ["GEMINI_API_KEY"] = self.api_key
            client = genai.Client()

            system_instruction = prompt
            user_content = user_prompt

            config = genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=json_schema.model_json_schema(),
                system_instruction=system_instruction,
                temperature=0.7,
            )
            try:
                response = client.models.generate_content(
                    model=self.config.model_name,
                    contents=user_content,
                    config=config,
                )
                data = json_schema.model_validate_json(response.text)
                return data
            except Exception as e:
                # Fallback to without system instruction if it failed
                print(f"Gemini generation error: {e}")
                raise e
        return ""

    def generate_stream(
        self, prompt: str, type: str, num_flashcards: int | None = None
    ):
        json_schema = self.resolve_json_schema(type)
        full_prompt = self.resolve_prompt(
            type, topic=prompt, num_flashcards=num_flashcards
        )
        provider = self.config.provider_name.lower()

        # load api key into environment
        os.environ[f"{provider.upper()}_API_KEY"] = self.api_key

        model_name = self.config.model_name
        # litellm expects "openrouter/" prefix for OpenRouter models
        if provider == "openrouter" and not model_name.startswith("openrouter/"):
            model_name = f"openrouter/{model_name}"

        # Setup litellm completion kwargs
        litellm_kwargs = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a helpful educational assistant. Return as JSON matching this schema: {json_schema.model_json_schema()}",
                },
                {
                    "role": "user",
                    "content": full_prompt + "\nContext details: " + prompt,
                },
            ],
            "stream": True,
            "response_format": {"type": "json_object"},
        }

        # apply custom api_base if configured
        if getattr(self.config, "base_url", None):
            litellm_kwargs["api_base"] = self.config.base_url

        try:
            # litellm completion
            response_stream = litellm.completion(**litellm_kwargs)
            for chunk in response_stream:
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Litellm stream error: {e}")
            raise e

    def resolve_json_schema(self, type: str):
        """
        Function for resolving the type of schema to be used in the generation
        """
        if type == "lecture":
            return LectureSchema
        elif type == "step":
            return LectureStepSchema
        elif type == "flashcard":
            return CardList
        elif type == "deck":
            return DeckWithCardsFlashcard
        elif type == "chat":
            # TODO: implement chat schema
            pass
        else:
            print(type)
            raise HTTPException(status_code=400, detail="Invalid generation type")

    def resolve_prompt(
        self,
        type: str,
        topic: str | None,
        num_flashcards: int | None = None,
        difficulty: str | None = None,
    ) -> str:
        """
        Function for resolving the prompt based on the type of generation
        """
        # determine the type of generation
        if type == "lecture":
            return self.prompt_manager.get_lecture_system_prompt(topic)
        elif type == "step":
            return self.prompt_manager.get_generate_content_prompt(topic)
        elif type == "flashcard":
            return self.prompt_manager.get_flashcard_prompt(
                topic, num_flashcards, difficulty
            )
        elif type == "deck":
            return self.prompt_manager.get_deck_prompt(
                topic, num_flashcards, difficulty
            )
        elif type == "chat":
            # TODO: implement chat prompt
            pass
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
