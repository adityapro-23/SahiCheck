/**
 * ProgressView.jsx – Step B: live progress screen.
 *
 * Renders all 16 rows (from GET /api/checks) immediately, then updates each
 * row as NDJSON events arrive from the stream.
 *
 * State per row: "pending" | "running" | "done"
 * Only one row is "running" at any moment (enforced by the backend).
 *
 * On success the parent switches us to Step C (ResultView).
 * On error we show a friendly message + "Try again" button.
 */

import { useState, useEffect, useRef } from "react";
import { Loader2 } from "lucide-react";
import CheckRow from "./CheckRow.jsx";
import { streamCheck } from "./api.js";

// Stage label shown above the checklist during extraction
const STAGE_LABEL = {
  extract: "Reading your input…",
};

export default function ProgressView({ checks, formData, onDone, onError, onReset, savedInput }) {
  // rowStates: array of "pending" | "running" | "done" (one per check)
  const [rowStates, setRowStates] = useState(() => checks.map(() => "pending"));
  // rowResults: array of result objects (null until done)
  const [rowResults, setRowResults] = useState(() => checks.map(() => null));
  // stageLabel: text shown while extracting
  const [stageLabel, setStageLabel] = useState("Starting analysis…");
  const [errorMsg, setErrorMsg] = useState(null);

  // Use a ref for row state so the stream callback always sees current values
  const rowStatesRef = useRef(rowStates);
  rowStatesRef.current = rowStates;
  const rowResultsRef = useRef(rowResults);

  useEffect(() => {
    let cancelled = false;

    async function stream() {
      try {
        await streamCheck(formData, (event) => {
          if (cancelled) return;

          if (event.type === "stage") {
            const label = STAGE_LABEL[event.id] ?? `${event.id}…`;
            setStageLabel(event.state === "running" ? label : "Running checks…");
          }

          else if (event.type === "check") {
            const i = event.id; // 0-based index
            if (event.state === "running") {
              setRowStates(prev => {
                const next = [...prev];
                next[i] = "running";
                return next;
              });
            } else if (event.state === "done") {
              const result = {
                status: event.status,
                points: event.points,
                max_points: event.max_points,
                detail: event.detail ?? "",
                links: event.links ?? [],
              };
              const nextResults = [...rowResultsRef.current];
              nextResults[i] = result;
              rowResultsRef.current = nextResults;
              setRowResults(nextResults);
              setRowStates(prev => {
                const next = [...prev];
                next[i] = "done";
                return next;
              });
            }
          }

          else if (event.type === "final") {
            onDone({
              score: event.score,
              verdict: event.verdict,
              capReason: event.cap_reason,
              rowResults: rowResultsRef.current,
            });
          }

          else if (event.type === "error") {
            setErrorMsg(event.message || "An unexpected error occurred.");
          }
        });
      } catch (err) {
        if (!cancelled) setErrorMsg(err.message || "Network error. Please try again.");
      }
    }

    stream();
    return () => { cancelled = true; };
  }, []); // run once on mount

  if (errorMsg) {
    return (
      <div className="min-h-screen bg-surface flex flex-col items-center justify-center px-4">
        <div className="bg-white rounded-2xl border border-red-200 p-8 max-w-md w-full text-center shadow-card">
          <p className="text-red-700 font-semibold mb-4">⚠ {errorMsg}</p>
          <button
            onClick={onReset}
            className="px-6 py-3 bg-primary-container hover:bg-primary-hover text-white rounded-xl font-bold"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-slate-200 px-6 py-3 flex items-center gap-3">
        <Loader2 className="w-5 h-5 text-primary-container animate-spin" />
        <span className="font-black text-primary-container text-lg tracking-tight">SahiCheck</span>
        <span className="text-sm text-slate-500 ml-2 hidden sm:inline">{stageLabel}</span>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-10">
        <h2 className="text-xl font-black text-primary-container mb-1">Analyzing your offer…</h2>
        <p className="text-sm text-slate-500 mb-6">Watch each check complete in real time.</p>

        {/* "Reading input" pseudo-row */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-100 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <th className="py-2.5 px-3">Check</th>
                <th className="py-2.5 px-3">Tier</th>
                <th className="py-2.5 px-3">Source</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Points</th>
              </tr>
            </thead>
            <tbody>
              {/* Row 0 – extract stage */}
              <tr className="border-b border-slate-100 bg-slate-50/60">
                <td className="py-3 px-3">
                  <div className="flex items-center gap-2">
                    {stageLabel.includes("Running") || rowStates.some(s => s !== "pending")
                      ? <span className="w-5 h-5 rounded-full flex items-center justify-center bg-passed-bg text-passed-DEFAULT text-[10px] font-bold">✓</span>
                      : <Loader2 className="w-4 h-4 text-primary-container animate-spin" />
                    }
                    <span className="text-sm font-semibold text-on-surface">Reading your input</span>
                  </div>
                </td>
                <td className="py-3 px-3"><span className="text-[11px] font-bold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-500">stage</span></td>
                <td className="py-3 px-3 text-xs text-slate-400">internal</td>
                <td className="py-3 px-3 text-xs text-slate-400">—</td>
                <td className="py-3 px-3 text-xs text-slate-400">—</td>
              </tr>

              {checks.map((meta, i) => (
                <CheckRow
                  key={meta.id}
                  meta={meta}
                  rowState={rowStates[i]}
                  result={rowResults[i]}
                  isResult={false}
                />
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
