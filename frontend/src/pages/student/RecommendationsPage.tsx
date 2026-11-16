import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { matchingAPI } from '../../services/api';
import { Recommendation } from '../../types';
import { useToast } from '../../context/ToastContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Sparkles,
  Sliders,
  Building2,
  MapPin,
  CheckCircle2,
  XCircle,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  Info,
} from 'lucide-react';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecomputing, setIsRecomputing] = useState(false);
  const [showConfig, setShowConfig] = useState(false);

  // Configurable Weights State
  const [weights, setWeights] = useState({
    skill_weight: 0.50,
    education_weight: 0.20,
    location_weight: 0.15,
    industry_weight: 0.15,
  });

  const { showToast } = useToast();

  const fetchRecommendations = async () => {
    setIsLoading(true);
    try {
      const data = await matchingAPI.getRecommendations(weights);
      setRecommendations(data.recommendations);
    } catch (err) {
      showToast('Failed to generate AI recommendations', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleApplyWeights = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecommendations();
    showToast('Matching scores re-calculated with new weights', 'info');
  };

  const handleRecompute = async () => {
    setIsRecomputing(true);
    try {
      const data = await matchingAPI.recompute();
      setRecommendations(data.recommendations);
      showToast('Profile recommendations re-evaluated and cached!', 'success');
    } catch (err) {
      showToast('Failed to recompute recommendations', 'error');
    } finally {
      setIsRecomputing(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" /> Explainable Matching Engine
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">AI Internship Recommendations</h1>
          <p className="text-xs text-slate-500">
            Multidimensional ranking combining TF-IDF semantic cosine similarity with rule-based eligibility.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs flex items-center gap-1.5 transition shadow-2xs"
          >
            <Sliders className="w-4 h-4 text-slate-500" />
            {showConfig ? 'Hide Weight Tuning' : 'Tune Weights'}
          </button>

          <button
            onClick={handleRecompute}
            disabled={isRecomputing}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm transition disabled:opacity-60"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRecomputing ? 'animate-spin' : ''}`} />
            {isRecomputing ? 'Re-evaluating...' : 'Recompute'}
          </button>
        </div>
      </div>

      {/* Configurable Weights Drawer */}
      {showConfig && (
        <form onSubmit={handleApplyWeights} className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Configurable Matching Weights</h2>
              <p className="text-[11px] text-slate-500">Adjust the relative priority across evaluation dimensions</p>
            </div>
            <div className="text-xs font-mono font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
              Total: {Math.round((weights.skill_weight + weights.education_weight + weights.location_weight + weights.industry_weight) * 100)}%
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="space-y-1.5 p-3 rounded-xl bg-slate-50">
              <div className="flex justify-between font-bold text-slate-700">
                <span>Technical Skills</span>
                <span>{Math.round(weights.skill_weight * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.skill_weight}
                onChange={(e) => setWeights({ ...weights, skill_weight: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div className="space-y-1.5 p-3 rounded-xl bg-slate-50">
              <div className="flex justify-between font-bold text-slate-700">
                <span>Education Match</span>
                <span>{Math.round(weights.education_weight * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.education_weight}
                onChange={(e) => setWeights({ ...weights, education_weight: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div className="space-y-1.5 p-3 rounded-xl bg-slate-50">
              <div className="flex justify-between font-bold text-slate-700">
                <span>Location Preference</span>
                <span>{Math.round(weights.location_weight * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.location_weight}
                onChange={(e) => setWeights({ ...weights, location_weight: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div className="space-y-1.5 p-3 rounded-xl bg-slate-50">
              <div className="flex justify-between font-bold text-slate-700">
                <span>Industry Preference</span>
                <span>{Math.round(weights.industry_weight * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.industry_weight}
                onChange={(e) => setWeights({ ...weights, industry_weight: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs"
            >
              Update Recommendations
            </button>
          </div>
        </form>
      )}

      {/* Recommendations Cards */}
      {isLoading ? (
        <LoadingSpinner message="Calculating explainable matching scores..." />
      ) : recommendations.length === 0 ? (
        <div className="py-16 text-center space-y-3 bg-white rounded-2xl border border-slate-200">
          <Sparkles className="w-8 h-8 text-slate-400 mx-auto" />
          <div className="text-sm font-bold text-slate-800">No recommendations available</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Ensure your student profile has education and technical skills listed, then hit Recompute.
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {recommendations.map((rec, index) => (
            <div
              key={rec.internship_id}
              className={`p-6 rounded-2xl bg-white border transition shadow-2xs hover:shadow-md space-y-4 ${
                rec.is_eligible ? 'border-slate-200 hover:border-brand-300' : 'border-rose-200 bg-rose-50/20'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-extrabold text-slate-400">#{index + 1}</span>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                      {rec.industry}
                    </span>
                    {rec.is_eligible ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Eligible
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1">
                        <XCircle className="w-3 h-3 text-rose-600" /> Ineligible
                      </span>
                    )}
                  </div>

                  <h3 className="text-base sm:text-lg font-extrabold text-slate-900">
                    {rec.internship_title}
                  </h3>

                  <p className="text-xs font-semibold text-slate-600 flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <Building2 className="w-3.5 h-3.5 text-slate-400" /> {rec.company_name}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" /> {rec.location}
                    </span>
                    <span className="font-extrabold text-slate-900">₹{rec.stipend.toLocaleString()}/mo</span>
                  </p>
                </div>

                {/* Match Score Badge */}
                <div className="flex sm:flex-col items-center sm:items-end justify-between gap-1 shrink-0">
                  <div className="text-2xl sm:text-3xl font-extrabold text-brand-700">
                    {rec.overall_score}%
                  </div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase">Composite Match</div>
                </div>
              </div>

              {/* Multidimensional Score Meters */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-[11px]">
                <div>
                  <div className="text-slate-400 font-semibold">Skills Match</div>
                  <div className="font-extrabold text-slate-800 text-xs mt-0.5">{rec.skill_score}%</div>
                </div>
                <div>
                  <div className="text-slate-400 font-semibold">Education</div>
                  <div className="font-extrabold text-slate-800 text-xs mt-0.5">{rec.education_score}%</div>
                </div>
                <div>
                  <div className="text-slate-400 font-semibold">Location Pref</div>
                  <div className="font-extrabold text-slate-800 text-xs mt-0.5">{rec.location_score}%</div>
                </div>
                <div>
                  <div className="text-slate-400 font-semibold">Industry Pref</div>
                  <div className="font-extrabold text-slate-800 text-xs mt-0.5">{rec.industry_score}%</div>
                </div>
              </div>

              {/* Natural Language Explanation */}
              <div className="p-3 rounded-xl bg-blue-50/70 border border-blue-100 text-xs text-blue-900 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div className="leading-relaxed font-medium">
                  <span className="font-bold">AI Explanation: </span>
                  {rec.explanation}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
                <Link
                  to={`/skill-gap/${rec.internship_id}`}
                  className="text-xs font-bold text-slate-600 hover:text-brand-600 flex items-center gap-1.5"
                >
                  <Sparkles className="w-4 h-4 text-amber-500" /> View Personalized Skill Gap & Curriculum
                </Link>

                <div className="flex items-center gap-2">
                  <Link
                    to={`/internships/${rec.internship_id}`}
                    className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs transition flex items-center gap-1.5"
                  >
                    View & Apply <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
