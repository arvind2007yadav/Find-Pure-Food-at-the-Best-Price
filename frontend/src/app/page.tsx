"use client";

import { useEffect, useState } from "react";
import { getProducts, triggerSearch, triggerUrlCrawl, getJob } from "@/lib/api";
import type { Product } from "@/lib/types";
import { ProductCard } from "@/components/ProductCard";

const ALL_SOURCES = [
  { key: "batiora",  label: "Batiora Farm Fresh" },
  { key: "amazon",   label: "Amazon" },
  { key: "flipkart", label: "Flipkart" },
  { key: "anveshan", label: "Anveshan" },
  { key: "rosier",   label: "Rosier Foods" },
  { key: "twobros",  label: "Two Brothers Organic" },
  
];

const ALLOWED_URL_HINT =
  "amazon.in · flipkart.com · anveshan.farm · rosierfoods.com · twobrothersindiashop.com · batiora.com";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [sources, setSources] = useState<string[]>(ALL_SOURCES.map((s) => s.key));
  const [products, setProducts] = useState<Product[]>([]);
  const [searched, setSearched] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch(() => {/* backend may not be running yet */})
      .finally(() => setInitialLoading(false));
  }, []);

  const toggleSource = (key: string) =>
    setSources((prev) =>
      prev.includes(key) ? prev.filter((x) => x !== key) : [...prev, key]
    );

  const handleSearch = async () => {
    if (!query.trim()) return;
    if (sources.length === 0) {
      setError("Select at least one source.");
      return;
    }
    setLoading(true);
    setError(null);
    setSearched(false);
    try {
      const job = await triggerSearch(query, sources);
      setJobId(job.job_id);
      const completed = await pollJob(job.job_id);
      if (completed?.status === "failed") {
        setError("Crawl job failed. Check the Jobs page for details.");
        return;
      }
      const results = await getProducts({ search: query });
      setProducts(results);
      setSearched(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleUrlCrawl = async () => {
    const url = urlInput.trim();
    if (!url) return;
    setLoading(true);
    setError(null);
    setSearched(false);
    try {
      const job = await triggerUrlCrawl(url);
      setJobId(job.job_id);
      const completed = await pollJob(job.job_id);
      if (completed?.status === "failed") {
        setError("Crawl job failed. Check the Jobs page for details.");
        return;
      }
      const results = await getProducts({});
      setProducts(results);
      setSearched(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Crawl failed");
    } finally {
      setLoading(false);
    }
  };

  const pollJob = async (id: string) => {
    for (let i = 0; i < 60; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      const job = await getJob(id);
      if (job.status === "done" || job.status === "failed") return job;
    }
    return null;
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-[#282828]">Find Pure Food at the Best Price</h1>
        <p className="text-[#5b5b5b]">
          Searches Batiora Farm Fresh, Anveshan, Rosier Foods & Two Brothers across Amazon, Flipkart and their own websites.
        </p>
      </div>

      {/* Search panel */}
      <div className="rounded-2xl border border-[#e7e7e7] bg-white p-6 shadow-sm space-y-5">

        {/* Keyword search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search by product name
          </label>
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-lg border px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#d2b777]"
              placeholder="e.g. ghee, cold pressed oil, honey"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="rounded-full bg-[#282828] px-5 py-2.5 text-sm font-semibold text-white hover:bg-black disabled:opacity-60 transition-colors"
            >
              {loading ? "Searching…" : "Search"}
            </button>
          </div>

          {/* Source checkboxes */}
          <div className="mt-3">
            <p className="text-xs text-gray-400 mb-1.5">Search in:</p>
            <div className="flex flex-wrap gap-x-4 gap-y-1.5">
              {ALL_SOURCES.map((s) => (
                <label
                  key={s.key}
                  className="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={sources.includes(s.key)}
                    onChange={() => toggleSource(s.key)}
                    className="accent-[#d2b777]"
                  />
                  {s.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t" />

        {/* URL crawl */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Or paste a product URL
          </label>
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-lg border px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#d2b777]"
              placeholder="https://www.anveshan.farm/products/..."
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
            />
            <button
              onClick={handleUrlCrawl}
              disabled={loading}
              className="rounded-full border border-[#282828] px-5 py-2.5 text-sm font-semibold text-[#282828] hover:bg-[#f6edd9] disabled:opacity-60 transition-colors"
            >
              {loading ? "Crawling…" : "Crawl URL"}
            </button>
          </div>
          <p className="mt-1 text-xs text-gray-400">Allowed: {ALLOWED_URL_HINT}</p>
        </div>
      </div>

      {/* Status */}
      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#d2b777] border-t-transparent" />
          Crawling selected sources and analyzing quality — this may take 30–90 seconds…
          {jobId && <span className="text-gray-400">(Job {jobId.slice(-6)})</span>}
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {/* Results */}
      {initialLoading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#d2b777] border-t-transparent" />
          Loading stored products…
        </div>
      )}
      {!initialLoading && products.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            {searched
              ? `${products.length} results for "${query}"`
              : `${products.length} products in database`}
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </div>
      )}
      {searched && products.length === 0 && !loading && !error && (
        <p className="text-sm text-gray-500">
          No products found. Only <strong>Anveshan</strong>, <strong>Rosier Foods</strong>,{" "}
          <strong>Two Brothers Organic</strong>, and <strong>Batiora Farm Fresh</strong> products
          are tracked — check that this product is sold by one of these brands.
        </p>
      )}
    </div>
  );
}
