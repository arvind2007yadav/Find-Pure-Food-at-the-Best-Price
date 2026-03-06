export interface PricePoint {
  price: number;
  currency: string;
  unit: string | null;
  in_stock: boolean | null;
  recorded_at: string;
}

export interface QualityScore {
  overall_score: number;
  ingredient_score: number | null;
  review_score: number | null;
  certification_score: number | null;
  social_score: number | null;
  red_flags: string[];
  green_flags: string[];
  summary: string | null;
  scored_at: string;
}

export interface Product {
  id: string;            // MongoDB ObjectId string
  name: string;
  brand: string | null;
  source: string;
  source_url: string;
  image_url: string | null;
  ingredients: string | null;
  certifications: string[];
  description: string | null;
  rating: number | null;
  review_count: number | null;
  latest_price: number | null;
  latest_quality_score: number | null;
  created_at: string;
}

export interface ProductDetail extends Product {
  price_history: PricePoint[];
  quality_scores: QualityScore[];
}

export interface CrawlJob {
  id: string;            // MongoDB ObjectId string
  url: string | null;
  source: string;
  query: string | null;
  status: "pending" | "running" | "done" | "failed";
  products_found: number;
  error: string | null;
  created_at: string;
  completed_at: string | null;
}
