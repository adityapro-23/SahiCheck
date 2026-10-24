/**
 * ScoreBadge.jsx – Shows the confidence score, colored by band.
 *
 * Verdict bands use the same thresholds as the backend.
 */

export default function ScoreBadge({ score, verdict, capReason }) {
  const band =
    verdict === "SAFE" ? "green"
    : verdict === "SUSPICIOUS" ? "amber"
    : "red";

  const colourMap = {
    green: { ring: "ring-green-500", num: "text-green-700", bg: "bg-green-50" },
    amber: { ring: "ring-amber-500", num: "text-amber-700", bg: "bg-amber-50" },
    red:   { ring: "ring-red-500",   num: "text-red-700",   bg: "bg-red-50"   },
  };
  const c = colourMap[band];

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Big score circle */}
      <div className={`ring-4 ${c.ring} ${c.bg} rounded-full w-40 h-40 flex flex-col items-center justify-center shadow-card`}>
        <span className={`text-5xl font-black ${c.num}`}>{score}</span>
        <span className="text-sm font-semibold text-on-surface/60 mt-0.5">/ 100</span>
      </div>

      <p className="text-xs font-bold uppercase tracking-widest text-on-surface/50">
        Confidence score
      </p>
      <p className={`text-lg font-extrabold ${
        band === "green" ? "text-green-700"
        : band === "amber" ? "text-amber-700"
        : "text-red-700"
      }`}>
        {verdict === "SAFE" ? "Likely genuine"
          : verdict === "SUSPICIOUS" ? "Needs caution"
          : "Likely scam"}
      </p>
      <p className="text-xs text-on-surface/60">Higher means more likely genuine</p>

      {/* Cap notice – only shown when a hard cap was applied */}
      {capReason && (
        <p className="text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-center max-w-xs">
          {capReason}
        </p>
      )}
    </div>
  );
}
