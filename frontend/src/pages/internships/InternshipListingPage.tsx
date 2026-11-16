import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { internshipsAPI } from '../../services/api';
import { Internship, PaginatedResponse } from '../../types';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  Search,
  Filter,
  Building2,
  MapPin,
  Calendar,
  Users,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export const InternshipListingPage: React.FC = () => {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [industry, setIndustry] = useState('');
  const [location, setLocation] = useState('');
  const [minStipend, setMinStipend] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  const fetchInternships = async () => {
    setIsLoading(true);
    try {
      const data = await internshipsAPI.list({
        page,
        page_size: 9,
        search: search.trim() || undefined,
        industry: industry || undefined,
        location: location || undefined,
        min_stipend: minStipend,
      });
      setInternships(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to load internships:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInternships();
  }, [page, industry, location, minStipend]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchInternships();
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Browse Internship Opportunities</h1>
        <p className="text-xs text-slate-500">
          Discover government scheme internships from certified industry partners with transparent seat availability.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by role, company, or technical keywords (e.g. Python, AI, Cloud)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:ring-2 focus:ring-brand-500/30"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-sm transition"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap gap-3 pt-2 border-t border-slate-100 text-xs">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-bold text-slate-600">Filters:</span>
          </div>

          <select
            value={industry}
            onChange={(e) => { setIndustry(e.target.value); setPage(1); }}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium"
          >
            <option value="">All Industries</option>
            <option value="Information Technology">Information Technology</option>
            <option value="Artificial Intelligence">Artificial Intelligence</option>
            <option value="Data Analytics">Data Analytics</option>
            <option value="Cloud Computing">Cloud Computing</option>
            <option value="Consulting">Consulting</option>
            <option value="Finance">Finance</option>
          </select>

          <select
            value={location}
            onChange={(e) => { setLocation(e.target.value); setPage(1); }}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium"
          >
            <option value="">All Locations</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Delhi">Delhi</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Pune">Pune</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Remote">Remote</option>
          </select>

          <select
            value={minStipend || ''}
            onChange={(e) => { setMinStipend(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium"
          >
            <option value="">Any Stipend</option>
            <option value="10000">₹10,000+ / mo</option>
            <option value="20000">₹20,000+ / mo</option>
            <option value="25000">₹25,000+ / mo</option>
          </select>
        </div>
      </div>

      {/* Internships Grid */}
      {isLoading ? (
        <LoadingSpinner message="Searching available internships..." />
      ) : internships.length === 0 ? (
        <div className="py-16 text-center space-y-3 bg-white rounded-2xl border border-slate-200">
          <Search className="w-8 h-8 text-slate-400 mx-auto" />
          <div className="text-sm font-bold text-slate-800">No matching internships found</div>
          <p className="text-xs text-slate-500">Try adjusting your keyword search or clearing some filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {internships.map((internship) => (
            <div
              key={internship.id}
              className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md hover:border-brand-300 transition flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                    {internship.industry}
                  </span>
                  <StatusBadge status={internship.status} size="sm" />
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-900 line-clamp-1">{internship.title}</h3>
                  <p className="text-xs text-slate-500 font-medium flex items-center gap-1.5 mt-0.5">
                    <Building2 className="w-3.5 h-3.5" />
                    {internship.company?.company_name || 'Partner Company'}
                  </p>
                </div>

                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                  {internship.description}
                </p>

                <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-600 pt-1">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-slate-400" /> {internship.location}
                  </span>
                  <span className="font-semibold text-slate-900">
                    ₹{internship.stipend.toLocaleString()}/mo
                  </span>
                  <span className="flex items-center gap-1 text-brand-700 font-bold">
                    <Users className="w-3 h-3" />
                    {internship.available_seats} / {internship.total_seats} Seats
                  </span>
                </div>

                {/* Skills Preview */}
                <div className="flex flex-wrap gap-1 pt-1">
                  {internship.skills?.slice(0, 4).map((s) => (
                    <span
                      key={s.id}
                      className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                        s.is_mandatory
                          ? 'bg-amber-50 text-amber-800 border border-amber-200'
                          : 'bg-slate-50 text-slate-600 border border-slate-100'
                      }`}
                    >
                      {s.skill_name}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <Link
                  to={`/skill-gap/${internship.id}`}
                  className="text-[11px] font-bold text-brand-600 hover:underline flex items-center gap-1"
                >
                  <Sparkles className="w-3 h-3 text-brand-500" /> Skill Gap
                </Link>

                <Link
                  to={`/internships/${internship.id}`}
                  className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs flex items-center gap-1.5 transition"
                >
                  Details <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
