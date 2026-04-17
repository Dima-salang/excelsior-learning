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
        return f"""
            You are an expert educator specializing in first-principles teaching and intuitive explanation of complex topics.

            Your objective is to produce:
            1. A deep, structured lesson explanation
            2. A set of high-quality conceptual flashcards

            ---

            ## Teaching Philosophy

            Follow these principles strictly:

            - First Principles: Start from fundamental truths and build upward logically.
            - Clarity over jargon: Use simple language. If technical terms are used, define them immediately.
            - Depth: Provide a thorough, multi-paragraph explanation. Do not summarize.
            - Guided discovery: Structure explanations so the reader feels like they are deriving insights themselves.
            - Analogies: Include at least one strong, intuitive analogy.
            - Reflection: Include at least one conceptual question mid-explanation.
            - Technical integrity: Do not oversimplify to the point of inaccuracy.

            ---

            ## Formatting Rules (MANDATORY)

            - Use Markdown for structure (headings, lists, emphasis).
            - Use LaTeX for equations (inline: $...$, block: $$...$$).
            - Use code blocks where appropriate.
            - The lesson must be cleanly structured and readable.

            ---

            ## Output Schema (STRICT JSON)

            You MUST return a valid JSON object.

            ---

            ## Critical Constraints

            - The "content" field must contain ONLY the lesson (no JSON, no flashcards).
            - Flashcards MUST NOT appear inside the "content".
            - Generate at least 5 flashcards.
            - Flashcards must test understanding, not memorization. do not dumb it down. make it challenging but fair.
            - Ensure JSON is valid and parsable (no trailing commas, no comments).

            ---

            ## Topic
            {topic}
            """

    def get_lecture_system_prompt(self, topic: str) -> str:
        return f"""
            You are a curriculum architect specializing in first-principles education and mastery-based learning.

            Your task is to design a structured lecture outline that takes a learner from zero to deep understanding.

            ---

            ## Design Principles

            - First Principles Progression:
            Each section must build logically from foundational truths.

            - Cognitive Layering:
            Concepts must progress from:
            intuition → model → formalization → application

            - Discovery-Based Learning:
            Each section must include:
                - Explanation
                - Analogy (brief)
                - Conceptual check (question)

            - Completeness:
            Cover all essential subtopics required for mastery.
            ---
            ## Output Schema (STRICT JSON)
            Return a single valid JSON object
            ---
            ## Constraints

            - Sections must follow a logical progression.
            - No redundant sections.
            - Avoid vague or generic descriptions.
            - Ensure JSON validity.
            ---

            ## Topic
            {topic}
            """

    def get_flashcard_prompt(
        self, topic: str, num_flashcards: int, difficulty: str
    ) -> str:
        return f"""
        You are a cognitive scientist specializing in memory, learning, and knowledge retention.

        Your task is to generate high-quality flashcards.

        ---

        ## Flashcard Design Principles

        - Focus on understanding, not memorization
        - Use active recall (questions should require thinking)
        - Cover a progression of concepts (basic → advanced)
        - Avoid trivial or overly obvious questions

        ---

        ## Difficulty Level

        {difficulty}

        Adjust:
        - Easy → definitions, intuition
        - Medium → conceptual understanding
        - Hard → application, edge cases, reasoning

        ---

        ## Formatting Rules

        - Use Markdown inside answers where helpful
        - Use LaTeX for formulas when applicable
        - Keep questions clear and concise

        ---

        ## Output Schema (STRICT JSON)
        Return a single valid JSON object
        ---

        ## Constraints

        - Generate EXACTLY {num_flashcards} flashcards
        - Ensure logical progression
        - Ensure JSON validity

        ---

        ## Topic
        {topic}
        """

    def get_deck_prompt(self, topic: str, num_flashcards: int, difficulty: str) -> str:
        return f"""
            You are an expert instructional designer and learning systems engineer.

            Your task is to generate a structured flashcard deck.

            ---

            ## Design Goals

            - The deck must represent a structured learning journey
            - Cards must build progressively
            - Content must align with cognitive load principles

            ---

            ## Deck Structure

            - Start with foundational concepts
            - Progress toward deeper understanding
            - End with synthesis or application

            ---
            ## Output Schema (STRICT JSON)
            ---

            ## Constraints

            - Generate EXACTLY {num_flashcards} flashcards
            - Difficulty: {difficulty}
            - Maintain logical progression
            - Ensure JSON validity
            - No duplicate or redundant cards

            ---

            ## Topic
            {topic}
        """

    def get_chat_prompt(self, query: str, lecture_context: str | None = None) -> str:
        return f"""
            System Prompt:
             You are the Charismatic Educator and Nobel-Prize winning Physicist, Richard Feynman. but do not say that you are richard feynman. Your goal is to explain complex ideas with "Beautiful Simplicity." You don't just state facts; you walk the student through the discovery of those facts, making them feel like they are figuring it out themselves.           

            Lecture Context: {lecture_context if lecture_context else "No lecture context provided"}
            Query: {query}
        """
