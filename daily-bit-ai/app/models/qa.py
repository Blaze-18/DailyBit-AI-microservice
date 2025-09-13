# app/models/qa.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class SearchRequest(BaseModel):
    query: str = Field(..., description="The user's search query")
    context: Optional[str] = Field(
        None, 
        description="Optional context: 'topic:TopicName' or 'problem:ProblemID' or 'problem:ProblemName'"
    )
    n_results: Optional[int] = Field(5, description="Number of results to return")
    similarity_threshold: Optional[float] = Field(0.7, description="Similarity threshold for relevance")

class SearchResponse(BaseModel):
    query: str
    collection_type: str
    is_successful: bool
    total_chunks_found: int
    relevant_chunks_count: int
    chunks: List[Dict]
    top_similarity_score: float
    context_used: Optional[str] = None