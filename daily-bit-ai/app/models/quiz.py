# app/models/quiz.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class QuizQuestion(BaseModel):
    question: str = Field(..., description="The quiz question")
    options: List[str] = Field(..., description="List of multiple choice options")
    correct_answer: str = Field(..., description="The correct answer option")
    explanation: str = Field(..., description="Explanation of the correct answer")

class QuizRequest(BaseModel):
    topic: str = Field(..., description="Programming topic for the quiz", min_length=1)
    difficulty: DifficultyLevel = Field(DifficultyLevel.INTERMEDIATE, description="Difficulty level")
    num_questions: int = Field(5, description="Number of questions to generate", ge=1, le=10)

class QuizResponse(BaseModel):
    topic: str
    difficulty: DifficultyLevel
    questions: List[QuizQuestion]
    total_questions: int

class AnswerEvaluation(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str

class QuizSubmission(BaseModel):
    quiz_id: Optional[str] = Field(None, description="Optional quiz ID for tracking")
    answers: List[str] = Field(..., description="List of user answers in order")

class QuizResult(BaseModel):
    topic: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    evaluations: List[AnswerEvaluation]