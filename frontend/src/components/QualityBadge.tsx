import clsx from "clsx";

interface Props {
  score: number | null;
  size?: "sm" | "md" | "lg";
}

export function QualityBadge({ score, size = "md" }: Props) {
  if (score === null) return <span className="text-gray-400 text-sm">Unscored</span>;

  const color =
    score >= 75 ? "bg-green-100 text-green-800 border-green-200" :
    score >= 50 ? "bg-yellow-100 text-yellow-800 border-yellow-200" :
    "bg-red-100 text-red-800 border-red-200";

  const label =
    score >= 75 ? "Good" :
    score >= 50 ? "Average" :
    "Poor";

  const sizeClass = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
    lg: "text-base px-4 py-1.5",
  }[size];

  return (
    <span className={clsx("inline-flex items-center gap-1.5 rounded-full border font-semibold", color, sizeClass)}>
      <span className="font-bold">{Math.round(score)}</span>
      <span className="opacity-70">{label}</span>
    </span>
  );
}
