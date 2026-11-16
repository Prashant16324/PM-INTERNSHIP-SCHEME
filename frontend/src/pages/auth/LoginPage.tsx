import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { authAPI } from '../../services/api';
import { Sparkles, Lock, Mail, ArrowRight, ShieldCheck, UserCircle2 } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      showToast('Please enter both email and password', 'warning');
      return;
    }

    setIsLoading(true);
    try {
      const data = await authAPI.login(email, password);
      login(data.access_token, data.user);
      showToast(`Welcome back, ${data.user.full_name}!`, 'success');

      const redirect = location.state?.from?.pathname || (data.user.role === 'ADMIN' ? '/admin/dashboard' : '/dashboard');
      navigate(redirect, { replace: true });
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Authentication failed. Please verify your credentials.';
      showToast(detail, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const fillAdminCredentials = () => {
    setEmail('admin@pm-internship.edu.in');
    setPassword('AdminSecurePass@2026');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-10 px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-700 to-brand-500 items-center justify-center text-white shadow-lg shadow-brand-500/20 mb-1">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Portal Sign In</h1>
          <p className="text-xs text-slate-500 font-medium">
            AI-Based Smart Allocation Engine for PM Internship Scheme
          </p>
        </div>

        <div className="p-8 rounded-3xl bg-white border border-slate-200/80 shadow-xl shadow-slate-200/40 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@university.edu.in"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Verifying Credentials...
                </>
              ) : (
                <>
                  Sign In to Account <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Fill Buttons */}
          <div className="pt-4 border-t border-slate-100 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center">
              Quick Demo Fill
            </div>
            <button
              type="button"
              onClick={fillAdminCredentials}
              className="w-full py-2 px-3 rounded-lg border border-purple-200 bg-purple-50 hover:bg-purple-100/70 text-purple-700 text-xs font-semibold flex items-center justify-center gap-2 transition"
            >
              <ShieldCheck className="w-4 h-4 text-purple-600" /> Use System Admin Credentials
            </button>
          </div>

          <div className="text-center pt-2 text-xs text-slate-500">
            Don't have a student account?{' '}
            <Link to="/register" className="font-bold text-brand-600 hover:underline">
              Register here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
