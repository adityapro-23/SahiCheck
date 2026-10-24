import React from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  FileLock2, 
  Hourglass, 
  UserX,
  AlertTriangle,
  ShieldCheck
} from 'lucide-react';

export default function WarningSigns() {
  const signs = [
    {
      id: 'upfront-fees',
      title: '1. Demands for Upfront Fees or Deposits',
      subtitle: '"Laptop deposit, training fees, uniform kit, registration fee"',
      icon: DollarSign,
      iconColor: 'bg-red-100 text-red-600',
      badge: 'Critical Red Flag',
      badgeColor: 'bg-red-100 text-red-700',
      description:
        'Legitimate companies—including TCS, Infosys, Wipro, and global MNCs—will NEVER ask for payment at any point during recruitment. Scammers claim the fee is "100% refundable" upon joining, then disappear.',
      typicalPhrases: [
        '"Pay Rs. 1,999 refundable courier & insurance charge for company laptop"',
        '"Security deposit required for 15-day certified training module"',
        '"Pay documentation processing charge via PhonePe/GPay QR code"',
      ],
      ruleOfThumb: 'Zero tolerance rule: If they ask for even 1 Rupee, it is a scam.',
    },
    {
      id: 'unrealistic-earnings',
      title: '2. Unrealistic Earnings for Low-Effort Roles',
      subtitle: '"Earn Rs. 3,000–5,000 daily with 1–2 hours part-time typing"',
      icon: TrendingUp,
      iconColor: 'bg-amber-100 text-amber-700',
      badge: 'High Red Flag',
      badgeColor: 'bg-amber-100 text-amber-800',
      description:
        'Fraudsters bait students and freshers with disproportionately high compensation for entry tasks (data entry, ad clicking, YouTube video liking, telegram tasks). They later lock funds behind "VIP withdrawal tiers".',
      typicalPhrases: [
        '"Daily payout Rs. 2,500 just for liking 5 Google Maps locations"',
        '"Work from home, no experience needed, guaranteed Rs. 60,000/month"',
        '"Direct joining without interview or aptitude test"',
      ],
      ruleOfThumb: 'If the salary exceeds normal market rates for the skills required, investigate thoroughly.',
    },
    {
      id: 'early-info-requests',
      title: '3. Early Requests for Sensitive Personal Documents',
      subtitle: '"Send Aadhaar, PAN card, and blank signed cheque on WhatsApp"',
      icon: FileLock2,
      iconColor: 'bg-red-100 text-red-600',
      badge: 'Identity Theft Risk',
      badgeColor: 'bg-red-100 text-red-700',
      description:
        'While authentic companies do verify KYC during onboarding, they collect these via authenticated enterprise portals after formal interviews and offer sign-off—never through random recruiter WhatsApp chats.',
      typicalPhrases: [
        '"Send clear photo of Aadhaar front/back and bank account passbook for salary setup"',
        '"Share OTP received on your mobile to verify your job application"',
        '"Provide credit card statement to prove financial background"',
      ],
      ruleOfThumb: 'Never share OTPs, credit cards, or bank credentials over messaging apps.',
    },
    {
      id: 'pressure-to-act-fast',
      title: '4. Artificial Urgency & High-Pressure Deadlines',
      subtitle: '"Offer expires in 30 minutes, only 3 seats left in your state"',
      icon: Hourglass,
      iconColor: 'bg-orange-100 text-orange-700',
      badge: 'Psychological Manipulation',
      badgeColor: 'bg-orange-100 text-orange-800',
      description:
        'Scammers use scarcity and panic to keep victims from checking with college placement cells, consulting mentors, or researching the company. Genuine hiring cycles offer 5–14 business days.',
      typicalPhrases: [
        '"Hurry, your offer letter will be reallocated if not verified in 1 hour"',
        '"Immediate selection drive ends at 6 PM sharp today"',
        '"Deposit fee within 20 mins to secure your offer letter"',
      ],
      ruleOfThumb: 'Real HR teams respect professional deliberation and never demand instant payment.',
    },
    {
      id: 'unverifiable-recruiters',
      title: '5. Unverifiable Recruiters & Disposable Communication',
      subtitle: '"Free @gmail.com IDs, WhatsApp-only contact, newly registered domains"',
      icon: UserX,
      iconColor: 'bg-purple-100 text-purple-700',
      badge: 'Domain Impersonation',
      badgeColor: 'bg-purple-100 text-purple-800',
      description:
        'Scammers frequently pose as HR managers from reputed firms like Amazon, Google, Deloitte, or TCS, but communicate exclusively via free webmail (@gmail.com, @hotmail.com) or burner Telegram handles.',
      typicalPhrases: [
        'hr.deloitte.careers.india@gmail.com (instead of @deloitte.com)',
        'Links to domains like infosys-jobs-portal.xyz registered last week',
        'Refusal to provide official company landline or video interview via Google Meet/Teams',
      ],
      ruleOfThumb: 'Always cross-reference the sender domain with the company’s official investor or careers page.',
    },
  ];

  return (
    <section id="warning-signs" className="py-20 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary-fixed/70 border border-secondary/20 mb-3">
            <span className="text-xs font-bold text-secondary uppercase tracking-wider">
              Essential Fraud Awareness
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-on-surface tracking-tight">
            5 Warning Signs Worth Checking
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-600">
            More than 95% of job frauds reported across India exhibit one or more of these 
            five distinct behavioral patterns.
          </p>
        </div>

        {/* 5 Signs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {signs.map((sign, index) => {
            const Icon = sign.icon;
            const isFullSpan = index === 4; // Fifth card spans cleanly on 3-col grids
            return (
              <div
                key={sign.id}
                className={`bg-white rounded-2xl border border-slate-200/90 p-7 shadow-soft-card hover:shadow-elevated-card transition-all flex flex-col justify-between ${
                  isFullSpan ? 'md:col-span-2 lg:col-span-1' : ''
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${sign.iconColor}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${sign.badgeColor}`}>
                      {sign.badge}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-on-surface mb-1">
                    {sign.title}
                  </h3>
                  <p className="text-xs font-semibold text-secondary mb-4 italic">
                    {sign.subtitle}
                  </p>

                  <p className="text-sm text-slate-600 leading-relaxed mb-5">
                    {sign.description}
                  </p>

                  {/* Red flag speech bubbles */}
                  <div className="space-y-2 mb-6">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                      Common Bait Phrases
                    </span>
                    {sign.typicalPhrases.map((phrase, pIdx) => (
                      <div
                        key={pIdx}
                        className="text-xs bg-slate-50 border border-slate-200/70 text-slate-700 px-3 py-2 rounded-lg font-mono leading-snug"
                      >
                        {phrase}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bottom Safety Rule */}
                <div className="pt-4 border-t border-slate-100 flex items-start gap-2 text-xs font-medium text-slate-800 bg-surface-container/40 p-3 rounded-xl">
                  <ShieldCheck className="w-4 h-4 text-safe shrink-0 mt-0.5" />
                  <span>{sign.ruleOfThumb}</span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
