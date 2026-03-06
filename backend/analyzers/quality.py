"""
Quality analyzer: uses Claude to evaluate food product quality from all available signals.

Scoring breakdown (out of 100):
  - ingredient_score  (35 pts): ingredient list analysis — additives, preservatives, harmful chemicals
  - review_score      (25 pts): rating + review count as proxy for consumer satisfaction
  - certification_score (20 pts): FSSAI, organic, ISO etc.
  - social_score      (20 pts): placeholder — future social media sentiment integration
"""
import json

import anthropic

from config import settings
from crawlers.base import ScrapedProduct

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

QUALITY_PROMPT = """\
You are a food quality analyst. Analyze the following food product data and return a detailed quality assessment.

Product data:
{product_json}

Evaluate the product on these dimensions and return a JSON object with EXACTLY these keys:
{{
  "overall_score": <float 0-100>,
  "ingredient_score": <float 0-100, null if no ingredients available>,
  "review_score": <float 0-100, null if no rating data>,
  "certification_score": <float 0-100>,
  "social_score": null,
  "red_flags": [<list of specific concerns as strings>],
  "green_flags": [<list of positive quality signals as strings>],
  "summary": "<2-3 sentence plain-English quality summary for a consumer>"
}}

Scoring guidance:
- ingredient_score: penalize artificial preservatives (E-numbers), synthetic colors, trans fats, high sugar/sodium. Reward whole ingredients, no additives.
- review_score: 4.5+ = 90-100, 4.0-4.4 = 70-89, 3.5-3.9 = 50-69, below 3.5 = 0-49. Adjust down for low review counts (<50 reviews).
- certification_score: FSSAI license = baseline 50, add 15 for Organic cert, 10 for ISO, 10 for Halal/Kosher, 15 for multiple certs.
- overall_score: weighted average (ingredient 35%, review 25%, certification 20%, social 20% — use 0 if social null).

Return ONLY valid JSON. No markdown, no explanation.
"""


async def analyze_product(product: ScrapedProduct) -> dict:
    """Run Claude quality analysis on a scraped product. Returns score dict."""
    product_data = {
        "name": product.name,
        "brand": product.brand,
        "ingredients": product.ingredients,
        "certifications": product.certifications,
        "description": product.description,
        "rating": product.rating,
        "review_count": product.review_count,
        "raw_data": product.raw_data,
    }

    try:
        response = await _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": QUALITY_PROMPT.format(product_json=json.dumps(product_data, indent=2))
            }],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        # Fallback: compute simple rule-based score
        return _fallback_score(product, str(e))


def _fallback_score(product: ScrapedProduct, error: str) -> dict:
    """Simple rule-based fallback if Claude call fails."""
    cert_score = 0.0
    for c in (product.certifications or []):
        if "FSSAI" in c:
            cert_score += 50
        elif "Organic" in c:
            cert_score += 15
        elif "ISO" in c:
            cert_score += 10
    cert_score = min(cert_score, 100)

    review_score = None
    if product.rating is not None:
        review_score = max(0, min(100, (product.rating / 5) * 100))
        if product.review_count and product.review_count < 50:
            review_score *= 0.8

    overall = cert_score * 0.2
    if review_score is not None:
        overall += review_score * 0.25
    overall = min(overall, 100)

    return {
        "overall_score": round(overall, 1),
        "ingredient_score": None,
        "review_score": round(review_score, 1) if review_score else None,
        "certification_score": round(cert_score, 1),
        "social_score": None,
        "red_flags": [f"AI analysis unavailable: {error}"],
        "green_flags": list(product.certifications or []),
        "summary": "Automated analysis unavailable. Score based on certifications and ratings only.",
    }
