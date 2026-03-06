# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

A food quality and price comparison tool. It crawls **only these 5 sources** to scrape food product data (ingredients, certifications, ratings), scores quality using Claude AI, and tracks prices over time:

| Source key | Domain | Type |
|---|---|---|
| `amazon` | amazon.in | Marketplace |
| `flipkart` | flipkart.com | Marketplace |
| `anveshan` | anveshan.farm | Brand site |
| `rosier` | rosierfoods.com | Brand site |
| `twobros` | twobrothersindiashop.com | Brand site |

Amazon/Flipkart searches are scoped to these 3 brands only. URL crawls from any other domain are rejected.

## Commands

### Backend (Python / FastAPI)

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium     # must run once before crawlers work
cp .env.example .env            # fill ANTHROPIC_API_KEY and MONGODB_URI
uvicorn main:app --reload --port 8000
```

API docs auto-generated at `http://localhost:8000/docs`.

### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev          # http://localhost:3000
npm run build        # production build
npm run lint         # ESLint
```

## Architecture

### Backend (`backend/`)

```
main.py              ← FastAPI app, CORS, startup/shutdown DB lifecycle
config.py            ← pydantic-settings (reads .env)
db/
  database.py        ← Motor (async MongoDB) client, get_db(), init_db() creates indexes
  models.py          ← Pydantic document models: ProductDoc, CrawlJobDoc, PricePoint, QualityScore
crawlers/
  base.py            ← BaseCrawler ABC + ScrapedProduct dataclass
  amazon.py          ← Playwright-based Amazon.in scraper
  flipkart.py        ← Playwright-based Flipkart scraper
  brand_sites.py     ← BrandSiteCrawler for Anveshan/Rosier/Two Brothers (Shopify-aware)
                       Also exports BRAND_CONFIGS, DOMAIN_TO_BRAND, brand_key_from_url()
analyzers/
  quality.py         ← Claude Sonnet quality scoring (0-100 across 4 dimensions)
services/
  crawl_service.py   ← Orchestrates crawlers → MongoDB upsert → quality analysis
                       VALID_SOURCES constant, _detect_source() domain allowlist
api/
  products.py        ← GET /products/, GET /products/{id}, GET /products/compare/
  crawl.py           ← POST /crawl/search, POST /crawl/url, POST /crawl/brand, GET /crawl/jobs
```

**Data flow**: `POST /crawl/search` → FastAPI BackgroundTask → `crawl_service.crawl_and_save()` → crawlers → `_upsert_product()` → `analyzers/quality.py` → MongoDB write.

**Crawl jobs** run in FastAPI `BackgroundTasks`. Status (`pending → running → done/failed`) tracked in `crawl_jobs` collection. Frontend polls `GET /crawl/jobs/{id}` every 3 seconds.

**Quality scoring**: `analyzers/quality.py` sends product data to `claude-sonnet-4-6`. Rule-based fallback runs if Claude call fails.

**Brand site crawler** (`brand_sites.py`): Shopify-aware — uses `/collections/all` for browsing and `/search?type=product&q=` for keyword search. Claude Haiku extracts structured fields from page text.

### Allowed sources enforcement

- `VALID_SOURCES` in `crawl_service.py` — set of accepted source keys; API validates against this
- `_detect_source(url)` returns the source key or `None` for disallowed domains; `crawl_url_and_save()` raises `ValueError` for `None`
- Amazon/Flipkart search results filtered via `_is_allowed_brand()` — only keeps products whose name contains Anveshan, Rosier Foods, or Two Brothers

### MongoDB schema

Two collections:

**`products`** — price history and quality scores embedded as arrays:
```
{ source_url (unique), name, brand, source, ingredients, certifications,
  rating, review_count, raw_data,
  price_history: [{price, currency, unit, in_stock, recorded_at}],
  quality_scores: [{overall_score, ingredient_score, review_score,
                    certification_score, red_flags, green_flags, summary, scored_at}],
  created_at, last_crawled_at }
```

**`crawl_jobs`** — `{ url, source, query, status, products_found, error, created_at, completed_at }`

Product IDs are MongoDB ObjectId strings (24-char hex).

### Frontend (`frontend/src/`)

```
app/
  page.tsx              ← Home: search + URL crawl; source checkboxes for all 5 sources
  products/[id]/page.tsx ← Product detail: quality score card, price chart, ingredients
  jobs/page.tsx         ← Crawl job status list (polls every 5s)
components/
  ProductCard.tsx       ← Card shown in search results (SOURCE_LABEL maps all 5 source keys)
  QualityBadge.tsx      ← Color-coded 0-100 badge (green/yellow/red)
  QualityScoreCard.tsx  ← Breakdown bars + red/green flags + AI summary
  PriceHistory.tsx      ← Recharts AreaChart of price over time
lib/
  api.ts                ← fetch wrappers: getProducts, triggerSearch, triggerUrlCrawl, triggerBrandCrawl
  types.ts              ← TypeScript interfaces matching backend Pydantic schemas
```

Frontend is **Next.js 14 App Router**. Product detail page is a server component; home and jobs pages are `"use client"`.

## Key patterns

- **Shopify brand sites**: all 3 brand sites use Shopify. Product links are detected by `/products/` in href. Collection browsing via `/collections/all`, search via `/search?type=product&q=`.
- **Crawler anti-bot**: realistic Chrome user-agent, `domcontentloaded` wait. Flipkart popup dismissed programmatically.
- **DB upsert**: `_upsert_product()` matches on `source_url` (unique index). Uses `$push` to append new price/score entries.
- **Price/quality filtering**: applied post-cursor in Python — acceptable for current data volumes.
- **Currency**: default INR. `unit` (e.g. "500g") stored separately.

## Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | backend `.env` | Claude API access |
| `MONGODB_URI` | backend `.env` | MongoDB connection string |
| `MONGODB_DB` | backend `.env` | Database name (default: `food_profiler`) |
| `NEXT_PUBLIC_API_URL` | frontend `.env.local` | Backend base URL |

## Adding a new brand site

1. Add a `BrandConfig` entry to `BRAND_CONFIGS` in `backend/crawlers/brand_sites.py`
2. Add the domain to `DOMAIN_TO_BRAND` in the same file
3. Add the brand name to `ALLOWED_BRANDS` in `backend/services/crawl_service.py`
4. Add the source key to `VALID_SOURCES` in `crawl_service.py`
5. Add the source to `ALL_SOURCES` in `frontend/src/app/page.tsx`
6. Add the label to `SOURCE_LABEL` in `frontend/src/components/ProductCard.tsx`
