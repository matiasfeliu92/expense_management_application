from fastapi import FastAPI
import uvicorn

from src_v2.user.infrastructure.api.user_routes import router as users_v2_router
from src_v2.user.infrastructure.db import config as db_config  # ensure DB initialized


def create_app() -> FastAPI:
    app = FastAPI(title="Expense Management (v2)")
    app.include_router(users_v2_router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("src_v2.main:app", host="127.0.0.1", port=8000, reload=True)
