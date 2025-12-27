import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ResumesListPage } from './pages/ResumesListPage';
import { ResumeDetailPage } from './pages/ResumeDetailPage';
import { ResumeVacanciesPage } from './pages/ResumeVacanciesPage';
import { ResumeResponsesPage } from './pages/ResumeResponsesPage';
import { HhAuthSettingsPage } from './pages/HhAuthSettingsPage';
import { ProfilePage } from './pages/ProfilePage';
import { PlansPage } from './pages/PlansPage';
import { StatisticsPage } from './pages/StatisticsPage';
import { ChatsListPage } from './pages/ChatsListPage';
import { ChatDetailPage } from './pages/ChatDetailPage';
import { EventsPage } from './pages/EventsPage';
import { MainLayout } from './components/Layout/MainLayout';
import { ProtectedRoute } from './components/Layout/ProtectedRoute';
import { useAuthStore } from './stores/authStore';

function App() {
  const { token } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page - публичная */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Auth pages */}
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
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ProfilePage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/plans"
          element={
            <ProtectedRoute>
              <MainLayout>
                <PlansPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/statistics"
          element={
            <ProtectedRoute>
              <MainLayout>
                <StatisticsPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/events"
          element={
            <ProtectedRoute>
              <MainLayout>
                <EventsPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/chats"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ChatsListPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/chats/:chatId"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ChatDetailPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        {/* Редиректы со старых маршрутов */}
        <Route path="/vacancies" element={<Navigate to="/resumes" replace />} />
        <Route path="/vacancies/:id" element={<Navigate to="/resumes" replace />} />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to={token ? '/resumes' : '/'} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
