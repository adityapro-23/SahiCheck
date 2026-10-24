/**
 * InputView.jsx – Step A: the input screen.
 *
 * Rules enforced here:
 *  - Choosing a file clears the text field; typing clears the selected file.
 *  - Hard limit: text 5,000 chars; file 10 MB, types PNG/JPG/PDF only.
 *  - Analyze button disabled until there is valid input.
 *  - "Try a Sample" dropdown offers scam and safe samples.
 *  - Footer line: uploads processed in memory; not legal advice.
 */

import { useState, useRef } from "react";
import { FileUp, FileText, Globe, Loader2, X, Trash2, FileCheck } from "lucide-react";
import { fetchDemo } from "./api.js";

const MAX_TEXT = 5000;
const MAX_FILE = 10 * 1024 * 1024;
const ALLOWED_EXTS = [".png", ".jpg", ".jpeg", ".pdf"];
const ALLOWED_TYPES = ["image/png", "image/jpeg", "application/pdf"];

export default function InputView({ onAnalyze }) {
  const [pastedText, setPastedText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [runWebChecks, setRunWebChecks] = useState(true);
  const [error, setError] = useState("");
  const [loadingSample, setLoadingSample] = useState(false);
  const [showSampleMenu, setShowSampleMenu] = useState(false);
  const fileRef = useRef(null);

  // Picking a file clears text
  function pickFile(f) {
    if (!f) return;
    const ext = ("." + f.name.split(".").pop()).toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      setError(`File type "${ext}" not supported. Use PNG, JPG or PDF.`);
      return;
    }
    if (f.size > MAX_FILE) {
      setError("File exceeds the 10 MB limit.");
      return;
    }
    setSelectedFile(f);
    setPastedText("");           // mutual exclusion
    setError("");
  }

  // Typing clears the file
  function handleTextChange(e) {
    const val = e.target.value.slice(0, MAX_TEXT);
    setPastedText(val);
    setSelectedFile(null);       // mutual exclusion
    if (fileRef.current) fileRef.current.value = "";
    setError("");
  }

  async function loadSample(name) {
    setShowSampleMenu(false);
    setLoadingSample(true);
    setError("");
    try {
      const { text } = await fetchDemo(name);
      setPastedText(text.slice(0, MAX_TEXT));
      setSelectedFile(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingSample(false);
    }
  }

  function handleAnalyze() {
    if (!pastedText.trim() && !selectedFile) {
      setError("Please paste text or upload a file first.");
      return;
    }
    const formData = new FormData();
    if (selectedFile) formData.append("file", selectedFile);
    else formData.append("pasted_text", pastedText.trim());
    formData.append("run_web_checks", runWebChecks ? "true" : "false");
    onAnalyze(formData);
  }

  const hasInput = Boolean(pastedText.trim() || selectedFile);
  const charPct = (pastedText.length / MAX_TEXT) * 100;

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-black text-primary-container text-lg tracking-tight">SahiCheck</span>
          <span className="text-xs font-semibold text-slate-400 ml-1 hidden sm:inline">v2 · Job Offer Fraud Detector</span>
        </div>
        {/* "Try a sample" button with mini dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowSampleMenu(v => !v)}
            disabled={loadingSample}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-sm font-semibold text-slate-700 hover:border-primary-container hover:text-primary-container transition-all disabled:opacity-50"
          >
            {loadingSample ? <Loader2 className="w-4 h-4 animate-spin" /> : "Try a Sample"}
            <span className="text-xs">▾</span>
          </button>
          {showSampleMenu && (
            <div className="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-modal z-20 min-w-[160px] overflow-hidden">
              <button onClick={() => loadSample("scam")} className="block w-full text-left px-4 py-2.5 text-sm hover:bg-red-50 text-red-700 font-semibold">
                🧪 Scam sample
              </button>
              <button onClick={() => loadSample("safe")} className="block w-full text-left px-4 py-2.5 text-sm hover:bg-green-50 text-green-700 font-semibold">
                ✅ Safe sample
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-3xl">
          <h1 className="text-3xl sm:text-4xl font-black text-primary-container tracking-tight mb-2 text-center">
            Is this job offer genuine?
          </h1>
          <p className="text-center text-slate-500 mb-8 text-sm">
            Paste recruiter text or upload an offer letter. We run 16 checks and give you a confidence score.
          </p>

          {/* Error banner */}
          {error && (
            <div className="mb-6 flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700">
              <X className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{error}</span>
              <button className="ml-auto" onClick={() => setError("")}><X className="w-4 h-4" /></button>
            </div>
          )}

          {/* Two input options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">

            {/* Option A: textarea */}
            <div className="flex flex-col">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Paste text or a job link
              </label>
              <div className="relative flex-1">
                <textarea
                  rows={9}
                  value={pastedText}
                  onChange={handleTextChange}
                  placeholder={"Paste recruiter message, WhatsApp text, email body, or job-post URL…\n\nSupports English, Hindi & Hinglish."}
                  className="w-full h-56 p-4 rounded-2xl border border-slate-300 focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 text-sm resize-none bg-white text-on-surface placeholder:text-slate-400 transition-all"
                />
                {pastedText && (
                  <button
                    onClick={() => { setPastedText(""); setError(""); }}
                    className="absolute top-2 right-2 p-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500"
                    title="Clear text"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              {/* Live character counter */}
              <div className="mt-1.5 flex items-center gap-2">
                <div className="flex-1 h-1 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${charPct > 90 ? "bg-red-400" : "bg-primary-container/50"}`}
                    style={{ width: `${Math.min(charPct, 100)}%` }}
                  />
                </div>
                <span className={`text-[11px] font-mono ${pastedText.length >= MAX_TEXT ? "text-red-600 font-bold" : "text-slate-400"}`}>
                  {pastedText.length.toLocaleString()} / {MAX_TEXT.toLocaleString()}
                </span>
              </div>
            </div>

            {/* Option B: dropzone */}
            <div className="flex flex-col">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <FileUp className="w-3.5 h-3.5" /> Upload offer letter / screenshot
              </label>
              <div
                onDragOver={e => e.preventDefault()}
                onDrop={e => { e.preventDefault(); pickFile(e.dataTransfer.files?.[0]); }}
                onClick={() => !selectedFile && fileRef.current?.click()}
                className={`flex-1 h-56 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-all ${
                  selectedFile
                    ? "border-green-400 bg-green-50"
                    : "border-slate-300 hover:border-primary-container bg-white hover:bg-slate-50"
                }`}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept=".png,.jpg,.jpeg,.pdf"
                  className="hidden"
                  onChange={e => pickFile(e.target.files?.[0])}
                />
                {selectedFile ? (
                  <div className="flex flex-col items-center gap-3 text-center px-4">
                    <FileCheck className="w-10 h-10 text-green-600" />
                    <p className="text-sm font-bold text-on-surface truncate max-w-[200px]">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500">{(selectedFile.size / 1048576).toFixed(2)} MB</p>
                    <button
                      onClick={e => { e.stopPropagation(); setSelectedFile(null); if (fileRef.current) fileRef.current.value = ""; }}
                      className="text-xs text-red-600 underline"
                    >
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3 text-center px-4">
                    <FileUp className="w-10 h-10 text-slate-400" />
                    <p className="text-sm font-semibold text-slate-600">Drop or click to upload</p>
                    <p className="text-xs text-slate-400">PNG, JPG, PDF · max 10 MB</p>
                  </div>
                )}
              </div>
              <p className="text-[11px] text-slate-400 mt-1.5">
                {pastedText && "Typing clears any uploaded file."}
                {selectedFile && "Uploading a file clears any pasted text."}
              </p>
            </div>
          </div>

          {/* Web checks toggle */}
          <label className="flex items-center gap-3 cursor-pointer select-none mb-6 p-3 rounded-xl bg-white border border-slate-200">
            <input
              type="checkbox"
              checked={runWebChecks}
              onChange={e => setRunWebChecks(e.target.checked)}
              className="w-4 h-4 accent-primary-container rounded"
            />
            <Globe className="w-4 h-4 text-slate-500" />
            <div>
              <p className="text-sm font-semibold text-on-surface">Run web checks (RDAP domain age + legal pages)</p>
              <p className="text-xs text-slate-500">Checks 14 & 15 make live network requests — adds a few seconds.</p>
            </div>
          </label>

          {/* Analyze button */}
          <button
            onClick={handleAnalyze}
            disabled={!hasInput}
            className="w-full py-4 rounded-2xl bg-primary-container hover:bg-primary-hover text-white font-bold text-base shadow-card transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Analyze for Scam Indicators
          </button>

          {/* Footer note */}
          <p className="text-center text-[11px] text-slate-400 mt-4">
            Uploads are processed in memory and not stored. SahiCheck is guidance, not legal advice.
          </p>
        </div>
      </main>
    </div>
  );
}
