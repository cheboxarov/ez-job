import { create } from 'zustand';
import { getDailyResponses } from '../api/subscription';
import type { DailyResponsesResponse } from '../types/api';

interface DailyResponsesState {
  count: number;
  limit: number;
  remaining: number;
  secondsUntilReset: number | null;
  loading: boolean;
  fetchDailyResponses: () => Promise<void>;
  incrementCount: () => void;
}

export const useDailyResponsesStore = create<DailyResponsesState>((set, get) => ({
  count: 0,
  limit: 0,
  remaining: 0,
  secondsUntilReset: null,
  loading: false,

  fetchDailyResponses: async () => {
    set({ loading: true });
    try {
      const data: DailyResponsesResponse = await getDailyResponses();
      set({
        count: data.count,
        limit: data.limit,
        remaining: data.remaining,
        secondsUntilReset: data.seconds_until_reset,
        loading: false,
      });
    } catch (error) {
      console.error('Ошибка при загрузке daily responses:', error);
      set({ loading: false });
    }
  },

  incrementCount: () => {
    set((state) => {
      const newCount = state.count + 1;
      const newRemaining = Math.max(0, state.remaining - 1);
      return {
        count: newCount,
        remaining: newRemaining,
      };
    });
  },
}));
