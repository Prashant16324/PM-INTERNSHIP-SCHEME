import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { applicationsAPI } from '../../services/api';
import { Application } from '../../types';
import { useToast } from '../../context/ToastContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { FileText, Building2, MapPin, Search, ArrowRight, XCircle } from 'lucide-react';

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { showToast } = useToast();

  const fetchApplications = async () => {
    setIsLoading(true);
    try {
      const data = await applicationsAPI.getMyApplications();
      setApplications(data);
    } catch (err) {
      showToast('Failed to load application history', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const handleWithdraw = async (appId: number) => {
    if (!window.confirm('Are you sure you want to withdraw this application?')) return;

    try {
      await applicationsAPI.withdraw(appId);
      showToast('Application withdrawn successfully', 'info');
      fetchApplications();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to withdraw application';
      showToast(msg, 'error');
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Retrieving your submitted applications..." />;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">My Internship Applications</h1>
        <p className="text-xs text-slate-500">
          Track real-time evaluation stages, AI matching snapshots, and allocation status across your submissions.
        </p>
      </div>

      {applications.length === 0 ? (
        <div className="py-16 text-center space-y-4 bg-white rounded-3xl border border-slate-200 shadow-sm p-8">
          <FileText className="w-10 h-10 text-slate-400 mx-auto" />
          <div className="text-base font-bold text-slate-800">No applications submitted yet</div>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Browse through approved opportunities under the scheme and submit applications to begin the matching cycle.
          </p>
          <Link
            to="/internships"
            className="inline-flex px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md transition"
          >
            Explore Internships
          </Link>
        </div>
      ) : (
        <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Internship Role</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Match Score</th>
                  <th className="py-3 px-4">Submitted On</th>
                  <th className="py-3 px-4">Current Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      <Link
                        to={`/internships/${app.internship_id}`}
                        className="hover:text-brand-600 transition"
                      >
                        {app.internship?.title || `Internship #${app.internship_id}`}
                      </Link>
                    </td>

                    <td className="py-3.5 px-4 text-slate-600">
                      {app.internship?.company?.company_name || 'Partner Org'}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="font-extrabold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-100">
                        {app.match_score}%
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </td>

                    <td className="py-3.5 px-4">
                      <StatusBadge status={app.status} size="sm" />
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      {app.status !== 'ALLOCATED' && app.status !== 'WITHDRAWN' && (
                        <button
                          onClick={() => handleWithdraw(app.id)}
                          className="text-xs font-bold text-rose-600 hover:text-rose-800 transition px-2.5 py-1 rounded-lg hover:bg-rose-50"
                        >
                          Withdraw
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
