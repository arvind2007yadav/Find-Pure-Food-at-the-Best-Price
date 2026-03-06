import type { QualityScore } from "@/lib/types";

function Bar({ label, score }: { label: string; score: number | null }) {
  if (score === null) return null;
  const color =
    score >= 75 ? "bg-green-500" :
    score >= 50 ? "bg-yellow-500" :
    "bg-red-500";

  return (
    <div className="flex items-center gap-3">
      <span className="w-28 shrink-0 text-sm text-gray-600">{label}</span>
      <div className="flex-1 rounded-full bg-gray-100 h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
      </div>
      <span className="w-8 text-right text-sm font-medium">{Math.round(score)}</span>
    </div>
  );
}

export function QualityScoreCard({ score }: { score: QualityScore }) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">Quality Analysis</h2>
        <span className="text-2xl font-bold text-[#d2b777]">{Math.round(score.overall_score)}/100</span>
      </div>

      {score.summary && (
        <p className="mb-4 text-sm text-gray-600 leading-relaxed">{score.summary}</p>
      )}

      <div className="space-y-2 mb-4">
        <Bar label="Ingredients" score={score.ingredient_score} />
        <Bar label="Reviews" score={score.review_score} />
        <Bar label="Certifications" score={score.certification_score} />
        <Bar label="Social" score={score.social_score} />
      </div>

      {score.red_flags && score.red_flags.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-red-600 mb-1">Concerns</p>
          <ul className="space-y-0.5">
            {score.red_flags.map((f, i) => (
              <li key={i} className="text-sm text-red-700 flex gap-1.5">
                <span>⚠</span> {f}
              </li>
            ))}
          </ul>
        </div>
      )}

      {score.green_flags && score.green_flags.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-green-600 mb-1">Positives</p>
          <ul className="space-y-0.5">
            {score.green_flags.map((f, i) => (
              <li key={i} className="text-sm text-green-700 flex gap-1.5">
                <span>✓</span> {f}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
