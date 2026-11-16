import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { studentsAPI, matchingAPI, applicationsAPI, allocationsAPI } from '../../services/api';
import { StudentProfile, Recommendation, Application, Allocation } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Sparkles,
  Award,
  FileText,
  Search,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Building2,
  MapPin,
  Clock,
  UploadCloud,
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [allocation, setAllocation] = useState<Allocation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profData, recData, appData, allocData] = await Promise.all([
          studentsAPI.getProfile(),
          matchingAPI.getRecommendations(),
          applicationsAPI.getMyApplications(),
          allocationsAPI.getMyAllocation(),
        ]);
        setProfile(profData);
        setRecommendations(recData.recommendations.slice(0, 3));
        setApplications(appData.slice(0, 5));
        setAllocation(allocData);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Assembling your personalized AI dashboard..." />;
  }

  const completion = profile?.profile_completion_percentage || 20;

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-brand-900 via-brand-800 to-slate-900 text-white p-6 sm:p-8 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-[11px] font-semibold text-brand-200">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" /> PM Internship Scheme Portal
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Welcome back, {user?.full_name}!
            </h1>
            <p className="text-xs sm:text-sm text-slate-300">
              Your AI-matched recommendations are active. Keep your technical skills and resume updated to improve allocation precision.
            </p>
          </div>

          {/* Allocation Spotlight Pill */}
          {allocation ? (
            <div className="p-4 rounded-2xl bg-white/10 backdrop-blur border border-white/20 space-y-2 shrink-0">
              <div className="text-[11px] font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                <Award className="w-4 h-4" /> Seat Allocation Result
              </div>
              <div className="text-sm font-bold text-white">
                {allocation.internship?.title || 'Allocated Internship'}
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={allocation.status} size="sm" />
                <span className="text-xs text-slate-300 font-medium">Round {allocation.allocation_round}</span>
              </div>
            </div>
          ) : (
            <Link
              to="/recommendations"
              className="px-5 py-3 rounded-xl bg-brand-500 hover:bg-brand-400 text-white font-bold text-xs shadow-md transition flex items-center gap-2 shrink-0 self-start md:self-auto"
            >
              View All Recommendations <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      </div>

      {/* KPI Cards Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Profile Completion */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>Profile Completion</span>
            <span className="text-brand-600 font-extrabold text-sm">{completion}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-brand-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${completion}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500">
            {completion < 80 ? (
              <Link to="/resume" className="text-brand-600 font-bold hover:underline">
                Upload resume & skills (+30%)
              </Link>
            ) : (
              'Profile optimized for matching'
            )}
          </p>
        </div>

        {/* AI Matches */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-bold text-slate-500 flex items-center justify-between">
            <span>AI Matches</span>
            <Sparkles className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">{recommendations.length}</div>
          <p className="text-[11px] text-slate-500">Evaluated opportunities</p>
        </div>

        {/* Applications */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-bold text-slate-500 flex items-center justify-between">
            <span>Active Applications</span>
            <FileText className="w-4 h-4 text-brand-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">{applications.length}</div>
          <p className="text-[11px] text-slate-500">Submitted to companies</p>
        </div>

        {/* Skills Listed */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-bold text-slate-500 flex items-center justify-between">
            <span>Skills Listed</span>
            <TrendingUp className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            {profile?.skills?.length || 0}
          </div>
          <p className="text-[11px] text-slate-500">Technical & soft skills</p>
        </div>
      </div>

      {/* Top AI Recommendations Preview */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-extrabold text-slate-900">Top AI Recommendations</h2>
            <p className="text-xs text-slate-500">Ranked by explainable skills & education compatibility</p>
          </div>
          <Link
            to="/recommendations"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            Explore All ({recommendations.length}) <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recommendations.length === 0 ? (
          <div className="p-8 rounded-2xl bg-white border border-slate-200 text-center space-y-3">
            <Search className="w-8 h-8 text-slate-400 mx-auto" />
            <div className="text-sm font-bold text-slate-800">No matching recommendations yet</div>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Add technical skills to your profile or browse open internships to begin receiving personalized recommendations.
            </p>
            <Link
              to="/profile"
              className="inline-flex px-4 py-2 rounded-xl bg-brand-600 text-white font-bold text-xs"
            >
              Add Profile Skills
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {recommendations.map((rec) => (
              <div
                key={rec.internship_id}
                className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md hover:border-brand-300 transition flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-brand-50 text-brand-700 border border-brand-100">
                      {rec.industry}
                    </span>
                    <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-extrabold text-xs border border-emerald-200">
                      <Sparkles className="w-3 h-3 text-emerald-500" />
                      {rec.overall_score}% Match
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-slate-900 line-clamp-1">{rec.internship_title}</h3>
                    <p className="text-xs text-slate-500 font-medium flex items-center gap-1.5 mt-0.5">
                      <Building2 className="w-3.5 h-3.5" /> {rec.company_name}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2 text-[11px] text-slate-600 pt-1">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-400" /> {rec.location}
                    </span>
                    <span className="font-semibold text-slate-800">
                      ₹{rec.stipend.toLocaleString()}/mo
                    </span>
                  </div>

                  {/* Skills Tag Pills */}
                  <div className="space-y-1 pt-1">
                    <div className="text-[10px] font-bold text-slate-400 uppercase">Matched Skills</div>
                    <div className="flex flex-wrap gap-1">
                      {rec.matched_skills.slice(0, 3).map((s) => (
                        <span key={s} className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-medium border border-emerald-100">
                          ✓ {s}
                        </span>
                      ))}
                      {rec.missing_skills.length > 0 && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-rose-50 text-rose-700 font-medium border border-rose-100">
                          - {rec.missing_skills[0]}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <Link
                    to={`/skill-gap/${rec.internship_id}`}
                    className="text-[11px] font-bold text-slate-600 hover:text-brand-600"
                  >
                    Skill Gap
                  </Link>
                  <Link
                    to={`/internships/${rec.internship_id}`}
                    className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs transition"
                  >
                    View & Apply
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Applications Table */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Applications</h2>
            <p className="text-xs text-slate-500">Track application statuses and allocation progress</p>
          </div>
          <Link to="/applications" className="text-xs font-bold text-brand-600 hover:underline">
            View All ({applications.length})
          </Link>
        </div>

        {applications.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            You haven't submitted any internship applications yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Internship</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Match Score</th>
                  <th className="py-3 px-4">Applied Date</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4 font-bold text-slate-900">
                      {app.internship?.title || `Internship #${app.internship_id}`}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {app.internship?.company?.company_name || 'Partner Org'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-100">
                        {app.match_score}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={app.status} size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
