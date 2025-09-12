from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import ask_llm

router = APIRouter()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    answer = ask_llm(req.question)
    return {"answer": answer}

@router.get("/test")
async def test():
    return {"message": "Test endpoint is working!"}
