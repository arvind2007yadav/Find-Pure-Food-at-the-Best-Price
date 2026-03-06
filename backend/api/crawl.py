"""Endpoints to trigger crawls and check crawl job status."""
import logging
import traceback
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from db.database import get_db
from db.models import CrawlJobDoc, serialize_doc
from services.crawl_service import (
    VALID_SOURCES,
    crawl_and_save,
    crawl_brand_site_all,
    crawl_url_and_save,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crawl", tags=["crawl"])


class SearchRequest(BaseModel):
    query: str
    sources: list[str] = ["amazon", "flipkart", "anveshan", "rosier", "twobros"]
    max_results: int = 20


class UrlRequest(BaseModel):
    url: str


class BrandCrawlRequest(BaseModel):
    brand: str   # anveshan | rosier | twobros
    max_results: int = 50


class CrawlJobOut(BaseModel):
    id: str
    url: str | None
    source: str
    query: str | None
    status: str
    products_found: int
    error: str | None
    created_at: str
    completed_at: str | None


def _job_out(doc: dict) -> CrawlJobOut:
    doc = serialize_doc(doc)
    return CrawlJobOut(
        id=doc["id"],
        url=doc.get("url"),
        source=doc["source"],
        query=doc.get("query"),
        status=doc["status"],
        products_found=doc.get("products_found", 0),
        error=doc.get("error"),
        created_at=doc["created_at"].isoformat() if hasattr(doc.get("created_at"), "isoformat") else str(doc.get("created_at", "")),
        completed_at=doc["completed_at"].isoformat() if doc.get("completed_at") and hasattr(doc["completed_at"], "isoformat") else None,
    )


@router.post("/search", status_code=202)
async def trigger_search(req: SearchRequest, background_tasks: BackgroundTasks):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")
    bad = set(req.sources) - VALID_SOURCES
    if bad:
        raise HTTPException(status_code=400, detail=f"Unknown sources: {bad}. Allowed: {VALID_SOURCES}")

    db: AsyncIOMotorDatabase = get_db()
    doc = CrawlJobDoc(url="search", source=",".join(req.sources), query=req.query).model_dump()
    result = await db.crawl_jobs.insert_one(doc)
    job_id = str(result.inserted_id)

    background_tasks.add_task(_run_search, job_id, req.query, req.sources, req.max_results)
    return {"job_id": job_id, "status": "pending"}


@router.post("/url", status_code=202)
async def trigger_url_crawl(req: UrlRequest, background_tasks: BackgroundTasks):
    db: AsyncIOMotorDatabase = get_db()
    doc = CrawlJobDoc(url=req.url, source="url").model_dump()
    result = await db.crawl_jobs.insert_one(doc)
    job_id = str(result.inserted_id)

    background_tasks.add_task(_run_url_crawl, job_id, req.url)
    return {"job_id": job_id, "status": "pending"}


@router.post("/brand", status_code=202)
async def trigger_brand_crawl(req: BrandCrawlRequest, background_tasks: BackgroundTasks):
    brand_sources = {"anveshan", "rosier", "twobros"}
    if req.brand not in brand_sources:
        raise HTTPException(status_code=400, detail=f"brand must be one of {brand_sources}")

    db: AsyncIOMotorDatabase = get_db()
    doc = CrawlJobDoc(url=req.brand, source=req.brand, query="full collection").model_dump()
    result = await db.crawl_jobs.insert_one(doc)
    job_id = str(result.inserted_id)

    background_tasks.add_task(_run_brand_crawl, job_id, req.brand, req.max_results)
    return {"job_id": job_id, "status": "pending"}


@router.get("/jobs/{job_id}", response_model=CrawlJobOut)
async def get_job(job_id: str):
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    db: AsyncIOMotorDatabase = get_db()
    doc = await db.crawl_jobs.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_out(doc)


@router.get("/jobs", response_model=list[CrawlJobOut])
async def list_jobs(limit: int = 20):
    db: AsyncIOMotorDatabase = get_db()
    cursor = db.crawl_jobs.find().sort("created_at", -1).limit(limit)
    return [_job_out(doc) async for doc in cursor]


# ── Background task runners ───────────────────────────────────────────────────

async def _run_search(job_id: str, query: str, sources: list[str], max_results: int):
    db: AsyncIOMotorDatabase = get_db()
    oid = ObjectId(job_id)
    await db.crawl_jobs.update_one({"_id": oid}, {"$set": {"status": "running"}})
    try:
        ids = await crawl_and_save(db, query, sources, max_results)
        await db.crawl_jobs.update_one(
            {"_id": oid},
            {"$set": {"status": "done", "products_found": len(ids), "completed_at": datetime.utcnow()}},
        )
    except Exception as e:
        err = traceback.format_exc()
        logger.error("Search job %s failed:\n%s", job_id, err)
        await db.crawl_jobs.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "error": err, "completed_at": datetime.utcnow()}},
        )


async def _run_url_crawl(job_id: str, url: str):
    db: AsyncIOMotorDatabase = get_db()
    oid = ObjectId(job_id)
    await db.crawl_jobs.update_one({"_id": oid}, {"$set": {"status": "running"}})
    try:
        pid = await crawl_url_and_save(db, url)
        await db.crawl_jobs.update_one(
            {"_id": oid},
            {"$set": {"status": "done", "products_found": 1 if pid else 0, "completed_at": datetime.utcnow()}},
        )
    except Exception as e:
        err = traceback.format_exc()
        logger.error("URL crawl job %s failed:\n%s", job_id, err)
        await db.crawl_jobs.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "error": err, "completed_at": datetime.utcnow()}},
        )


async def _run_brand_crawl(job_id: str, brand_key: str, max_results: int):
    db: AsyncIOMotorDatabase = get_db()
    oid = ObjectId(job_id)
    await db.crawl_jobs.update_one({"_id": oid}, {"$set": {"status": "running"}})
    try:
        ids = await crawl_brand_site_all(db, brand_key, max_results)
        await db.crawl_jobs.update_one(
            {"_id": oid},
            {"$set": {"status": "done", "products_found": len(ids), "completed_at": datetime.utcnow()}},
        )
    except Exception as e:
        err = traceback.format_exc()
        logger.error("Brand crawl job %s failed:\n%s", job_id, err)
        await db.crawl_jobs.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "error": err, "completed_at": datetime.utcnow()}},
        )
