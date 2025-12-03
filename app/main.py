import uvicorn
from fastapi import FastAPI
from config import settings
from contextlib import asynccontextmanager

from models import db_helper,Base
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from task_queue import broker
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if not broker.is_worker_process:
        await broker.startup()

    yield
    await db_helper.dispose()

    if not broker.is_worker_process:
        await broker.shutdown()

main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(
    api_router,
)
main_app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    'http://127.0.0.1:8001/',
    "http://localhost:8001",
]

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["Authorization"],
    expose_headers=["X-File-Name"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
