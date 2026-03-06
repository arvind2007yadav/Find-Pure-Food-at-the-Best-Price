"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PricePoint } from "@/lib/types";

export function PriceHistory({ history }: { history: PricePoint[] }) {
  if (!history.length) {
    return <p className="text-sm text-gray-400">No price history yet.</p>;
  }

  const data = history.map((p) => ({
    date: new Date(p.recorded_at).toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
    price: p.price,
  }));

  const min = Math.min(...data.map((d) => d.price));
  const max = Math.max(...data.map((d) => d.price));

  return (
    <div>
      <div className="mb-2 flex gap-4 text-sm">
        <span className="text-gray-500">
          Low: <span className="font-semibold text-green-600">₹{min.toLocaleString("en-IN")}</span>
        </span>
        <span className="text-gray-500">
          High: <span className="font-semibold text-red-500">₹{max.toLocaleString("en-IN")}</span>
        </span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${v}`} width={60} />
          <Tooltip formatter={(v: number) => [`₹${v.toLocaleString("en-IN")}`, "Price"]} />
          <Area
            type="monotone"
            dataKey="price"
            stroke="#22c55e"
            strokeWidth={2}
            fill="url(#priceGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
