"""
POST /chat  — natural-language Q&A over the stored product database.

Loads all products (with full price history and quality scores) from MongoDB,
formats them as context, then asks Claude to answer the user's question.
"""
from datetime import datetime, timezone

import anthropic
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from config import settings
from db.database import get_db
from db.models import serialize_doc

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


# ── helpers ───────────────────────────────────────────────────────────────────

def _fmt_date(val) -> str:
    if val is None:
        return "unknown"
    if hasattr(val, "isoformat"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]


def _build_product_context(docs: list[dict]) -> str:
    """Serialize products into compact text for Claude's context."""
    lines: list[str] = []
    for doc in docs:
        doc = serialize_doc(doc)
        name = doc.get("name", "?")
        brand = doc.get("brand") or doc.get("source", "?")
        source = doc.get("source", "?")
        ingredients = doc.get("ingredients") or "not available"
        certs = ", ".join(doc.get("certifications") or []) or "none"
        rating = doc.get("rating")
        latest_score = None

        scores = doc.get("quality_scores") or []
        if scores:
            s = scores[-1]  # latest
            latest_score = s.get("overall_score")

        prices = doc.get("price_history") or []
        price_lines = []
        for p in prices:
            price_lines.append(
                f"  {_fmt_date(p.get('recorded_at'))}: ₹{p.get('price')} / {p.get('unit') or 'unit'}"
            )

        lines.append(f"---\nProduct: {name}")
        lines.append(f"Brand: {brand} | Source: {source}")
        if latest_score is not None:
            lines.append(f"Quality score: {latest_score:.0f}/100")
        if rating is not None:
            lines.append(f"Customer rating: {rating}")
        lines.append(f"Certifications: {certs}")
        lines.append(f"Ingredients: {ingredients[:300]}" if len(ingredients) > 300 else f"Ingredients: {ingredients}")
        if price_lines:
            lines.append("Price history:")
            lines.extend(price_lines)
        else:
            lines.append("Price history: none recorded")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are a helpful food quality assistant for the Batiora food profiler tool.
You have access to a database of food products (mainly from Anveshan, Rosier Foods, Two Brothers Organic, and Batiora Farm Fresh) including their price history, quality scores, ingredients, and certifications.

Answer questions about prices, quality, ingredients, or comparisons using the PRODUCT DATABASE provided.
When answering price questions, always mention the specific date and unit (e.g. per kg, per 500g).
If the requested product or date is not in the database, say so clearly.
Be concise and factual. Do not make up data."""


# ── endpoint ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    db: AsyncIOMotorDatabase = get_db()

    # Fetch all products with history (cap at 200 for context size)
    cursor = db.products.find({}).limit(200)
    docs = [doc async for doc in cursor]

    product_context = _build_product_context(docs)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    system_with_data = (
        f"{SYSTEM_PROMPT}\n\nToday's date: {today}\n\n"
        f"PRODUCT DATABASE ({len(docs)} products):\n{product_context}"
    )

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system_with_data,
        messages=messages,
    )

    reply = response.content[0].text
    return ChatResponse(reply=reply)
