import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ResumesListPage } from './pages/ResumesListPage';
import { ResumeDetailPage } from './pages/ResumeDetailPage';
import { ResumeAutolikePage } from './pages/ResumeAutolikePage';
import { ResumeVacanciesPage } from './pages/ResumeVacanciesPage';
import { ResumeResponsesPage } from './pages/ResumeResponsesPage';
import { HhAuthSettingsPage } from './pages/HhAuthSettingsPage';
import { TelegramSettingsPage } from './pages/TelegramSettingsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ProfilePage } from './pages/ProfilePage';
import { PlansPage } from './pages/PlansPage';
import { StatisticsPage } from './pages/StatisticsPage';
import { ChatsListPage } from './pages/ChatsListPage';
import { ChatDetailPage } from './pages/ChatDetailPage';
import { EventsPage } from './pages/EventsPage';
import { MainLayout } from './components/Layout/MainLayout';
import { ProtectedRoute } from './components/Layout/ProtectedRoute';
import { AdminLayout } from './components/Layout/AdminLayout';
import { AdminProtectedRoute } from './components/Layout/AdminProtectedRoute';
import { AdminUsersPage } from './pages/admin/AdminUsersPage';
import { AdminUserDetailPage } from './pages/admin/AdminUserDetailPage';
import { AdminPlansPage } from './pages/admin/AdminPlansPage';
import { AdminLlmCallsPage } from './pages/admin/AdminLlmCallsPage';
import { AdminMetricsDashboardPage } from './pages/admin/AdminMetricsDashboardPage';
import { useAuthStore } from './stores/authStore';
import { trackPageView } from './utils/yandex-metrika';

// ID счетчика Яндекс.Метрики
const YANDEX_METRIKA_ID = 106056695;

// Компонент для отслеживания навигации в SPA
function PageTracker() {
  const location = useLocation();

  useEffect(() => {
    // Отслеживаем просмотр страницы при изменении маршрута
    trackPageView(YANDEX_METRIKA_ID, location.pathname + location.search);
  }, [location]);

  return null;
}

function App() {
  const { token, initialize } = useAuthStore();

  // Инициализируем приложение при монтировании
  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <BrowserRouter>
      <PageTracker />
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
          path="/resumes/:resumeId/autolike"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ResumeAutolikePage />
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
          path="/settings"
          element={
            <ProtectedRoute>
              <MainLayout>
                <SettingsPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/telegram"
          element={
            <ProtectedRoute>
              <MainLayout>
                <Navigate to="/settings" replace />
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
        {/* Админ-панель */}
        <Route
          path="/admin"
          element={
            <AdminProtectedRoute>
              <AdminLayout>
                <Navigate to="/admin/users" replace />
              </AdminLayout>
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <AdminProtectedRoute>
              <AdminLayout>
                <AdminUsersPage />
              </AdminLayout>
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/users/:id"
          element={
            <AdminProtectedRoute>
              <AdminLayout>
                <AdminUserDetailPage />
              </AdminLayout>
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/plans"
          element={
            <AdminProtectedRoute>
              <AdminLayout>
                <AdminPlansPage />
              </AdminLayout>
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/llm-calls"
          element={
            <AdminProtectedRoute>
              <AdminLayout>
                <AdminLlmCallsPage />
              </AdminLayout>
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/metrics"
          element={
            <AdminProtectedRoute>
              <AdminLayout>
                <AdminMetricsDashboardPage />
              </AdminLayout>
            </AdminProtectedRoute>
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
