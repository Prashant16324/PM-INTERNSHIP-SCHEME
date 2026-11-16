import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { matchingAPI } from '../../services/api';
import { SkillGapDetail } from '../../types';
import { useToast } from '../../context/ToastContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  BookOpen,
  Clock,
  ArrowLeft,
  Building2,
  TrendingUp,
} from 'lucide-react';

export const SkillGapAnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const internshipId = parseInt(id || '0');
  const [gapData, setGapData] = useState<SkillGapDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    const fetchSkillGap = async () => {
      try {
        const data = await matchingAPI.getSkillGap(internshipId);
        setGapData(data);
      } catch (err) {
        showToast('Failed to load skill gap breakdown', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    if (internshipId) fetchSkillGap();
  }, [internshipId]);

  if (isLoading || !gapData) {
    return <LoadingSpinner message="Diagnosing candidate skill gap..." />;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <Link
        to="/recommendations"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Recommendations
      </Link>

      {/* Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" /> Explainable Skill Gap Diagnosis
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
              {gapData.internship_title}
            </h1>
            <p className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5" /> {gapData.company_name}
            </p>
          </div>

          <div className="flex items-center gap-3 p-4 rounded-2xl bg-brand-50 border border-brand-100 shrink-0">
            <div className="text-right">
              <div className="text-xs font-bold text-slate-500 uppercase">Skill Match</div>
              <div className="text-2xl font-extrabold text-brand-700">{gapData.skill_match_percentage}%</div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
          <div
            className={`h-3 rounded-full transition-all duration-700 ${
              gapData.skill_match_percentage >= 70
                ? 'bg-emerald-500'
                : gapData.skill_match_percentage >= 40
                ? 'bg-amber-500'
                : 'bg-rose-500'
            }`}
            style={{ width: `${gapData.skill_match_percentage}%` }}
          />
        </div>
      </div>

      {/* Comparative Skills Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matched Skills */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-sm font-bold text-emerald-800 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Matched Skills
            </h2>
            <span className="text-xs font-extrabold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              {gapData.matched_skills.length} Skills
            </span>
          </div>

          {gapData.matched_skills.length === 0 ? (
            <div className="py-6 text-center text-xs text-slate-400">
              None of your profile skills match this role's listed requirements.
            </div>
          ) : (
            <div className="space-y-2">
              {gapData.matched_skills.map((skill) => (
                <div
                  key={skill}
                  className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs font-bold text-emerald-900 flex items-center justify-between"
                >
                  <span>✓ {skill}</span>
                  <span className="text-[10px] uppercase font-semibold text-emerald-600">Verified</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Missing Skills */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-sm font-bold text-rose-800 flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-600" /> Missing Competencies
            </h2>
            <span className="text-xs font-extrabold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
              {gapData.missing_skills.length} Skills
            </span>
          </div>

          {gapData.missing_skills.length === 0 ? (
            <div className="py-6 text-center text-xs text-emerald-600 font-bold">
              Congratulations! You possess 100% of the required technical skills for this role.
            </div>
          ) : (
            <div className="space-y-2">
              {gapData.missing_skills.map((skill) => (
                <div
                  key={skill}
                  className="p-3 rounded-xl bg-rose-50/60 border border-rose-100 text-xs font-bold text-rose-900 flex items-center justify-between"
                >
                  <span>✕ {skill}</span>
                  <span className="text-[10px] uppercase font-semibold text-rose-600">Action Required</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Suggested Learning Topics & Study Modules */}
      {gapData.learning_recommendations.length > 0 && (
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
          <div>
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-brand-600" /> Suggested Learning Curricula
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Targeted modules recommended by the AI engine to bridge competency gaps and boost your matching score.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {gapData.learning_recommendations.map((rec) => (
              <div
                key={rec.skill_name}
                className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="font-extrabold text-xs text-slate-900 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-brand-500" />
                    {rec.skill_name}
                  </div>
                  <span className="text-[10px] font-semibold text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" /> ~{rec.estimated_hours} hrs
                  </span>
                </div>

                <ul className="space-y-1.5 text-xs text-slate-600">
                  {rec.suggested_topics.map((topic, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-brand-500 font-bold">•</span>
                      <span>{topic}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
