export type UserRole = 'STUDENT' | 'ADMIN' | 'COMPANY';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface StudentSkill {
  id: number;
  student_profile_id: number;
  skill_name: string;
  proficiency_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  source: string;
  created_at: string;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  phone_number?: string;
  college_name?: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  cgpa?: number;
  profile_completion_percentage: number;
  preferred_locations: string[];
  preferred_industries: string[];
  resume_url?: string;
  bio?: string;
  skills: StudentSkill[];
  user?: User;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: number;
  user_id?: number;
  company_name: string;
  industry: string;
  description?: string;
  website?: string;
  location: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface InternshipSkill {
  id: number;
  internship_id: number;
  skill_name: string;
  is_mandatory: boolean;
  weight: number;
}

export type InternshipStatus = 'OPEN' | 'CLOSED' | 'ARCHIVED';

export interface Internship {
  id: number;
  company_id: number;
  title: string;
  description: string;
  location: string;
  industry: string;
  duration_weeks: number;
  stipend: number;
  total_seats: number;
  available_seats: number;
  min_cgpa: number;
  preferred_education?: string;
  eligibility_criteria?: string;
  application_deadline?: string;
  status: InternshipStatus;
  skills: InternshipSkill[];
  company?: Company;
  created_at: string;
  updated_at: string;
}

export type ApplicationStatus =
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'SHORTLISTED'
  | 'REJECTED'
  | 'SELECTED'
  | 'ALLOCATED'
  | 'WITHDRAWN';

export interface Application {
  id: number;
  student_profile_id: number;
  internship_id: number;
  status: ApplicationStatus;
  match_score: number;
  cover_letter?: string;
  applied_at: string;
  updated_at: string;
  internship?: Internship;
  student_profile?: StudentProfile;
}

export type AllocationStatus = 'PROVISIONAL' | 'CONFIRMED' | 'CANCELLED' | 'REJECTED_BY_STUDENT';

export interface Allocation {
  id: number;
  application_id: number;
  student_profile_id: number;
  internship_id: number;
  allocation_round: number;
  allocated_by_user_id?: number;
  allocation_score: number;
  status: AllocationStatus;
  allocation_reason?: string;
  allocated_at: string;
  confirmed_at?: string;
  internship?: Internship;
  student_profile?: StudentProfile;
}

export interface Recommendation {
  internship_id: number;
  internship_title: string;
  company_name: string;
  location: string;
  industry: string;
  stipend: number;
  overall_score: number;
  skill_score: number;
  education_score: number;
  location_score: number;
  industry_score: number;
  is_eligible: boolean;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
  generated_at: string;
}

export interface LearningTopicSuggestion {
  skill_name: string;
  suggested_topics: string[];
  estimated_hours: number;
}

export interface SkillGapDetail {
  internship_id: number;
  internship_title: string;
  company_name: string;
  student_skills: string[];
  required_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  skill_match_percentage: number;
  learning_recommendations: LearningTopicSuggestion[];
}

export interface AdminDashboardStats {
  total_students: number;
  total_companies: number;
  total_internships: number;
  total_applications: number;
  total_seats: number;
  available_seats: number;
  allocated_students: number;
  pending_applications: number;
  overall_seat_utilization_rate: number;
}

export interface AnalyticsDashboardResponse {
  summary: AdminDashboardStats;
  applications_by_status: { status: string; count: number }[];
  industry_distribution: { industry: string; internship_count: number; total_seats: number }[];
  top_skills_distribution: { skill_name: string; student_count: number }[];
  seat_utilization: {
    internship_id: number;
    title: string;
    company_name: string;
    total_seats: number;
    allocated_seats: number;
    utilization_percentage: number;
  }[];
}

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
