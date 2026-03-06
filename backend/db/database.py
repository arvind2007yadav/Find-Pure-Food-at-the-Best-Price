"""Motor (async MongoDB) client. Collections are accessed via `get_db()`."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongodb_db]


async def close_client():
    global _client
    if _client:
        _client.close()
        _client = None


async def init_db():
    """Create indexes on startup."""
    db = get_db()
    await db.products.create_index("source_url", unique=True)
    await db.products.create_index("source")
    await db.products.create_index("name")
    await db.crawl_jobs.create_index("created_at")
