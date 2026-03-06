"""
Pydantic document models for MongoDB collections.

Collections:
  products   — embedded price_history[] and quality_scores[] arrays
  crawl_jobs — background crawl job tracking

ObjectIds are serialized as strings in API responses.
"""
from datetime import datetime

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.utcnow()


# ── Embedded sub-documents ────────────────────────────────────────────────────

class PricePoint(BaseModel):
    price: float
    currency: str = "INR"
    unit: str | None = None
    in_stock: bool | None = None
    recorded_at: datetime = Field(default_factory=_now)


class QualityScore(BaseModel):
    overall_score: float
    ingredient_score: float | None = None
    review_score: float | None = None
    certification_score: float | None = None
    social_score: float | None = None
    red_flags: list[str] = []
    green_flags: list[str] = []
    summary: str | None = None
    raw_analysis: dict = {}
    scored_at: datetime = Field(default_factory=_now)


# ── Top-level documents ───────────────────────────────────────────────────────

class ProductDoc(BaseModel):
    """Inserted into the `products` collection."""
    name: str
    brand: str | None = None
    category: str | None = None
    source: str                    # amazon | flipkart | brand_site
    source_url: str                # unique index
    image_url: str | None = None
    ingredients: str | None = None
    certifications: list[str] = []
    description: str | None = None
    rating: float | None = None
    review_count: int | None = None
    raw_data: dict = {}
    price_history: list[PricePoint] = []
    quality_scores: list[QualityScore] = []
    created_at: datetime = Field(default_factory=_now)
    last_crawled_at: datetime | None = None


class CrawlJobDoc(BaseModel):
    """Inserted into the `crawl_jobs` collection."""
    url: str
    source: str
    query: str | None = None
    status: str = "pending"        # pending | running | done | failed
    products_found: int = 0
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)
    completed_at: datetime | None = None


# ── Helper ────────────────────────────────────────────────────────────────────

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB _id (ObjectId) to string 'id' for API responses."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc
