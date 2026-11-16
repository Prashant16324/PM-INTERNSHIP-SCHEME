import React, { useState, useEffect } from 'react';
import { studentsAPI } from '../../services/api';
import { StudentProfile, StudentSkill } from '../../types';
import { useToast } from '../../context/ToastContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  UserCircle2,
  GraduationCap,
  Sparkles,
  Plus,
  Trash2,
  Save,
  CheckCircle2,
  MapPin,
  Building,
} from 'lucide-react';

export const StudentProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillLevel, setNewSkillLevel] = useState<'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'>('INTERMEDIATE');

  // Preference string buffers
  const [locationsInput, setLocationsInput] = useState('');
  const [industriesInput, setIndustriesInput] = useState('');

  const { showToast } = useToast();

  const loadProfile = async () => {
    try {
      const data = await studentsAPI.getProfile();
      setProfile(data);
      setLocationsInput(data.preferred_locations?.join(', ') || '');
      setIndustriesInput(data.preferred_industries?.join(', ') || '');
    } catch (err) {
      showToast('Failed to load profile details', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfile((prev) => (prev ? {
      ...prev,
      [name]: name === 'cgpa' ? parseFloat(value) || 0 : name === 'graduation_year' ? parseInt(value) || 2026 : value,
    } : null));
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;

    setIsSaving(true);
    try {
      const locList = locationsInput.split(',').map((s) => s.trim()).filter(Boolean);
      const indList = industriesInput.split(',').map((s) => s.trim()).filter(Boolean);

      const updated = await studentsAPI.updateProfile({
        phone_number: profile.phone_number,
        college_name: profile.college_name,
        degree: profile.degree,
        branch: profile.branch,
        graduation_year: profile.graduation_year,
        cgpa: profile.cgpa,
        bio: profile.bio,
        preferred_locations: locList,
        preferred_industries: indList,
      });

      setProfile(updated);
      showToast('Profile updated successfully!', 'success');
    } catch (err: any) {
      showToast('Failed to update profile', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;

    try {
      const added = await studentsAPI.addSkill(newSkillName.trim(), newSkillLevel);
      setProfile((prev) => prev ? { ...prev, skills: [...prev.skills, added] } : null);
      setNewSkillName('');
      showToast(`Skill '${added.skill_name}' added to profile`, 'success');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to add skill';
      showToast(msg, 'warning');
    }
  };

  const handleDeleteSkill = async (skillId: number) => {
    try {
      await studentsAPI.removeSkill(skillId);
      setProfile((prev) => prev ? {
        ...prev,
        skills: prev.skills.filter((s) => s.id !== skillId),
      } : null);
      showToast('Skill removed', 'info');
    } catch (err) {
      showToast('Failed to remove skill', 'error');
    }
  };

  if (isLoading || !profile) {
    return <LoadingSpinner message="Loading candidate profile..." />;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Candidate Profile & Skills</h1>
        <p className="text-xs text-slate-500">
          The AI matching engine evaluates your academic credentials, technical skills, and preferences to recommend optimal scheme placements.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details Form */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleSaveProfile} className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Academic & Personal Details</h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">College / University</label>
                <input
                  type="text"
                  name="college_name"
                  value={profile.college_name || ''}
                  onChange={handleProfileChange}
                  placeholder="e.g. Delhi Technological University"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Phone Number</label>
                <input
                  type="text"
                  name="phone_number"
                  value={profile.phone_number || ''}
                  onChange={handleProfileChange}
                  placeholder="9876543210"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Degree</label>
                <select
                  name="degree"
                  value={profile.degree || 'B.Tech'}
                  onChange={handleProfileChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                >
                  <option value="B.Tech">B.Tech</option>
                  <option value="M.Tech">M.Tech</option>
                  <option value="BCA">BCA</option>
                  <option value="MCA">MCA</option>
                  <option value="B.Sc">B.Sc</option>
                  <option value="M.Sc">M.Sc</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Branch</label>
                <input
                  type="text"
                  name="branch"
                  value={profile.branch || ''}
                  onChange={handleProfileChange}
                  placeholder="e.g. Computer Science"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Cumulative CGPA (10.0)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  name="cgpa"
                  value={profile.cgpa ?? ''}
                  onChange={handleProfileChange}
                  placeholder="8.5"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-brand-700"
                />
              </div>
            </div>

            <div className="space-y-4 pt-2 border-t border-slate-100">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Internship Preferences</h2>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Preferred Locations (comma separated)</label>
                <input
                  type="text"
                  value={locationsInput}
                  onChange={(e) => setLocationsInput(e.target.value)}
                  placeholder="Bangalore, Delhi, Pune, Remote"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Preferred Industries (comma separated)</label>
                <input
                  type="text"
                  value={industriesInput}
                  onChange={(e) => setIndustriesInput(e.target.value)}
                  placeholder="Information Technology, Artificial Intelligence, Finance"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Professional Summary / Bio</label>
                <textarea
                  name="bio"
                  rows={3}
                  value={profile.bio || ''}
                  onChange={handleProfileChange}
                  placeholder="Summarize your key engineering projects, strengths, and career aspirations..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSaving}
              className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-sm flex items-center gap-2 transition disabled:opacity-60"
            >
              <Save className="w-4 h-4" /> {isSaving ? 'Saving Changes...' : 'Save Profile Changes'}
            </button>
          </form>
        </div>

        {/* Skills Manager Sidebar Card */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center justify-between">
                <span>Technical Skills</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 font-extrabold">
                  {profile.skills?.length || 0}
                </span>
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Evaluated against internship requirements for matching.
              </p>
            </div>

            {/* Add Skill Form */}
            <form onSubmit={handleAddSkill} className="space-y-2">
              <input
                type="text"
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                placeholder="e.g. Python, Docker, React"
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium"
              />
              <div className="flex gap-2">
                <select
                  value={newSkillLevel}
                  onChange={(e: any) => setNewSkillLevel(e.target.value)}
                  className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium"
                >
                  <option value="BEGINNER">Beginner</option>
                  <option value="INTERMEDIATE">Intermediate</option>
                  <option value="ADVANCED">Advanced</option>
                </select>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs flex items-center gap-1 shadow-sm transition"
                >
                  <Plus className="w-4 h-4" /> Add
                </button>
              </div>
            </form>

            {/* Current Skills List */}
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {profile.skills?.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-400">
                  No skills listed yet. Add skills or upload your resume to extract them automatically.
                </div>
              ) : (
                profile.skills?.map((s) => (
                  <div
                    key={s.id}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs"
                  >
                    <div>
                      <div className="font-bold text-slate-800">{s.skill_name}</div>
                      <div className="text-[10px] text-slate-400 flex items-center gap-1">
                        <span className="font-semibold text-brand-600">{s.proficiency_level}</span>
                        <span>•</span>
                        <span>{s.source === 'RESUME_EXTRACTED' ? 'Parsed from Resume' : 'Manual Entry'}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteSkill(s.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                      title="Remove skill"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
