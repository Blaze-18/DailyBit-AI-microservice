# app/routes/qa.py
from fastapi import APIRouter, HTTPException, Query
from app.models.qa import FullRAGResponse, LLMResponse, SearchRequest, SearchResponse  # Use the new models
from app.services.qa_service import qa_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse, summary="Search knowledge base with context")
async def search_with_context(request: SearchRequest):
    """
    Search the knowledge base with optional context filtering.
    """
    try:
        # Use the new context-aware search
        n_results = request.n_results if request.n_results is not None else 5  # Provide a default value
        chunks = qa_service.retrieve_relevant_chunks_with_context(
            query=request.query,
            context=request.context,
            n_results=n_results
        )
        
        similarity_threshold = request.similarity_threshold if request.similarity_threshold is not None else 0.7  # Default threshold
        is_successful = qa_service.is_search_successful(chunks, similarity_threshold)
        relevant_chunks_count = sum(1 for chunk in chunks if chunk['is_relevant'])
        top_similarity = max((chunk['similarity_score'] for chunk in chunks), default=0.0)
        
        # Determine collection type from context or automatically
        collection_type = "topics"  # Default
        if request.context and request.context.startswith("problem:"):
            collection_type = "problems"
        
        return SearchResponse(
            query=request.query,
            collection_type=collection_type,
            is_successful=is_successful,
            total_chunks_found=len(chunks),
            relevant_chunks_count=relevant_chunks_count,
            chunks=chunks,
            top_similarity_score=top_similarity,
            context_used=request.context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

# Keep the old endpoint for backward compatibility if needed
@router.get("/search-simple", summary="Simple search endpoint (backward compatible)")
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

@router.post("/ask", response_model=FullRAGResponse, summary="Full RAG pipeline: search + LLM response")
async def ask_with_rag(request: SearchRequest):
    """
    Complete RAG pipeline: search knowledge base and generate LLM response.
    """
    try:
        # Step 1: Retrieve relevant chunks
        n_results = request.n_results if request.n_results is not None else 5  # Provide a default value
        chunks = qa_service.retrieve_relevant_chunks_with_context(
            query=request.query,
            context=request.context,
            n_results=n_results
        )
        
        # Step 2: Check if search was successful
        similarity_threshold = request.similarity_threshold if request.similarity_threshold is not None else 0.7  # Default threshold
        is_successful = qa_service.is_search_successful(chunks, similarity_threshold)
        relevant_chunks_count = sum(1 for chunk in chunks if chunk['is_relevant'])
        top_similarity = max((chunk['similarity_score'] for chunk in chunks), default=0.0)
        
        # Step 3: Generate LLM response
        llm_response = qa_service.generate_llm_response(request.query, chunks)
        
        # Prepare responses
        search_response = SearchResponse(
            query=request.query,
            collection_type="topics",  # Will be dynamic based on context
            is_successful=is_successful,
            total_chunks_found=len(chunks),
            relevant_chunks_count=relevant_chunks_count,
            chunks=chunks,
            top_similarity_score=top_similarity,
            context_used=request.context
        )
        
        llm_response_obj = LLMResponse(
            query=request.query,
            context_used=request.context,
            retrieved_chunks=chunks,
            llm_response=llm_response,
            is_successful=is_successful,
            top_similarity_score=top_similarity
        )
        
        return FullRAGResponse(
            search_results=search_response,
            llm_response=llm_response_obj
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG pipeline: {str(e)}")