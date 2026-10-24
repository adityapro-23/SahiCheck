import React, { useState } from 'react';
import { 
  AlertOctagon, 
  CheckCircle, 
  ArrowRight, 
  Mail, 
  CreditCard, 
  Clock, 
  ExternalLink, 
  UserCheck, 
  FileWarning 
} from 'lucide-react';

export default function SampleBreakdown() {
  const [activeTab, setActiveTab] = useState('scam');

  const scamIndicators = [
    {
      title: 'Upfront "Security Deposit" / Training Fee',
      icon: CreditCard,
      indicator: 'Demands ₹2,499 via UPI before sending laptop kit.',
      whyScam:
        'Legitimate companies never ask candidates for security deposits, equipment fees, or training charges. Any monetary request is a 100% scam signal.',
      severity: 'Critical',
    },
    {
      title: 'Free Webmail / Imposter Recruiter Address',
      icon: Mail,
      indicator: 'Email: tcs.recruitment.india2026@gmail.com',
      whyScam:
        'Top tier enterprises never conduct official recruitment via free @gmail.com, @yahoo.com, or temporary email services. Verified offers originate from official domains like @tcs.com.',
      severity: 'High',
    },
    {
      title: 'Lookalike / Newly Registered Web Domain',
      icon: ExternalLink,
      indicator: 'Link: https://tcs-careers-india.xyz/apply (Registered 6 days ago)',
      whyScam:
        'Scammers purchase disposable domains with suffixes like .xyz, .site, or hyphenated brand names. Live RDAP lookup immediately flags domains created recently.',
      severity: 'High',
    },
    {
      title: 'Artificial Urgency & Telegram/WhatsApp Onboarding',
      icon: Clock,
      indicator: '"Complete verification within 30 minutes or seat cancelled."',
      whyScam:
        'Fraudsters rush victims to prevent them from consulting friends, family, or official company HR desks. Off-platform migration to Telegram avoids enterprise oversight.',
      severity: 'Medium',
    },
  ];

  const safeIndicators = [
    {
      title: 'Zero-Fee Transparency Statement',
      icon: CheckCircle,
      indicator: '"Infosys Limited never charges any fee at any stage of recruitment."',
      whySafe:
        'Reputable organizations include explicit anti-fraud disclaimers and reporting contact emails directly in their offer documentation.',
      tier: 'Strong Positive',
    },
    {
      title: 'Authenticated Corporate Domain',
      icon: Mail,
      indicator: 'Recruiter domain matches official corporate entity: @infosys.com',
      whySafe:
        'Sender email domain matches the exact corporate root domain with established reputation and valid MX / SPF records.',
      tier: 'Strong Positive',
    },
    {
      title: 'Official Candidate Career Portal',
      icon: ExternalLink,
      indicator: 'Acceptance via https://www.infosys.com/careers/ Launchpad portal',
      whySafe:
        'Candidate signs in to an established, TLS-secured subdomain under the corporate parent domain, not a third-party link.',
      tier: 'Strong Positive',
    },
    {
      title: 'Reasonable Acceptance Window',
      icon: Clock,
      indicator: '7 business days provided to review and digitally accept terms.',
      whySafe:
        'Normal professional onboarding allows candidates ample time to evaluate offer terms and ask questions.',
      tier: 'Supporting',
    },
  ];

  return (
    <section id="sample-breakdown" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary-fixed/60 border border-secondary/20 mb-3">
            <span className="text-xs font-bold text-secondary uppercase tracking-wider">
              Anatomy of an Offer
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-on-surface tracking-tight">
            How SahiCheck Analyzes Signals
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-600">
            Compare the anatomy of a sophisticated scam message with an authentic enterprise offer letter.
          </p>

          {/* Toggle Tab */}
          <div className="inline-flex p-1.5 bg-surface-container rounded-xl mt-8 border border-outline-variant/30">
            <button
              onClick={() => setActiveTab('scam')}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition-all ${
                activeTab === 'scam'
                  ? 'bg-error-container text-error shadow-sm'
                  : 'text-slate-600 hover:text-on-surface'
              }`}
            >
              <AlertOctagon className="w-4 h-4 text-error" />
              <span>Fraudulent Offer (Scam)</span>
            </button>
            <button
              onClick={() => setActiveTab('safe')}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition-all ${
                activeTab === 'safe'
                  ? 'bg-safe-container text-safe-text shadow-sm'
                  : 'text-slate-600 hover:text-on-surface'
              }`}
            >
              <CheckCircle className="w-4 h-4 text-safe" />
              <span>Legitimate Offer (Safe)</span>
            </button>
          </div>
        </div>

        {/* Breakdown Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left: Message Sample Display */}
          <div className="lg:col-span-5 bg-surface rounded-2xl border border-slate-200 p-6 shadow-soft-card font-mono text-xs leading-relaxed">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
              <span className="font-bold text-slate-500 uppercase tracking-wider">
                {activeTab === 'scam' ? 'Raw Imposter WhatsApp Message' : 'Official HR Offer Excerpt'}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  activeTab === 'scam'
                    ? 'bg-error-container text-error'
                    : 'bg-safe-container text-safe-text'
                }`}
              >
                {activeTab === 'scam' ? 'Flags Triggered: 4' : 'All Checks Passed'}
              </span>
            </div>

            {activeTab === 'scam' ? (
              <div className="text-slate-700 whitespace-pre-wrap select-all bg-white p-4 rounded-xl border border-red-100 shadow-inner">
                {`CONGRATULATIONS DEAR CANDIDATE! 🎉
Your resume has been shortlisted for Tata Consultancy Services (TCS) Work From Home Drive 2026!
Role: Junior Associate Data Entry & Software Trainee
Salary: Rs. 48,000/- per month (Fixed) + Daily Payout options
Selection: Direct Joining (No Interview Required)

To receive your Offer Letter and Laptop Kit today, complete onboarding verification within 30 minutes:
1. Pay Refundable Laptop & Training Security Deposit: Rs. 2,499/-
2. Payment UPI ID: tcs.hr.onboarding@ybl (Scan QR / GPay)
3. Send Aadhaar & PAN Card photo on WhatsApp immediately.

Official HR Desk Email: tcs.recruitment.india2026@gmail.com
Portal Link: https://tcs-careers-india.xyz/apply
Contact HR on Telegram: https://t.me/tcs_direct_joining_hr`}
              </div>
            ) : (
              <div className="text-slate-700 whitespace-pre-wrap select-all bg-white p-4 rounded-xl border border-emerald-100 shadow-inner">
                {`Subject: Offer of Full-Time Employment - Systems Engineer Trainee at Infosys Limited

Dear Candidate,
Following your campus technical and HR interviews, we are pleased to offer you the position of Systems Engineer Trainee at Infosys Limited.
Role: Systems Engineer Trainee (Fresher)
Compensation: INR 3.6 LPA (Approx. Rs. 30,000 per month gross)
Location: Pune Development Center, Hinjewadi

Please digitally accept your offer letter by logging into the official Infosys Launchpad portal at https://www.infosys.com/careers/ within 7 business days.

Please note: Infosys Limited never charges any fee at any stage of its recruitment process. If anyone demands payment, please report to talent.acquisition@infosys.com.

Campus Talent Acquisition Team
Infosys Limited | campus.recruitment@infosys.com`}
              </div>
            )}
          </div>

          {/* Right: Signal Cards */}
          <div className="lg:col-span-7 space-y-4">
            {(activeTab === 'scam' ? scamIndicators : safeIndicators).map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  className={`p-5 rounded-xl border transition-all ${
                    activeTab === 'scam'
                      ? 'bg-white border-red-100 hover:border-red-300 shadow-sm'
                      : 'bg-white border-emerald-100 hover:border-emerald-300 shadow-sm'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                          activeTab === 'scam'
                            ? 'bg-error-container text-error'
                            : 'bg-safe-container text-safe-text'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <h4 className="text-base font-bold text-on-surface">{item.title}</h4>
                    </div>

                    <span
                      className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase tracking-wide shrink-0 ${
                        activeTab === 'scam'
                          ? 'bg-red-100 text-error'
                          : 'bg-emerald-100 text-safe-text'
                      }`}
                    >
                      {activeTab === 'scam' ? item.severity : item.tier}
                    </span>
                  </div>

                  <div className="pl-10 space-y-1.5">
                    <p className="text-xs font-mono bg-slate-50 text-slate-800 p-2 rounded border border-slate-100">
                      {item.indicator}
                    </p>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {activeTab === 'scam' ? item.whyScam : item.whySafe}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

        </div>

      </div>
    </section>
  );
}
