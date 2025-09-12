# app/routes/qa.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.qa_service import qa_service

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    collection_type: Optional[str] = None  # "topics" or "problems"
    n_results: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7

class SearchResponse(BaseModel):
    query: str
    collection_type: str
    is_successful: bool
    total_chunks_found: int
    relevant_chunks_count: int
    chunks: List[Dict]
    top_similarity_score: float

@router.post("/search", response_model=SearchResponse, summary="Search knowledge base")
async def search_knowledge_base(request: SearchRequest):
    """
    Search the knowledge base and return relevant chunks with success indicator.
    """
    try:
        # Determine which collection to search (topics or problems)
        collection_type = request.collection_type or qa_service.determine_collection_type(request.query)
        
        # Retrieve relevant chunks from the knowledge base
        chunks = qa_service.retrieve_relevant_chunks(
            query=request.query,
            collection_type=collection_type,
            n_results=request.n_results if request.n_results is not None else 5
        )
        
        # Determine if search was successful
        similarity_threshold = request.similarity_threshold if request.similarity_threshold is not None else 0.7
        is_successful = qa_service.is_search_successful(chunks, similarity_threshold)
        
        # Count relevant chunks
        relevant_chunks_count = sum(1 for chunk in chunks if chunk['is_relevant'])
        
        # Get top similarity score
        top_similarity = max((chunk['similarity_score'] for chunk in chunks), default=0.0)
        
        return SearchResponse(
            query=request.query,
            collection_type=collection_type,
            is_successful=is_successful,
            total_chunks_found=len(chunks),
            relevant_chunks_count=relevant_chunks_count,
            chunks=chunks,
            top_similarity_score=top_similarity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching knowledge base: {str(e)}")

@router.get("/search-simple", summary="Simple search endpoint")
async def search_simple(
    query: str = Query(..., description="Search query"), 
    n_results: int = Query(5, description="Number of results"),
    threshold: float = Query(0.7, description="Similarity threshold for relevance")
):
    """
    Simple GET endpoint for searching the knowledge base.
    """
    try:
        collection_type = qa_service.determine_collection_type(query)
        chunks = qa_service.retrieve_relevant_chunks(query, collection_type, n_results)
        
        is_successful = qa_service.is_search_successful(chunks, threshold)
        relevant_chunks_count = sum(1 for chunk in chunks if chunk['is_relevant'])
        top_similarity = max((chunk['similarity_score'] for chunk in chunks), default=0.0)
        
        return {
            "query": query,
            "collection_type": collection_type,
            "search_successful": is_successful,
            "relevant_chunks": relevant_chunks_count,
            "total_chunks": len(chunks),
            "top_similarity_score": top_similarity,
            "results": chunks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")