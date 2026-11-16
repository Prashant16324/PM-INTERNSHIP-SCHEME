import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { internshipsAPI, applicationsAPI } from '../../services/api';
import { Internship } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  Building2,
  MapPin,
  Calendar,
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
  Send,
  ArrowLeft,
  GraduationCap,
} from 'lucide-react';

export const InternshipDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const internshipId = parseInt(id || '0');
  const [internship, setInternship] = useState<Internship | null>(null);
  const [eligibility, setEligibility] = useState<{
    internship_id: number;
    is_eligible: boolean;
    reasons: string[];
    missing_mandatory_skills: string[];
    matched_mandatory_skills: string[];
    cgpa_satisfied: boolean;
    education_satisfied: boolean;
    deadline_valid: boolean;
  } | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isApplying, setIsApplying] = useState(false);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [coverLetter, setCoverLetter] = useState('');

  const { isAuthenticated, role } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const data = await internshipsAPI.getDetail(internshipId);
        setInternship(data);

        // If authenticated as student, check real-time eligibility
        if (isAuthenticated && role === 'STUDENT') {
          const elig = await internshipsAPI.checkEligibility(internshipId);
          setEligibility(elig);
        }
      } catch (err) {
        showToast('Failed to load internship details', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    if (internshipId) fetchDetails();
  }, [internshipId, isAuthenticated, role]);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!internship) return;

    setIsApplying(true);
    try {
      await applicationsAPI.apply(internship.id, coverLetter);
      showToast('Application submitted successfully!', 'success');
      setShowApplyModal(false);
      navigate('/applications');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Application submission failed.';
      showToast(msg, 'error');
    } finally {
      setIsApplying(false);
    }
  };

  if (isLoading || !internship) {
    return <LoadingSpinner message="Loading opportunity details..." />;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <Link
        to="/internships"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Internships Catalog
      </Link>

      {/* Main Header Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-brand-50 text-brand-700 border border-brand-100">
                {internship.industry}
              </span>
              <StatusBadge status={internship.status} size="sm" />
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {internship.title}
            </h1>

            <p className="text-sm font-semibold text-slate-600 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-slate-400" />
              {internship.company?.company_name || 'Partner Company'}
              {internship.company?.location && (
                <span className="text-xs text-slate-400 font-normal">({internship.company.location})</span>
              )}
            </p>
          </div>

          <div className="text-left sm:text-right space-y-1 shrink-0">
            <div className="text-2xl font-extrabold text-slate-900">
              ₹{internship.stipend.toLocaleString()}{' '}
              <span className="text-xs font-normal text-slate-500">/ month</span>
            </div>
            <div className="text-xs font-bold text-brand-700 flex items-center gap-1 sm:justify-end">
              <Users className="w-4 h-4 text-brand-500" />
              {internship.available_seats} Available / {internship.total_seats} Total Seats
            </div>
          </div>
        </div>

        {/* Quick Highlights Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Location</div>
            <div className="font-bold text-slate-800 flex items-center gap-1 mt-0.5">
              <MapPin className="w-3.5 h-3.5 text-slate-400" /> {internship.location}
            </div>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Duration</div>
            <div className="font-bold text-slate-800 flex items-center gap-1 mt-0.5">
              <Calendar className="w-3.5 h-3.5 text-slate-400" /> {internship.duration_weeks} Weeks
            </div>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Min CGPA Required</div>
            <div className="font-bold text-slate-800 mt-0.5">
              {internship.min_cgpa > 0 ? `${internship.min_cgpa} / 10.0` : 'None required'}
            </div>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Preferred Education</div>
            <div className="font-bold text-slate-800 mt-0.5">
              {internship.preferred_education || 'Open to all'}
            </div>
          </div>
        </div>

        {/* Real-time Rule-Based Eligibility Assessment Banner */}
        {eligibility && (
          <div
            className={`p-4 rounded-2xl border flex items-start gap-3 text-xs ${
              eligibility.is_eligible
                ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
                : 'bg-rose-50/70 border-rose-200 text-rose-900'
            }`}
          >
            {eligibility.is_eligible ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div className="space-y-1">
              <div className="font-bold text-sm">
                {eligibility.is_eligible
                  ? 'You are Eligible for this Internship'
                  : 'Mandatory Eligibility Disqualification'}
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-slate-700">
                {eligibility.reasons.map((r, idx) => (
                  <li key={idx}>{r}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Description */}
        <div className="space-y-2 pt-2">
          <h2 className="text-sm font-bold text-slate-900">About the Role & Responsibilities</h2>
          <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line">
            {internship.description}
          </p>
        </div>

        {/* Required Skills Matrix */}
        <div className="space-y-3 pt-2">
          <h2 className="text-sm font-bold text-slate-900">Required Skills & Competencies</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {internship.skills?.map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs"
              >
                <div className="font-bold text-slate-800">{s.skill_name}</div>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      s.is_mandatory
                        ? 'bg-amber-100 text-amber-800 border border-amber-200'
                        : 'bg-slate-200/70 text-slate-600'
                    }`}
                  >
                    {s.is_mandatory ? 'Mandatory' : 'Preferred'}
                  </span>
                  <span className="text-[10px] text-slate-400">Weight: {s.weight}x</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4">
          <Link
            to={`/skill-gap/${internship.id}`}
            className="px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs flex items-center gap-1.5 transition"
          >
            <Sparkles className="w-4 h-4 text-brand-600" /> Run Skill Gap Diagnosis
          </Link>

          {role === 'STUDENT' && (
            <button
              onClick={() => setShowApplyModal(true)}
              disabled={internship.available_seats <= 0 || internship.status !== 'OPEN'}
              className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition disabled:opacity-50 flex items-center gap-2"
            >
              <Send className="w-4 h-4" /> Apply for Internship
            </button>
          )}
        </div>
      </div>

      {/* Application Submission Modal */}
      {showApplyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in">
          <div className="w-full max-w-lg p-6 rounded-3xl bg-white shadow-2xl space-y-5 border border-slate-200">
            <div className="space-y-1">
              <h3 className="text-lg font-extrabold text-slate-900">
                Confirm Internship Application
              </h3>
              <p className="text-xs text-slate-500">
                Applying to <span className="font-bold text-slate-700">{internship.title}</span> at{' '}
                {internship.company?.company_name}
              </p>
            </div>

            <form onSubmit={handleApply} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Motivation / Cover Note (Optional)
                </label>
                <textarea
                  rows={4}
                  value={coverLetter}
                  onChange={(e) => setCoverLetter(e.target.value)}
                  placeholder="Mention why you are interested in this project and how your skills align..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:ring-2 focus:ring-brand-500/30"
                />
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-[11px] text-slate-500 space-y-1">
                <div className="font-bold text-slate-700">Scheme Guidelines:</div>
                <p>
                  Your current profile credentials and AI matching score will be submitted to the organization for evaluation during the upcoming allocation round.
                </p>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowApplyModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isApplying}
                  className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md transition disabled:opacity-60 flex items-center gap-1.5"
                >
                  {isApplying ? 'Submitting...' : 'Submit Application'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
