import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  Search,
  Cpu,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  Building2,
  GraduationCap,
  ArrowRight,
  BookOpen,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { isAuthenticated, role } = useAuth();
  const dashboardLink = role === 'ADMIN' ? '/admin/dashboard' : '/dashboard';

  return (
    <div className="space-y-16 py-6">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-900 via-brand-800 to-slate-900 text-white p-8 sm:p-14 lg:p-20 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 rounded-full bg-brand-500/20 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 rounded-full bg-gov-saffron/20 blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur border border-white/20 text-xs font-semibold text-brand-200">
            <Sparkles className="w-4 h-4 text-amber-300" />
            AI-Powered Academic Prototype for B.Tech Final Evaluation
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
            Smart Allocation Engine for the{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-white">
              PM Internship Scheme
            </span>
          </h1>

          <p className="text-sm sm:text-base lg:text-lg text-slate-300 font-normal leading-relaxed">
            Bridging talent with opportunity through explainable AI matching, resume skill-gap diagnosis,
            and automated, fairness-aware seat allocation across partner organizations.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-4">
            {isAuthenticated ? (
              <Link
                to={dashboardLink}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-brand-500 hover:bg-brand-400 text-white font-bold text-sm shadow-lg shadow-brand-500/30 transition hover:-translate-y-0.5"
              >
                Go to Dashboard <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-brand-500 hover:bg-brand-400 text-white font-bold text-sm shadow-lg shadow-brand-500/30 transition hover:-translate-y-0.5"
                >
                  Candidate Registration <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-semibold text-sm backdrop-blur transition"
                >
                  Sign In Portal
                </Link>
              </>
            )}

            <Link
              to="/internships"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 font-semibold text-sm border border-slate-700 transition"
            >
              <Search className="w-4 h-4 text-brand-400" /> Browse Internships
            </Link>
          </div>
        </div>

        {/* Feature Pills */}
        <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-4 mt-12 pt-8 border-t border-white/10">
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white">50% + 20%</div>
            <div className="text-xs text-slate-400 mt-0.5">Configurable Matching Weights</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white">NLP-Driven</div>
            <div className="text-xs text-slate-400 mt-0.5">Resume & Skill Extraction</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white">Zero Race</div>
            <div className="text-xs text-slate-400 mt-0.5">Row-Locked Seat Allocation</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white">100%</div>
            <div className="text-xs text-slate-400 mt-0.5">Explainable Recommendations</div>
          </div>
        </div>
      </section>

      {/* Feature Pillars */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Core Technological Innovations
          </h2>
          <p className="text-sm text-slate-600">
            How the prototype ensures fairness, transparency, and high precision in student-internship allocation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3 hover:border-brand-300 transition">
            <div className="w-12 h-12 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">TF-IDF & Cosine Similarity</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Combines exact technical skill set overlap with Scikit-learn TF-IDF semantic vector similarity across candidate profiles and job requirements.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3 hover:border-brand-300 transition">
            <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Personalized Skill Gap Diagnosis</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Identifies missing required competencies for each opportunity and suggests curated learning topics to help candidates bridge the gap.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3 hover:border-brand-300 transition">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Smart Allocation Engine</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Automated multi-round allocation using database transaction locks, preventing duplicate seat assignments while honoring eligibility constraints.
            </p>
          </div>
        </div>
      </section>

      {/* Academic Prototype Notice */}
      <section className="p-6 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-900 flex items-start gap-4">
        <BookOpen className="w-6 h-6 text-amber-700 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs">
          <div className="font-bold text-sm text-amber-900">Academic Prototype Notice</div>
          <p className="text-amber-800 leading-relaxed">
            This platform is an academic engineering demonstration for a B.Tech AI & Data Science capstone project.
            It utilizes synthetic demo data to evaluate explainable machine learning allocation algorithms and is not officially affiliated with the Government of India.
          </p>
        </div>
      </section>
    </div>
  );
};
