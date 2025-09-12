# app/routes/kb.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.topic import TopicJSON
from app.services.kb_service import kb_service  # Import the service instance

router = APIRouter()

# You can add a prefix to all routes in this file, e.g., /api/kb
# router = APIRouter(prefix="/kb", tags=["knowledge base"])

@router.post("/ingest", summary="Ingest a new topic into the knowledge base")
async def ingest_topic(topic_data: TopicJSON):
    """
    Accepts a topic JSON, chunks it, generates embeddings, and stores them in the vector database.
    """
    try:
        chunk_count = kb_service.ingest_topic(topic_data)
        return {"message": f"Successfully ingested topic '{topic_data.title}' into knowledge base with {chunk_count} chunks."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during ingestion: {str(e)}")