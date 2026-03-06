# Find Pure Food at the Best Price

A personal food intelligence tool that automatically scans trusted organic food brands across Amazon, Flipkart, and their own websites — then uses AI to score each product's quality based on ingredients, certifications, and customer reviews. It also tracks prices over time so you always know when to buy.

---

## Table of Contents

1. [What This Does](#1-what-this-does)
2. [Why This Exists](#2-why-this-exists)
3. [Tracked Brands & Sources](#3-tracked-brands--sources)
4. [How the Quality Score Works](#4-how-the-quality-score-works)
5. [Features at a Glance](#5-features-at-a-glance)
6. [What You Need Before Starting](#6-what-you-need-before-starting)
7. [Getting Your API Keys](#7-getting-your-api-keys)
8. [Installation: Step by Step](#8-installation-step-by-step)
9. [Running the App](#9-running-the-app)
10. [Using the App](#10-using-the-app)
11. [How the Technology Works (Plain English)](#11-how-the-technology-works-plain-english)
12. [Project File Map](#12-project-file-map)
13. [Adding a New Brand](#13-adding-a-new-brand)
14. [Troubleshooting](#14-troubleshooting)
15. [Environment Variables Reference](#15-environment-variables-reference)

---

## 1. What This Does

You type a product name like **"A2 cow ghee"** or **"cold pressed mustard oil"**. The app:

1. Opens Amazon, Flipkart, and brand websites in an invisible browser (like a robot shopper)
2. Reads the product page — ingredients, certifications, ratings, price
3. Sends that data to Claude AI, which gives the product a **quality score out of 100**
4. Saves everything to a database so you can track prices over time
5. Lets you ask plain-language questions like *"What was the price of Anveshan ghee on 5th March?"* using the built-in AI chat assistant

---

## 2. Why This Exists

The Indian organic food market is full of products that claim to be pure, natural, and premium — but reading ingredient labels across 5 websites for every product you want to buy is time-consuming and confusing. This tool automates that research and gives you a single honest score so you can:

- Know which ghee actually has clean ingredients vs. just good marketing
- See if a product is cheaper on Amazon vs. the brand's own website
- Track whether prices spiked around festivals
- Ask questions about your stored data any time, without re-searching

---

## 3. Tracked Brands & Sources

The app is intentionally limited to trusted sources to avoid noise:

| Source | Website | What gets searched |
|---|---|---|
| **Anveshan** | anveshan.farm | Brand's own website |
| **Rosier Foods** | rosierfoods.com | Brand's own website |
| **Two Brothers Organic** | twobrothersindiashop.com | Brand's own website |
| **Batiora Farm Fresh** | batiora.com | Brand's own website |
| **Amazon** | amazon.in | Only products from the 4 brands above |
| **Flipkart** | flipkart.com | Only products from the 4 brands above |

Amazon and Flipkart searches are filtered — the app ignores unrelated sellers and only keeps products from the 4 brands it knows.

---

## 4. How the Quality Score Works

Every product gets a score from **0 to 100** calculated by Claude AI across four signals:

| Signal | Weight | What it looks at |
|---|---|---|
| **Ingredients** | 35% | Additives, preservatives, synthetic colours, hydrogenated fats — fewer = better |
| **Customer Reviews** | 25% | Star rating and review count — high confidence reviews score higher |
| **Certifications** | 20% | FSSAI, USDA Organic, India Organic, ISO — more trusted certs = higher score |
| **Social / Sentiment** | 20% | Reserved for future social media sentiment analysis |

**Score meaning:**

- **80–100** — Excellent. Clean ingredients, well certified, highly rated
- **60–79** — Good. Minor concerns but generally trustworthy
- **40–59** — Average. Some questionable additives or missing certifications
- **Below 40** — Poor. Likely contains additives, preservatives, or misleading claims

The AI also gives you specific **green flags** (positives, e.g. "A2 milk certified, no additives") and **red flags** (concerns, e.g. "Contains added colour, no organic certification") for each product.

---

## 5. Features at a Glance

| Feature | Description |
|---|---|
| **Keyword Search** | Search any product by name across all sources simultaneously |
| **URL Crawl** | Paste a direct product link from any allowed website to analyse just that product |
| **Quality Score Badge** | Colour-coded 0–100 score on every product card |
| **Quality Breakdown** | Detailed score breakdown with red/green flags and AI summary |
| **Price History Chart** | Line chart showing how a product's price changed over time |
| **AI Chat Assistant** | Ask natural-language questions about your stored product data |
| **Crawl Jobs Tracker** | See the status of any ongoing or past search jobs |
| **Price Trends Page** | Visual trend comparisons across products |

---

## 6. What You Need Before Starting

You need three things installed on your computer before you can run this app:

### A. Python 3.11 or higher

Python powers the backend (the part that crawls websites and talks to AI).

- Download from: https://www.python.org/downloads/
- During installation on Windows, tick **"Add Python to PATH"**
- Verify it worked: open a terminal and type `python --version`

### B. Node.js 18 or higher

Node.js powers the frontend (the website you see in your browser).

- Download from: https://nodejs.org/
- Choose the "LTS" version
- Verify: open a terminal and type `node --version`

### C. Git

Git lets you download this project and push updates.

- Download from: https://git-scm.com/
- Default installation options are fine

> **What is a terminal?**
> On Windows: search for "PowerShell" or "Command Prompt" in the Start menu.
> On Mac: search for "Terminal" in Spotlight.

---

## 7. Getting Your API Keys

The app needs two external services. Both have free tiers to get started.

### A. Anthropic API Key (Claude AI)

This is what the app uses to score product quality and power the chat assistant.

1. Go to https://console.anthropic.com/
2. Create a free account
3. Go to **API Keys** in the left menu
4. Click **Create Key**, give it a name like "food-profiler"
5. Copy the key — it looks like `sk-ant-api03-...`
6. You will paste this into `backend/.env` in the next step

> **Cost note:** Claude charges per use. Scoring one product costs roughly $0.001–0.005. For personal use with a few hundred products, expect less than $1/month.

### B. MongoDB Atlas (Database)

This is where all product data, price history, and quality scores are stored in the cloud — for free.

1. Go to https://www.mongodb.com/atlas
2. Click **Try Free** and create an account
3. Create a free **M0 cluster** (choose any region)
4. Under **Database Access**, create a user with a username and password — save these
5. Under **Network Access**, click **Add IP Address** → **Allow Access from Anywhere** (for local development)
6. Click **Connect** on your cluster → **Connect your application** → copy the connection string
   - It looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`
   - Replace `<password>` with the password you set in step 4
7. You will paste this into `backend/.env` in the next step

---

## 8. Installation: Step by Step

### Step 1 — Download the project

Open a terminal and run:

```bash
git clone https://github.com/arvind2007yadav/Find-Pure-Food-at-the-Best-Price.git
cd Find-Pure-Food-at-the-Best-Price
```

### Step 2 — Set up the Backend

Navigate into the backend folder:

```bash
cd backend
```

**Create an isolated Python environment** (keeps this project's packages separate from anything else on your computer):

```bash
# On Mac / Linux:
python -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal prompt. This means the environment is active.

**Install Python packages:**

```bash
pip install -r requirements.txt
```

This installs everything the backend needs. Takes 1–3 minutes.

**Install the browser for crawling:**

```bash
playwright install chromium
```

This downloads a lightweight Chrome browser that the crawlers use to open product pages invisibly. Takes 1–2 minutes.

**Create your secrets file:**

```bash
# On Mac / Linux:
cp .env.example .env

# On Windows (PowerShell):
copy .env.example .env
```

Now open the `.env` file in any text editor (Notepad is fine) and fill in your keys:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
MONGODB_URI=mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/
MONGODB_DB=food_profiler
CRAWL_INTERVAL_HOURS=24
MAX_CONCURRENT_CRAWLS=5
LOG_LEVEL=INFO
```

Save and close the file.

### Step 3 — Set up the Frontend

Open a **new terminal window** (keep the backend terminal open), then navigate to the frontend folder:

```bash
cd Find-Pure-Food-at-the-Best-Price/frontend
npm install
```

This installs all the website packages. Takes 1–3 minutes.

**Create the frontend config file:**

```bash
# On Mac / Linux:
cp .env.local.example .env.local

# On Windows:
copy .env.local.example .env.local
```

Open `.env.local` and verify it contains:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This tells the frontend where to find the backend on your computer.

---

## 9. Running the App

You need **two terminal windows open at the same time** — one for the backend, one for the frontend.

### Terminal 1 — Start the Backend

```bash
cd backend

# Activate the virtual environment first:
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac / Linux

python run.py
```

You should see:

```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

Leave this terminal open.

### Terminal 2 — Start the Frontend

```bash
cd frontend
npm run dev
```

You should see:

```
- Local: http://localhost:3000
```

Open your browser and go to **http://localhost:3000**

---

## 10. Using the App

### Searching for a product

1. Type a product name in the search box, e.g. `A2 ghee` or `cold pressed oil`
2. Select which sources to search (all are selected by default)
3. Click **Search**
4. The app crawls the selected websites (takes 30–90 seconds the first time)
5. Results appear as cards with quality score badges and latest prices

### Analysing a specific product URL

1. Find a product page on an allowed website (e.g. anveshan.farm)
2. Copy the URL from your browser's address bar
3. Paste it into the **"Or paste a product URL"** box
4. Click **Crawl URL**
5. The product is analysed and saved to your database

### Viewing product details

Click any product card to open the detail page, which shows:

- Full quality score breakdown (ingredient / review / certification sub-scores)
- Red flags (concerns) and green flags (positives) identified by AI
- AI-written summary of the product's quality
- Price history chart showing all recorded prices over time

### Using the AI Chat Assistant

Click the **chat bubble button** in the bottom-right corner of any page. Ask anything about your stored products:

- *"What was the price of Anveshan A2 cow ghee on 5th March?"*
- *"Which ghee has the highest quality score?"*
- *"Compare the certifications of Two Brothers and Anveshan honey"*
- *"Are there any products with red flags I should avoid?"*
- *"What is the cheapest cold pressed oil in my database?"*

The assistant reads your entire product database before answering, so it has full context and will not make up data.

### Checking crawl job status

Click **Crawl Jobs** in the navigation bar to see all search jobs — including ones still running, completed ones, and any that failed with error details.

---

## 11. How the Technology Works (Plain English)

### The Backend (Python / FastAPI)

Think of the backend as the **engine room**. It runs on your computer but has no visible interface — it does the heavy lifting in the background.

- **FastAPI** — Creates an API: a set of rules for how the frontend and backend communicate. When you click "Search", the frontend sends a request to the backend.
- **Playwright** — Controls a real Chrome browser invisibly. When the backend "crawls" Amazon, it is literally opening Amazon.in in a hidden window, reading the page, then closing it.
- **Anthropic SDK** — The library that sends data to Claude AI and receives scores back.
- **Motor** — The library that reads and writes to MongoDB.

### The Frontend (Next.js)

The frontend is the **website you see in your browser**. It never stores data itself — everything lives in MongoDB via the backend. The chat assistant widget sends your message to the backend, which calls Claude AI and returns the answer.

### The Database (MongoDB)

MongoDB stores everything permanently:

- Every product crawled (name, brand, ingredients, certifications, image, URL)
- Every price recorded (price, date, unit, in-stock status)
- Every quality score (overall score, sub-scores, flags, AI summary)
- Every crawl job (status, products found, any errors)

MongoDB Atlas is the cloud-hosted version, so your data is saved even if you restart your computer.

### Claude AI (Anthropic)

Two Claude models are used for different tasks:

| Model | Used for |
|---|---|
| **Claude Haiku** | Cheap and fast: extracts structured product data from raw webpage text; answers chat questions |
| **Claude Sonnet** | More capable: analyses ingredients, certifications, reviews and produces the nuanced 0–100 quality score |

### What happens when you click Search

```
You type "ghee" and click Search
        ↓
Frontend sends a search request to the backend
        ↓
Backend creates a crawl job (status: pending) and starts working in the background
        ↓
Invisible Chrome browser opens Amazon, Flipkart, brand websites
        ↓
Each product page is read — ingredients, price, rating extracted
        ↓
Brand site text is sent to Claude Haiku to parse into structured fields
        ↓
All product data is sent to Claude Sonnet → quality score returned
        ↓
Product saved to MongoDB (or updated if it already exists)
        ↓
Frontend checks every 3 seconds: "is the job done?"
        ↓
Job marked done → frontend fetches updated product list → cards appear on screen
```

---

## 12. Project File Map

```
Find-Pure-Food-at-the-Best-Price/
│
├── README.md                        ← This documentation
├── CLAUDE.md                        ← Instructions for the AI coding assistant
├── architecture.md                  ← Detailed technical diagram (Mermaid)
├── .gitignore                       ← Files excluded from version control
│
├── backend/                         ← Python backend (the engine room)
│   ├── main.py                      ← App entry point, wires everything together
│   ├── config.py                    ← Reads settings from the .env file
│   ├── run.py                       ← Shortcut script to start the server
│   ├── requirements.txt             ← List of Python packages needed
│   ├── .env.example                 ← Template — copy to .env and fill in your keys
│   │
│   ├── api/
│   │   ├── products.py              ← Endpoints: list products, get one, compare
│   │   ├── crawl.py                 ← Endpoints: trigger search, crawl URL, job status
│   │   └── chat.py                  ← Endpoint: AI chat assistant Q&A
│   │
│   ├── crawlers/
│   │   ├── base.py                  ← Shared crawler logic and data shapes
│   │   ├── amazon.py                ← Amazon.in scraper
│   │   ├── flipkart.py              ← Flipkart.com scraper
│   │   ├── brand_sites.py           ← Anveshan / Rosier / Two Brothers / Batiora scraper
│   │   └── generic.py               ← Fallback for any allowed brand URL
│   │
│   ├── analyzers/
│   │   └── quality.py               ← Sends product data to Claude Sonnet, returns score
│   │
│   ├── services/
│   │   └── crawl_service.py         ← Orchestrates the full crawl → save → score pipeline
│   │
│   └── db/
│       ├── database.py              ← MongoDB connection setup
│       └── models.py                ← Data shapes: Product, PricePoint, QualityScore, CrawlJob
│
└── frontend/                        ← Next.js website (what you see in the browser)
    ├── package.json                 ← List of JS packages needed
    ├── .env.local.example           ← Template — copy to .env.local and set backend URL
    │
    └── src/
        ├── app/
        │   ├── layout.tsx           ← Shared header, navigation, chat button (all pages)
        │   ├── page.tsx             ← Home: search + URL crawl + product grid
        │   ├── products/[id]/       ← Product detail: quality breakdown + price chart
        │   ├── jobs/                ← Crawl jobs status list
        │   └── trends/              ← Price trend visualisations
        │
        ├── components/
        │   ├── ChatAssistant.tsx    ← Floating AI chat widget (bottom-right corner)
        │   ├── ProductCard.tsx      ← Card shown in search results grid
        │   ├── QualityBadge.tsx     ← Colour-coded score badge (green / yellow / red)
        │   ├── QualityScoreCard.tsx ← Detailed score breakdown with flags
        │   └── PriceHistory.tsx     ← Price-over-time area chart
        │
        └── lib/
            ├── api.ts               ← Functions that call the backend API
            └── types.ts             ← Data type definitions
```

---

## 13. Adding a New Brand

To add a new food brand (e.g. Organic India), edit these 6 places:

1. **`backend/crawlers/brand_sites.py`** — Add a `BrandConfig` entry with the brand's name, domain, and URL patterns
2. **`backend/crawlers/brand_sites.py`** — Add the domain to the `DOMAIN_TO_BRAND` dictionary
3. **`backend/services/crawl_service.py`** — Add the brand name to `ALLOWED_BRANDS`
4. **`backend/services/crawl_service.py`** — Add the source key to `VALID_SOURCES`
5. **`frontend/src/app/page.tsx`** — Add the source to the `ALL_SOURCES` array
6. **`frontend/src/components/ProductCard.tsx`** — Add the label to `SOURCE_LABEL`

---

## 14. Troubleshooting

### "Cannot connect to backend" or blank product list

- Make sure the backend terminal is running and shows no errors
- Check that you see `Uvicorn running on http://0.0.0.0:8000`
- Visit http://localhost:8000/health in your browser — you should see `{"status":"ok"}`

### "ImportError" when starting the backend

- Make sure you activated the virtual environment — you should see `(venv)` at the start of your terminal prompt
- Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac) from inside the `backend/` folder

### "Playwright browser not found" error

Run this from the backend folder (with venv active):

```bash
playwright install chromium
```

### "Authentication failed" (MongoDB)

- Double-check the username and password in your `MONGODB_URI` in `backend/.env`
- Make sure your IP is whitelisted in MongoDB Atlas → Network Access
- Try adding `0.0.0.0/0` (allow all IPs) under Network Access for testing

### "Invalid API key" (Anthropic)

- Check that `ANTHROPIC_API_KEY` in `backend/.env` starts with `sk-ant-api03-`
- Make sure there are no extra spaces or quotes around the key
- Verify the key is active at https://console.anthropic.com/

### Crawl jobs stay "pending" or "running" forever

- Check the backend terminal for error messages
- Amazon and Flipkart sometimes block scrapers with CAPTCHAs — try crawling brand websites directly by pasting a URL instead
- Brand website crawls are more reliable than marketplace crawls

### Frontend shows "module not found" errors

Run `npm install` again from the `frontend/` folder.

---

## 15. Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Your Claude AI API key from console.anthropic.com |
| `MONGODB_URI` | Yes | — | MongoDB Atlas connection string |
| `MONGODB_DB` | No | `food_profiler` | Name of the database inside MongoDB |
| `CRAWL_INTERVAL_HOURS` | No | `24` | Reserved for future scheduled crawls |
| `MAX_CONCURRENT_CRAWLS` | No | `5` | Maximum simultaneous crawl jobs |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, or `ERROR` |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | URL of the backend. Change this if you deploy the backend to a cloud server |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│            Your Browser (localhost:3000)          │
│                                                   │
│  [Search Bar]  [URL Input]  [Chat Assistant]      │
│  [Product Cards with Quality Scores]              │
│  [Price History Charts]                           │
└───────────────────┬─────────────────────────────-┘
                    │ HTTP requests
                    ▼
┌─────────────────────────────────────────────────┐
│           Backend API (localhost:8000)            │
│                                                   │
│  /products  →  list, detail, compare              │
│  /crawl     →  search, URL crawl, job status      │
│  /chat      →  AI Q&A over product database       │
└──────┬───────────────────┬───────────────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐   ┌────────────────────────────────┐
│  MongoDB    │   │    Invisible Chrome Browser     │
│  Atlas      │   │    (Playwright)                 │
│             │   │                                 │
│  products   │   │  amazon.in    flipkart.com      │
│  crawl_jobs │   │  anveshan.farm                 │
│             │   │  rosierfoods.com               │
└─────────────┘   │  twobrothersindiashop.com      │
       ▲          │  batiora.com                   │
       │          └───────────────┬────────────────┘
       │                          │ raw product data
       │                          ▼
       │          ┌────────────────────────────────┐
       └──────────│        Claude AI (Anthropic)    │
    scores saved  │                                │
                  │  Haiku  → parse HTML to JSON   │
                  │  Sonnet → quality score 0-100  │
                  │  Haiku  → chat assistant Q&A   │
                  └────────────────────────────────┘
```

---
### High Level Architecture Diagram

```mermaid
flowchart TD

    User["👤 User"]

    subgraph Frontend["Frontend — Next.js"]
        UI["Search UI"]
        ProductPage["Product Results Page"]
        Charts["Price History Charts"]
    end

    subgraph Backend["Backend — FastAPI"]
        API["API Endpoints"]
        CrawlService["Crawl Service"]
        Analyzer["Quality Analyzer"]
    end

    subgraph Crawlers["Web Crawlers"]
        Amazon["Amazon Crawler"]
        Flipkart["Flipkart Crawler"]
        Brand["Brand Website Crawler"]
    end

    subgraph AI["AI Models"]
        Extract["Claude Haiku — Data Extraction"]
        Score["Claude Sonnet — Quality Scoring"]
    end

    subgraph DB["Database — MongoDB"]
        Products["Products Collection"]
        Prices["Price History"]
    end

    User --> UI
    UI --> API

    API --> CrawlService
    CrawlService --> Amazon
    CrawlService --> Flipkart
    CrawlService --> Brand

    Amazon --> Extract
    Flipkart --> Extract
    Brand --> Extract

    Extract --> Score

    Score --> Products
    Amazon --> Prices
    Flipkart --> Prices
    Brand --> Prices

    Products --> API
    Prices --> API

    API --> ProductPage
    ProductPage --> Charts
```

---

*Built to cut through the noise in the Indian organic food market and find products that are genuinely pure — not just marketed as pure.*
