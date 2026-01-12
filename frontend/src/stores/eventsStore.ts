import { create } from 'zustand';
import { getAgentActions, type GetAgentActionsParams } from '../api/agentActions';
import type { AgentAction } from '../types/api';

type FilterMode = 'include' | 'exclude';

interface EventsState {
  events: AgentAction[];
  loading: boolean;
  filterMode: FilterMode;
  selectedTypes: string[];
  selectedEventTypes: string[];
  fetchEvents: () => Promise<void>;
  setFilterMode: (mode: FilterMode) => void;
  toggleType: (type: string) => void;
  toggleEventType: (eventType: string) => void;
  clearFilters: () => void;
  addEventToTop: (event: AgentAction) => void;
  clearEvents: () => void;
}

const buildQueryParams = (
  filterMode: FilterMode,
  selectedTypes: string[],
  selectedEventTypes: string[]
): GetAgentActionsParams | undefined => {
  const hasTypes = selectedTypes.length > 0;
  const hasEventTypes = selectedEventTypes.length > 0;

  if (!hasTypes && !hasEventTypes) {
    return undefined;
  }

  if (filterMode === 'include') {
    const types = hasEventTypes && !selectedTypes.includes('create_event')
      ? [...selectedTypes, 'create_event']
      : selectedTypes;
    return {
      types: types.length > 0 ? types : undefined,
      event_types: hasEventTypes ? selectedEventTypes : undefined,
    };
  }

  return {
    exclude_types: hasTypes ? selectedTypes : undefined,
    exclude_event_types: hasEventTypes ? selectedEventTypes : undefined,
  };
};

const matchesFilters = (
  event: AgentAction,
  filterMode: FilterMode,
  selectedTypes: string[],
  selectedEventTypes: string[]
) => {
  const hasTypes = selectedTypes.length > 0;
  const hasEventTypes = selectedEventTypes.length > 0;

  if (!hasTypes && !hasEventTypes) {
    return true;
  }

  if (filterMode === 'include') {
    const includeTypes = hasEventTypes && !selectedTypes.includes('create_event')
      ? [...selectedTypes, 'create_event']
      : selectedTypes;
    if (includeTypes.length > 0 && !includeTypes.includes(event.type)) {
      return false;
    }
    if (hasEventTypes && event.type === 'create_event') {
      return selectedEventTypes.includes(event.data?.event_type);
    }
    return true;
  }

  if (selectedTypes.includes(event.type)) {
    return false;
  }
  if (event.type === 'create_event' && selectedEventTypes.includes(event.data?.event_type)) {
    return false;
  }
  return true;
};

export const useEventsStore = create<EventsState>((set, get) => ({
  events: [],
  loading: false,
  filterMode: 'include',
  selectedTypes: [],
  selectedEventTypes: [],

  fetchEvents: async () => {
    set({ loading: true });
    try {
      const { filterMode, selectedTypes, selectedEventTypes } = get();
      const params = buildQueryParams(filterMode, selectedTypes, selectedEventTypes);
      const response = await getAgentActions(params);
      set({ events: response.items, loading: false });
    } catch (error) {
      console.error('Ошибка при загрузке событий:', error);
      set({ loading: false });
    }
  },

  setFilterMode: (mode) => {
    set({ filterMode: mode });
  },

  toggleType: (type) => {
    set((state) => ({
      selectedTypes: state.selectedTypes.includes(type)
        ? state.selectedTypes.filter((item) => item !== type)
        : [...state.selectedTypes, type],
      selectedEventTypes:
        type === 'create_event' &&
        state.filterMode === 'include' &&
        state.selectedTypes.includes(type)
          ? []
          : state.selectedEventTypes,
    }));
  },

  toggleEventType: (eventType) => {
    set((state) => ({
      selectedEventTypes: state.selectedEventTypes.includes(eventType)
        ? state.selectedEventTypes.filter((item) => item !== eventType)
        : [...state.selectedEventTypes, eventType],
      selectedTypes:
        state.filterMode === 'include' &&
        !state.selectedTypes.includes('create_event') &&
        !state.selectedEventTypes.includes(eventType)
          ? [...state.selectedTypes, 'create_event']
          : state.selectedTypes,
    }));
  },

  clearFilters: () => {
    set({
      filterMode: 'include',
      selectedTypes: [],
      selectedEventTypes: [],
    });
  },

  addEventToTop: (event: AgentAction) => {
    set((state) => {
      // Проверяем, нет ли уже такого события в списке
      const exists = state.events.some((e) => e.id === event.id);
      if (exists) {
        return state;
      }
      if (!matchesFilters(event, state.filterMode, state.selectedTypes, state.selectedEventTypes)) {
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
