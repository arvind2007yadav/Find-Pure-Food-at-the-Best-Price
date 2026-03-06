from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from db.database import get_db
from db.models import serialize_doc

router = APIRouter(prefix="/products", tags=["products"])


# ── Response schemas ──────────────────────────────────────────────────────────

class PricePointOut(BaseModel):
    price: float
    currency: str
    unit: str | None
    in_stock: bool | None
    recorded_at: str


class QualityScoreOut(BaseModel):
    overall_score: float
    ingredient_score: float | None
    review_score: float | None
    certification_score: float | None
    social_score: float | None
    red_flags: list[str]
    green_flags: list[str]
    summary: str | None
    scored_at: str


class ProductOut(BaseModel):
    id: str
    name: str
    brand: str | None
    source: str
    source_url: str
    image_url: str | None
    ingredients: str | None
    certifications: list[str]
    description: str | None
    rating: float | None
    review_count: int | None
    latest_price: float | None
    latest_quality_score: float | None
    created_at: str


class ProductDetail(ProductOut):
    price_history: list[PricePointOut]
    quality_scores: list[QualityScoreOut]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_product_out(doc: dict) -> ProductOut:
    doc = serialize_doc(doc)
    prices = doc.get("price_history") or []
    scores = doc.get("quality_scores") or []
    return ProductOut(
        id=doc["id"],
        name=doc["name"],
        brand=doc.get("brand"),
        source=doc["source"],
        source_url=doc["source_url"],
        image_url=doc.get("image_url"),
        ingredients=doc.get("ingredients"),
        certifications=doc.get("certifications") or [],
        description=doc.get("description"),
        rating=doc.get("rating"),
        review_count=doc.get("review_count"),
        latest_price=prices[-1]["price"] if prices else None,
        latest_quality_score=scores[0]["overall_score"] if scores else None,
        created_at=doc["created_at"].isoformat() if hasattr(doc.get("created_at"), "isoformat") else str(doc.get("created_at", "")),
    )


def _to_product_detail(doc: dict) -> ProductDetail:
    base = _to_product_out(doc)
    prices = doc.get("price_history") or []
    scores = doc.get("quality_scores") or []

    return ProductDetail(
        **base.model_dump(),
        price_history=[
            PricePointOut(
                price=p["price"],
                currency=p.get("currency", "INR"),
                unit=p.get("unit"),
                in_stock=p.get("in_stock"),
                recorded_at=p["recorded_at"].isoformat() if hasattr(p.get("recorded_at"), "isoformat") else str(p.get("recorded_at", "")),
            )
            for p in prices
        ],
        quality_scores=[
            QualityScoreOut(
                overall_score=s["overall_score"],
                ingredient_score=s.get("ingredient_score"),
                review_score=s.get("review_score"),
                certification_score=s.get("certification_score"),
                social_score=s.get("social_score"),
                red_flags=s.get("red_flags") or [],
                green_flags=s.get("green_flags") or [],
                summary=s.get("summary"),
                scored_at=s["scored_at"].isoformat() if hasattr(s.get("scored_at"), "isoformat") else str(s.get("scored_at", "")),
            )
            for s in scores
        ],
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ProductOut])
async def list_products(
    search: str | None = Query(None),
    source: str | None = Query(None),
    min_quality: float | None = Query(None),
    max_price: float | None = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    db: AsyncIOMotorDatabase = get_db()
    query: dict = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if source:
        query["source"] = source

    cursor = db.products.find(query).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        out = _to_product_out(doc)
        if min_quality is not None and (out.latest_quality_score is None or out.latest_quality_score < min_quality):
            continue
        if max_price is not None and (out.latest_price is None or out.latest_price > max_price):
            continue
        results.append(out)
    return results


@router.get("/with-history/", response_model=list[ProductDetail])
async def list_products_with_history(
    search: str | None = Query(None),
    source: str | None = Query(None),
    skip: int = 0,
    limit: int = 100,
):
    db: AsyncIOMotorDatabase = get_db()
    query: dict = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if source:
        query["source"] = source

    cursor = db.products.find(query).sort("last_crawled_at", -1).skip(skip).limit(limit)
    return [_to_product_detail(doc) async for doc in cursor]


@router.get("/compare/", response_model=list[ProductDetail])
async def compare_products(ids: str = Query(..., description="Comma-separated product IDs")):
    from bson import ObjectId
    try:
        oid_list = [ObjectId(i.strip()) for i in ids.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="ids must be valid MongoDB ObjectIds")

    db: AsyncIOMotorDatabase = get_db()
    results = []
    for oid in oid_list:
        doc = await db.products.find_one({"_id": oid})
        if doc:
            results.append(_to_product_detail(doc))
    return results


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: str):
    from bson import ObjectId
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    db: AsyncIOMotorDatabase = get_db()
    doc = await db.products.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return _to_product_detail(doc)
