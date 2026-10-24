import React, { useState, useRef } from 'react';
import { 
  FileUp, 
  FileText, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  ShieldCheck, 
  ExternalLink, 
  RefreshCw, 
  Trash2, 
  ChevronDown, 
  ChevronUp, 
  Code2, 
  Eye, 
  HelpCircle,
  FileCheck,
  Globe2,
  X
} from 'lucide-react';

const MAX_PREVIEW_CHARS = 5000;

export default function Scanner() {
  const [pastedText, setPastedText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [runWebChecks, setRunWebChecks] = useState(true);
  const [loading, setLoading] = useState(false);
  const [sampleLoading, setSampleLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [result, setResult] = useState(null);

  // Accordion state for transparent pipeline inspector
  const [openAccordions, setOpenAccordions] = useState({
    transcription: false,
    extracted: false,
    redFlags: false,
    json: false,
  });

  const fileInputRef = useRef(null);

  const toggleAccordion = (key) => {
    setOpenAccordions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setErrorMsg(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setErrorMsg(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const clearAll = () => {
    setPastedText('');
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setErrorMsg(null);
    setResult(null);
  };

  const loadSample = async (sampleType) => {
    try {
      setSampleLoading(true);
      setErrorMsg(null);
      const res = await fetch(`/api/demo/${sampleType}`);
      if (!res.ok) {
        throw new Error(`Failed to load demo sample (${res.status})`);
      }
      const data = await res.json();
      setPastedText(data.text || '');
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setErrorMsg(`Could not load sample: ${err.message}`);
    } finally {
      setSampleLoading(false);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!pastedText.trim() && !selectedFile) {
      setErrorMsg('Please paste recruiter text or upload an offer document/screenshot.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const formData = new FormData();
    if (selectedFile) {
      formData.append('file', selectedFile);
    }
    if (pastedText.trim()) {
      formData.append('pasted_text', pastedText.trim());
    }
    formData.append('run_web_checks', runWebChecks ? 'true' : 'false');

    try {
      const response = await fetch('/api/check', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Server error (${response.status})`);
      }

      const data = await response.json();
      setResult(data);
      
      // Auto-scroll slightly to show results
      setTimeout(() => {
        const resultsEl = document.getElementById('analysis-results');
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);

    } catch (err) {
      setErrorMsg(err.message || 'An error occurred while inspecting the offer.');
    } finally {
      setLoading(false);
    }
  };

  const report = result?.report;
  const debug = result?.debug;

  return (
    <section id="scanner-anchor" className="py-16 md:py-24 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Main Scanner Container Card */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-elevated-card overflow-hidden">
          
          {/* Card Top Banner */}
          <div className="bg-gradient-to-r from-primary-container via-slate-900 to-primary-container p-6 sm:p-8 text-white">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                  <span className="text-xs font-bold uppercase tracking-wider text-secondary-fixed">
                    Autonomous Multi-Agent Scanner
                  </span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                  Inspect Any Job Offer or Recruiter Message
                </h2>
                <p className="text-sm text-slate-300 mt-1 max-w-2xl">
                  Upload an offer letter screenshot/PDF or paste WhatsApp/Telegram/Email text. 
                  Zero data is stored or logged.
                </p>
              </div>

              {/* Demo Sample Quick-Buttons */}
              <div className="flex items-center gap-2 self-start sm:self-center">
                <span className="text-xs font-bold text-slate-400 mr-1 hidden sm:inline">Try Demo:</span>
                <button
                  type="button"
                  disabled={sampleLoading || loading}
                  onClick={() => loadSample('scam')}
                  className="px-3 py-1.5 rounded-lg bg-red-950/70 border border-red-700/60 text-red-200 hover:bg-red-900 text-xs font-bold transition-all shadow-sm disabled:opacity-50"
                >
                  🧪 Demo Scam
                </button>
                <button
                  type="button"
                  disabled={sampleLoading || loading}
                  onClick={() => loadSample('safe')}
                  className="px-3 py-1.5 rounded-lg bg-emerald-950/70 border border-emerald-700/60 text-emerald-200 hover:bg-emerald-900 text-xs font-bold transition-all shadow-sm disabled:opacity-50"
                >
                  🧪 Demo Safe
                </button>
              </div>
            </div>
          </div>

          {/* Card Form Body */}
          <form onSubmit={handleAnalyze} className="p-6 sm:p-8 lg:p-10">
            
            {/* Error Notification */}
            {errorMsg && (
              <div className="mb-8 p-4 rounded-xl bg-error-container/60 border border-error/30 text-error flex items-start gap-3 text-sm">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <strong className="font-bold">Input Error: </strong>
                  <span>{errorMsg}</span>
                </div>
                <button 
                  type="button" 
                  onClick={() => setErrorMsg(null)}
                  className="text-error hover:opacity-80 p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Strictly 2 Input Options Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start mb-8">
              
              {/* Left Option: Pasted Textarea */}
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="pasted-text" className="text-sm font-bold text-on-surface flex items-center gap-2">
                    <FileText className="w-4 h-4 text-primary-container" />
                    <span>Option A: Paste Message or Job Text</span>
                  </label>
                  <span className={`text-xs font-mono font-medium ${
                    pastedText.length > MAX_PREVIEW_CHARS ? 'text-amber-600 font-bold' : 'text-slate-400'
                  }`}>
                    {pastedText.length.toLocaleString()} / {MAX_PREVIEW_CHARS.toLocaleString()}
                  </span>
                </div>

                <div className="relative flex-1">
                  <textarea
                    id="pasted-text"
                    rows={9}
                    value={pastedText}
                    onChange={(e) => setPastedText(e.target.value)}
                    placeholder="Paste the recruiter message or offer text here...&#10;&#10;Examples:&#10;• WhatsApp / Telegram job offer message&#10;• Recruiter email text with interview links&#10;• Freelance data entry typing offer&#10;• English, Hindi, or Hinglish supported natively"
                    className="w-full h-64 p-4 rounded-2xl border border-slate-300 focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 text-sm text-slate-800 placeholder:text-slate-400 bg-surface/50 font-sans transition-all resize-none"
                  />
                  {pastedText && (
                    <button
                      type="button"
                      onClick={() => setPastedText('')}
                      className="absolute top-3 right-3 p-1.5 rounded-lg bg-slate-200/70 hover:bg-slate-300 text-slate-600 transition-colors"
                      title="Clear text"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 mt-2">
                  Tip: Include sender details, phone numbers, UPI IDs, or links for maximum detection accuracy.
                </p>
              </div>

              {/* Right Option: Image / PDF Dropzone */}
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-bold text-on-surface flex items-center gap-2">
                    <FileUp className="w-4 h-4 text-primary-container" />
                    <span>Option B: Upload Offer Letter / Screenshot</span>
                  </label>
                  <span className="text-xs text-slate-400">PDF, PNG, JPG (Max 15MB)</span>
                </div>

                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onClick={() => fileInputRef.current?.click()}
                  className={`h-64 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all ${
                    selectedFile
                      ? 'border-emerald-400 bg-emerald-50/40'
                      : 'border-slate-300 hover:border-primary-container bg-surface/50 hover:bg-surface-container/50'
                  }`}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf,.png,.jpg,.jpeg,.webp"
                    className="hidden"
                  />

                  {selectedFile ? (
                    <div className="flex flex-col items-center space-y-3">
                      <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-sm">
                        <FileCheck className="w-7 h-7" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-800 max-w-xs truncate">
                          {selectedFile.name}
                        </p>
                        <p className="text-xs text-slate-500">
                          {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for vision scan
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile();
                        }}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 text-xs font-semibold transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span>Remove File</span>
                      </button>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center space-y-3">
                      <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-500 flex items-center justify-center group-hover:scale-105 transition-transform">
                        <FileUp className="w-7 h-7" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-on-surface">
                          Drop your Offer Letter or Screenshot here
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          or <span className="text-secondary font-semibold underline">browse files</span> from your computer
                        </p>
                      </div>
                      <span className="text-[11px] text-slate-400 bg-slate-100 px-3 py-1 rounded-full">
                        PDF (first 2 pages) • PNG • JPG • WEBP
                      </span>
                    </div>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 mt-2">
                  Visual cues inspect letterhead resolution, alignment, forged stamps, and layout defects.
                </p>
              </div>

            </div>

            {/* Bottom Controls Row */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pt-6 border-t border-slate-200/80">
              
              {/* Web Checks Toggle */}
              <label className="flex items-center gap-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={runWebChecks}
                  onChange={(e) => setRunWebChecks(e.target.checked)}
                  className="w-4 h-4 text-primary-container rounded border-slate-300 focus:ring-primary-container"
                />
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
                    <Globe2 className="w-4 h-4 text-secondary" />
                    <span>Run Web Verification Checks (RDAP & Corporate URLs)</span>
                  </span>
                  <span className="text-xs text-slate-500">
                    Queries domain age & official company career links via safe_fetch
                  </span>
                </div>
              </label>

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                {(pastedText || selectedFile || result) && (
                  <button
                    type="button"
                    onClick={clearAll}
                    disabled={loading}
                    className="px-4 py-3 rounded-xl border border-slate-300 text-slate-600 hover:bg-slate-100 text-sm font-semibold transition-all disabled:opacity-50"
                  >
                    Clear All
                  </button>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 rounded-xl bg-primary-container hover:bg-primary-container-hover text-white text-base font-bold shadow-soft-card hover:shadow-elevated-card transition-all disabled:opacity-50 active:scale-[0.98]"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Running Multi-Agent Inspection...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 text-secondary-fixed" />
                      <span>Analyze for Scam Indicators</span>
                    </>
                  )}
                </button>
              </div>

            </div>

          </form>

        </div>

        {/* RESULTS SECTION */}
        {report && (
          <div id="analysis-results" className="mt-12 space-y-8 animate-fadeIn">
            
            {/* 1. Main Verdict Card */}
            <div
              className={`rounded-3xl border-2 p-6 sm:p-8 shadow-elevated-card transition-all ${
                report.verdict === 'SCAM'
                  ? 'bg-red-50/90 border-error text-red-950'
                  : report.verdict === 'SUSPICIOUS'
                  ? 'bg-amber-50/90 border-warning text-amber-950'
                  : 'bg-emerald-50/90 border-safe text-emerald-950'
              }`}
            >
              {/* Verdict Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-black/10">
                <div className="flex items-center gap-3.5">
                  <div
                    className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-md ${
                      report.verdict === 'SCAM'
                        ? 'bg-error text-white'
                        : report.verdict === 'SUSPICIOUS'
                        ? 'bg-warning text-white'
                        : 'bg-safe text-white'
                    }`}
                  >
                    {report.verdict === 'SCAM' ? (
                      <ShieldAlert className="w-8 h-8" />
                    ) : report.verdict === 'SUSPICIOUS' ? (
                      <AlertTriangle className="w-8 h-8" />
                    ) : (
                      <ShieldCheck className="w-8 h-8" />
                    )}
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider opacity-75">
                      SahiCheck Final Verdict
                    </span>
                    <h3 className="text-2xl sm:text-3xl font-black tracking-tight">
                      VERDICT: {report.verdict}
                    </h3>
                  </div>
                </div>

                {/* Score & Coverage */}
                <div className="flex items-center gap-6 bg-white/70 backdrop-blur-sm px-6 py-3 rounded-2xl border border-black/5 self-start sm:self-auto">
                  <div className="text-right">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                      Legitimacy Score
                    </span>
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-black text-on-surface">
                        {report.legitimacy_score}
                      </span>
                      <span className="text-sm font-semibold text-slate-400">/ 100</span>
                    </div>
                  </div>

                  <div className="h-8 w-px bg-slate-200" />

                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                      Evidence Coverage
                    </span>
                    <span className="inline-block mt-0.5 text-xs font-extrabold uppercase px-2.5 py-0.5 rounded-full bg-slate-800 text-white tracking-wide">
                      {report.evidence_coverage}
                    </span>
                  </div>
                </div>
              </div>

              {/* Summary Statement */}
              <div className="py-6 border-b border-black/10">
                <h4 className="text-xs font-bold uppercase tracking-wider opacity-70 mb-1">
                  Executive Assessment
                </h4>
                <p className="text-base sm:text-lg font-medium leading-relaxed">
                  {report.summary}
                </p>

                {/* Extracted Claimed Meta */}
                <div className="mt-4 flex flex-wrap items-center gap-3 text-xs font-semibold">
                  <span className="bg-white/80 px-3 py-1.5 rounded-xl border border-black/5">
                    Claimed Company: <strong className="text-on-surface">{report.extracted?.company || 'Not explicitly stated'}</strong>
                  </span>
                  <span className="bg-white/80 px-3 py-1.5 rounded-xl border border-black/5">
                    Claimed Role: <strong className="text-on-surface">{report.extracted?.role || 'Not explicitly stated'}</strong>
                  </span>
                  {report.extracted?.pay && (
                    <span className="bg-white/80 px-3 py-1.5 rounded-xl border border-black/5">
                      Pay Quoted: <strong className="text-on-surface">{report.extracted?.pay}</strong>
                    </span>
                  )}
                </div>
              </div>

              {/* Triggered Red Flags */}
              {report.red_flags && report.red_flags.length > 0 && (
                <div className="py-6 border-b border-black/10">
                  <h4 className="text-sm font-black uppercase tracking-wider text-error flex items-center gap-2 mb-4">
                    <ShieldAlert className="w-4 h-4 text-error" />
                    <span>Red Flags Triggered ({report.red_flags.length})</span>
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {report.red_flags.map((flag, idx) => (
                      <div
                        key={idx}
                        className="bg-white/95 rounded-2xl p-4 border border-red-200 shadow-sm text-xs space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800 font-mono">
                            {flag.id}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide ${
                              flag.severity === 'high'
                                ? 'bg-red-600 text-white'
                                : flag.severity === 'medium'
                                ? 'bg-amber-600 text-white'
                                : 'bg-slate-700 text-white'
                            }`}
                          >
                            {flag.severity} Severity
                          </span>
                        </div>
                        <p className="font-mono bg-red-50 text-red-900 p-2 rounded-lg border border-red-100">
                          "{flag.evidence}"
                        </p>
                        <p className="text-slate-600 leading-relaxed">
                          <strong>Why it matters:</strong> {flag.why_it_matters}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Positive Signals (if any) */}
              {report.positive_signs && report.positive_signs.length > 0 && (
                <div className="py-5 border-b border-black/10">
                  <h4 className="text-xs font-black uppercase tracking-wider text-emerald-800 flex items-center gap-2 mb-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                    <span>Legitimacy Signals Verified</span>
                  </h4>
                  <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {report.positive_signs.map((pos, pIdx) => (
                      <li key={pIdx} className="flex items-center gap-2 bg-white/70 px-3 py-2 rounded-xl">
                        <CheckCircle2 className="w-3.5 h-3.5 text-safe shrink-0" />
                        <span>{pos}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommended Next Steps */}
              {report.next_steps && report.next_steps.length > 0 && (
                <div className="pt-6">
                  <h4 className="text-xs font-black uppercase tracking-wider text-slate-700 mb-3">
                    Recommended Safety Actions
                  </h4>
                  <ol className="space-y-2 text-xs sm:text-sm">
                    {report.next_steps.map((step, sIdx) => (
                      <li
                        key={sIdx}
                        className="flex items-start gap-3 bg-white/80 p-3 rounded-xl border border-black/5"
                      >
                        <span className="w-5 h-5 rounded-full bg-slate-800 text-white font-bold text-xs flex items-center justify-center shrink-0">
                          {sIdx + 1}
                        </span>
                        <span className="text-slate-800 font-medium">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

            </div>

            {/* 2. Verification Checks Breakdown Table (Agent 2b) */}
            {report.checks && report.checks.length > 0 && (
              <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-soft-card">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-on-surface">
                      Verification Checks Breakdown (Agent 2b)
                    </h3>
                    <p className="text-xs text-slate-500">
                      Independent checks across offline patterns and live RDAP web registration.
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs sm:text-sm border-collapse">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500 uppercase text-[11px] font-bold">
                        <th className="py-3 px-3">Check</th>
                        <th className="py-3 px-3">Status</th>
                        <th className="py-3 px-3">Tier</th>
                        <th className="py-3 px-3">Source</th>
                        <th className="py-3 px-3">Score Delta</th>
                        <th className="py-3 px-3">Finding Detail</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                      {report.checks.map((chk, cIdx) => (
                        <tr key={cIdx} className="hover:bg-slate-50/70 transition-colors">
                          <td className="py-3.5 px-3 font-bold text-on-surface whitespace-nowrap">
                            {chk.name}
                          </td>
                          <td className="py-3.5 px-3">
                            <span
                              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${
                                chk.status === 'passed'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : chk.status === 'failed'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-slate-100 text-slate-600'
                              }`}
                            >
                              {chk.status === 'passed' ? '✓ Passed' : chk.status === 'failed' ? '✕ Failed' : 'Unavailable'}
                            </span>
                          </td>
                          <td className="py-3.5 px-3 font-mono text-xs uppercase text-slate-500">
                            {chk.tier}
                          </td>
                          <td className="py-3.5 px-3 font-mono text-xs uppercase text-slate-500">
                            {chk.source}
                          </td>
                          <td className="py-3.5 px-3 font-mono font-bold">
                            <span
                              className={
                                chk.score_delta > 0
                                  ? 'text-emerald-600'
                                  : chk.score_delta < 0
                                  ? 'text-red-600'
                                  : 'text-slate-400'
                              }
                            >
                              {chk.score_delta > 0 ? `+${chk.score_delta}` : chk.score_delta}
                            </span>
                          </td>
                          <td className="py-3.5 px-3 text-xs text-slate-600 max-w-md">
                            {chk.detail}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 3. Independent Verification Links Grid */}
            {report.verify_links && report.verify_links.length > 0 && (
              <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-soft-card">
                <div className="mb-5">
                  <h3 className="text-lg font-bold text-on-surface">
                    Independent Verification Links
                  </h3>
                  <p className="text-xs text-slate-500">
                    SahiCheck never accesses private accounts. Open these direct public portals to verify the recruiter yourself:
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {report.verify_links.map((link, lIdx) => (
                    <a
                      key={lIdx}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-4 rounded-xl border border-slate-200 hover:border-primary-container bg-surface hover:bg-surface-container/60 transition-all group flex items-center justify-between"
                    >
                      <div className="flex items-center gap-2.5">
                        <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-primary-container" />
                        <span className="text-xs font-bold text-slate-800 group-hover:text-primary-container">
                          {link.label}
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 group-hover:translate-x-0.5 transition-transform">
                        &rarr;
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* 4. Transparent Multi-Agent Pipeline Inspector (Expandable Accordions) */}
            <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-soft-card">
              <div className="mb-6">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-bold uppercase mb-2">
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Pipeline Transparency (Live Demo Judges)</span>
                </div>
                <h3 className="text-lg font-bold text-on-surface">
                  Multi-Agent Step-by-Step Inspector
                </h3>
                <p className="text-xs text-slate-500">
                  Inspect the raw transcription, extracted entity dictionaries, heuristic flag arrays, and final JSON schema.
                </p>
              </div>

              <div className="space-y-3">
                
                {/* Agent 1 Transcription */}
                <div className="border border-slate-200 rounded-2xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => toggleAccordion('transcription')}
                    className="w-full flex items-center justify-between p-4 bg-slate-50 text-left hover:bg-slate-100 text-xs font-bold text-slate-800"
                  >
                    <span>Agent 1 — Verbatim Transcription (Vision / PDF Text Layer)</span>
                    {openAccordions.transcription ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {openAccordions.transcription && (
                    <div className="p-4 bg-slate-900 text-emerald-400 font-mono text-xs whitespace-pre-wrap max-h-72 overflow-y-auto">
                      {debug?.transcription || 'No transcription available.'}
                    </div>
                  )}
                </div>

                {/* Agent 1 Extracted Fields & Visual Cues */}
                <div className="border border-slate-200 rounded-2xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => toggleAccordion('extracted')}
                    className="w-full flex items-center justify-between p-4 bg-slate-50 text-left hover:bg-slate-100 text-xs font-bold text-slate-800"
                  >
                    <span>Agent 1 — Extracted Structured Fields & Visual Layout Cues</span>
                    {openAccordions.extracted ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {openAccordions.extracted && (
                    <div className="p-4 bg-slate-900 text-slate-200 font-mono text-xs whitespace-pre-wrap max-h-72 overflow-y-auto">
                      {JSON.stringify(debug?.extracted || {}, null, 2)}
                    </div>
                  )}
                </div>

                {/* Agent 2 Red Flags */}
                <div className="border border-slate-200 rounded-2xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => toggleAccordion('redFlags')}
                    className="w-full flex items-center justify-between p-4 bg-slate-50 text-left hover:bg-slate-100 text-xs font-bold text-slate-800"
                  >
                    <span>Agent 2 — Deterministic Heuristic Red-Flag Hits</span>
                    {openAccordions.redFlags ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {openAccordions.redFlags && (
                    <div className="p-4 bg-slate-900 text-amber-300 font-mono text-xs whitespace-pre-wrap max-h-72 overflow-y-auto">
                      {JSON.stringify(debug?.red_flags || [], null, 2)}
                    </div>
                  )}
                </div>

                {/* Final JSON Schema */}
                <div className="border border-slate-200 rounded-2xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => toggleAccordion('json')}
                    className="w-full flex items-center justify-between p-4 bg-slate-50 text-left hover:bg-slate-100 text-xs font-bold text-slate-800"
                  >
                    <span>Agent 3 — Final Validated Output Schema (JSON)</span>
                    {openAccordions.json ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {openAccordions.json && (
                    <div className="p-4 bg-slate-900 text-cyan-300 font-mono text-xs whitespace-pre-wrap max-h-72 overflow-y-auto">
                      {JSON.stringify(report, null, 2)}
                    </div>
                  )}
                </div>

              </div>
            </div>

          </div>
        )}

      </div>
    </section>
  );
}
