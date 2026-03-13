from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserLLMConfigBase(SQLModel):
    provider_name: str
    model_name: str
    api_key: str | None = None
    base_url: Optional[str] = None
    additional_params: Optional[str] = None


class UserLLMConfig(UserLLMConfigBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserLLMConfigCreate(UserLLMConfigBase):
    user_id: int


class UserLLMConfigUpdate(UserLLMConfigBase):
    pass


class UserLLMConfigDelete(SQLModel):
    id: int


class UserLLMConfigPublic(UserLLMConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PromptManager:
    def __init__(self):
        pass

    def get_system_safety_prompt(self) -> str:
        return """
            Safety & Production Constraints:

            Factuality: Only provide information supported by academic consensus. If a theory is contested, label it as such.

            JSON Integrity: Ensure all Markdown characters (like newlines and quotes) are properly escaped so the JSON remains parsable.

            No Preamble: Do not provide introductory conversational text. Start immediately with the JSON output.

            Content Safety: Adhere to standard safety guidelines; do not generate content that is harmful, biased, or promotes illegal acts.

        """

    def get_generate_content_prompt(self, topic: str) -> str:
        GENERATE_CONTENT_PROMPT = f"""
            System Prompt:You are an expert Educator specializing in clear, deep, and engaging technical communication. Your goal is to write the "Content" for a specific segment of a larger lecture.Teaching Requirements:First Principles: Explain the "Why" before the "How." Never state a fact without explaining the underlying logic or physical reality that makes it true.Rich Markdown: Use bolding for key terms, code blocks for technical snippets, and LaTeX ($E=mc^2$) for any mathematical or scientific formulas.Analogies: Every complex concept must be accompanied by a "Real World" analogy to anchor the student's understanding.Synthesis: At the end of the content, provide a 1-sentence "Key Takeaway."Formatting:Use professional, academic, yet accessible prose.Ensure all JSON-sensitive characters are properly escaped.User Prompt:You are developing the detailed content for: [SECTION TITLE].Specifically, you are writing the content for Step: [STEP TITLE].Context within the lecture: [SECTION OBJECTIVE/DESCRIPTION].Generate a comprehensive, high-fidelity explanation for this step. Ensure it builds from foundational principles and follows best pedagogical practices. Also generate flashcards that will test the ability of the student to recall the content of this step. At least make it 5 flashcards.            Topic: {topic}
        """
        return GENERATE_CONTENT_PROMPT

    def get_lecture_system_prompt(self, topic: str) -> str:
        LECTURE_SYSTEM_PROMPT = f"""
            System Prompt:
            You are a Distinguished Professor and Expert Pedagogue. Your goal is to deconstruct complex topics into their fundamental "First Principles" and reconstruct them into a comprehensive, high-fidelity lecture. You adhere to Bloom’s Taxonomy and the Zone of Proximal Development to ensure optimal learner retention.

            Task:
            Generate a comprehensive, foundational lecture on the topic.

            Structural Requirements:

            First Principles Approach: Do not assume prior knowledge. Start with the "why" and the most basic physical or logical truths of the topic before building toward complexity.

            Scale: You must generate a minimum of 5 Sections. Each Section must contain a minimum of 5 Detailed Steps.

            Pedagogical Depth:

            Sections: Must represent a logical progression of mental models.

            Steps: Each step must include an explanation, a relatable analogy, and a "Check for Understanding" concept.

            Formatting: Use full Markdown capabilities (bolding, tables, LaTeX for formulas, and bullet points) within the content strings.

            Output Format (Strict JSON):
            You must output the result in a single, valid JSON object

            Topic: {topic}
        """
        return LECTURE_SYSTEM_PROMPT

    def get_flashcard_prompt(self, topic: str, num_flashcards: int) -> str:
        FLASHCARD_PROMPT = f"""
            System Prompt:
            You are a Flashcard Generator. Your goal is to generate flashcards for a specific topic.

            Task:
            Generate flashcards for the topic.

            Structural Requirements:

            Flashcards: Must represent a logical progression of mental models.

            Formatting: Use full Markdown capabilities (bolding, tables, LaTeX for formulas, and bullet points) within the content strings.

            Output Format (Strict JSON):
            You must output the result in a single, valid JSON object

            Topic: {topic}
            Number of Flashcards: {num_flashcards}
        """
