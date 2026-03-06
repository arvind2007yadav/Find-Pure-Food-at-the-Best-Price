import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.crawl import router as crawl_router
from api.products import router as products_router
from db.database import close_client, init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_client()


app = FastAPI(
    title="Food Quality Risk Profiler",
    description="Crawl Amazon/Flipkart/brand sites, score food product quality, track prices over time.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(crawl_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}
