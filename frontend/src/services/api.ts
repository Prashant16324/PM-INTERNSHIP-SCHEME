import axios from 'axios';
import {
  APIResponse,
  PaginatedResponse,
  User,
  StudentProfile,
  StudentSkill,
  Company,
  Internship,
  Application,
  Allocation,
  Recommendation,
  SkillGapDetail,
  AnalyticsDashboardResponse,
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for session expiry handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't auto-redirect if already on login/register to allow error messages to show
      const path = window.location.pathname;
      if (!path.includes('/login') && !path.includes('/register')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (email: string, password: string) => {
    const res = await api.post<{ access_token: string; token_type: string; user: User }>('/auth/login', { email, password });
    return res.data;
  },
  register: async (payload: {
    email: string;
    password: string;
    full_name: string;
    phone_number?: string;
    college_name?: string;
    degree?: string;
    branch?: string;
    graduation_year?: number;
  }) => {
    const res = await api.post<APIResponse<User>>('/auth/register', payload);
    return res.data;
  },
  getMe: async () => {
    const res = await api.get<APIResponse<User>>('/auth/me');
    return res.data.data;
  },
};

export const studentsAPI = {
  getProfile: async () => {
    const res = await api.get<APIResponse<StudentProfile>>('/students/me/profile');
    return res.data.data;
  },
  updateProfile: async (data: Partial<StudentProfile>) => {
    const res = await api.put<APIResponse<StudentProfile>>('/students/me/profile', data);
    return res.data.data;
  },
  addSkill: async (skill_name: string, proficiency_level: string = 'INTERMEDIATE') => {
    const res = await api.post<APIResponse<StudentSkill>>('/students/me/skills', { skill_name, proficiency_level });
    return res.data.data;
  },
  removeSkill: async (skillId: number) => {
    const res = await api.delete<APIResponse<null>>(`/students/me/skills/${skillId}`);
    return res.data;
  },
  confirmBatchSkills: async (skills: string[]) => {
    const res = await api.post<APIResponse<StudentSkill[]>>('/students/me/skills/confirm-batch', skills);
    return res.data.data;
  },
  uploadResume: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post<APIResponse<{
      filename: string;
      file_size_bytes: number;
      extracted_text_preview: string;
      detected_skills: string[];
      detected_education?: string;
      message: string;
    }>>('/students/me/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data.data;
  },
  downloadResumeUrl: '/api/v1/students/me/resume/download',
};

export const internshipsAPI = {
  list: async (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    industry?: string;
    location?: string;
    min_stipend?: number;
  }) => {
    const res = await api.get<APIResponse<PaginatedResponse<Internship>>>('/internships', { params });
    return res.data.data;
  },
  getDetail: async (id: number) => {
    const res = await api.get<APIResponse<Internship>>(`/internships/${id}`);
    return res.data.data;
  },
  create: async (data: any) => {
    const res = await api.post<APIResponse<Internship>>('/internships', data);
    return res.data.data;
  },
  update: async (id: number, data: any) => {
    const res = await api.put<APIResponse<Internship>>(`/internships/${id}`, data);
    return res.data.data;
  },
  delete: async (id: number) => {
    const res = await api.delete<APIResponse<null>>(`/internships/${id}`);
    return res.data;
  },
  checkEligibility: async (id: number) => {
    const res = await api.get<APIResponse<{
      internship_id: number;
      is_eligible: boolean;
      reasons: string[];
      missing_mandatory_skills: string[];
      matched_mandatory_skills: string[];
      cgpa_satisfied: boolean;
      education_satisfied: boolean;
      deadline_valid: boolean;
    }>>(`/internships/${id}/eligibility`);
    return res.data.data;
  },
};

export const matchingAPI = {
  getRecommendations: async (weights?: {
    skill_weight?: number;
    education_weight?: number;
    location_weight?: number;
    industry_weight?: number;
  }) => {
    const res = await api.get<APIResponse<{
      student_id: number;
      total_recommendations: number;
      recommendations: Recommendation[];
    }>>('/matching/recommendations', { params: weights });
    return res.data.data;
  },
  getSkillGap: async (internshipId: number) => {
    const res = await api.get<APIResponse<SkillGapDetail>>(`/matching/skill-gap/${internshipId}`);
    return res.data.data;
  },
  recompute: async () => {
    const res = await api.post<APIResponse<{
      student_id: number;
      total_recommendations: number;
      recommendations: Recommendation[];
    }>>('/matching/recompute');
    return res.data.data;
  },
};

export const applicationsAPI = {
  apply: async (internship_id: number, cover_letter?: string) => {
    const res = await api.post<APIResponse<Application>>('/applications', { internship_id, cover_letter });
    return res.data.data;
  },
  getMyApplications: async () => {
    const res = await api.get<APIResponse<Application[]>>('/applications/me');
    return res.data.data;
  },
  withdraw: async (id: number) => {
    const res = await api.delete<APIResponse<Application>>(`/applications/${id}/withdraw`);
    return res.data.data;
  },
  getInternshipApplications: async (internshipId: number, params?: { status_filter?: string; page?: number }) => {
    const res = await api.get<APIResponse<PaginatedResponse<Application>>>(`/applications/internship/${internshipId}`, { params });
    return res.data.data;
  },
  updateStatus: async (id: number, status: string, note?: string) => {
    const res = await api.put<APIResponse<Application>>(`/applications/${id}/status`, { status, note });
    return res.data.data;
  },
};

export const allocationsAPI = {
  run: async (payload: { allocation_round?: number; min_score_threshold?: number; auto_confirm?: boolean }) => {
    const res = await api.post<APIResponse<{
      round: number;
      total_applications_evaluated: number;
      total_allocated_in_round: number;
      total_seats_filled: number;
      execution_time_seconds: number;
      allocations: Allocation[];
    }>>('/allocations/run', payload);
    return res.data.data;
  },
  list: async (params?: { round_number?: number; status_filter?: string; page?: number; page_size?: number }) => {
    const res = await api.get<APIResponse<PaginatedResponse<Allocation>>>('/allocations', { params });
    return res.data.data;
  },
  confirm: async (id: number) => {
    const res = await api.put<APIResponse<Allocation>>(`/allocations/${id}/confirm`);
    return res.data.data;
  },
  cancel: async (id: number, reason?: string) => {
    const res = await api.put<APIResponse<Allocation>>(`/allocations/${id}/cancel`, null, { params: { reason } });
    return res.data.data;
  },
  getMyAllocation: async () => {
    const res = await api.get<APIResponse<Allocation | null>>('/allocations/my');
    return res.data.data;
  },
};

export const analyticsAPI = {
  getDashboard: async () => {
    const res = await api.get<APIResponse<AnalyticsDashboardResponse>>('/analytics/dashboard');
    return res.data.data;
  },
};

export const companiesAPI = {
  list: async (params?: { page?: number; search?: string }) => {
    const res = await api.get<APIResponse<PaginatedResponse<Company>>>('/companies', { params });
    return res.data.data;
  },
  create: async (data: Partial<Company>) => {
    const res = await api.post<APIResponse<Company>>('/companies', data);
    return res.data.data;
  },
  update: async (id: number, data: Partial<Company>) => {
    const res = await api.put<APIResponse<Company>>(`/companies/${id}`, data);
    return res.data.data;
  },
};

export default api;
