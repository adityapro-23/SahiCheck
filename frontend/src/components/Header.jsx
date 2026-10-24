import React, { useState } from 'react';
import { Shield, ShieldAlert, ArrowRight, Menu, X, ExternalLink } from 'lucide-react';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-outline-variant/30 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <a href="#" className="flex items-center gap-3 group">
              <div className="w-11 h-11 rounded-xl bg-primary-container text-white flex items-center justify-center shadow-soft-card group-hover:scale-105 transition-transform">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="text-xl font-extrabold tracking-tight text-on-surface">
                    Sahi<span className="text-secondary">Check</span>
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-secondary-fixed text-secondary tracking-wide uppercase">
                    v2.0
                  </span>
                </div>
                <span className="text-xs text-slate-500 font-medium">
                  AI Job Offer Fraud Shield
                </span>
              </div>
            </a>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600">
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="hover:text-primary-container transition-colors"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('sample-breakdown')}
              className="hover:text-primary-container transition-colors"
            >
              Sample Breakdown
            </button>
            <button
              onClick={() => scrollToSection('warning-signs')}
              className="hover:text-primary-container transition-colors"
            >
              5 Warning Signs
            </button>
            <button
              onClick={() => scrollToSection('faq')}
              className="hover:text-primary-container transition-colors"
            >
              FAQ
            </button>
            <button
              onClick={() => scrollToSection('resources')}
              className="hover:text-primary-container transition-colors"
            >
              Safety Resources
            </button>
          </nav>

          {/* Right Action Button */}
          <div className="hidden md:flex items-center gap-4">
            <button
              onClick={() => scrollToSection('scanner-anchor')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-container text-white text-sm font-semibold shadow-soft-card hover:bg-primary-container-hover hover:shadow-elevated-card transition-all active:scale-[0.98]"
            >
              <span>Check a Job</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-on-surface hover:bg-slate-100"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-outline-variant/30 bg-white px-4 pt-3 pb-6 space-y-3 shadow-lg">
          <button
            onClick={() => scrollToSection('how-it-works')}
            className="block w-full text-left py-2 px-3 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            How It Works
          </button>
          <button
            onClick={() => scrollToSection('sample-breakdown')}
            className="block w-full text-left py-2 px-3 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Sample Breakdown
          </button>
          <button
            onClick={() => scrollToSection('warning-signs')}
            className="block w-full text-left py-2 px-3 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            5 Warning Signs
          </button>
          <button
            onClick={() => scrollToSection('faq')}
            className="block w-full text-left py-2 px-3 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            FAQ
          </button>
          <button
            onClick={() => scrollToSection('resources')}
            className="block w-full text-left py-2 px-3 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Safety Resources
          </button>
          <button
            onClick={() => scrollToSection('scanner-anchor')}
            className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-primary-container text-white text-sm font-semibold shadow-soft-card hover:bg-primary-container-hover"
          >
            <span>Check a Job Now</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </header>
  );
}
