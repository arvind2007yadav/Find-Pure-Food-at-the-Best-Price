"use client";

import { useEffect, useState } from "react";
import { listJobs } from "@/lib/api";
import type { CrawlJob } from "@/lib/types";
import clsx from "clsx";

const STATUS_COLOR: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600",
  running: "bg-blue-100 text-blue-700",
  done: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<CrawlJob[]>([]);

  useEffect(() => {
    listJobs().then(setJobs).catch(() => {});
    const t = setInterval(() => listJobs().then(setJobs).catch(() => {}), 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Crawl Jobs</h1>
      <p className="text-sm text-gray-500">Auto-refreshes every 5 seconds.</p>

      {jobs.length === 0 && <p className="text-gray-400">No jobs yet. Start a search from the home page.</p>}

      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className="rounded-xl border bg-white p-4 shadow-sm flex items-start justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono text-gray-400">#{job.id}</span>
                <span className={clsx("rounded-full px-2.5 py-0.5 text-xs font-semibold", STATUS_COLOR[job.status])}>
                  {job.status}
                </span>
              </div>
              {job.query && <p className="text-sm font-medium">Query: <span className="text-[#978c3e]">{job.query}</span></p>}
              {job.url && job.url !== "search" && (
                <p className="text-xs text-gray-500 truncate max-w-md">{job.url}</p>
              )}
              <p className="text-xs text-gray-400">Sources: {job.source}</p>
              {job.error && <p className="text-xs text-red-600">{job.error}</p>}
            </div>
            <div className="text-right text-xs text-gray-400 shrink-0">
              <p>{job.products_found} products</p>
              <p>{new Date(job.created_at).toLocaleString("en-IN")}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
