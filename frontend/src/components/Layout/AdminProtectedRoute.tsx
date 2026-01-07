import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

interface AdminProtectedRouteProps {
  children: React.ReactNode;
}

export const AdminProtectedRoute = ({ children }: AdminProtectedRouteProps) => {
  const { token, user } = useAuthStore();
  const location = useLocation();

  // Сначала проверяем авторизацию
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Затем проверяем права суперпользователя
  if (!user?.is_superuser) {
    return <Navigate to="/resumes" replace />;
  }

  return <>{children}</>;
};
