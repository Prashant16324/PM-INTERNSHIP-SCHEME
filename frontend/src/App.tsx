import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/common/ProtectedRoute';

// Public & Auth Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { NotFoundPage } from './pages/NotFoundPage';

// Student Pages
import { StudentDashboard } from './pages/student/StudentDashboard';
import { StudentProfilePage } from './pages/student/StudentProfilePage';
import { ResumeUploadPage } from './pages/student/ResumeUploadPage';
import { RecommendationsPage } from './pages/student/RecommendationsPage';
import { SkillGapAnalysisPage } from './pages/student/SkillGapAnalysisPage';
import { ApplicationsPage } from './pages/student/ApplicationsPage';
import { AllocationResultPage } from './pages/student/AllocationResultPage';

// Internship Catalog Pages
import { InternshipListingPage } from './pages/internships/InternshipListingPage';
import { InternshipDetailPage } from './pages/internships/InternshipDetailPage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { AdminAllocationsPage } from './pages/admin/AdminAllocationsPage';
import { AdminApplicationsPage } from './pages/admin/AdminApplicationsPage';
import { AdminInternshipsPage } from './pages/admin/AdminInternshipsPage';
import { AdminCompaniesPage } from './pages/admin/AdminCompaniesPage';
import { AdminStudentsPage } from './pages/admin/AdminStudentsPage';
import { AdminAnalyticsPage } from './pages/admin/AdminAnalyticsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route element={<AppLayout />}>
              {/* 1. Landing Page */}
              <Route path="/" element={<LandingPage />} />

              {/* 2. Login Page */}
              <Route path="/login" element={<LoginPage />} />

              {/* 3. Student Registration Page */}
              <Route path="/register" element={<RegisterPage />} />

              {/* 7. Internship Listing Page (Public / Browse) */}
              <Route path="/internships" element={<InternshipListingPage />} />

              {/* 8. Internship Details Page */}
              <Route path="/internships/:id" element={<InternshipDetailPage />} />

              {/* Protected Student Routes */}
              {/* 4. Student Dashboard */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT']}>
                    <StudentDashboard />
                  </ProtectedRoute>
                }
              />

              {/* 5. Student Profile Page */}
              <Route
                path="/profile"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT']}>
                    <StudentProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* 6. Resume Upload Page */}
              <Route
                path="/resume"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT']}>
                    <ResumeUploadPage />
                  </ProtectedRoute>
                }
              />

              {/* 9. AI Recommendations Page */}
              <Route
                path="/recommendations"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT']}>
                    <RecommendationsPage />
                  </ProtectedRoute>
                }
              />

              {/* 10. Skill Gap Analysis Page */}
              <Route
                path="/skill-gap/:id"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT', 'ADMIN']}>
                    <SkillGapAnalysisPage />
                  </ProtectedRoute>
                }
              />

              {/* 11. Applications Page */}
              <Route
                path="/applications"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT']}>
                    <ApplicationsPage />
                  </ProtectedRoute>
                }
              />

              {/* 12. Allocation Results Page */}
              <Route
                path="/allocation"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT']}>
                    <AllocationResultPage />
                  </ProtectedRoute>
                }
              />

              {/* Protected Admin Routes */}
              {/* 13. Admin Dashboard */}
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />

              {/* 14. Student Management Page */}
              <Route
                path="/admin/students"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminStudentsPage />
                  </ProtectedRoute>
                }
              />

              {/* 15. Company Management Page */}
              <Route
                path="/admin/companies"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminCompaniesPage />
                  </ProtectedRoute>
                }
              />

              {/* 16. Internship Management Page */}
              <Route
                path="/admin/internships"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminInternshipsPage />
                  </ProtectedRoute>
                }
              />

              {/* 17. Application Management Page */}
              <Route
                path="/admin/applications"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminApplicationsPage />
                  </ProtectedRoute>
                }
              />

              {/* 18. Allocation Management Page */}
              <Route
                path="/admin/allocations"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminAllocationsPage />
                  </ProtectedRoute>
                }
              />

              {/* 19. Analytics and Reports Page */}
              <Route
                path="/admin/analytics"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminAnalyticsPage />
                  </ProtectedRoute>
                }
              />

              {/* 20. Not Found Page */}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
