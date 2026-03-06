# 🥗 Find Pure Food at the Best Price

An AI-powered system that analyzes food products across e-commerce platforms and brand websites to identify **the purest product at the lowest price**.

This project crawls product pages, extracts ingredient and certification data, evaluates product quality using AI, and tracks price trends over time.

---

# 🚀 Project Goal

Consumers often struggle to answer two important questions:

1. **Which product is the purest / healthiest?**
2. **Where can I buy it at the lowest price?**

This project aims to solve both using **AI + web crawling + price tracking**.

---

# 🧠 How It Works

The system follows a multi-stage pipeline.

```
User Search / Product URL
        ↓
Crawler collects product data
        ↓
HTML parsing + structured extraction
        ↓
AI quality analysis
        ↓
Database stores product + price history
        ↓
Frontend shows ranked results
```

---

# 🔎 Key Features

| Feature                | Description                                                     |
| ---------------------- | --------------------------------------------------------------- |
| 🕸 Web Crawling        | Scrapes product pages from Amazon, Flipkart, and brand websites |
| 🧾 Ingredient Analysis | Extracts ingredients and certifications                         |
| 🤖 AI Quality Scoring  | AI evaluates product purity and assigns a score                 |
| 💰 Price Tracking      | Stores price snapshots over time                                |
| 📊 Product Ranking     | Displays best quality products at lowest price                  |
| 📉 Price History       | Shows how product prices change                                 |

---

# 🏗 System Architecture

### Frontend

* Next.js 14
* Tailwind CSS
* Recharts (price charts)

### Backend

* FastAPI
* Python
* Playwright (web scraping)
* BeautifulSoup

### AI Models

* Claude Haiku → Structured data extraction
* Claude Sonnet → Quality scoring

### Database

* MongoDB

---

# 📂 Repository Structure

```
Find-Pure-Food-at-the-Best-Price
│
├── backend
│   ├── api
│   ├── crawlers
│   ├── analyzers
│   ├── services
│   └── db
│
├── frontend
│   ├── components
│   ├── pages
│   └── lib
│
├── README.md
└── docs
```

---

# 🧪 Example Workflow

Example search:

```
Raw Honey
```

System will:

1. Crawl multiple product sources
2. Extract:

   * Ingredients
   * Certifications
   * Ratings
3. Run AI quality scoring
4. Track product prices
5. Rank results

Example output:

| Product           | Quality Score | Price |
| ----------------- | ------------- | ----- |
| Brand A Raw Honey | 92            | ₹420  |
| Brand B Raw Honey | 85            | ₹380  |
| Brand C Raw Honey | 74            | ₹350  |

Users can choose **best purity vs best price**.

---

# 🛠 Tech Stack

| Layer        | Technology    |
| ------------ | ------------- |
| Frontend     | Next.js       |
| Backend      | FastAPI       |
| Crawler      | Playwright    |
| HTML Parsing | BeautifulSoup |
| AI           | Claude        |
| Database     | MongoDB       |
| Charts       | Recharts      |

---

# ⚙️ Local Setup

### Clone Repository

```
git clone https://github.com/arvind2007yadav/Find-Pure-Food-at-the-Best-Price.git
```

---

### Backend Setup

```
cd backend

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

playwright install chromium
uvicorn main:app --reload
```

---

### Frontend Setup

```
cd frontend

npm install
npm run dev
```

Open:

```
http://localhost:3000
```

---

# 💡 Future Improvements

* Product authenticity detection
* Fake review detection
* Nutritional scoring
* Grocery comparison engine
* AI recommendation engine
* Mobile app

---

# 👤 Author

**Arvind Yadav**

AI Product Builder

Interested in:

* AI systems
* Agent orchestration
* Product analytics
* AI-powered marketplaces

GitHub:

https://github.com/arvind2007yadav

---

# ⭐ Support

If you find this project interesting:

* ⭐ Star the repository
* 🍴 Fork it
* 🤝 Contribute

---
