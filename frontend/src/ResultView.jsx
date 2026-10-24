/**
 * ResultView.jsx – Step C: the final screen.
 *
 * Shows ONLY:
 *  1. The confidence score (ScoreBadge) + optional cap line.
 *  2. The complete 16-row checks table with columns:
 *     check name | tier | source | status | points (earned / max)
 *     Check 16 (verify links) shows links inside its detail cell.
 *
 * Nothing else: no summary card, no red-flag blocks, no next-steps,
 * no transcription, no verdict word, no evidence-coverage indicator.
 *
 * "Check another" resets everything back to Step A.
 */

import ScoreBadge from "./ScoreBadge.jsx";
import CheckRow from "./CheckRow.jsx";

export default function ResultView({ checks, rowResults, score, verdict, capReason, onReset }) {
  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <span className="font-black text-primary-container text-lg tracking-tight">SahiCheck</span>
        <button
          onClick={onReset}
          className="px-4 py-2 rounded-xl border border-slate-300 text-sm font-semibold text-slate-700 hover:border-primary-container hover:text-primary-container transition-all"
        >
          Check another
        </button>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-12">
        {/* 1. Score badge */}
        <div className="flex justify-center mb-12">
          <ScoreBadge score={score} verdict={verdict} capReason={capReason} />
        </div>

        {/* 2. Full checks table */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-100 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <th className="py-2.5 px-3">Check</th>
                <th className="py-2.5 px-3">Tier</th>
                <th className="py-2.5 px-3">Source</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Points</th>
                <th className="py-2.5 px-3">Detail</th>
              </tr>
            </thead>
            <tbody>
              {checks.map((meta, i) => (
                <CheckRow
                  key={meta.id}
                  meta={meta}
                  rowState="done"
                  result={rowResults[i]}
                  isResult={true}
                />
              ))}
            </tbody>
          </table>
        </div>

        {/* Check another button (bottom) */}
        <div className="flex justify-center mt-10">
          <button
            onClick={onReset}
            className="px-8 py-3 bg-primary-container hover:bg-primary-hover text-white font-bold rounded-2xl shadow-card transition-all"
          >
            Check another offer
          </button>
        </div>
      </main>
    </div>
  );
}
