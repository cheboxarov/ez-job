export interface PlanTask {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed';
  description?: string;
  agent_type?: 'question' | 'patch' | 'chat';
}

export interface ResumeEditWebSocketMessage {
  type:
    | 'assistant_message'
    | 'questions'
    | 'patches'
    | 'plan'
    | 'streaming'
    | 'error'
    | 'warnings'
    | 'patch_applied';
  data: any;
}

export interface AssistantMessageData {
  message: string;
}

export interface PlanData {
  plan: PlanTask[];
}

export interface QuestionsData {
  questions: Array<{
    id: string;
    text: string;
    required: boolean;
    suggested_answers?: string[];
    allow_multiple?: boolean;
  }>;
}

export interface PatchesData {
  patches: Array<{
    id: string;
    type: 'replace' | 'insert' | 'delete';
    start_line: number;
    end_line: number;
    old_text: string;
    new_text: string | null;
    reason: string;
  }>;
}

export interface StreamingData {
  chunk: string;
  is_complete: boolean;
}

export interface ErrorData {
  message: string;
}

export class ResumeEditWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private isConnecting = false;
  private shouldReconnect = true;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageListeners: Map<string, Set<(data: any) => void>> = new Map();
  private resumeId: string | null = null;

  constructor() {
    // Инициализируем Map для каждого типа события
    this.messageListeners.set('assistant_message', new Set());
    this.messageListeners.set('questions', new Set());
    this.messageListeners.set('patches', new Set());
    this.messageListeners.set('plan', new Set());
    this.messageListeners.set('streaming', new Set());
    this.messageListeners.set('error', new Set());
    this.messageListeners.set('warnings', new Set());
    this.messageListeners.set('patch_applied', new Set());
  }

  connect(resumeId: string): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.resumeId = resumeId;
    this.isConnecting = true;
    this.shouldReconnect = true;

    const token = localStorage.getItem('auth_token');

    if (!token) {
      console.warn('ResumeEditWebSocket: Нет токена авторизации, подключение невозможно');
      this.isConnecting = false;
      return;
    }

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const wsUrl =
      API_BASE_URL.replace(/^http/, 'ws') +
      `/ws/resume-edit/${resumeId}?token=${encodeURIComponent(token)}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('ResumeEditWebSocket: Соединение установлено');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const data: ResumeEditWebSocketMessage = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('ResumeEditWebSocket: Ошибка при парсинге сообщения', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('ResumeEditWebSocket: Ошибка соединения', error);
        this.isConnecting = false;
      };

      this.ws.onclose = (event) => {
        console.log('ResumeEditWebSocket: Соединение закрыто', event.code, event.reason);
        this.isConnecting = false;

        // Автоматическое переподключение
        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.handleReconnect();
        }
      };
    } catch (error) {
      console.error('ResumeEditWebSocket: Ошибка при создании соединения', error);
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
    this.resumeId = null;
  }

  sendMessage(message: string, resumeText?: string, history?: any[]): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('ResumeEditWebSocket: Соединение не установлено');
      return;
    }

    this.ws.send(
      JSON.stringify({
        type: 'user_message',
        data: {
          message,
          resume_text: resumeText,
          history,
        },
      })
    );
  }

  answerQuestion(questionId: string, answer: string, resumeText?: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('ResumeEditWebSocket: Соединение не установлено');
      return;
    }

    this.ws.send(
      JSON.stringify({
        type: 'answer_question',
        data: {
          question_id: questionId,
          answer,
          resume_text: resumeText,
        },
      })
    );
  }

  answerAllQuestions(
    answers: Array<{ questionId: string; answer: string }>,
    resumeText?: string
  ): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('ResumeEditWebSocket: Соединение не установлено');
      return;
    }

    this.ws.send(
      JSON.stringify({
        type: 'answer_all_questions',
        data: {
          answers: answers,
          resume_text: resumeText,
        },
      })
    );
  }

  applyPatch(patchId: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('ResumeEditWebSocket: Соединение не установлено');
      return;
    }

    this.ws.send(
      JSON.stringify({
        type: 'apply_patch',
        data: {
          patch_id: patchId,
        },
      })
    );
  }

  on<T>(eventType: ResumeEditWebSocketMessage['type'], callback: (data: T) => void): () => void {
    const listeners = this.messageListeners.get(eventType);
    if (listeners) {
      listeners.add(callback as (data: any) => void);
    }

    // Возвращаем функцию для отписки
    return () => {
      const listeners = this.messageListeners.get(eventType);
      if (listeners) {
        listeners.delete(callback as (data: any) => void);
      }
    };
  }

  off(eventType: ResumeEditWebSocketMessage['type'], callback: (data: any) => void): void {
    const listeners = this.messageListeners.get(eventType);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  private handleMessage(message: ResumeEditWebSocketMessage): void {
    const listeners = this.messageListeners.get(message.type);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(message.data);
        } catch (error) {
          console.error(
            `ResumeEditWebSocket: Ошибка в обработчике события ${message.type}`,
            error
          );
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

    console.log(
      `ResumeEditWebSocket: Переподключение через ${delay}ms (попытка ${this.reconnectAttempts})`
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.resumeId) {
        this.connect(this.resumeId);
      }
    }, delay);
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
