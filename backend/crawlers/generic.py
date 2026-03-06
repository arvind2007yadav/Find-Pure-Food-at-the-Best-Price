"""Generic crawler — sync_playwright in thread + Claude Haiku extraction."""
import asyncio
import json

import anthropic
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from config import settings
from crawlers._win_compat import ensure_proactor_loop
from crawlers.base import BaseCrawler, ScrapedProduct

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

EXTRACT_PROMPT = """\
You are a product data extractor. Given the text content of a food product page,
extract the following fields in JSON format:
- name, brand, price (float), currency (default INR), unit, ingredients,
  certifications (list), description, rating (float), review_count (int), in_stock (bool)
Return ONLY valid JSON. Use null for missing fields.

Page text:
{text}
"""


class GenericCrawler(BaseCrawler):

    async def search(self, query: str, max_results: int = 20) -> list[ScrapedProduct]:
        return []

    async def get_product(self, url: str) -> ScrapedProduct | None:
        page_text = await asyncio.to_thread(_sync_fetch_text, url)
        if not page_text:
            return None
        data = await _extract_with_claude(page_text)
        if not data:
            return None
        return ScrapedProduct(
            name=data.get("name") or "Unknown",
            source="brand_site", source_url=url,
            price=_sf(data.get("price")), currency=data.get("currency") or "INR",
            unit=data.get("unit"), brand=data.get("brand"),
            ingredients=data.get("ingredients"),
            certifications=data.get("certifications") or [],
            description=data.get("description"),
            rating=_sf(data.get("rating")), review_count=_si(data.get("review_count")),
            in_stock=data.get("in_stock"), raw_data=data,
        )


def _sync_fetch_text(url: str) -> str | None:
    ensure_proactor_loop()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator=" ", strip=True)[:8000]
        except PlaywrightTimeout:
            return None
        finally:
            context.close()
            browser.close()


async def _extract_with_claude(text: str) -> dict | None:
    try:
        response = await _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": EXTRACT_PROMPT.format(text=text)}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return None


def _sf(v):
    try: return float(v) if v is not None else None
    except: return None

def _si(v):
    try: return int(v) if v is not None else None
    except: return None
