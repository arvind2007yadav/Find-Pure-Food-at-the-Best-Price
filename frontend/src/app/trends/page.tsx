"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getProductsWithHistory } from "@/lib/api";
import type { ProductDetail } from "@/lib/types";
import { QualityBadge } from "@/components/QualityBadge";

const SOURCE_LABEL: Record<string, string> = {
  amazon: "Amazon",
  flipkart: "Flipkart",
  anveshan: "Anveshan",
  rosier: "Rosier Foods",
  twobros: "Two Brothers",
  batiora: "Batiora",
};

function MiniPriceChart({ history }: { history: ProductDetail["price_history"] }) {
  if (history.length < 2) {
    return (
      <p className="text-xs text-gray-400 text-center py-4">
        {history.length === 1 ? `₹${history[0].price.toLocaleString("en-IN")} — only 1 data point` : "No price data"}
      </p>
    );
  }
  const data = history.map((p) => ({
    date: new Date(p.recorded_at).toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
    price: p.price,
  }));
  return (
    <ResponsiveContainer width="100%" height={90}>
      <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} />
        <YAxis tick={{ fontSize: 9 }} tickFormatter={(v) => `₹${v}`} width={46} />
        <Tooltip formatter={(v: number) => [`₹${v.toLocaleString("en-IN")}`, "Price"]} />
        <Area type="monotone" dataKey="price" stroke="#22c55e" strokeWidth={1.5} fill="url(#pg)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function MiniQualityChart({ scores }: { scores: ProductDetail["quality_scores"] }) {
  if (scores.length < 2) {
    return (
      <p className="text-xs text-gray-400 text-center py-4">
        {scores.length === 1 ? `Score: ${Math.round(scores[0].overall_score)} — only 1 data point` : "No score data"}
      </p>
    );
  }
  // Scores are stored newest-first; reverse for chronological display
  const data = [...scores].reverse().map((s) => ({
    date: new Date(s.scored_at).toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
    score: Math.round(s.overall_score),
  }));
  return (
    <ResponsiveContainer width="100%" height={90}>
      <LineChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 9 }} width={28} />
        <Tooltip formatter={(v: number) => [v, "Quality"]} />
        <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={1.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function ProductTrendCard({ product }: { product: ProductDetail }) {
  const latestScore = product.quality_scores[0] ?? null;
  return (
    <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <Link
              href={`/products/${product.id}`}
              className="text-sm font-semibold text-[#282828] hover:text-[#d2b777] leading-snug line-clamp-2"
            >
              {product.name}
            </Link>
            <div className="mt-1 flex items-center gap-2 flex-wrap">
              {product.brand && (
                <span className="text-xs text-gray-400">{product.brand}</span>
              )}
              <span className="text-xs rounded-full bg-gray-100 px-2 py-0.5 text-gray-500">
                {SOURCE_LABEL[product.source] ?? product.source}
              </span>
            </div>
          </div>
          <QualityBadge score={latestScore?.overall_score ?? null} size="sm" />
        </div>
        <div className="mt-2 flex gap-4 text-xs text-gray-500">
          {product.latest_price !== null && (
            <span>₹{product.latest_price.toLocaleString("en-IN")}</span>
          )}
          <span>{product.price_history.length} price points</span>
          <span>{product.quality_scores.length} score snapshots</span>
        </div>
      </div>

      {/* Price trend */}
      <div className="px-4 pt-3 pb-1">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Price trend</p>
        <MiniPriceChart history={product.price_history} />
      </div>

      {/* Quality trend */}
      <div className="px-4 pt-2 pb-4">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Quality score trend</p>
        <MiniQualityChart scores={product.quality_scores} />
      </div>
    </div>
  );
}

export default function TrendsPage() {
  const [products, setProducts] = useState<ProductDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    getProductsWithHistory()
      .then(setProducts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = search.trim()
    ? products.filter((p) => p.name.toLowerCase().includes(search.toLowerCase()))
    : products;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Price &amp; Quality Trends</h1>
          <p className="text-sm text-gray-500 mt-0.5">All {products.length} stored products — historical price and quality score over time</p>
        </div>
        <input
          className="rounded-lg border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#d2b777] w-60"
          placeholder="Filter by name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#d2b777] border-t-transparent" />
          Loading stored products…
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && filtered.length === 0 && (
        <p className="text-sm text-gray-500">
          No products stored yet. Use the{" "}
          <Link href="/" className="text-[#d2b777] hover:underline">Search page</Link> to crawl products first.
        </p>
      )}

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((p) => (
          <ProductTrendCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
