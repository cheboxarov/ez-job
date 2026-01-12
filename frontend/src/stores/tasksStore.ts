import { create } from 'zustand';
import {
  getAgentActions,
  updateAgentActionStatus,
  type GetAgentActionsParams,
} from '../api/agentActions';
import type { AgentAction, EventStatus } from '../types/api';

type StatusFilter = EventStatus | 'all';

interface TasksState {
  tasks: AgentAction[];
  loading: boolean;
  statusFilter: StatusFilter;
  pendingCount: number;
  fetchTasks: () => Promise<void>;
  fetchPendingCount: () => Promise<void>;
  setStatusFilter: (status: StatusFilter) => void;
  updateTaskStatus: (taskId: string, status: EventStatus) => Promise<void>;
  addTaskToTop: (task: AgentAction) => void;
  incrementPendingCount: () => void;
}

const TASK_EVENT_TYPES = ['fill_form', 'test_task'];

const getTaskStatus = (task: AgentAction): EventStatus =>
  (task.data?.status as EventStatus | undefined) || 'pending';

const buildTaskParams = (statusFilter: StatusFilter): GetAgentActionsParams => {
  const params: GetAgentActionsParams = {
    types: ['create_event'],
    event_types: TASK_EVENT_TYPES,
  };

  if (statusFilter !== 'all') {
    params.statuses = [statusFilter];
  }

  return params;
};

export const useTasksStore = create<TasksState>((set, get) => ({
  tasks: [],
  loading: false,
  statusFilter: 'pending',
  pendingCount: 0,

  fetchTasks: async () => {
    set({ loading: true });
    try {
      const { statusFilter } = get();
      const params = buildTaskParams(statusFilter);
      const response = await getAgentActions(params);
      set({ tasks: response.items, loading: false });

      if (statusFilter === 'pending' || statusFilter === 'all') {
        const pendingCount = response.items.filter(
          (task) => getTaskStatus(task) === 'pending'
        ).length;
        set({ pendingCount });
      }
    } catch (error) {
      console.error('Ошибка при загрузке заданий:', error);
      set({ loading: false });
    }
  },

  fetchPendingCount: async () => {
    try {
      const params = buildTaskParams('pending');
      const response = await getAgentActions(params);
      set({ pendingCount: response.items.length });
    } catch (error) {
      console.error('Ошибка при загрузке количества заданий:', error);
    }
  },

  setStatusFilter: (status) => {
    set({ statusFilter: status });
  },

  updateTaskStatus: async (taskId, status) => {
    const updated = await updateAgentActionStatus(taskId, status);
    set((state) => {
      const existing = state.tasks.find((task) => task.id === taskId);
      const previousStatus = existing ? getTaskStatus(existing) : null;
      let nextTasks = state.tasks.map((task) =>
        task.id === taskId ? updated : task
      );

      const matchesFilter =
        state.statusFilter === 'all' || status === state.statusFilter;
      if (!matchesFilter) {
        nextTasks = nextTasks.filter((task) => task.id !== taskId);
      }

      let pendingCount = state.pendingCount;
      if (previousStatus === 'pending' && status !== 'pending') {
        pendingCount = Math.max(0, pendingCount - 1);
      }
      if (previousStatus !== 'pending' && status === 'pending') {
        pendingCount += 1;
      }

      return { tasks: nextTasks, pendingCount };
    });
  },

  addTaskToTop: (task) => {
    const eventType = task.data?.event_type;
    if (!TASK_EVENT_TYPES.includes(eventType || '')) {
      return;
    }

    set((state) => {
      const exists = state.tasks.some((item) => item.id === task.id);
      if (exists) {
        return state;
      }

      const taskStatus = getTaskStatus(task);
      const matchesFilter =
        state.statusFilter === 'all' || taskStatus === state.statusFilter;

      if (!matchesFilter) {
        return state;
      }

      return { tasks: [task, ...state.tasks] };
    });
  },

  incrementPendingCount: () => {
    set((state) => ({ pendingCount: state.pendingCount + 1 }));
  },
}));
