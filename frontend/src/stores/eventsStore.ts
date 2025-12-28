import { create } from 'zustand';
import { getAgentActions, type GetAgentActionsParams } from '../api/agentActions';
import type { AgentAction } from '../types/api';

interface EventsState {
  events: AgentAction[];
  loading: boolean;
  filterType: string;
  fetchEvents: (filterType?: string) => Promise<void>;
  addEventToTop: (event: AgentAction) => void;
  clearEvents: () => void;
}

export const useEventsStore = create<EventsState>((set) => ({
  events: [],
  loading: false,
  filterType: 'all',

  fetchEvents: async (filterType: string = 'all') => {
    set({ loading: true, filterType });
    try {
      const params: GetAgentActionsParams | undefined =
        filterType !== 'all' ? { type: filterType } : undefined;
      const response = await getAgentActions(params);
      set({ events: response.items, loading: false });
    } catch (error) {
      console.error('Ошибка при загрузке событий:', error);
      set({ loading: false });
    }
  },

  addEventToTop: (event: AgentAction) => {
    set((state) => {
      // Проверяем, нет ли уже такого события в списке
      const exists = state.events.some((e) => e.id === event.id);
      if (exists) {
        return state;
      }
      // Добавляем в начало списка
      return {
        events: [event, ...state.events],
      };
    });
  },

  clearEvents: () => {
    set({ events: [] });
  },
}));
