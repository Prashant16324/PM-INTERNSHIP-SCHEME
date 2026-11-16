import React, { useState, useEffect } from 'react';
import { internshipsAPI, companiesAPI } from '../../services/api';
import { Internship, Company } from '../../types';
import { useToast } from '../../context/ToastContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Briefcase,
  Plus,
  Building2,
  MapPin,
  Users,
  Trash2,
  Calendar,
} from 'lucide-react';

export const AdminInternshipsPage: React.FC = () => {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // New Internship Form state
  const [formData, setFormData] = useState({
    title: '',
    company_id: 1,
    description: '',
    industry: 'Information Technology',
    location: 'Bangalore',
    duration_weeks: 12,
    stipend: 25000,
    total_seats: 5,
    min_cgpa: 7.0,
    preferred_education: 'B.Tech, BCA, MCA',
    skills: [
      { skill_name: 'Python', is_mandatory: true, weight: 1.0 },
      { skill_name: 'SQL', is_mandatory: false, weight: 1.0 },
    ],
  });

  const [skillInput, setSkillInput] = useState('');
  const [isMandatoryInput, setIsMandatoryInput] = useState(true);

  const { showToast } = useToast();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [intData, compData] = await Promise.all([
        internshipsAPI.list({ page_size: 50 }),
        companiesAPI.list({ page: 1 }),
      ]);
      setInternships(intData.items);
      setCompanies(compData.items);
      if (compData.items.length > 0) {
        setFormData((prev) => ({ ...prev, company_id: compData.items[0].id }));
      }
    } catch (err) {
      showToast('Failed to load internships registry', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddSkillToForm = () => {
    if (!skillInput.trim()) return;
    setFormData((prev) => ({
      ...prev,
      skills: [...prev.skills, { skill_name: skillInput.trim(), is_mandatory: isMandatoryInput, weight: 1.0 }],
    }));
    setSkillInput('');
  };

  const handleRemoveSkillFromForm = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index),
    }));
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await internshipsAPI.create(formData);
      showToast('Internship opportunity created successfully!', 'success');
      setShowCreateModal(false);
      fetchData();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to create internship';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this internship?')) return;
    try {
      await internshipsAPI.delete(id);
      showToast('Internship deleted successfully', 'info');
      fetchData();
    } catch (err) {
      showToast('Failed to delete internship', 'error');
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading scheme opportunities..." />;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Internship Management</h1>
          <p className="text-xs text-slate-500">
            Publish, edit, and configure available seats for partner organization postings.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add New Internship
        </button>
      </div>

      <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Title & Industry</th>
                <th className="py-3 px-4">Company</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Stipend</th>
                <th className="py-3 px-4">Available / Total Seats</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {internships.map((i) => (
                <tr key={i.id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    <div>{i.title}</div>
                    <span className="text-[10px] text-slate-400 font-normal">{i.industry}</span>
                  </td>

                  <td className="py-3.5 px-4 text-slate-600">
                    {i.company?.company_name || 'Partner Org'}
                  </td>

                  <td className="py-3.5 px-4 text-slate-600">{i.location}</td>

                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    ₹{i.stipend.toLocaleString()}
                  </td>

                  <td className="py-3.5 px-4 font-bold text-brand-700">
                    {i.available_seats} / {i.total_seats}
                  </td>

                  <td className="py-3.5 px-4">
                    <StatusBadge status={i.status} size="sm" />
                  </td>

                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => handleDelete(i.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                      title="Delete internship"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Internship Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in overflow-y-auto">
          <div className="w-full max-w-2xl p-6 sm:p-8 rounded-3xl bg-white shadow-2xl space-y-5 border border-slate-200 my-8">
            <h3 className="text-lg font-extrabold text-slate-900">Create Internship Opportunity</h3>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Internship Title *</label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="e.g. AI Research Intern"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Partner Company *</label>
                  <select
                    value={formData.company_id}
                    onChange={(e) => setFormData({ ...formData, company_id: parseInt(e.target.value) })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  >
                    {companies.map((c) => (
                      <option key={c.id} value={c.id}>{c.company_name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Role Description *</label>
                <textarea
                  rows={3}
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Detail the technical responsibilities and goals..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Industry</label>
                  <input
                    type="text"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Location</label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Total Seats</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.total_seats}
                    onChange={(e) => setFormData({ ...formData, total_seats: parseInt(e.target.value) || 1 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Monthly Stipend (INR)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.stipend}
                    onChange={(e) => setFormData({ ...formData, stipend: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Minimum CGPA</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    value={formData.min_cgpa}
                    onChange={(e) => setFormData({ ...formData, min_cgpa: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                </div>
              </div>

              {/* Skills Requirements Manager */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <label className="block text-xs font-bold text-slate-700">Required Skills</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    placeholder="Skill name (e.g. Python, Docker)"
                    className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium"
                  />
                  <label className="flex items-center gap-1.5 text-xs text-slate-600 px-3 bg-slate-50 rounded-xl border border-slate-200">
                    <input
                      type="checkbox"
                      checked={isMandatoryInput}
                      onChange={(e) => setIsMandatoryInput(e.target.checked)}
                      className="rounded text-brand-600"
                    />
                    Mandatory
                  </label>
                  <button
                    type="button"
                    onClick={handleAddSkillToForm}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-white font-bold text-xs"
                  >
                    Add
                  </button>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {formData.skills.map((s, idx) => (
                    <span
                      key={idx}
                      className={`text-xs px-2.5 py-1 rounded-lg flex items-center gap-1.5 ${
                        s.is_mandatory ? 'bg-amber-100 text-amber-900 font-bold' : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {s.skill_name} {s.is_mandatory && '(Mandatory)'}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkillFromForm(idx)}
                        className="hover:text-rose-600"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md transition disabled:opacity-60"
                >
                  {isSubmitting ? 'Creating...' : 'Publish Internship'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
