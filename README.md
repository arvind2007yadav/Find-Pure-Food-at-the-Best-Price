# Food Quality Risk Profiler

Crawls Amazon, Flipkart, and brand websites to score food product quality using AI, then tracks prices over time so you can find the **purest product at the cheapest price**.

## How it works

1. **Search** by product name or paste a direct product URL
2. Crawlers scrape product details (ingredients, ratings, certifications) using Playwright
3. Claude AI analyzes all quality signals and produces a **quality score (0-100)**
4. Price snapshots are stored over time to show price trends
5. Front-end displays ranked results with quality badges and price history charts

## Quality scoring

| Signal | Weight |
|---|---|
| Ingredients (additives, preservatives) | 35% |
| Customer reviews & ratings | 25% |
| Certifications (FSSAI, Organic, ISO…) | 20% |
| Social/sentiment (future) | 20% |

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env       # fill in ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000
