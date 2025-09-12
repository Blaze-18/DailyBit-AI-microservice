# app/routes/problems.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict
from app.models.problem import Problem
from app.services.problem_service import problem_service

router = APIRouter()

@router.post("/ingest", summary="Ingest a new coding problem into the knowledge base")
async def ingest_problem(problem_data: Problem):
    """
    Accepts a coding problem, chunks it, generates embeddings, and stores it.
    """
    try:
        chunk_count = problem_service.ingest_problem(problem_data)
        return {
            "message": f"Successfully ingested problem '{problem_data.title}' with {chunk_count} chunks.",
            "problem_id": problem_data.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting problem: {str(e)}")

@router.get("/search", summary="Search for similar problems")
async def search_problems(
    query: str = Query(..., description="Search query about a problem"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    n_results: int = Query(3, description="Number of results to return")
):
    """
    Search for coding problems similar to the query with optional filters.
    """
    try:
        # Build filters
        filters = {}
        if difficulty:
            filters["difficulty"] = difficulty
        if topic:
            filters["topics"] = {"$contains": topic}
        
        results = problem_service.search_similar_problems(
            query=query,
            n_results=n_results,
            filters=filters if filters else None
        )
        
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching problems: {str(e)}")

@router.get("/{problem_id}/hints", summary="Get hints for a specific problem")
async def get_problem_hints(problem_id: str, n_hints: int = Query(3, description="Number of hints to return")):
    """
    Retrieve hints for a specific problem to help stuck students.
    """
    try:
        # Query for hints specifically for this problem
        results = problem_service.search_similar_problems(
            query="hints guidance help stuck",
            n_results=n_hints,
            filters={"problem_id": problem_id, "chunk_type": "hints_guidance"}
        )
        
        return {
            "problem_id": problem_id,
            "hints": results["documents"][0] if results["documents"] else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hints: {str(e)}")