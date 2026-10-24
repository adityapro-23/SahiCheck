import React from 'react';
import { Shield, ExternalLink, Heart, AlertTriangle, PhoneCall } from 'lucide-react';

export default function Footer() {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer id="resources" className="bg-primary-container text-white pt-16 pb-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-12 pb-14 border-b border-slate-800">
          
          {/* Col 1: Brand & Mission */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-white shadow-md">
                <Shield className="w-5 h-5" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-black tracking-tight text-white">
                  Sahi<span className="text-secondary-fixed">Check</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 uppercase">
                  v2.0 Open Source
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-400 leading-relaxed max-w-sm">
              An open-source AI safety harness protecting freshers, students, and job seekers across India
              from recruitment fraud, fee extortion, and impersonation scams.
            </p>

            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center gap-3 text-xs text-slate-300">
              <div className="w-8 h-8 rounded-lg bg-red-900/60 text-red-300 flex items-center justify-center shrink-0">
                <PhoneCall className="w-4 h-4 text-red-400" />
              </div>
              <div>
                <span className="font-bold text-white block">Cyber Fraud Emergency Helpline: 1930</span>
                <span className="text-[11px] text-slate-400">Toll-free 24/7 National Cyber Crime Support</span>
              </div>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="lg:col-span-3 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-secondary-fixed">
              Platform Navigation
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>
                <button onClick={() => scrollTo('scanner-anchor')} className="hover:text-white transition-colors">
                  AI Job Scanner
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('how-it-works')} className="hover:text-white transition-colors">
                  How SahiCheck Works
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('sample-breakdown')} className="hover:text-white transition-colors">
                  Sample Offer Breakdown
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('warning-signs')} className="hover:text-white transition-colors">
                  5 Warning Signs
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('faq')} className="hover:text-white transition-colors">
                  Frequently Asked Questions
                </button>
              </li>
            </ul>
          </div>

          {/* Col 3: Official Verification & Government Portals */}
          <div className="lg:col-span-4 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-secondary-fixed">
              Official Indian Govt Portals
            </h4>
            <ul className="space-y-2.5 text-xs text-slate-300">
              <li>
                <a
                  href="https://cybercrime.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 hover:text-white transition-colors text-slate-300 group"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-secondary group-hover:text-white" />
                  <span className="font-semibold text-white">National Cyber Crime Reporting Portal</span>
                  <span className="text-slate-500">(cybercrime.gov.in)</span>
                </a>
              </li>
              <li>
                <a
                  href="https://www.ncs.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 hover:text-white transition-colors text-slate-300 group"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-secondary group-hover:text-white" />
                  <span className="font-semibold text-white">National Career Service (NCS)</span>
                  <span className="text-slate-500">(Ministry of Labour)</span>
                </a>
              </li>
              <li>
                <a
                  href="https://www.mca.gov.in/content/mca/global/en/home.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 hover:text-white transition-colors text-slate-300 group"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-secondary group-hover:text-white" />
                  <span className="font-semibold text-white">MCA Company Master Data Search</span>
                  <span className="text-slate-500">(mca.gov.in)</span>
                </a>
              </li>
              <li>
                <a
                  href="https://sancharsaathi.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 hover:text-white transition-colors text-slate-300 group"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-secondary group-hover:text-white" />
                  <span className="font-semibold text-white">Chakshu Portal - Report Fraud Numbers</span>
                  <span className="text-slate-500">(sancharsaathi.gov.in)</span>
                </a>
              </li>
            </ul>
          </div>

        </div>

        {/* Mandatory Government Disclaimer Banner */}
        <div className="mt-8 p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-400 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-slate-200">Legal & Regulatory Disclaimer:</strong> SahiCheck is an independent, 
            open-source public service software project and is <strong>not affiliated with, endorsed by, or operated by any government body</strong>, 
            ministry, or regulatory agency. Results produced are algorithmic risk assessments intended for awareness and educational screening. 
            They do not constitute binding legal counsel. If you have been defrauded, report immediately to your local police cyber cell and at cybercrime.gov.in.
          </div>
        </div>

        {/* Bottom Credits */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} SahiCheck v2. Zero-data retention, open-source technology.</p>
          <p className="flex items-center gap-1">
            Built with care to keep careers safe.
          </p>
        </div>

      </div>
    </footer>
  );
}
