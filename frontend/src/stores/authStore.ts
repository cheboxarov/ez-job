import { create } from 'zustand';
import type { User } from '../types/user';
import { login as apiLogin, register as apiRegister } from '../api/auth';
import { getCurrentUser } from '../api/users';
import { loginByCode as hhLoginByCode } from '../api/hhAuth';

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithHhOtp: (params: {
    phone: string;
    code: string;
    cookies: Record<string, string>;
  }) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
  }) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem('auth_token'),
  user: null,
  loading: false,

  login: async (email: string, password: string) => {
    set({ loading: true });
    try {
      const response = await apiLogin(email, password);
      const token = response.access_token;
      localStorage.setItem('auth_token', token);
      set({ token, loading: false });
      await get().fetchCurrentUser();
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  loginWithHhOtp: async ({ phone, code, cookies }) => {
    set({ loading: true });
    try {
      const response = await hhLoginByCode(phone, code, cookies);
      const token = response.access_token;
      localStorage.setItem('auth_token', token);
      set({ token, loading: false });
      await get().fetchCurrentUser();
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  register: async (data) => {
    set({ loading: true });
    try {
      await apiRegister(data);
      // После успешной регистрации автоматически логинимся
      await get().login(data.email, data.password);
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    set({ token: null, user: null });
  },

  fetchCurrentUser: async () => {
    const token = get().token;
    if (!token) return;

    try {
      const user = await getCurrentUser();
      localStorage.setItem('user', JSON.stringify(user));
      set({ user });
    } catch (error) {
      // Если не удалось загрузить пользователя, очищаем токен
      get().logout();
      throw error;
    }
  },

  initialize: async () => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      set({ token });
      try {
        await get().fetchCurrentUser();
      } catch (error) {
        // Если токен невалидный, просто очищаем его
        get().logout();
      }
    }
  },
}));


