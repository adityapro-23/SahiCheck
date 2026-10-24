/**
 * App.jsx – Top-level state machine.
 *
 * step: "input" → "progress" → "result"
 *       Any step can go to "error" via the ProgressView.
 *
 * On mount we fetch GET /api/checks once and store the 16-check metadata.
 * The checks list is passed to both ProgressView (to render rows) and
 * ResultView (for the final table).
 */

import { useState, useEffect } from "react";
import InputView from "./InputView.jsx";
import ProgressView from "./ProgressView.jsx";
import ResultView from "./ResultView.jsx";
import { fetchChecks } from "./api.js";

export default function App() {
  const [step, setStep] = useState("input");   // "input" | "progress" | "result"

  // 16 check metadata objects from /api/checks
  const [checks, setChecks] = useState([]);
  const [checksLoading, setChecksLoading] = useState(true);
  const [checksError, setChecksError] = useState(null);

  // FormData built by InputView, passed to ProgressView
  const [formData, setFormData] = useState(null);

  // Final result from the stream
  const [finalScore, setFinalScore] = useState(null);
  const [finalVerdict, setFinalVerdict] = useState(null);
  const [capReason, setCapReason] = useState(null);
  const [rowResults, setRowResults] = useState([]);

  async function loadChecks() {
    setChecksLoading(true);
    setChecksError(null);
    try {
      const result = await fetchChecks();
      setChecks(result);
    } catch (err) {
      setChecksError(err.message || "Could not load the checks list.");
    } finally {
      setChecksLoading(false);
    }
  }

  useEffect(() => {
    loadChecks();
  }, []);

  function handleAnalyze(fd) {
    setFormData(fd);
    setRowResults([]);
    setFinalScore(null);
    setFinalVerdict(null);
    setCapReason(null);
    setStep("progress");
  }

  function handleDone({ score, verdict, capReason: cap, rowResults: rr }) {
    setFinalScore(score);
    setFinalVerdict(verdict);
    setCapReason(cap ?? null);
    // ProgressView passes back the collected rowResults so ResultView can render them
    setRowResults(rr || []);
    setStep("result");
  }

  function handleReset() {
    setStep("input");
    setFormData(null);
    setFinalScore(null);
    setFinalVerdict(null);
    setCapReason(null);
    setRowResults([]);
  }

  if (checksLoading || checksError) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center px-4">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 max-w-md w-full text-center shadow-card">
          {checksLoading ? (
            <p className="text-slate-600">Loading SahiCheck…</p>
          ) : (
            <>
              <p className="text-red-700 font-semibold mb-4">{checksError}</p>
              <button
                onClick={loadChecks}
                className="px-6 py-3 bg-primary-container hover:bg-primary-hover text-white rounded-xl font-bold"
              >
                Try again
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  if (step === "input") {
    return <InputView onAnalyze={handleAnalyze} />;
  }

  if (step === "progress") {
    return (
      <ProgressView
        checks={checks}
        formData={formData}
        onDone={handleDone}
        onReset={handleReset}
      />
    );
  }

  if (step === "result") {
    return (
      <ResultView
        checks={checks}
        rowResults={rowResults}
        score={finalScore}
        verdict={finalVerdict}
        capReason={capReason}
        onReset={handleReset}
      />
    );
  }

  return null;
}
