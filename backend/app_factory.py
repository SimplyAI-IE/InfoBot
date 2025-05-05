# backend/app_factory.py
from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    return app
