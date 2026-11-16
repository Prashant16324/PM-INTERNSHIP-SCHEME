import React, { useState, useEffect } from 'react';
import { applicationsAPI, internshipsAPI } from '../../services/api';
import { Application, ApplicationStatus, Internship } from '../../types';
import { useToast } from '../../context/ToastContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { FileText, Filter, CheckCircle2, XCircle, Building2, Search } from 'lucide-react';

export const AdminApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [internships, setInternships] = useState<Internship[]>([]);
  const [selectedInternshipId, setSelectedInternshipId] = useState<number | ''>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  const { showToast } = useToast();

  useEffect(() => {
    const init = async () => {
      try {
        const intList = await internshipsAPI.list({ page_size: 50 });
        setInternships(intList.items);
        if (intList.items.length > 0) {
          setSelectedInternshipId(intList.items[0].id);
        }
      } catch (err) {
        console.error('Failed to load internships:', err);
      }
    };
    init();
  }, []);

  const fetchApplications = async () => {
    if (!selectedInternshipId) return;
    setIsLoading(true);
    try {
      const data = await applicationsAPI.getInternshipApplications(Number(selectedInternshipId), {
        status_filter: statusFilter || undefined,
      });
      setApplications(data.items);
    } catch (err) {
      showToast('Failed to load applications for selected internship', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedInternshipId) {
      fetchApplications();
    } else {
      setIsLoading(false);
    }
  }, [selectedInternshipId, statusFilter]);

  const handleUpdateStatus = async (appId: number, newStatus: string) => {
    try {
      await applicationsAPI.updateStatus(appId, newStatus);
      showToast(`Status updated to ${newStatus}`, 'success');
      fetchApplications();
    } catch (err) {
      showToast('Failed to update application status', 'error');
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Applications Management</h1>
        <p className="text-xs text-slate-500">
          Review student applications per internship, evaluate AI match score snapshots, and update recruitment stages.
        </p>
      </div>

      {/* Filter Strip */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-wrap items-center gap-4 text-xs">
        <div className="flex-1 min-w-[240px]">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
            Select Internship
          </label>
          <select
            value={selectedInternshipId}
            onChange={(e) => setSelectedInternshipId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium"
          >
            {internships.map((i) => (
              <option key={i.id} value={i.id}>
                {i.title} ({i.company?.company_name || 'Partner Org'})
              </option>
            ))}
          </select>
        </div>

        <div className="w-48">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
            Filter Status
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium"
          >
            <option value="">All Statuses</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="SHORTLISTED">Shortlisted</option>
            <option value="SELECTED">Selected</option>
            <option value="ALLOCATED">Allocated</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {/* Applications Table */}
      <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        {isLoading ? (
          <LoadingSpinner message="Retrieving applications..." />
        ) : applications.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">
            No applications found matching the selected filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Applicant ID</th>
                  <th className="py-3 px-4">Match Score</th>
                  <th className="py-3 px-4">Cover Note</th>
                  <th className="py-3 px-4">Applied Date</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Quick Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      Candidate #{app.student_profile_id}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="font-extrabold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-md border border-brand-100">
                        {app.match_score}%
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-slate-500 max-w-xs truncate">
                      {app.cover_letter || 'No note attached'}
                    </td>

                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </td>

                    <td className="py-3.5 px-4">
                      <StatusBadge status={app.status} size="sm" />
                    </td>

                    <td className="py-3.5 px-4 text-right space-x-1">
                      {app.status !== 'SHORTLISTED' && app.status !== 'ALLOCATED' && (
                        <button
                          onClick={() => handleUpdateStatus(app.id, 'SHORTLISTED')}
                          className="px-2.5 py-1 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-[11px] transition"
                        >
                          Shortlist
                        </button>
                      )}
                      {app.status !== 'REJECTED' && app.status !== 'ALLOCATED' && (
                        <button
                          onClick={() => handleUpdateStatus(app.id, 'REJECTED')}
                          className="px-2.5 py-1 rounded-lg hover:bg-rose-50 text-rose-600 font-bold text-[11px] transition"
                        >
                          Reject
                        </button>
                      )}
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
