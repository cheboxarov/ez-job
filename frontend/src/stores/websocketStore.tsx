import { create } from 'zustand';
import { notification, Button } from 'antd';
import {
  wsClient,
  type AgentAction as WebSocketAgentAction,
  type VacancyResponseCreatedPayload,
} from '../api/websocket';
import type { AgentAction as ApiAgentAction } from '../types/api';
import { useAgentActionsStore } from './agentActionsStore';
import { useDailyResponsesStore } from './dailyResponsesStore';
import { useEventsStore } from './eventsStore';
import { useTasksStore } from './tasksStore';
import { useVacancyResponsesStore } from './vacancyResponsesStore';
import { playNotificationSound } from '../utils/notificationSound';

interface WebSocketState {
  isConnected: boolean;
  lastAgentAction: WebSocketAgentAction | null;
  lastVacancyResponse: VacancyResponseCreatedPayload | null;

  connect: () => void;
  disconnect: () => void;
  setLastAgentAction: (action: WebSocketAgentAction) => void;
  setLastVacancyResponse: (response: VacancyResponseCreatedPayload) => void;
}

// Вспомогательные функции для формирования текста уведомлений
const getNotificationTitle = (type: string): string => {
  switch (type) {
    case 'send_message':
      return 'Отправлено сообщение';
    case 'create_event':
      return 'Создано событие';
    default:
      return 'Новое действие агента';
  }
};

const getNotificationDescription = (payload: WebSocketAgentAction): string => {
  if (payload.type === 'send_message' && payload.data.message_text) {
    const messagePreview = payload.data.message_text.length > 100
      ? payload.data.message_text.substring(0, 100) + '...'
      : payload.data.message_text;
    return messagePreview;
  }
  const eventType =
    typeof (payload.data as { event_type?: unknown }).event_type === 'string'
      ? (payload.data as { event_type?: string }).event_type
      : undefined;
  if (payload.type === 'create_event' && eventType) {
    const eventTypeLabels: Record<string, string> = {
      call_request: 'Запрос на созвон',
      external_action_request: 'Требуется действие',
      fill_form: 'Заполнение формы',
      test_task: 'Тестовое задание',
      question_answered: 'Ответ на вопрос',
    };
    const eventLabel = eventTypeLabels[eventType] || eventType;
    return `Событие: ${eventLabel}`;
  }
  return 'Агент выполнил новое действие';
};

const getNotificationActionUrl = (payload: WebSocketAgentAction): string => {
  const eventType =
    typeof (payload.data as { event_type?: unknown }).event_type === 'string'
      ? (payload.data as { event_type?: string }).event_type
      : undefined;
  if (payload.type === 'create_event' && (eventType === 'fill_form' || eventType === 'test_task')) {
    return '/tasks';
  }
  if (payload.entity_type === 'hh_dialog') {
    return `/chats/${payload.entity_id}`;
  }
  return '/events';
};

// Инициализация подписок на WebSocket события
let unsubscribeAgentAction: (() => void) | null = null;
let unsubscribeVacancyResponse: (() => void) | null = null;
let connectionCheckInterval: NodeJS.Timeout | null = null;

export const useWebSocketStore = create<WebSocketState>((set, get) => {
  // Функция для инициализации подписок
  const initializeSubscriptions = () => {
    // Отписываемся от старых подписок, если они есть
    if (unsubscribeAgentAction) {
      unsubscribeAgentAction();
    }
    if (unsubscribeVacancyResponse) {
      unsubscribeVacancyResponse();
    }

    // Подписываемся на agent_action_created
    unsubscribeAgentAction = wsClient.on<WebSocketAgentAction>(
      'agent_action_created',
      (payload) => {
        // Воспроизводим звук
        playNotificationSound();

        // Показываем уведомление
        const actionUrl = getNotificationActionUrl(payload);
        const notificationKey = `agent-action-${payload.id}`;

        notification.info({
          key: notificationKey,
          message: getNotificationTitle(payload.type),
          description: getNotificationDescription(payload),
          placement: 'topRight',
          duration: 5,
          btn: (
            <Button
              type="primary"
              size="small"
              onClick={() => {
                // Используем window.location для навигации
                window.location.href = actionUrl;
                notification.destroy(notificationKey);
              }}
            >
              Посмотреть
            </Button>
          ),
        });

        // Обновляем stores
        useAgentActionsStore.getState().incrementUnreadCount();
        useEventsStore.getState().addEventToTop(payload);
        const eventType =
          typeof (payload.data as { event_type?: unknown }).event_type === 'string'
            ? (payload.data as { event_type?: string }).event_type
            : undefined;
        if (payload.type === 'create_event' && (eventType === 'fill_form' || eventType === 'test_task')) {
          useTasksStore.getState().incrementPendingCount();
          useTasksStore.getState().addTaskToTop(payload as unknown as ApiAgentAction);
        }

        // Обновляем локальное состояние
        set({ lastAgentAction: payload });
      }
    );

    // Подписываемся на vacancy_response_created
    unsubscribeVacancyResponse = wsClient.on<VacancyResponseCreatedPayload>(
      'vacancy_response_created',
      (payload) => {
        // Обновляем stores
        useDailyResponsesStore.getState().incrementCount();
        
        // Преобразуем payload в VacancyResponseItem для vacancyResponsesStore
        const responseItem = {
          id: payload.id,
          vacancy_id: payload.vacancy_id,
          vacancy_name: payload.vacancy_name,
          vacancy_url: payload.vacancy_url,
          cover_letter: payload.cover_letter,
          created_at: payload.created_at || new Date().toISOString(),
        };
        useVacancyResponsesStore.getState().addResponseToTop(responseItem, payload.resume_hash);

        // Обновляем локальное состояние
        set({ lastVacancyResponse: payload });
      }
    );
  };

  // Инициализируем подписки при создании store
  initializeSubscriptions();

  // Проверяем состояние соединения периодически
  const checkConnection = () => {
    set({ isConnected: wsClient.isConnected });
  };

  connectionCheckInterval = setInterval(checkConnection, 1000);

  return {
    isConnected: false,
    lastAgentAction: null,
    lastVacancyResponse: null,

    connect: () => {
      wsClient.connect();
      checkConnection();
      // Переинициализируем подписки при подключении
      initializeSubscriptions();
    },

    disconnect: () => {
      wsClient.disconnect();
      set({ isConnected: false });
      if (unsubscribeAgentAction) {
        unsubscribeAgentAction();
        unsubscribeAgentAction = null;
      }
      if (unsubscribeVacancyResponse) {
        unsubscribeVacancyResponse();
        unsubscribeVacancyResponse = null;
      }
      if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
        connectionCheckInterval = null;
      }
    },

    setLastAgentAction: (action) => {
      set({ lastAgentAction: action });
    },

    setLastVacancyResponse: (response) => {
      set({ lastVacancyResponse: response });
    },
  };
});
