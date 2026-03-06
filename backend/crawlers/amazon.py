"""Amazon.in crawler — sync_playwright in asyncio.to_thread() for Windows compatibility."""
import asyncio
import re

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from crawlers._win_compat import ensure_proactor_loop
from crawlers.base import BaseCrawler, ScrapedProduct

AMAZON_BASE = "https://www.amazon.in"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class AmazonCrawler(BaseCrawler):

    async def search(self, query: str, max_results: int = 20) -> list[ScrapedProduct]:
        return await asyncio.to_thread(_sync_search, query, max_results)

    async def get_product(self, url: str) -> ScrapedProduct | None:
        return await asyncio.to_thread(_sync_get_product, url)


def _sync_search(query: str, max_results: int) -> list[ScrapedProduct]:
    ensure_proactor_loop()
    results: list[ScrapedProduct] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=USER_AGENT, locale="en-IN")
        context.set_extra_http_headers({"Accept-Language": "en-IN,en;q=0.9"})
        page = context.new_page()
        try:
            page.goto(f"{AMAZON_BASE}/s?k={query.replace(' ', '+')}", wait_until="domcontentloaded", timeout=30000)
            for item in page.query_selector_all("[data-component-type='s-search-result']")[:max_results]:
                try:
                    title_el = item.query_selector("h2 a span")
                    link_el = item.query_selector("h2 a")
                    price_el = item.query_selector(".a-price .a-offscreen")
                    rating_el = item.query_selector(".a-icon-alt")
                    img_el = item.query_selector(".s-image")

                    name = title_el.inner_text().strip() if title_el else ""
                    href = link_el.get_attribute("href") if link_el else None
                    src_url = f"{AMAZON_BASE}{href}" if href and href.startswith("/") else href or ""
                    price = _parse_price(price_el.inner_text() if price_el else "")
                    rating = _parse_rating(rating_el.inner_text() if rating_el else "")
                    img = img_el.get_attribute("src") if img_el else None

                    if name and src_url:
                        results.append(ScrapedProduct(
                            name=name, source="amazon", source_url=src_url,
                            price=price, rating=rating, image_url=img,
                        ))
                except Exception:
                    continue
        except PlaywrightTimeout:
            pass
        finally:
            context.close()
            browser.close()
    return results


def _sync_get_product(url: str) -> ScrapedProduct | None:
    ensure_proactor_loop()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=USER_AGENT, locale="en-IN")
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            name = _text(page, "#productTitle")
            brand = _text(page, "#bylineInfo")
            price = _parse_price(_text(page, ".a-price .a-offscreen") or "")
            img_el = page.query_selector("#landingImage")
            img = img_el.get_attribute("src") if img_el else None
            desc = _text(page, "#productDescription p")
            rating = _parse_rating(_text(page, "span[data-hook='rating-out-of-text']") or "")
            review_count = _parse_int(_text(page, "span[data-hook='total-review-count']") or "")
            in_stock = "in stock" in (_text(page, "#availability span") or "").lower()
            ingredients = _table_value(page, "Ingredients")
            certifications = _extract_certifications(page)
            return ScrapedProduct(
                name=name or "Unknown", source="amazon", source_url=url,
                price=price, brand=brand, image_url=img, description=desc,
                ingredients=ingredients, certifications=certifications,
                rating=rating, review_count=review_count, in_stock=in_stock,
                raw_data={"detail_bullets": _detail_bullets(page)},
            )
        except Exception:
            return None
        finally:
            context.close()
            browser.close()


def _text(page, selector):
    el = page.query_selector(selector)
    return el.inner_text().strip() if el else None

def _table_value(page, key):
    for row in page.query_selector_all("#productDetails_techSpec_section_1 tr, #detailBullets_feature_div li"):
        txt = row.inner_text()
        if key.lower() in txt.lower():
            parts = txt.split(":", 1)
            return parts[1].strip() if len(parts) > 1 else None
    return None

def _detail_bullets(page):
    bullets = {}
    for row in page.query_selector_all("#detailBullets_feature_div li"):
        txt = row.inner_text().strip()
        parts = txt.split(":", 1)
        if len(parts) == 2:
            bullets[parts[0].strip()] = parts[1].strip()
    return bullets

def _extract_certifications(page):
    full_text = page.inner_text("body")
    return [p for p in ["FSSAI", "ISO", "USDA Organic", "India Organic", "Halal", "Kosher", "GMP"]
            if p.lower() in full_text.lower()]

def _parse_price(text):
    if not text: return None
    m = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(m.group()) if m else None

def _parse_rating(text):
    if not text: return None
    m = re.search(r"(\d+\.?\d*)", text)
    return float(m.group()) if m else None

def _parse_int(text):
    if not text: return None
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None
