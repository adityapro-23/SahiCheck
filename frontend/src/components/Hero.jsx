import React from 'react';
import { 
  ShieldAlert, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  Globe, 
  Lock, 
  Sparkles, 
  FileSearch,
  ExternalLink
} from 'lucide-react';

export default function Hero() {
  const scrollToScanner = () => {
    const el = document.getElementById('scanner-anchor');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToBreakdown = () => {
    const el = document.getElementById('sample-breakdown');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative overflow-hidden pt-12 pb-20 md:pt-16 md:pb-28">
      {/* Background decorative gradient blurs */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-br from-surface-variant/40 via-surface-container/30 to-transparent -z-10 blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Left Column: Copy & CTAs */}
          <div className="lg:col-span-7 flex flex-col items-start text-left">
            
            {/* Amber Eyebrow Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-secondary-fixed border border-secondary/20 shadow-sm mb-6">
              <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-wider text-secondary">
                SMARTER JOB SEARCH. SAFER DECISIONS.
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-on-surface tracking-tight leading-[1.15] mb-6">
              Not Every Job Offer <br className="hidden sm:inline" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container via-slate-800 to-secondary">
                Is What It Seems.
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed mb-8 max-w-2xl">
              Verify recruiter messages, appointment letters, and freelance offers with 
              transparent multi-agent AI. Catch fake domains, upfront fee demands, and spoofed 
              letterheads before you share personal documents or send money.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-4 w-full sm:w-auto mb-10">
              <button
                onClick={scrollToScanner}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-primary-container text-white font-semibold text-base shadow-soft-card hover:bg-primary-container-hover hover:shadow-elevated-card transition-all active:scale-[0.98]"
              >
                <span>Analyze an Offer Now</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              <button
                onClick={scrollToBreakdown}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white border border-outline-variant/60 text-slate-700 font-semibold text-base hover:bg-slate-50 transition-all shadow-sm"
              >
                <FileSearch className="w-4 h-4 text-slate-500" />
                <span>See How Scams Look</span>
              </button>
            </div>

            {/* Micro Quick-Tags */}
            <div className="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-3 text-xs font-medium text-slate-600 pt-2 border-t border-slate-200/80 w-full">
              <div className="flex items-center gap-1.5 py-1">
                <Globe className="w-4 h-4 text-primary-container" />
                <span>Live Domain RDAP Checks</span>
              </div>
              <div className="flex items-center gap-1.5 py-1">
                <Lock className="w-4 h-4 text-primary-container" />
                <span>Zero-Data Retention</span>
              </div>
              <div className="flex items-center gap-1.5 py-1">
                <Sparkles className="w-4 h-4 text-secondary" />
                <span>Gemma 4 Multi-Agent</span>
              </div>
              <div className="flex items-center gap-1.5 py-1">
                <CheckCircle2 className="w-4 h-4 text-safe" />
                <span>Supports Hinglish & Hindi</span>
              </div>
            </div>

          </div>

          {/* Right Column: Illustrative High-Risk Preview Card */}
          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-elevated-card p-6 overflow-hidden">
              
              {/* Header inside preview card */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-red-100 text-error flex items-center justify-center">
                    <ShieldAlert className="w-4 h-4 text-error" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-on-surface">Live Case Assessment</h3>
                    <p className="text-[11px] text-slate-500 font-medium">WhatsApp Work-From-Home Drive</p>
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-error-container text-error tracking-wide">
                  HIGH RISK (SCAM)
                </span>
              </div>

              {/* Imposter Target info */}
              <div className="p-3 bg-surface-container rounded-xl mb-4 text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-500">Claimed Company:</span>
                  <span className="font-semibold text-on-surface">Tata Consultancy Services (TCS)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Legitimacy Score:</span>
                  <span className="font-bold text-error">4 / 100 (Critical Risk)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Evidence Coverage:</span>
                  <span className="font-semibold text-slate-700 uppercase">HIGH</span>
                </div>
              </div>

              {/* Detected Warning Flags */}
              <div className="space-y-2.5 mb-5">
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Critical Red Flags Uncovered
                </p>

                <div className="p-2.5 rounded-lg bg-red-50/70 border border-red-200/80 flex items-start gap-2.5 text-xs text-red-950">
                  <AlertTriangle className="w-4 h-4 text-error shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Upfront Security Deposit:</span> Demands ₹2,499 via UPI (<code className="bg-white/80 px-1 rounded text-[11px] font-mono text-error">tcs.hr.onboarding@ybl</code>) for laptop kit.
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-red-50/70 border border-red-200/80 flex items-start gap-2.5 text-xs text-red-950">
                  <Globe className="w-4 h-4 text-error shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Spoofed Domain:</span> Links to <span className="font-mono text-error">tcs-careers-india.xyz</span> (Registered 6 days ago) instead of official <span className="font-semibold">tcs.com</span>.
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-red-50/70 border border-red-200/80 flex items-start gap-2.5 text-xs text-red-950">
                  <ShieldAlert className="w-4 h-4 text-error shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Personal Document Theft:</span> Solicits PAN, Aadhaar, and passbook photos via personal WhatsApp with a 30-min countdown.
                  </div>
                </div>
              </div>

              {/* Verified Action Recommendation */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <div className="text-slate-500 font-medium">
                  Recommendation: <strong className="text-error">Do Not Pay</strong>
                </div>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600">
                  <span>Report on 1930 / cybercrime.gov.in</span>
                </span>
              </div>

              {/* Subtle background glow effect */}
              <div className="absolute -bottom-8 -right-8 w-32 h-32 bg-secondary-fixed/50 rounded-full blur-2xl pointer-events-none -z-10" />
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
