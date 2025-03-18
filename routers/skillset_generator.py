import json
from typing import List, Optional, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, ValidationError

# Initialize Google Generative AI model

# --- Pydantic Model ---
class AssessmentQuestion(BaseModel):
    """Represents a skill assessment question."""
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of multiple-choice options")
    answer: str = Field(description="The correct answer")
    level: int = Field(description="Difficulty level (1-5)")
    explanation: Optional[str] = Field(description="Explanation of the answer", default=None)


class SkillsetGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key='AIzaSyCqcRw49l81hOkG6khQifY4otkxU9Vwk3s'
        )

    def generate(self, topics: List[Dict[str, int]], num_questions: int):
        try:
            # --- Prompt Template ---
            prompt_template = """
            Let me show you how I create skill assessment questions step by step:

            Question: What is the correct file extension for Python files?
            Options: ["A: .py", "B: .python", "C: .pt", "D: .txt"]
            Answer: A
            Level: 1

            Now, using the question and answer above, generate new question(s) for each of the following topics and levels using the same approach.
            Level 1 is easy. Level 5 is the hardest. Stick to multiple choice options.

            {topic_level_pairs}

            **Return the response as valid JSON.**
            Each "questions" should be a list of dictionaries with keys: "topic", "level", "question", "options", "answer", "explanation".
            - "options" should be a list of strings, not a dictionary.
            - Limit options to be 4 only
            - Example: ["A: Choice 1", "B: Choice 2", "C: Choice 3", "D: Choice 4"]
            - Generate only {num_questions} questions in total of all topics.
            """

            topic_level_pairs = ""
            for topic_info in topics:
                topic = topic_info["topic"]
                level_min = topic_info["level_min"]
                level_max = topic_info["level_max"]
                for level in range(level_min, level_max + 1):
                    topic_level_pairs += f"Topic: {topic}, Level: {level}\n"

            prompt_str = prompt_template.format(num_questions=num_questions, topic_level_pairs=topic_level_pairs)
            # print(prompt_str)

            # Create chain
            chain = PromptTemplate(template=prompt_str) | self.llm | JsonOutputParser(pydantic_object=AssessmentQuestion)
            response = chain.invoke({})
            return response
        except ValidationError as e:
            print(f"Pydantic Validation Error: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None