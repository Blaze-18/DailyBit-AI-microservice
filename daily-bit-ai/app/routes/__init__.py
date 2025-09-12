# app/routes/__init__.py
from fastapi import APIRouter
from app.routes import qa, topic_route , problem_route

router = APIRouter()

# routers from other modules
router.include_router(qa.router, tags=["Q&A"])
router.include_router(topic_route.router, tags=["Knowledge Base"])
router.include_router(problem_route.router, tags=["Problems"])
