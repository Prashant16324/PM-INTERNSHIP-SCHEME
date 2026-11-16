import React from 'react';
import {
  CheckCircle,
  Clock,
  XCircle,
  Award,
  AlertCircle,
  FileCheck,
} from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = status.toUpperCase().replace(/\s+/g, '_');

  let style = 'bg-slate-100 text-slate-700 border-slate-200';
  let icon = <Clock className="w-3.5 h-3.5" />;
  let label = status;

  switch (norm) {
    case 'SUBMITTED':
      style = 'bg-blue-50 text-blue-700 border-blue-200';
      icon = <Clock className="w-3.5 h-3.5" />;
      label = 'Submitted';
      break;
    case 'UNDER_REVIEW':
      style = 'bg-amber-50 text-amber-800 border-amber-200';
      icon = <Clock className="w-3.5 h-3.5" />;
      label = 'Under Review';
      break;
    case 'SHORTLISTED':
      style = 'bg-indigo-50 text-indigo-700 border-indigo-200';
      icon = <FileCheck className="w-3.5 h-3.5" />;
      label = 'Shortlisted';
      break;
    case 'SELECTED':
    case 'CONFIRMED':
      style = 'bg-emerald-50 text-emerald-800 border-emerald-200';
      icon = <CheckCircle className="w-3.5 h-3.5" />;
      label = norm === 'CONFIRMED' ? 'Confirmed' : 'Selected';
      break;
    case 'ALLOCATED':
    case 'PROVISIONAL':
      style = 'bg-purple-50 text-purple-800 border-purple-200';
      icon = <Award className="w-3.5 h-3.5" />;
      label = norm === 'PROVISIONAL' ? 'Provisional Allocation' : 'Allocated';
      break;
    case 'REJECTED':
    case 'CANCELLED':
      style = 'bg-rose-50 text-rose-800 border-rose-200';
      icon = <XCircle className="w-3.5 h-3.5" />;
      label = norm === 'CANCELLED' ? 'Cancelled' : 'Rejected';
      break;
    case 'WITHDRAWN':
      style = 'bg-slate-100 text-slate-600 border-slate-200';
      icon = <AlertCircle className="w-3.5 h-3.5" />;
      label = 'Withdrawn';
      break;
    case 'OPEN':
      style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      icon = <CheckCircle className="w-3.5 h-3.5" />;
      label = 'Open';
      break;
    case 'CLOSED':
      style = 'bg-slate-100 text-slate-600 border-slate-200';
      icon = <XCircle className="w-3.5 h-3.5" />;
      label = 'Closed';
      break;
  }

  const sizeClasses = size === 'sm' ? 'text-[10px] px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full border shadow-2xs ${sizeClasses} ${style}`}
    >
      {icon}
      <span>{label}</span>
    </span>
  );
};
