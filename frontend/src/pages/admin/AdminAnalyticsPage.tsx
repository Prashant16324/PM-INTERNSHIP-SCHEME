import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../../services/api';
import { AnalyticsDashboardResponse } from '../../types';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  BarChart3,
  Download,
  PieChart as PieIcon,
  TrendingUp,
  Cpu,
  Layers,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export const AdminAnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await analyticsAPI.getDashboard();
        setData(res);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  const handleExportData = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pm_internship_analytics_report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  };

  if (isLoading || !data) {
    return <LoadingSpinner message="Generating analytics reports..." />;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Analytics & Scheme Reporting</h1>
          <p className="text-xs text-slate-500">
            Exportable metrics on candidate distribution, technical skills demand, and seat allocation efficiency.
          </p>
        </div>

        <button
          onClick={handleExportData}
          className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-md transition flex items-center gap-2"
        >
          <Download className="w-4 h-4" /> Export Analytics JSON
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Candidate Skills Distribution */}
        <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" /> Top Candidate Skills in Pool
            </h2>
            <span className="text-xs text-slate-400">Most frequent verified skills</span>
          </div>

          <div className="h-64 w-full">
            {data.top_skills_distribution.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No candidate skills recorded yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_skills_distribution} layout="vertical">
                  <XAxis type="number" tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="skill_name" tick={{ fontSize: 10 }} width={80} />
                  <Tooltip />
                  <Bar dataKey="student_count" fill="#10b981" radius={[0, 6, 6, 0]} name="Students" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Seat Utilization Breakdown */}
        <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-brand-600" /> Seat Utilization Overview
            </h2>
            <span className="text-xs font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
              {data.summary.overall_seat_utilization_rate}% Overall
            </span>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Total Available Seats</span>
              <span>{data.summary.available_seats} / {data.summary.total_seats}</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
              <div
                className="bg-brand-600 h-3 rounded-full"
                style={{ width: `${data.summary.overall_seat_utilization_rate}%` }}
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <div className="text-[10px] uppercase font-bold text-slate-400">Filled Seats</div>
                <div className="text-lg font-extrabold text-slate-900 mt-0.5">
                  {data.summary.total_seats - data.summary.available_seats}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <div className="text-[10px] uppercase font-bold text-slate-400">Allocated Candidates</div>
                <div className="text-lg font-extrabold text-emerald-700 mt-0.5">
                  {data.summary.allocated_students}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
