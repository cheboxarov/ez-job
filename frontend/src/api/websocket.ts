export type WebSocketEventType = 'agent_action_created' | 'vacancy_response_created';

export interface WebSocketEvent<T = unknown> {
  event_type: WebSocketEventType;
  payload: T;
  created_at: string;
}

export interface AgentAction {
  id: string;
  type: string;
  entity_type: string;
  entity_id: number;
  created_by: string;
  user_id: string;
  resume_hash: string | null;
  data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  is_read: boolean;
}

export interface VacancyResponseCreatedPayload {
  id: string;
  vacancy_id: number;
  resume_id: string;
  resume_hash: string | null;
  user_id: string;
  cover_letter: string;
  vacancy_name: string;
  vacancy_url: string | null;
  created_at: string | null;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // 1 секунда
  private maxReconnectDelay = 30000; // 30 секунд
  private listeners: Map<WebSocketEventType, Set<(payload: unknown) => void>> = new Map();
  private isConnecting = false;
  private shouldReconnect = true;
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor() {
    // Инициализируем Map для каждого типа события
    this.listeners.set('agent_action_created', new Set());
    this.listeners.set('vacancy_response_created', new Set());
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    this.shouldReconnect = true;

    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.warn('WebSocket: Нет токена авторизации, подключение невозможно');
      this.isConnecting = false;
      return;
    }

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + `/ws?token=${encodeURIComponent(token)}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket: Соединение установлено');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.notifyListeners('connected', null);
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const data: WebSocketEvent = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('WebSocket: Ошибка при парсинге сообщения', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket: Ошибка соединения', error);
        this.isConnecting = false;
        this.notifyListeners('error', error);
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket: Соединение закрыто', event.code, event.reason);
        this.isConnecting = false;
        this.notifyListeners('disconnected', { code: event.code, reason: event.reason });

        // Автоматическое переподключение
        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.handleReconnect();
        }
      };
    } catch (error) {
      console.error('WebSocket: Ошибка при создании соединения', error);
      this.isConnecting = false;
      if (this.shouldReconnect) {
        this.handleReconnect();
      }
    }
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on<T>(eventType: WebSocketEventType, callback: (payload: T) => void): () => void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.add(callback as (payload: unknown) => void);
    }

    // Возвращаем функцию для отписки
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(callback as (payload: unknown) => void);
      }
    };
  }

  off(eventType: WebSocketEventType, callback: (payload: unknown) => void): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  private handleMessage(event: WebSocketEvent): void {
    const listeners = this.listeners.get(event.event_type);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(event.payload);
        } catch (error) {
          console.error(`WebSocket: Ошибка в обработчике события ${event.event_type}`, error);
        }
      });
    }
  }

  private handleReconnect(): void {
    if (this.reconnectTimer) {
      return; // Уже запланировано переподключение
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`WebSocket: Переподключение через ${delay}ms (попытка ${this.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  private notifyListeners(event: 'connected' | 'disconnected' | 'error', data: unknown): void {
    // Можно добавить специальные обработчики для системных событий
    // Пока оставляем пустым, можно расширить в будущем
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
export const wsClient = new WebSocketClient();
