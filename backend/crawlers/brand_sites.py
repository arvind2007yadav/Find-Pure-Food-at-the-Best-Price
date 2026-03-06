"""
Brand site crawlers — sync_playwright in asyncio.to_thread() for Windows compatibility.
Claude Haiku extracts structured fields from page text (async, called after thread returns).

Allowed brands:
  anveshan  → https://www.anveshan.farm
  rosier    → https://www.rosierfoods.com
  twobros   → https://twobrothersindiashop.com
  batiora   → https://batiora.com
"""
import asyncio
import json
import logging
from dataclasses import dataclass

import anthropic
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from config import settings
from crawlers._win_compat import ensure_proactor_loop
from crawlers.base import BaseCrawler, ScrapedProduct

logger = logging.getLogger(__name__)
_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

EXTRACT_PROMPT = """\
You are a product data extractor for an Indian food brand website.
Given the text content of a food product page, extract the following fields as JSON:
- name: product name (string)
- price: numeric price in INR (float, no symbol)
- unit: pack size or unit (e.g. "500g", "1L", "per piece") or null
- ingredients: full ingredients list as a string, or null
- certifications: list of certifications (e.g. ["FSSAI", "Organic", "ISO"]) — empty list if none
- description: short product description (1-3 sentences) or null
- in_stock: true or false

Return ONLY valid JSON with exactly these keys. Use null for missing fields.

Page text:
{text}
"""


@dataclass
class BrandConfig:
    key: str
    name: str
    base_url: str
    collections_path: str


BRAND_CONFIGS: dict[str, BrandConfig] = {
    "anveshan": BrandConfig(
        key="anveshan", name="Anveshan",
        base_url="https://www.anveshan.farm",
        collections_path="/collections/all",
    ),
    "rosier": BrandConfig(
        key="rosier", name="Rosier Foods",
        base_url="https://www.rosierfoods.com",
        collections_path="/collections/all",
    ),
    "twobros": BrandConfig(
        key="twobros", name="Two Brothers Organic",
        base_url="https://twobrothersindiashop.com",
        collections_path="/collections/all",
    ),
    "batiora": BrandConfig(
        key="batiora", name="Batiora Farm Fresh",
        base_url="https://batiora.com",
        collections_path="/collections/all",
    ),
}

DOMAIN_TO_BRAND: dict[str, str] = {
    "anveshan.farm": "anveshan",
    "rosierfoods.com": "rosier",
    "twobrothersindiashop.com": "twobros",
    "batiora.com": "batiora",
}


class BrandSiteCrawler(BaseCrawler):

    def __init__(self, brand_key: str):
        if brand_key not in BRAND_CONFIGS:
            raise ValueError(f"Unknown brand: {brand_key}. Allowed: {list(BRAND_CONFIGS)}")
        self.config = BRAND_CONFIGS[brand_key]

    async def search(self, query: str, max_results: int = 20) -> list[ScrapedProduct]:
        search_url = (
            f"{self.config.base_url}/search?type=product&q={query.replace(' ', '+')}"
            if query.strip()
            else self.config.base_url + self.config.collections_path
        )
        product_urls = await asyncio.to_thread(
            _sync_get_product_links, self.config.base_url, search_url, max_results
        )
        if not product_urls:
            fallback_url = self.config.base_url + self.config.collections_path
            product_urls = await asyncio.to_thread(
                _sync_get_product_links, self.config.base_url, fallback_url, max_results
            )

        logger.info("Brand %s: found %d product URLs", self.config.key, len(product_urls))

        results = []
        for url in product_urls[:max_results]:
            product = await self.get_product(url)
            if product:
                results.append(product)
        return results

    async def get_product(self, url: str) -> ScrapedProduct | None:
        page_text, image_url = await asyncio.to_thread(_sync_fetch_page, url)
        if not page_text:
            return None
        data = await _extract_with_claude(page_text)
        if not data:
            return None
        return ScrapedProduct(
            name=data.get("name") or "Unknown",
            source=self.config.key,
            source_url=url,
            price=_safe_float(data.get("price")),
            currency="INR",
            unit=data.get("unit"),
            brand=self.config.name,
            image_url=image_url,
            ingredients=data.get("ingredients"),
            certifications=data.get("certifications") or [],
            description=data.get("description"),
            in_stock=data.get("in_stock"),
            raw_data=data,
        )


# ── Sync browser functions ────────────────────────────────────────────────────

def _sync_get_product_links(base_url: str, url: str, limit: int) -> list[str]:
    ensure_proactor_loop()
    links: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        try:
            # networkidle waits for JS-rendered product grids to finish loading
            page.goto(url, wait_until="networkidle", timeout=45000)

            # Extract all hrefs from the live DOM (post-JS-execution)
            all_hrefs: list[str] = page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]'))
                          .map(a => a.getAttribute('href'))
            """)

            seen: set[str] = set()
            for href in all_hrefs:
                if not href:
                    continue
                # Match Shopify product URLs: /products/<slug>
                if "/products/" in href:
                    # Strip query strings and fragments
                    clean = href.split("?")[0].split("#")[0]
                    full = clean if clean.startswith("http") else base_url + clean
                    if full not in seen:
                        seen.add(full)
                        links.append(full)
                if len(links) >= limit:
                    break

            logger.info("_sync_get_product_links(%s): found %d links", url, len(links))
        except PlaywrightTimeout:
            logger.warning("Timeout loading %s", url)
        finally:
            context.close()
            browser.close()
    return links


def _sync_fetch_page(url: str) -> tuple[str | None, str | None]:
    ensure_proactor_loop()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            # 1. og:image is the most reliable product image on Shopify sites
            image_url = None
            og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
            if og and og.get("content"):
                src = og["content"]
                image_url = src if src.startswith("http") else "https:" + src

            # 2. Fallback: first Shopify CDN product image in the DOM
            if not image_url:
                for img in soup.find_all("img", src=True):
                    src: str = img["src"]
                    if "cdn.shopify" in src and any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                        image_url = src if src.startswith("http") else "https:" + src
                        break

            # 3. Last resort: any image with a known extension
            if not image_url:
                for img in soup.find_all("img", src=True):
                    src = img["src"]
                    if any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                        image_url = src if src.startswith("http") else "https:" + src
                        break

            for tag in soup(["script", "style", "nav", "footer", "header", "svg", "noscript"]):
                tag.decompose()

            return soup.get_text(separator=" ", strip=True)[:8000], image_url
        except PlaywrightTimeout:
            logger.warning("Timeout loading product page %s", url)
            return None, None
        finally:
            context.close()
            browser.close()


# ── Async Claude extraction ───────────────────────────────────────────────────

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


def brand_key_from_url(url: str) -> str | None:
    for domain, key in DOMAIN_TO_BRAND.items():
        if domain in url:
            return key
    return None


def _safe_float(v) -> float | None:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None
