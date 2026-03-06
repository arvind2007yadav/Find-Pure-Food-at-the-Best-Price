import type { CrawlJob, Product, ProductDetail } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json() as Promise<T>;
}

// Products
export const getProducts = (params: Record<string, string> = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request<Product[]>(`/products/${qs ? `?${qs}` : ""}`);
};

export const getProductsWithHistory = (params: Record<string, string> = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request<ProductDetail[]>(`/products/with-history/${qs ? `?${qs}` : ""}`);
};

export const getProduct = (id: string) =>
  request<ProductDetail>(`/products/${id}`);

export const compareProducts = (ids: string[]) =>
  request<ProductDetail[]>(`/products/compare/?ids=${ids.join(",")}`);

// Crawl
export const triggerSearch = (query: string, sources: string[], maxResults = 20) =>
  request<{ job_id: string; status: string }>("/crawl/search", {
    method: "POST",
    body: JSON.stringify({ query, sources, max_results: maxResults }),
  });

export const triggerUrlCrawl = (url: string) =>
  request<{ job_id: string; status: string }>("/crawl/url", {
    method: "POST",
    body: JSON.stringify({ url }),
  });

// Crawl all products from a specific brand site (anveshan | rosier | twobros)
export const triggerBrandCrawl = (brand: string, maxResults = 50) =>
  request<{ job_id: string; status: string }>("/crawl/brand", {
    method: "POST",
    body: JSON.stringify({ brand, max_results: maxResults }),
  });

export const getJob = (id: string) => request<CrawlJob>(`/crawl/jobs/${id}`);

export const listJobs = (limit = 20) =>
  request<CrawlJob[]>(`/crawl/jobs?limit=${limit}`);

// Chat
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export const sendChatMessage = (message: string, history: ChatMessage[]) =>
  request<{ reply: string }>("/chat/", {
    method: "POST",
    body: JSON.stringify({ message, history }),
  });
