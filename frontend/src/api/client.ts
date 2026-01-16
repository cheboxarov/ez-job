import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor для добавления токена
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      // Редирект будет обработан в ProtectedRoute
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    if (error.response?.status === 422) {
      const responseData = error.response.data;
      let detail = responseData?.detail ?? responseData;
      if (typeof detail !== 'string') {
        try {
          detail = JSON.stringify(detail);
        } catch (stringifyError) {
          detail = String(detail);
        }
      }
      if (responseData && typeof responseData === 'object') {
        responseData.detail = detail;
      } else {
        error.response.data = { detail };
      }
      error.message = detail ? `422: ${detail}` : error.message;
    }
    return Promise.reject(error);
  }
);

export default apiClient;

