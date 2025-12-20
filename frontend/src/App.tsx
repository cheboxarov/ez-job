import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ResumesListPage } from './pages/ResumesListPage';
import { ResumeDetailPage } from './pages/ResumeDetailPage';
import { ResumeVacanciesPage } from './pages/ResumeVacanciesPage';
import { ResumeResponsesPage } from './pages/ResumeResponsesPage';
import { HhAuthSettingsPage } from './pages/HhAuthSettingsPage';
import { MainLayout } from './components/Layout/MainLayout';
import { ProtectedRoute } from './components/Layout/ProtectedRoute';
import { useAuthStore } from './stores/authStore';

function App() {
  const { token } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        {/* Новые маршруты для резюме */}
        <Route
          path="/resumes"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ResumesListPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resumes/:resumeId"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ResumeDetailPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resumes/:resumeId/vacancies"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ResumeVacanciesPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resumes/:resumeId/responses"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ResumeResponsesPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/hh-auth"
          element={
            <ProtectedRoute>
              <MainLayout>
                <HhAuthSettingsPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        {/* Редиректы со старых маршрутов */}
        <Route path="/vacancies" element={<Navigate to="/resumes" replace />} />
        <Route path="/vacancies/:id" element={<Navigate to="/resumes" replace />} />
        <Route path="/profile" element={<Navigate to="/resumes" replace />} />
        <Route
          path="/"
          element={<Navigate to={token ? '/resumes' : '/login'} replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
