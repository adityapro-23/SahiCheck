/**
 * CheckRow.jsx – One row in the checks table (used in both ProgressView and ResultView).
 *
 * Props:
 *   meta      – {id, name, tier, source, max_points} from /api/checks
 *   rowState  – "pending" | "running" | "done"
 *   result    – when done: {status, points, max_points, detail}  (may be null while pending/running)
 *   isResult  – true when rendered in the final result table (shows detail column)
 */

import { Loader2, Check, X, Minus, Info } from "lucide-react";

// Status → icon + colour
const STATUS_MAP = {
  passed:    { icon: Check,  cls: "text-passed-DEFAULT bg-passed-bg"   },
  failed:    { icon: X,      cls: "text-failed-DEFAULT bg-failed-bg"   },
  unavailable:{ icon: Minus, cls: "text-neutral-DEFAULT bg-neutral-bg" },
  skipped:   { icon: Minus,  cls: "text-neutral-DEFAULT bg-neutral-bg" },
  info:      { icon: Info,   cls: "text-info-DEFAULT bg-info-bg"       },
};

// Tier badge colours
const TIER_CLS = {
  high:      "bg-red-100   text-red-700",
  medium:    "bg-amber-100 text-amber-700",
  low:       "bg-slate-100 text-slate-600",
  strong:    "bg-indigo-100 text-indigo-700",
  supporting:"bg-blue-100  text-blue-700",
  weak:      "bg-gray-100  text-gray-600",
  info:      "bg-sky-100   text-sky-700",
};

export default function CheckRow({ meta, rowState, result, isResult }) {
  const isInfo = meta.max_points === 0; // check 16
  const earned = result?.points ?? 0;

  // Points display: "8 / 8" or "-" for info
  const pointsDisplay = isInfo
    ? "—"
    : result
      ? `${earned} / ${meta.max_points}`
      : `— / ${meta.max_points}`;

  const pointsCls = !isInfo && result
    ? earned > 0 ? "text-green-700 font-bold" : "text-slate-400"
    : "text-slate-400";

  return (
    <tr className="border-b border-slate-100 last:border-0 hover:bg-slate-50/60 transition-colors">

      {/* Check name + spinner / status icon */}
      <td className="py-3 px-3 min-w-[200px]">
        <div className="flex items-center gap-2">
          {rowState === "running" && (
            <Loader2 className="w-4 h-4 text-primary-container animate-spin shrink-0" />
          )}
          {rowState === "done" && result && (() => {
            const s = STATUS_MAP[result.status] ?? STATUS_MAP.unavailable;
            const Icon = s.icon;
            return (
              <span className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${s.cls}`}>
                <Icon className="w-3 h-3" />
              </span>
            );
          })()}
          {rowState === "pending" && (
            <span className="w-4 h-4 rounded-full bg-slate-200 shrink-0" />
          )}
          <span className={`text-sm font-semibold ${rowState === "running" ? "text-primary-container" : "text-on-surface"}`}>
            {meta.name}
          </span>
        </div>
      </td>

      {/* Tier badge */}
      <td className="py-3 px-3 whitespace-nowrap">
        <span className={`text-[11px] font-bold uppercase px-2 py-0.5 rounded ${TIER_CLS[meta.tier] ?? "bg-slate-100 text-slate-500"}`}>
          {meta.tier}
        </span>
      </td>

      {/* Source */}
      <td className="py-3 px-3 text-xs text-slate-500 whitespace-nowrap">
        {meta.source}
      </td>

      {/* Status label */}
      <td className="py-3 px-3 whitespace-nowrap">
        {rowState === "done" && result ? (
          <span className={`text-xs font-bold capitalize ${
            result.status === "passed"    ? "text-green-700"
            : result.status === "failed"  ? "text-red-700"
            : result.status === "info"    ? "text-blue-700"
            : "text-slate-500"
          }`}>
            {result.status}
          </span>
        ) : rowState === "running" ? (
          <span className="text-xs text-slate-400 italic">checking…</span>
        ) : (
          <span className="text-xs text-slate-300">pending</span>
        )}
      </td>

      {/* Points */}
      <td className={`py-3 px-3 text-sm font-mono whitespace-nowrap ${pointsCls}`}>
        {pointsDisplay}
      </td>

      {/* Detail – only in result view; also show verify links for check 16 */}
      {isResult && (
        <td className="py-3 px-3 text-xs text-slate-600 max-w-xs">
        {result?.links?.length ? (
          <div className="flex flex-col gap-1">
            {result.links.map(link => (
              <a
                key={link.url}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-container underline underline-offset-2 hover:text-primary-hover"
              >
                {link.label}
              </a>
            ))}
          </div>
        ) : result?.detail || "—"}
      </td>
      )}
    </tr>
  );
}
