import React, { useState, useEffect } from 'react';
import { allocationsAPI } from '../../services/api';
import { Allocation } from '../../types';
import { useToast } from '../../context/ToastContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Cpu,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Award,
  Sliders,
  Building2,
  UserCheck,
  Download,
  Sparkles,
} from 'lucide-react';

export const AdminAllocationsPage: React.FC = () => {
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [showRunModal, setShowRunModal] = useState(false);

  // Allocation parameters
  const [roundNumber, setRoundNumber] = useState(1);
  const [minScoreThreshold, setMinScoreThreshold] = useState(40.0);
  const [autoConfirm, setAutoConfirm] = useState(false);

  const { showToast } = useToast();

  const fetchAllocations = async () => {
    setIsLoading(true);
    try {
      const data = await allocationsAPI.list({ page: 1, page_size: 50 });
      setAllocations(data.items);
    } catch (err) {
      showToast('Failed to load system allocations', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAllocations();
  }, []);

  const handleExecuteAllocation = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRunning(true);
    try {
      const summary = await allocationsAPI.run({
        allocation_round: roundNumber,
        min_score_threshold: minScoreThreshold,
        auto_confirm: autoConfirm,
      });

      showToast(
        `Allocation Round ${roundNumber} completed! Assigned ${summary.total_allocated_in_round} seats in ${summary.execution_time_seconds}s.`,
        'success'
      );
      setShowRunModal(false);
      fetchAllocations();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Allocation process execution failed.';
      showToast(msg, 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const handleConfirm = async (allocId: number) => {
    try {
      await allocationsAPI.confirm(allocId);
      showToast('Allocation confirmed successfully', 'success');
      fetchAllocations();
    } catch (err) {
      showToast('Failed to confirm allocation', 'error');
    }
  };

  const handleCancel = async (allocId: number) => {
    const reason = window.prompt('Please enter cancellation reason (seat will be restored to internship):');
    if (reason === null) return;

    try {
      await allocationsAPI.cancel(allocId, reason || undefined);
      showToast('Allocation cancelled and internship seat restored', 'info');
      fetchAllocations();
    } catch (err) {
      showToast('Failed to cancel allocation', 'error');
    }
  };

  const handleExportCSV = () => {
    const token = localStorage.getItem('token');
    const url = `/api/v1/allocations/export${roundNumber ? `?round_number=${roundNumber}` : ''}`;
    fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(res => res.blob())
      .then(blob => {
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `pm_internship_allocations_round_${roundNumber || 'all'}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('Allocation report exported successfully', 'success');
      })
      .catch(() => showToast('Failed to export CSV report', 'error'));
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading smart allocation registry..." />;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider mb-1">
            <Cpu className="w-3.5 h-3.5" /> Automated Matching & Seat Allocation
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Smart Allocation Engine
          </h1>
          <p className="text-xs text-slate-500">
            Execute fairness-aware allocation rounds with row-level database locking and duplicate prevention.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCSV}
            className="px-4 py-2.5 rounded-xl border border-slate-300 hover:border-slate-400 bg-white text-slate-700 font-bold text-xs shadow-sm transition flex items-center gap-2"
            title="Download complete allocation registry as CSV"
          >
            <Download className="w-4 h-4 text-slate-500" /> Export CSV
          </button>
          <button
            onClick={() => setShowRunModal(true)}
            className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition flex items-center gap-2"
          >
            <Play className="w-4 h-4 fill-current" /> Execute Allocation Round
          </button>
        </div>
      </div>

      {/* Allocations Table */}
      <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Allocation Records & Decisions</h2>
            <p className="text-xs text-slate-500">Review provisional assignments or confirm candidates</p>
          </div>
          <span className="text-xs font-extrabold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-lg">
            {allocations.length} Records
          </span>
        </div>

        {allocations.length === 0 ? (
          <div className="py-16 text-center space-y-3">
            <Award className="w-10 h-10 text-slate-300 mx-auto" />
            <div className="text-sm font-bold text-slate-800">No allocation rounds run yet</div>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Click "Execute Allocation Round" above to run the algorithm across pending candidate applications.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Round</th>
                  <th className="py-3 px-4">Student Profile ID</th>
                  <th className="py-3 px-4">Internship Role</th>
                  <th className="py-3 px-4">Merit Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Allocated Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {allocations.map((alloc) => (
                  <tr key={alloc.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3.5 px-4 font-bold text-brand-700">
                      R{alloc.allocation_round}
                    </td>

                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      Candidate #{alloc.student_profile_id}
                    </td>

                    <td className="py-3.5 px-4 text-slate-800 font-medium">
                      {alloc.internship?.title || `Internship #${alloc.internship_id}`}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="font-extrabold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-100">
                        {alloc.allocation_score}%
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <StatusBadge status={alloc.status} size="sm" />
                    </td>

                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(alloc.allocated_at).toLocaleDateString()}
                    </td>

                    <td className="py-3.5 px-4 text-right space-x-2">
                      {alloc.status === 'PROVISIONAL' && (
                        <button
                          onClick={() => handleConfirm(alloc.id)}
                          className="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-xs transition"
                        >
                          Confirm
                        </button>
                      )}

                      {alloc.status !== 'CANCELLED' && (
                        <button
                          onClick={() => handleCancel(alloc.id)}
                          className="px-2.5 py-1 rounded-lg hover:bg-rose-50 text-rose-600 font-bold text-xs transition"
                        >
                          Cancel
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

      {/* Allocation Execution Modal */}
      {showRunModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in">
          <div className="w-full max-w-lg p-6 rounded-3xl bg-white shadow-2xl space-y-5 border border-slate-200">
            <div className="space-y-1">
              <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-brand-600" /> Execute AI Smart Allocation Round
              </h3>
              <p className="text-xs text-slate-500">
                The engine processes submitted applications in merit order, checks mandatory eligibility, locks seat availability, and prevents duplicate allocations.
              </p>
            </div>

            <form onSubmit={handleExecuteAllocation} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Allocation Round Sequence</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={roundNumber}
                  onChange={(e) => setRoundNumber(parseInt(e.target.value) || 1)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 flex justify-between">
                  <span>Minimum Match Score Threshold</span>
                  <span className="text-brand-600 font-extrabold">{minScoreThreshold}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="90"
                  step="5"
                  value={minScoreThreshold}
                  onChange={(e) => setMinScoreThreshold(parseFloat(e.target.value))}
                  className="w-full accent-brand-600"
                />
              </div>

              <div className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-xs cursor-pointer">
                <input
                  type="checkbox"
                  id="autoConfirmToggle"
                  checked={autoConfirm}
                  onChange={(e) => setAutoConfirm(e.target.checked)}
                  className="rounded text-brand-600 focus:ring-brand-500"
                />
                <label htmlFor="autoConfirmToggle" className="cursor-pointer font-medium text-slate-700">
                  <span className="font-bold">Auto-Confirm:</span> Immediately set status to CONFIRMED (skipping manual provisional review)
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowRunModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isRunning}
                  className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md transition disabled:opacity-60 flex items-center gap-2"
                >
                  {isRunning ? 'Processing Algorithm...' : 'Run Round Now'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
