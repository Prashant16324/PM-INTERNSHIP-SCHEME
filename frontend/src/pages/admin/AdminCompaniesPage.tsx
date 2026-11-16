import React, { useState, useEffect } from 'react';
import { companiesAPI } from '../../services/api';
import { Company } from '../../types';
import { useToast } from '../../context/ToastContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { Building2, Plus, MapPin, Globe, CheckCircle2, ShieldCheck } from 'lucide-react';

export const AdminCompaniesPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    company_name: '',
    industry: 'Information Technology',
    location: 'Bangalore',
    website: 'https://',
    description: '',
  });

  const { showToast } = useToast();

  const fetchCompanies = async () => {
    setIsLoading(true);
    try {
      const data = await companiesAPI.list({ page: 1 });
      setCompanies(data.items);
    } catch (err) {
      showToast('Failed to load companies directory', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await companiesAPI.create(formData);
      showToast('Partner company added successfully', 'success');
      setShowModal(false);
      setFormData({ company_name: '', industry: 'Information Technology', location: 'Bangalore', website: 'https://', description: '' });
      fetchCompanies();
    } catch (err) {
      showToast('Failed to register company', 'error');
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading partner organizations..." />;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Partner Organizations</h1>
          <p className="text-xs text-slate-500">
            Registered corporate and public sector employers participating in the PM Internship Scheme.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add Partner Company
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {companies.map((company) => (
          <div
            key={company.id}
            className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4 hover:border-brand-300 transition"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold text-sm">
                <Building2 className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-600" /> Verified Partner
              </span>
            </div>

            <div>
              <h3 className="text-base font-bold text-slate-900">{company.company_name}</h3>
              <p className="text-xs text-brand-600 font-semibold">{company.industry}</p>
            </div>

            <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
              {company.description || 'Approved partner organization participating in the scheme allocation rounds.'}
            </p>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" /> {company.location}
              </span>
              {company.website && (
                <a
                  href={company.website}
                  target="_blank"
                  rel="noreferrer"
                  className="text-brand-600 hover:underline flex items-center gap-1 font-semibold"
                >
                  <Globe className="w-3.5 h-3.5" /> Portal
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Add Company Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in">
          <div className="w-full max-w-md p-6 rounded-3xl bg-white shadow-2xl space-y-5 border border-slate-200">
            <h3 className="text-lg font-extrabold text-slate-900">Add Partner Company</h3>

            <form onSubmit={handleCreateCompany} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Company Name *</label>
                <input
                  type="text"
                  required
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  placeholder="e.g. Larsen & Toubro"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Industry Sector *</label>
                <input
                  type="text"
                  required
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  placeholder="e.g. Engineering & IT"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Headquarters / Location *</label>
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g. Mumbai, India"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Website</label>
                <input
                  type="url"
                  value={formData.website}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  placeholder="https://company.com"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md transition"
                >
                  Register Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
