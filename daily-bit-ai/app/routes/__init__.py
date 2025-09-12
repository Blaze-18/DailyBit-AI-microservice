# app/routes/__init__.py
from fastapi import APIRouter
from app.routes import qa, kb 

router = APIRouter()

# routers from other modules
router.include_router(qa.router, tags=["Q&A"])
router.include_router(kb.router, tags=["Knowledge Base"]) 