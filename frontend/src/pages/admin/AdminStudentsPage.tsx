import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../../services/api';
import { Users, GraduationCap, Award, Search } from 'lucide-react';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const AdminStudentsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Registered Candidates Directory</h1>
        <p className="text-xs text-slate-500">
          Manage enrolled students, academic credentials, and view AI recommendation profiles.
        </p>
      </div>

      <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search students by name, email, or college..."
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-xs font-medium"
            />
          </div>
        </div>

        <div className="py-12 text-center space-y-3">
          <GraduationCap className="w-12 h-12 text-slate-300 mx-auto" />
          <div className="text-sm font-bold text-slate-800">Student Directory View</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Student registrations and profile vectors are automatically populated as candidates enroll and upload resumes.
          </p>
        </div>
      </div>
    </div>
  );
};
