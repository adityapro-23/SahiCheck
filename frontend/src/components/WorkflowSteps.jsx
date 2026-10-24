import React from 'react';
import { UploadCloud, Cpu, ShieldCheck, Check } from 'lucide-react';

export default function WorkflowSteps() {
  const steps = [
    {
      number: '01',
      title: 'Submit Offer or Message',
      subtitle: 'Image, PDF, or Plain Text',
      description:
        'Upload your appointment letter screenshot or PDF document, or simply paste the recruiter message from WhatsApp, Telegram, LinkedIn, or Email. SahiCheck supports English, Hindi, and Hinglish natively.',
      icon: UploadCloud,
      highlights: ['PDF & Image OCR', 'Zero server storage', 'Multi-lingual support'],
      badgeColor: 'bg-surface-variant text-primary-container',
    },
    {
      number: '02',
      title: 'Multi-Agent Inspection',
      subtitle: 'Deterministic & Web Checks',
      description:
        'The harness triggers Agent 1 (Entity Extraction), Agent 2 (15+ deterministic red-flag heuristic checks), and Agent 2b (Live RDAP domain age & official company career portal verification via safe_fetch).',
      icon: Cpu,
      highlights: ['Domain age validation', 'UPI handle detection', 'Impersonation screening'],
      badgeColor: 'bg-secondary-fixed text-secondary',
    },
    {
      number: '03',
      title: 'Decide With Confidence',
      subtitle: 'Actionable & Transparent',
      description:
        'Review a color-coded verdict card, a legitimacy score (3–97), exact quotes of triggered red flags with plain-language explanations, and official direct links to verify the company without being tracked.',
      icon: ShieldCheck,
      highlights: ['Transparent scoring', 'Official verification links', 'Next-step safety advice'],
      badgeColor: 'bg-safe-container text-safe-text',
    },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-surface border-y border-outline-variant/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container border border-outline-variant/40 mb-3">
            <span className="text-xs font-bold text-primary-container uppercase tracking-wider">
              Transparent 3-Step Verification
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-on-surface tracking-tight">
            How SahiCheck Protects You
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-600">
            A privacy-first pipeline that inspects recruitment offers systematically before 
            fraudsters can extract personal data or security deposits.
          </p>
        </div>

        {/* 3 Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={step.number}
                className="relative bg-white rounded-2xl border border-slate-200/80 p-8 shadow-soft-card hover:shadow-elevated-card transition-all duration-300 flex flex-col justify-between group"
              >
                {/* Step Number & Icon */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="text-3xl font-black text-slate-200 group-hover:text-primary-container transition-colors font-mono">
                      {step.number}
                    </span>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${step.badgeColor} shadow-sm`}>
                      <Icon className="w-6 h-6" />
                    </div>
                  </div>

                  <span className="text-xs font-bold uppercase tracking-wider text-secondary">
                    {step.subtitle}
                  </span>
                  <h3 className="text-xl font-bold text-on-surface mt-1 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed mb-6">
                    {step.description}
                  </p>
                </div>

                {/* Micro highlights */}
                <div className="pt-5 border-t border-slate-100 space-y-2">
                  {step.highlights.map((h, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs font-medium text-slate-700">
                      <div className="w-4 h-4 rounded-full bg-surface-container flex items-center justify-center shrink-0">
                        <Check className="w-2.5 h-2.5 text-primary-container" />
                      </div>
                      <span>{h}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
