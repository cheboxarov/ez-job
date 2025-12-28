import { create } from 'zustand';
import {
  getAgentActionsUnreadCount,
  markAllAgentActionsAsRead,
} from '../api/agentActions';

interface AgentActionsState {
  unreadCount: number;
  loading: boolean;
  fetchUnreadCount: () => Promise<void>;
  markAllAsRead: () => Promise<void>;
  incrementUnreadCount: () => void;
}

export const useAgentActionsStore = create<AgentActionsState>((set) => ({
  unreadCount: 0,
  loading: false,

  fetchUnreadCount: async () => {
    set({ loading: true });
    try {
      const count = await getAgentActionsUnreadCount();
      set({ unreadCount: count, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  markAllAsRead: async () => {
    set({ loading: true });
    try {
      await markAllAgentActionsAsRead();
      set({ unreadCount: 0, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  incrementUnreadCount: () => {
    set((state) => ({ unreadCount: state.unreadCount + 1 }));
  },
}));


