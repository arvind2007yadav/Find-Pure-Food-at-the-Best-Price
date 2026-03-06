"""Flipkart crawler — sync_playwright in asyncio.to_thread() for Windows compatibility."""
import asyncio
import re

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from crawlers._win_compat import ensure_proactor_loop
from crawlers.base import BaseCrawler, ScrapedProduct

FLIPKART_BASE = "https://www.flipkart.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class FlipkartCrawler(BaseCrawler):

    async def search(self, query: str, max_results: int = 20) -> list[ScrapedProduct]:
        return await asyncio.to_thread(_sync_search, query, max_results)

    async def get_product(self, url: str) -> ScrapedProduct | None:
        return await asyncio.to_thread(_sync_get_product, url)


def _sync_search(query: str, max_results: int) -> list[ScrapedProduct]:
    ensure_proactor_loop()
    results: list[ScrapedProduct] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        try:
            page.goto(f"{FLIPKART_BASE}/search?q={query.replace(' ', '+')}", wait_until="domcontentloaded", timeout=30000)
            close_btn = page.query_selector("button._2KpZ6l._2doB4z")
            if close_btn:
                close_btn.click()
            items = page.query_selector_all("._1AtVbE") or page.query_selector_all("._2kHMtA")
            for item in items[:max_results]:
                try:
                    name_el = item.query_selector("._4rR01T, .s1Q9rs")
                    link_el = item.query_selector("a._1fQZEK, a.s1Q9rs")
                    price_el = item.query_selector("._30jeq3")
                    rating_el = item.query_selector("._3LWZlK")
                    img_el = item.query_selector("img._396cs4, img._2r_T1I")

                    name = name_el.inner_text().strip() if name_el else ""
                    href = link_el.get_attribute("href") if link_el else None
                    src_url = f"{FLIPKART_BASE}{href}" if href and href.startswith("/") else href or ""
                    price = _parse_price(price_el.inner_text() if price_el else "")
                    rating_txt = rating_el.inner_text().strip() if rating_el else ""
                    rating = float(rating_txt) if rating_txt else None
                    img = img_el.get_attribute("src") if img_el else None

                    if name and src_url:
                        results.append(ScrapedProduct(
                            name=name, source="flipkart", source_url=src_url,
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
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            close_btn = page.query_selector("button._2KpZ6l._2doB4z")
            if close_btn:
                close_btn.click()
            name = _text(page, ".B_NuCI")
            brand = _text(page, ".G6XhRU")
            price = _parse_price(_text(page, "._30jeq3._16Jk6d") or "")
            img_el = page.query_selector("._396cs4")
            img = img_el.get_attribute("src") if img_el else None
            rating_txt = _text(page, "._3LWZlK") or ""
            rating = float(rating_txt) if rating_txt else None
            review_count = _parse_int(_text(page, "._2_R_DZ span") or "")
            ingredients = _spec_value(page, "Ingredient")
            certifications = _extract_certifications(page)
            desc = _text(page, "._1mXcCf")
            return ScrapedProduct(
                name=name or "Unknown", source="flipkart", source_url=url,
                price=price, brand=brand, image_url=img, ingredients=ingredients,
                certifications=certifications, description=desc,
                rating=rating, review_count=review_count,
                raw_data={"specs": _all_specs(page)},
            )
        except Exception:
            return None
        finally:
            context.close()
            browser.close()


def _text(page, selector):
    el = page.query_selector(selector)
    return el.inner_text().strip() if el else None

def _spec_value(page, key):
    for row in page.query_selector_all("._3-wDH3 tr"):
        txt = row.inner_text()
        if key.lower() in txt.lower():
            parts = txt.split("\t", 1)
            return parts[1].strip() if len(parts) > 1 else None
    return None

def _all_specs(page):
    specs = {}
    for row in page.query_selector_all("._3-wDH3 tr"):
        txt = row.inner_text().strip()
        parts = txt.split("\t", 1)
        if len(parts) == 2:
            specs[parts[0].strip()] = parts[1].strip()
    return specs

def _extract_certifications(page):
    full_text = page.inner_text("body")
    return [p for p in ["FSSAI", "ISO", "USDA Organic", "India Organic", "Halal", "Kosher", "GMP"]
            if p.lower() in full_text.lower()]

def _parse_price(text):
    if not text: return None
    m = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(m.group()) if m else None

def _parse_int(text):
    if not text: return None
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None
