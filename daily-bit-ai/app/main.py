from fastapi import FastAPI
from app.routes import qa

def create_app() -> FastAPI:
    app = FastAPI(title="AI Assistant Service")

    # health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    # include routes
    app.include_router(qa.router, prefix="/api")

    return app

app = create_app()
