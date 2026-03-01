from models.llm_provider import (
    UserLLMConfig,
    UserLLMConfigBase,
    UserLLMConfigUpdate,
    UserLLMConfigPublic,
)
from models.lecture import Lecture, LectureBase
from models.lecture_section import LectureSection, LectureSectionBase
from models.lecture_step import LectureStep, LectureStepBase
from sqlmodel import Session
from cryptography.fernet import Fernet
import os
from fastapi import HTTPException
from litellm import completion
from pydantic import SecretStr
from google import genai
from schema.lecture_schema_json import LectureSchema


class LLMService:
    def __init__(self, session: Session):
        self.session = session

    def add_provider(self, provider: UserLLMConfigBase):
        db_provider = UserLLMConfig(**provider.dict())
        db_provider.api_key = self.encrypt_api_key(provider.api_key.get_secret_value())
        self.session.add(db_provider)
        self.session.commit()
        self.session.refresh(db_provider)
        return db_provider

    def get_provider(self, provider_id: int) -> UserLLMConfigPublic:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
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
            raise HTTPException(status_code=404, detail="Provider not found")
        provider.provider_name = provider_update.provider_name
        provider.model_name = provider_update.model_name
        provider.api_key = self.encrypt_api_key(
            provider_update.api_key.get_secret_value()
        )
        provider.base_url = provider_update.base_url
        self.session.add(provider)
        self.session.commit()
        self.session.refresh(provider)
        return provider

    def delete_provider(self, provider_id: int) -> UserLLMConfigPublic:
        provider = self.session.get(UserLLMConfig, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
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
            raise HTTPException(status_code=404, detail="Provider not found")

        # decrypt the api key
        api_key = self.decrypt_api_key(provider.api_key.get_secret_value())

        # Create a copy of provider config with decrypted key for the provider
        # provider.api_key = api_key # Avoid mutating the DB model if possible, or just use it

        # create llm provider
        llm_provider = LLMProvider(provider, api_key)

        # generate lecture
        lecture = llm_provider.generate_lecture(prompt)

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

        self.session.refresh(db_lecture)
        return db_lecture

    # FLASHCARDS
    def generate_flashcards(self, prompt: str, provider_id: int) -> str:
        pass

    # CHAT
    def generate_chat(self, prompt: str, provider_id: int) -> str:
        pass


class LLMProvider:
    def __init__(self, config: UserLLMConfigBase, api_key: str):
        self.config = config
        self.api_key = api_key

    def generate_lecture(self, prompt: str) -> LectureSchema:
        if self.config.provider_name == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key
            response = completion(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates lectures in JSON format according to the provided schema.",
                    },
                    {
                        "role": "user",
                        "content": f"Generate a lecture for: {prompt}. Return JSON.",
                    },
                ],
                response_format={"type": "json_object"},
            )
            content = response["choices"][0]["message"]["content"]
            return LectureSchema.model_validate_json(content)
        elif self.config.provider_name == "gemini":
            os.environ["GEMINI_API_KEY"] = self.api_key
            client = genai.Client()
            response = client.models.generate_content(
                model=self.config.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LectureSchema.model_json_schema(),
                ),
            )
            # convert to lecture schema
            lecture_schema = LectureSchema.model_validate_json(response.text)
            return lecture_schema

    def generate_flashcards(self, prompt: str) -> str:
        pass
