# app/routes/quiz.py
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
import logging
from app.models.quiz import (
    QuizRequest, QuizResponse, QuizSubmission, QuizResult, DifficultyLevel
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for active quizzes (for demo - use database in production)
active_quizzes: Dict[str, Dict] = {}
import shortuuid

@router.post("/generate", response_model=QuizResponse, summary="Generate a programming quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate a programming quiz on a specific topic.
    
    Example:
    - topic: "Python Lists", difficulty: "beginner"
    - topic: "Binary Trees", difficulty: "advanced"
    - topic: "SQL Joins", difficulty: "intermediate"
    """
    try:
        logger.info(f"Generating quiz for topic: {request.topic}, difficulty: {request.difficulty}")
        
        # Generate quiz using LLM
        result = await llm_service.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty.value,
            num_questions=request.num_questions
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to generate quiz")
            )
        
        quiz_data = result["quiz"]
        
        # Generate unique quiz ID and store questions
        quiz_id = shortuuid.uuid()
        active_quizzes[quiz_id] = {
            "topic": quiz_data["topic"],
            "questions": quiz_data["questions"],
            "generated_at": "2024-01-01T00:00:00Z"  # Add timestamp
        }
        
        # Return response with quiz ID for later submission
        response = QuizResponse(
            topic=quiz_data["topic"],
            difficulty=DifficultyLevel(quiz_data["difficulty"]),
            questions=quiz_data["questions"],
            total_questions=len(quiz_data["questions"])
        )
        
        # Include quiz_id in headers for client to use
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post("/evaluate", response_model=QuizResult, summary="Evaluate quiz answers")
async def evaluate_quiz(submission: QuizSubmission):
    """
    Evaluate user's quiz answers and provide detailed feedback.
    
    Expects a list of answers in the same order as the questions.
    Answers should be the option letters (A, B, C, D).
    """
    try:
        if not submission.quiz_id or submission.quiz_id not in active_quizzes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid quiz ID or quiz not found"
            )
        
        quiz = active_quizzes[submission.quiz_id]
        questions = quiz["questions"]
        
        # Evaluate answers
        result = await llm_service.evaluate_quiz_answers(questions, submission.answers)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to evaluate quiz")
            )
        
        # Format response
        quiz_result = QuizResult(
            topic=quiz["topic"],
            total_questions=result["result"]["total_questions"],
            correct_answers=result["result"]["correct_answers"],
            score_percentage=result["result"]["score_percentage"],
            evaluations=result["result"]["evaluations"]
        )
        
        # Clean up (optional - remove quiz from active storage)
        # del active_quizzes[submission.quiz_id]
        
        return quiz_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate quiz: {str(e)}"
        )

@router.get("/topics", summary="Get suggested quiz topics")
async def get_quiz_topics():
    """
    Get a list of suggested programming topics for quizzes.
    """
    suggested_topics = [
        "Python Lists and Tuples",
        "Java Object-Oriented Programming",
        "SQL Database Queries",
        "JavaScript Functions",
        "Data Structures: Arrays",
        "Data Structures: Linked Lists",
        "Data Structures: Trees",
        "Algorithms: Sorting",
        "Algorithms: Searching",
        "Time Complexity Analysis",
        "Recursion Concepts",
        "Dynamic Programming",
        "System Design Basics",
        "API Design Principles",
        "Testing Methodologies"
    ]
    
    return {"topics": suggested_topics}