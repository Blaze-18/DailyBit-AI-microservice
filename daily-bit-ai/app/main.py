from fastapi import FastAPI
from app.routes import qa,topic_route,problem_route, quiz_route

def create_app() -> FastAPI:
    app = FastAPI(title="AI Assistant Service")

    # health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    


    # include routes
    app.include_router(qa.router, prefix="/api")
    app.include_router(topic_route.router, prefix="/api/topics")
    app.include_router(problem_route.router, prefix="/api/problems")
    app.include_router(quiz_route.router, prefix="/api/quiz")

    return app

app = create_app()
