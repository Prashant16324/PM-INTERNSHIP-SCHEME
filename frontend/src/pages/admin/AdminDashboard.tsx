import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI } from '../../services/api';
import { AnalyticsDashboardResponse } from '../../types';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Users,
  Building2,
  Briefcase,
  FileText,
  Award,
  TrendingUp,
  Cpu,
  ArrowRight,
  PieChart as PieChartIcon,
  BarChart3,
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
  Legend,
} from 'recharts';

const STATUS_COLORS: Record<string, string> = {
  SUBMITTED: '#3b82f6',
  UNDER_REVIEW: '#f59e0b',
  SHORTLISTED: '#6366f1',
  SELECTED: '#10b981',
  ALLOCATED: '#8b5cf6',
  REJECTED: '#ef4444',
  WITHDRAWN: '#94a3b8',
};

export const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await analyticsAPI.getDashboard();
        setData(res);
      } catch (err) {
        console.error('Failed to load admin analytics:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (isLoading || !data) {
    return <LoadingSpinner message="Calculating real-time administrative analytics..." />;
  }

  const { summary } = data;

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-brand-950 to-brand-900 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-xs font-semibold text-brand-300">
            <Cpu className="w-3.5 h-3.5" /> Administrative Control Center
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            PM Internship Scheme Administration
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl">
            Monitor real-time scheme metrics, evaluate candidate distributions, and orchestrate the automated AI allocation engine.
          </p>
        </div>

        <Link
          to="/admin/allocations"
          className="px-5 py-3 rounded-xl bg-brand-500 hover:bg-brand-400 text-white font-bold text-xs shadow-lg shadow-brand-500/30 transition flex items-center gap-2 shrink-0 self-start md:self-auto"
        >
          <Cpu className="w-4 h-4" /> Run Smart Allocation <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* KPI Cards Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-slate-400 uppercase">Students</div>
          <div className="text-xl font-extrabold text-slate-900">{summary.total_students}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-slate-400 uppercase">Companies</div>
          <div className="text-xl font-extrabold text-slate-900">{summary.total_companies}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-slate-400 uppercase">Internships</div>
          <div className="text-xl font-extrabold text-slate-900">{summary.total_internships}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-slate-400 uppercase">Applications</div>
          <div className="text-xl font-extrabold text-slate-900">{summary.total_applications}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-slate-400 uppercase">Total Seats</div>
          <div className="text-xl font-extrabold text-slate-900">{summary.total_seats}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-emerald-600 uppercase">Allocated</div>
          <div className="text-xl font-extrabold text-emerald-700">{summary.allocated_students}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <div className="text-[10px] font-bold text-brand-600 uppercase">Utilization</div>
          <div className="text-xl font-extrabold text-brand-700">{summary.overall_seat_utilization_rate}%</div>
        </div>
      </div>

      {/* Visual Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Applications by Status Chart */}
        <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <PieChartIcon className="w-4 h-4 text-brand-600" /> Applications by Status
            </h2>
            <span className="text-xs text-slate-400">{summary.total_applications} Total</span>
          </div>

          <div className="h-64 w-full">
            {data.applications_by_status.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No application data logged yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.applications_by_status}
                    dataKey="count"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} (${((percent ?? 0) * 100).toFixed(0)}%)`}
                    labelLine={false}
                  >
                    {data.applications_by_status.map((entry) => (
                      <Cell key={entry.status} fill={STATUS_COLORS[entry.status] || '#cbd5e1'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Industry Distribution Chart */}
        <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-brand-600" /> Opportunities by Industry
            </h2>
            <span className="text-xs text-slate-400">{data.industry_distribution.length} Sectors</span>
          </div>

          <div className="h-64 w-full">
            {data.industry_distribution.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No industry opportunities created yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.industry_distribution}>
                  <XAxis dataKey="industry" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="internship_count" fill="#0c8fe9" radius={[6, 6, 0, 0]} name="Internships" />
                  <Bar dataKey="total_seats" fill="#8b5cf6" radius={[6, 6, 0, 0]} name="Seats" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Seat Utilization by Internship Table */}
      <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Internship Seat Utilization</h2>
            <p className="text-xs text-slate-500">Real-time seat filling across partner organizations</p>
          </div>
          <Link to="/admin/internships" className="text-xs font-bold text-brand-600 hover:underline">
            Manage Internships
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Internship Role</th>
                <th className="py-3 px-4">Organization</th>
                <th className="py-3 px-4">Total Seats</th>
                <th className="py-3 px-4">Filled Seats</th>
                <th className="py-3 px-4">Utilization Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data.seat_utilization.map((item) => (
                <tr key={item.internship_id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3 px-4 font-bold text-slate-900">{item.title}</td>
                  <td className="py-3 px-4 text-slate-600">{item.company_name}</td>
                  <td className="py-3 px-4">{item.total_seats}</td>
                  <td className="py-3 px-4 font-bold text-slate-900">{item.allocated_seats}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-brand-600 h-2 rounded-full"
                          style={{ width: `${item.utilization_percentage}%` }}
                        />
                      </div>
                      <span className="font-extrabold text-xs text-brand-700">
                        {item.utilization_percentage}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
