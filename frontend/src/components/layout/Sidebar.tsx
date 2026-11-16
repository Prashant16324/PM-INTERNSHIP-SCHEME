import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Search,
  Sparkles,
  FileText,
  Award,
  UserCircle2,
  UploadCloud,
  ShieldCheck,
  Building2,
  Users,
  Briefcase,
  Cpu,
  BarChart3,
  BookOpen,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const role = user?.role;

  const studentLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/internships', label: 'Browse Internships', icon: Search },
    { to: '/recommendations', label: 'AI Recommendations', icon: Sparkles },
    { to: '/applications', label: 'My Applications', icon: FileText },
    { to: '/allocation', label: 'Allocation Result', icon: Award },
    { to: '/profile', label: 'Profile & Skills', icon: UserCircle2 },
    { to: '/resume', label: 'Resume & NLP Parser', icon: UploadCloud },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Admin Overview', icon: LayoutDashboard },
    { to: '/admin/allocations', label: 'Smart Allocation Engine', icon: Cpu },
    { to: '/admin/applications', label: 'All Applications', icon: FileText },
    { to: '/admin/internships', label: 'Manage Internships', icon: Briefcase },
    { to: '/admin/companies', label: 'Partner Companies', icon: Building2 },
    { to: '/admin/students', label: 'Student Directory', icon: Users },
    { to: '/admin/analytics', label: 'Analytics & Reports', icon: BarChart3 },
  ];

  const links = role === 'ADMIN' ? adminLinks : studentLinks;

  return (
    <aside className="w-64 border-r border-slate-200 bg-white min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 hidden lg:flex">
      <div className="space-y-6">
        <div>
          <div className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            {role === 'ADMIN' ? 'Administration Portal' : 'Student Navigation'}
          </div>
          <nav className="space-y-1">
            {links.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-brand-50 text-brand-700 font-bold border border-brand-100 shadow-sm'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{link.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Academic Disclaimer Callout */}
      <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] text-slate-500 leading-relaxed">
        <div className="flex items-center gap-1.5 font-bold text-slate-700 mb-1">
          <BookOpen className="w-3.5 h-3.5 text-brand-600" />
          Academic Prototype
        </div>
        Designed for demonstration & evaluation of explainable AI matching algorithms.
      </div>
    </aside>
  );
};
