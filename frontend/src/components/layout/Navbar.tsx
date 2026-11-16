import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Sparkles, LogOut, UserCircle2, ShieldCheck, Briefcase } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-600 to-brand-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-slate-900 tracking-tight text-base sm:text-lg">
                PM Internship Scheme
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                AI Prototype
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium hidden sm:block">
              AI-Based Smart Allocation & Recommendation Engine
            </p>
          </div>
        </Link>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-100/80 border border-slate-200/80">
                <div className="w-8 h-8 rounded-lg bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-xs uppercase">
                  {user.full_name.substring(0, 2)}
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-xs font-bold text-slate-800 leading-tight">
                    {user.full_name}
                  </div>
                  <div className="text-[10px] font-medium text-slate-500 flex items-center gap-1">
                    {user.role === 'ADMIN' ? (
                      <span className="text-purple-600 font-semibold flex items-center gap-0.5">
                        <ShieldCheck className="w-3 h-3" /> Administrator
                      </span>
                    ) : user.role === 'COMPANY' ? (
                      <span className="text-emerald-600 font-semibold flex items-center gap-0.5">
                        <Briefcase className="w-3 h-3" /> Employer
                      </span>
                    ) : (
                      <span className="text-brand-600 font-semibold flex items-center gap-0.5">
                        <UserCircle2 className="w-3 h-3" /> Student
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <button
                onClick={handleLogout}
                title="Log out"
                className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition border border-transparent hover:border-rose-200"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="text-xs font-semibold px-4 py-2 text-slate-700 hover:text-brand-600 hover:bg-slate-100 rounded-lg transition"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="text-xs font-semibold px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg shadow-sm shadow-brand-500/20 transition"
              >
                Student Registration
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
