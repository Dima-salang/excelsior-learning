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
from models.deck import Deck
from schema.lecture_schema_json import LectureSchema, LectureStepSchema
from sqlmodel import Session
from cryptography.fernet import Fernet
import os
from fastapi import HTTPException
from litellm import completion
from google import genai
from datetime import datetime
from models.card import Card, CardBase
from models.llm_provider import PromptManager


class LLMService:
    prompt_manager: PromptManager
    PROVIDER_NOT_FOUND = "Provider not found"

    def __init__(self, session: Session):
        self.session = session
        self.prompt_manager = PromptManager()

    def add_provider(self, provider: UserLLMConfigCreate):
        db_provider = UserLLMConfig(**provider.dict())
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
        providers = (
            self.session.query(UserLLMConfig)
            .filter(UserLLMConfig.user_id == user_id)
            .order_by(UserLLMConfig.created_at.desc())
            .all()
        )
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

    def encrypt_api_key(self, api_key: str) -> str:
        # get the master key
        master_key = os.getenv("MASTER_KEY")
        if not master_key:
            raise ValueError("MASTER_KEY not found in environment variables")

        f = Fernet(master_key)
        return f.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self, api_key: str) -> str:
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

        # generate lecture
        lecture = llm_provider.generate(prompt, type="lecture")

        # save and return lecture
        return self.save_lecture(lecture, user_id)

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
    def generate_flashcards(self, prompt: str, provider_id: int) -> str:
        pass

    # CHAT
    def generate_chat(self, prompt: str, provider_id: int) -> str:
        pass

    def generate_step_content(self, lecture_id: int, step_id: int, provider_id: int):
        from models.lecture_step import LectureStep
        from models.lecture_section import LectureSection
        from models.lecture import LectureStepPublic

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

        # generate content
        data = llm_provider.generate(prompt, type="step")

        # save the step to the db
        step.content = data.content
        step.updated_at = datetime.now()
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)

        if data.flashcards:
            self.save_step_cards(step_id, data.flashcards)

        return LectureStepPublic.model_validate(step)

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
        self, prompt: str, type: str, num_flashcards: int | None = None
    ) -> str:
        # resolve the type
        json_schema = self.resolve_json_schema(type)
        prompt = self.resolve_prompt(type, topic=prompt, num_flashcards=num_flashcards)
        provider = self.config.provider_name.lower()

        if provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key
            response = completion(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful educational assistant. Return as JSON matching this schema: {json_schema.model_json_schema()}",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                response_format={"type": "json_object"}
                if "gpt-4" in self.config.model_name
                or "gpt-3.5-turbo-0125" in self.config.model_name
                else None,
            )
            content = response["choices"][0]["message"]["content"]
            return json_schema.model_validate_json(content)
        elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = self.api_key
            client = genai.Client()
            config = genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=json_schema.model_json_schema(),
            )
            response = client.models.generate_content(
                model=self.config.model_name,
                contents=prompt,
                config=config,
            )
            data = json_schema.model_validate_json(response.text)
            return data
        return ""

    def generate_stream(
        self, prompt: str, type: str, num_flashcards: int | None = None
    ):
        json_schema = self.resolve_json_schema(type)
        full_prompt = self.resolve_prompt(
            type, topic=prompt, num_flashcards=num_flashcards
        )
        provider = self.config.provider_name.lower()

        if provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key
            response_stream = completion(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful educational assistant. Return as JSON matching this schema: {json_schema.model_json_schema()}",
                    },
                    {
                        "role": "user",
                        "content": full_prompt + "\nContext details: " + prompt,
                    },
                ],
                stream=True,
                response_format={"type": "json_object"}
                if "gpt-4" in self.config.model_name
                else None,
            )
            for chunk in response_stream:
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    yield content

        elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = self.api_key
            client = genai.Client()
            config = genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                # response_schema=json_schema, # response_schema can sometimes break streaming in some SDK versions, or it works fine.
            )
            response_stream = client.models.generate_content_stream(
                model=self.config.model_name,
                contents=full_prompt + "\nContext details: " + prompt,
                config=config,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

    def resolve_json_schema(self, type: str):
        """
        Function for resolving the type of schema to be used in the generation
        """
        if type == "lecture":
            return LectureSchema
        elif type == "step":
            return LectureStepSchema
        elif type == "flashcard":
            return CardBase
        elif type == "chat":
            # TODO: implement chat schema
            pass
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")

    def resolve_prompt(
        self, type: str, topic: str | None, num_flashcards: int | None = None
    ) -> str:
        """
        Function for resolving the prompt based on the type of generation
        """
        if type == "lecture":
            return self.prompt_manager.get_lecture_system_prompt(topic)
        elif type == "step":
            return self.prompt_manager.get_generate_content_prompt(topic)
        elif type == "flashcard":
            return self.prompt_manager.get_flashcard_prompt(topic, num_flashcards)
        elif type == "chat":
            # TODO: implement chat prompt
            pass
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
