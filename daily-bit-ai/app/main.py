from fastapi import FastAPI
from app.routes import qa,topic_route,problem_route, quiz_route
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="AI Assistant Service")

    # health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    
# CORS middleware - allow requests from your Next.js app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            # Add your production URLs here when deploying
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"] 
    )
    


    # include routes
    app.include_router(qa.router, prefix="/api")
    app.include_router(topic_route.router, prefix="/api/topics")
    app.include_router(problem_route.router, prefix="/api/problems")
    app.include_router(quiz_route.router, prefix="/api/quiz")

    return app

app = create_app()
