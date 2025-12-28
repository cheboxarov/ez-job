import { create } from 'zustand';
import { getVacancyResponses, type GetVacancyResponsesParams } from '../api/vacancies';
import type { VacancyResponseItem } from '../types/api';

interface VacancyResponsesState {
  responses: VacancyResponseItem[];
  pagination: {
    total: number;
    offset: number;
    limit: number;
    current: number;
  };
  loading: boolean;
  currentResumeHash: string | null;
  fetchResponses: (resumeHash: string, page?: number) => Promise<void>;
  addResponseToTop: (response: VacancyResponseItem) => void;
}

export const useVacancyResponsesStore = create<VacancyResponsesState>((set, get) => ({
  responses: [],
  pagination: {
    total: 0,
    offset: 0,
    limit: 50,
    current: 1,
  },
  loading: false,
  currentResumeHash: null,

  fetchResponses: async (resumeHash: string, page: number = 1) => {
    set({ loading: true, currentResumeHash: resumeHash });
    const limit = get().pagination.limit;
    const offset = (page - 1) * limit;

    try {
      const params: GetVacancyResponsesParams = {
        resume_hash: resumeHash,
        offset,
        limit,
      };
      const data = await getVacancyResponses(params);
      set({
        responses: data.items,
        pagination: {
          total: data.total,
          offset: data.offset,
          limit: data.limit,
          current: page,
        },
        loading: false,
      });
    } catch (error) {
      console.error('Ошибка при загрузке откликов:', error);
      set({ loading: false });
    }
  },

  addResponseToTop: (response: VacancyResponseItem, resumeHash?: string | null) => {
    set((state) => {
      // Добавляем только если это отклик для текущего резюме
      const targetResumeHash = resumeHash || state.currentResumeHash;
      if (state.currentResumeHash && targetResumeHash === state.currentResumeHash) {
        // Проверяем, нет ли уже такого отклика в списке
        const exists = state.responses.some((r) => r.id === response.id);
        if (exists) {
          return state;
        }
        // Добавляем в начало списка и увеличиваем total
        return {
          responses: [response, ...state.responses],
          pagination: {
            ...state.pagination,
            total: state.pagination.total + 1,
          },
        };
      }
      return state;
    });
  },
}));
