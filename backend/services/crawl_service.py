"""Orchestrates crawlers + quality analysis and persists results to MongoDB.

Allowed sources:
  amazon   — searches Amazon.in, filtered to the 4 allowed brands
  flipkart — searches Flipkart, filtered to the 4 allowed brands
  anveshan — crawls anveshan.farm directly
  rosier   — crawls rosierfoods.com directly
  twobros  — crawls twobrothersindiashop.com directly
  batiora  — crawls batiora.com directly
"""
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from analyzers.quality import analyze_product
from crawlers.amazon import AmazonCrawler
from crawlers.base import ScrapedProduct
from crawlers.brand_sites import BRAND_CONFIGS, BrandSiteCrawler, brand_key_from_url
from crawlers.flipkart import FlipkartCrawler
from db.models import PricePoint, ProductDoc, QualityScore

# Brands we care about — Amazon/Flipkart searches are scoped to these names
ALLOWED_BRANDS = ["Anveshan", "Rosier Foods", "Two Brothers Organic", "Two Brothers", "Batiora Farm Fresh", "Batiora"]

# All valid source keys accepted by the API
VALID_SOURCES = {"amazon", "flipkart", "anveshan", "rosier", "twobros", "batiora"}


async def crawl_and_save(
    db: AsyncIOMotorDatabase,
    query: str,
    sources: list[str],
    max_results: int = 20,
) -> list[str]:
    """Search requested sources, save products + quality scores. Returns product IDs."""
    all_scraped: list[ScrapedProduct] = []

    # Amazon/Flipkart: prefix query with each brand name so results stay on-brand
    if "amazon" in sources:
        async with AmazonCrawler() as crawler:
            for brand in ALLOWED_BRANDS:
                branded_query = f"{brand} {query}"
                results = await crawler.search(branded_query, max_results // len(ALLOWED_BRANDS) + 1)
                # Keep only results whose name contains an allowed brand
                results = [r for r in results if _is_allowed_brand(r.name)]
                all_scraped.extend(results)

    if "flipkart" in sources:
        async with FlipkartCrawler() as crawler:
            for brand in ALLOWED_BRANDS:
                branded_query = f"{brand} {query}"
                results = await crawler.search(branded_query, max_results // len(ALLOWED_BRANDS) + 1)
                results = [r for r in results if _is_allowed_brand(r.name)]
                all_scraped.extend(results)

    # Brand sites: search within their own collections
    for brand_key in ("anveshan", "rosier", "twobros", "batiora"):
        if brand_key in sources:
            async with BrandSiteCrawler(brand_key) as crawler:
                results = await crawler.search(query, max_results)
                all_scraped.extend(results)

    product_ids = []
    for scraped in all_scraped:
        pid = await _upsert_product(db, scraped)
        if pid:
            product_ids.append(pid)

    return product_ids


async def crawl_url_and_save(db: AsyncIOMotorDatabase, url: str) -> str | None:
    """Crawl a single product URL. Only allowed domains are accepted."""
    source = _detect_source(url)
    if source is None:
        raise ValueError(
            f"URL not from an allowed source. Allowed: amazon.in, flipkart.com, "
            f"anveshan.farm, rosierfoods.com, twobrothersindiashop.com"
        )

    scraped: ScrapedProduct | None = None

    if source == "amazon":
        async with AmazonCrawler() as c:
            scraped = await c.get_product(url)
    elif source == "flipkart":
        async with FlipkartCrawler() as c:
            scraped = await c.get_product(url)
    else:
        # Brand site — source is the brand key
        async with BrandSiteCrawler(source) as c:
            scraped = await c.get_product(url)

    if not scraped:
        return None

    return await _upsert_product(db, scraped)


async def crawl_brand_site_all(
    db: AsyncIOMotorDatabase,
    brand_key: str,
    max_results: int = 50,
) -> list[str]:
    """Crawl all products from a brand site's full collection."""
    async with BrandSiteCrawler(brand_key) as crawler:
        results = await crawler.search("", max_results)  # empty query = browse all

    product_ids = []
    for scraped in results:
        pid = await _upsert_product(db, scraped)
        if pid:
            product_ids.append(pid)
    return product_ids


# ── Shared upsert logic ───────────────────────────────────────────────────────

async def _upsert_product(db: AsyncIOMotorDatabase, scraped: ScrapedProduct) -> str | None:
    now = datetime.utcnow()

    price_point = None
    if scraped.price is not None:
        price_point = PricePoint(
            price=scraped.price,
            currency=scraped.currency,
            unit=scraped.unit,
            in_stock=scraped.in_stock,
        ).model_dump()

    score_data = await analyze_product(scraped)
    quality_score = QualityScore(
        overall_score=score_data["overall_score"],
        ingredient_score=score_data.get("ingredient_score"),
        review_score=score_data.get("review_score"),
        certification_score=score_data.get("certification_score"),
        social_score=score_data.get("social_score"),
        red_flags=score_data.get("red_flags") or [],
        green_flags=score_data.get("green_flags") or [],
        summary=score_data.get("summary"),
        raw_analysis=score_data,
    ).model_dump()

    existing = await db.products.find_one({"source_url": scraped.source_url})

    if existing:
        update: dict = {
            "$set": {
                "rating": scraped.rating,
                "review_count": scraped.review_count,
                "last_crawled_at": now,
            },
            "$push": {"quality_scores": {"$each": [quality_score], "$position": 0}},
        }
        if scraped.ingredients:
            update["$set"]["ingredients"] = scraped.ingredients
        if scraped.certifications:
            update["$set"]["certifications"] = scraped.certifications
        if price_point:
            update["$push"]["price_history"] = price_point

        await db.products.update_one({"_id": existing["_id"]}, update)
        return str(existing["_id"])
    else:
        doc = ProductDoc(
            name=scraped.name,
            brand=scraped.brand,
            source=scraped.source,
            source_url=scraped.source_url,
            image_url=scraped.image_url,
            ingredients=scraped.ingredients,
            certifications=scraped.certifications or [],
            description=scraped.description,
            rating=scraped.rating,
            review_count=scraped.review_count,
            raw_data=scraped.raw_data,
            price_history=[PricePoint(**price_point)] if price_point else [],
            quality_scores=[QualityScore(**quality_score)],
            last_crawled_at=now,
        ).model_dump()

        result = await db.products.insert_one(doc)
        return str(result.inserted_id)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_source(url: str) -> str | None:
    """Return source key for the URL, or None if not an allowed domain."""
    if "amazon.in" in url or "amazon.com" in url:
        return "amazon"
    if "flipkart.com" in url:
        return "flipkart"
    brand_key = brand_key_from_url(url)
    return brand_key  # None if not an allowed brand domain


def _is_allowed_brand(product_name: str) -> bool:
    name_lower = product_name.lower()
    return any(b.lower() in name_lower for b in ALLOWED_BRANDS)
