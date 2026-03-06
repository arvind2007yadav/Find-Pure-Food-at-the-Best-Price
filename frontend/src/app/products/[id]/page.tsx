import Image from "next/image";
import Link from "next/link";
import { getProduct } from "@/lib/api";
import { QualityBadge } from "@/components/QualityBadge";
import { QualityScoreCard } from "@/components/QualityScoreCard";
import { PriceHistory } from "@/components/PriceHistory";

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);
  const latestScore = product.quality_scores[0] ?? null;

  return (
    <div className="space-y-6">
      <Link href="/" className="text-sm text-[#d2b777] hover:underline">← Back to search</Link>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left: image + basic info */}
        <div className="rounded-xl border border-[#e7e7e7] bg-white p-5 shadow-sm space-y-4">
          {product.image_url ? (
            <div className="relative h-56 w-full rounded-lg overflow-hidden bg-gray-100">
              <Image src={product.image_url} alt={product.name} fill className="object-contain p-4" unoptimized />
            </div>
          ) : (
            <div className="flex h-56 items-center justify-center rounded-lg bg-gray-100 text-6xl">🛒</div>
          )}

          <div>
            {product.brand && <p className="text-xs text-gray-400 font-medium uppercase">{product.brand}</p>}
            <h1 className="text-xl font-bold text-gray-900 leading-snug">{product.name}</h1>
          </div>

          <div className="flex items-center justify-between">
            {product.latest_price !== null ? (
              <p className="text-2xl font-bold">₹{product.latest_price.toLocaleString("en-IN")}</p>
            ) : (
              <p className="text-gray-400">Price unavailable</p>
            )}
            <QualityBadge score={product.latest_quality_score} size="lg" />
          </div>

          {product.rating !== null && (
            <p className="text-sm text-gray-500">
              ★ {product.rating.toFixed(1)} · {product.review_count?.toLocaleString()} reviews
            </p>
          )}

          {product.certifications && product.certifications.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {product.certifications.map((c) => (
                <span key={c} className="rounded-full bg-blue-50 border border-blue-200 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                  {c}
                </span>
              ))}
            </div>
          )}

          <a
            href={product.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block rounded-full bg-[#282828] py-2.5 text-center text-sm font-semibold text-white hover:bg-black transition-colors"
          >
            View on {product.source === "amazon" ? "Amazon" : product.source === "flipkart" ? "Flipkart" : "Site"} →
          </a>
        </div>

        {/* Middle + Right */}
        <div className="lg:col-span-2 space-y-6">
          {latestScore && <QualityScoreCard score={latestScore} />}

          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <h2 className="font-semibold text-gray-800 mb-4">Price History</h2>
            <PriceHistory history={product.price_history} />
          </div>

          {product.ingredients && (
            <div className="rounded-xl border bg-white p-5 shadow-sm">
              <h2 className="font-semibold text-gray-800 mb-2">Ingredients</h2>
              <p className="text-sm text-gray-600 leading-relaxed">{product.ingredients}</p>
            </div>
          )}

          {product.description && (
            <div className="rounded-xl border bg-white p-5 shadow-sm">
              <h2 className="font-semibold text-gray-800 mb-2">Description</h2>
              <p className="text-sm text-gray-600 leading-relaxed">{product.description}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
