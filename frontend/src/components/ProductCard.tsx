import Image from "next/image";
import Link from "next/link";
import type { Product } from "@/lib/types";
import { QualityBadge } from "./QualityBadge";

const SOURCE_LABEL: Record<string, string> = {
  amazon: "Amazon",
  flipkart: "Flipkart",
  anveshan: "Anveshan",
  rosier: "Rosier Foods",
  twobros: "Two Brothers Organic",
  batiora: "Batiora Farm Fresh",
  brand_site: "Brand Site",
};

export function ProductCard({ product }: { product: Product }) {
  return (
    <Link href={`/products/${product.id}`}>
      <div className="flex flex-col gap-3 rounded-xl border border-[#e7e7e7] bg-white p-4 shadow-sm transition hover:shadow-md hover:border-[#d2b777]">
        {product.image_url ? (
          <div className="relative h-40 w-full overflow-hidden rounded-lg bg-gray-100">
            <Image
              src={product.image_url}
              alt={product.name}
              fill
              className="object-contain p-2"
              unoptimized
            />
          </div>
        ) : (
          <div className="flex h-40 items-center justify-center rounded-lg bg-gray-100 text-gray-400 text-4xl">
            🛒
          </div>
        )}

        <div className="flex flex-col gap-1">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
            {SOURCE_LABEL[product.source] ?? product.source}
            {product.brand && ` · ${product.brand}`}
          </p>
          <h3 className="line-clamp-2 font-semibold text-gray-900 leading-snug">
            {product.name}
          </h3>
        </div>

        <div className="mt-auto flex items-center justify-between">
          <div>
            {product.latest_price !== null ? (
              <p className="text-lg font-bold text-gray-900">
                ₹{product.latest_price.toLocaleString("en-IN")}
              </p>
            ) : (
              <p className="text-sm text-gray-400">Price unavailable</p>
            )}
            {product.rating !== null && (
              <p className="text-xs text-gray-500">
                ★ {product.rating.toFixed(1)}
                {product.review_count && ` (${product.review_count.toLocaleString()})`}
              </p>
            )}
          </div>
          <QualityBadge score={product.latest_quality_score} size="sm" />
        </div>
      </div>
    </Link>
  );
}
