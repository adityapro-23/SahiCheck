import React, { useState } from 'react';
import { ChevronDown, HelpCircle, Shield, AlertCircle } from 'lucide-react';

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState(0);

  const toggleAccordion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const faqs = [
    {
      question: 'How does SahiCheck analyze job offers and recruiter messages?',
      answer:
        'SahiCheck uses a transparent multi-agent pipeline powered by Gemma 4 and deterministic heuristics. Agent 1 extracts entities (company name, role, salary figures, sender contact info, UPI IDs, URLs, and visual layout cues). Agent 2 runs 15+ deterministic red-flag checks for known fraud heuristics (upfront fees, personal data requests, urgency deadlines, disposable email providers). Agent 2b performs live RDAP domain lookup and verifies company career portals. Finally, Agent 3 synthesizes an explainable verdict with exact evidence quotes and next-step advice.',
    },
    {
      question: 'Can SahiCheck guarantee 100% detection of all job fraud?',
      answer:
        'No automated system can guarantee 100% immunity against novel or evolving fraud techniques. SahiCheck is designed as an intelligent safety shield and screening tool that flags high-risk indicators, detects spoofed domains, and catches common patterns. We encourage all job seekers to exercise independent verification and never transfer money or sensitive IDs to recruiters without confirming through official enterprise channels.',
    },
    {
      question: 'What does the Legitimacy Score mean and how is it calculated?',
      answer:
        'The Legitimacy Score is a bounded metric from 3 to 97 (we avoid 0 or 100 to prevent false certainty). It begins at a neutral baseline of 50. Passing independent verification checks (e.g. valid registered corporate domain, official careers link, zero-fee declarations) adds positive score deltas (+5 to +20). Conversely, triggering critical red flags (e.g. upfront fee demands, UPI IDs, disposable .xyz domains, Telegram-only contact) applies severe deterministic penalties (-25 to -45). Offers with scores below 35 are flagged as SCAM; 35–65 as SUSPICIOUS; and above 65 as SAFE.',
    },
    {
      question: 'What if the company is real, but the recruiter claiming to represent them is fake?',
      answer:
        'This is the most common form of employment fraud in India: scammers pose as recruiters from legitimate corporate brands like Tata Consultancy Services, Infosys, Amazon, or Reliance. SahiCheck explicitly separates the claimed company name from the sender communication channel. We inspect whether the recruiter’s email address ends in the authenticated corporate domain (e.g., @tcs.com) or a free public provider (@gmail.com, @ybl UPI, or a newly registered lookalike domain).',
    },
    {
      question: 'Is my uploaded offer letter, PDF, or text stored on your servers?',
      answer:
        'No. SahiCheck adheres strictly to a zero-data retention policy. All uploaded images, PDFs, and pasted messages are processed entirely in ephemeral server memory and discarded immediately once your analysis is returned. We do not retain copies of your documents, build training profiles on your data, or share inputs with third parties.',
    },
    {
      question: 'What should I do if SahiCheck flags an offer as a SCAM or SUSPICIOUS?',
      answer:
        'If an offer is flagged as SCAM: 1) Stop all communication with the recruiter immediately. 2) Do NOT transfer any money or share OTPs, bank statements, Aadhaar, or PAN cards. 3) Block the recruiter’s number and Telegram account. 4) If you have already lost money, immediately call the National Cyber Crime Helpline at 1930 to freeze fraudulent bank transactions.',
    },
    {
      question: 'How do I report a fraudulent recruiter or lost money to Indian cyber authorities?',
      answer:
        'You can lodge an official cyber complaint directly on the Government of India National Cyber Crime Reporting Portal at https://cybercrime.gov.in or by dialing the national toll-free helpline number 1930 (available 24/7). Additionally, you can report suspicious numbers on the Department of Telecommunications Chakshu portal (sancharsaathi.gov.in) to deactivate fraudulent SIM cards.',
    },
  ];

  return (
    <section id="faq" className="py-20 bg-white border-t border-outline-variant/30">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container border border-outline-variant/40 mb-3">
            <span className="text-xs font-bold text-primary-container uppercase tracking-wider">
              Common Questions
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-on-surface tracking-tight">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-600">
            Learn more about how SahiCheck operates, how scores are calculated, and how to stay safe.
          </p>
        </div>

        {/* 7 Accordion Items */}
        <div className="space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div
                key={index}
                className={`rounded-2xl border transition-all duration-200 overflow-hidden ${
                  isOpen
                    ? 'border-primary-container/30 bg-surface shadow-soft-card'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <button
                  type="button"
                  onClick={() => toggleAccordion(index)}
                  className="w-full flex items-center justify-between text-left p-6 gap-4 focus:outline-none"
                  aria-expanded={isOpen}
                >
                  <span className="text-base sm:text-lg font-bold text-on-surface">
                    {faq.question}
                  </span>
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-transform duration-200 ${
                      isOpen
                        ? 'bg-primary-container text-white rotate-180'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    <ChevronDown className="w-4 h-4" />
                  </div>
                </button>

                {isOpen && (
                  <div className="px-6 pb-6 pt-1 text-slate-600 text-sm sm:text-base leading-relaxed border-t border-slate-100/80">
                    {faq.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
