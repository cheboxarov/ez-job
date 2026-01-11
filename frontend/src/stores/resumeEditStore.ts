import { create } from 'zustand';
import { ResumeEditWebSocketClient } from '../api/resumeEditWebSocket';
import type {
  AssistantMessageData,
  QuestionsData,
  PatchesData,
  StreamingData,
  PlanData,
  PlanTask,
} from '../api/resumeEditWebSocket';

export interface ResumeEditPatch {
  id: string;
  type: 'replace' | 'insert' | 'delete';
  start_line: number;
  end_line: number;
  old_text: string;
  new_text: string | null;
  reason: string;
}

export interface ResumeEditQuestion {
  id: string;
  text: string;
  required: boolean;
  suggested_answers?: string[];
  allow_multiple?: boolean;
}

interface ChatMessage {
  type: 'user' | 'assistant' | 'question' | 'system' | 'checkpoint';
  content: string;
  questionId?: string;
  timestamp: Date;
}

function formatPlanTaskTitle(task: PlanTask): string {
  return task.title || task.id;
}

function buildPlanSystemMessages(prev: PlanTask[], next: PlanTask[]): string[] {
  const messages: string[] = [];

  if ((!prev || prev.length === 0) && next && next.length > 0) {
    const current = next.find((t) => t.status === 'in_progress');
    messages.push(
      `План создан: ${next.length} шагов.` +
        (current ? ` Текущий шаг: ${formatPlanTaskTitle(current)}.` : '')
    );
  }

  const prevById = new Map(prev.map((t) => [t.id, t]));
  const nextById = new Map(next.map((t) => [t.id, t]));
  const prevCompleted = prev.filter((t) => t.status === 'completed').length;
  const nextCompleted = next.filter((t) => t.status === 'completed').length;
  const prevCurrent = prev.find((t) => t.status === 'in_progress');
  const nextCurrent = next.find((t) => t.status === 'in_progress');

  if (prev.length > 0 && next.length > 0) {
    const parts: string[] = [];
    if (prev.length !== next.length) {
      parts.push(`шагов: ${prev.length} → ${next.length}`);
    }
    if (nextCompleted > prevCompleted) {
      parts.push(`выполнено: +${nextCompleted - prevCompleted} (${nextCompleted}/${next.length})`);
    }
    if (nextCurrent && (!prevCurrent || prevCurrent.id !== nextCurrent.id)) {
      parts.push(`текущий шаг: ${formatPlanTaskTitle(nextCurrent)}`);
    }
    if (parts.length > 0) {
      messages.push(`План обновлён • ${parts.join(' • ')}`);
    }
  }

  for (const [id, nextTask] of nextById.entries()) {
    const prevTask = prevById.get(id);
    if (!prevTask) continue;
    if (prevTask.status !== nextTask.status) {
      if (nextTask.status === 'completed') {
        messages.push(`Шаг выполнен: ${formatPlanTaskTitle(nextTask)}.`);
      } else if (nextTask.status === 'in_progress') {
        messages.push(`Переходим к шагу: ${formatPlanTaskTitle(nextTask)}.`);
      }
    }
  }

  if (next && next.length > 0 && next.every((t) => t.status === 'completed')) {
    if (!prev || prev.length === 0 || !prev.every((t) => t.status === 'completed')) {
      messages.push('План выполнен полностью.');
    }
  }

  return messages;
}

function mergeDraftPatches(
  existing: ResumeEditPatch[],
  incoming: ResumeEditPatch[]
): { merged: ResumeEditPatch[]; added: number; updated: number } {
  const existingById = new Map(existing.map((p) => [p.id, p]));
  const incomingById = new Map(incoming.map((p) => [p.id, p]));
  let added = 0;
  let updated = 0;

  for (const patch of incoming) {
    const prev = existingById.get(patch.id);
    if (!prev) {
      added += 1;
    } else {
      const isUpdated =
        prev.type !== patch.type ||
        prev.start_line !== patch.start_line ||
        prev.end_line !== patch.end_line ||
        prev.old_text !== patch.old_text ||
        prev.new_text !== patch.new_text ||
        prev.reason !== patch.reason;
      if (isUpdated) {
        updated += 1;
      }
    }
  }

  const merged = existing.map((p) => incomingById.get(p.id) || p);
  for (const patch of incoming) {
    if (!existingById.has(patch.id)) {
      merged.push(patch);
    }
  }

  return { merged, added, updated };
}

interface ResumeEditState {
  // Состояние резюме
  original_resume_text: string;
  current_resume_text: string;

  // Patch-операции
  applied_patches: ResumeEditPatch[];
  draft_patches: ResumeEditPatch[];

  // Чат
  chat_history: ChatMessage[];
  streaming_message: string;

  // WebSocket
  websocket_client: ResumeEditWebSocketClient | null;
  websocket_connected: boolean;

  // Вопросы
  pending_questions: ResumeEditQuestion[];

  // План
  current_plan: PlanTask[];
  
  // Статус обработки
  is_processing: boolean;

  // Действия
  initialize: (resumeId: string, originalText: string) => void;
  connectWebSocket: (resumeId: string) => void;
  disconnectWebSocket: () => void;
  sendMessage: (message: string) => void;
  answerQuestion: (questionId: string, answer: string) => void;
  answerAllQuestions: (answers: Array<{ questionId: string; answer: string }>) => void;
  applyPatch: (patchId: string) => void;
  rejectPatch: (patchId: string) => void;
  resetAll: () => void;
  saveDraft: () => void;
  setStreamingMessage: (message: string) => void;
  addChatMessage: (message: ChatMessage) => void;
  setPendingQuestions: (questions: ResumeEditQuestion[]) => void;
  setDraftPatches: (patches: ResumeEditPatch[]) => void;
}

export const useResumeEditStore = create<ResumeEditState>((set, get) => ({
  // Начальное состояние
  original_resume_text: '',
  current_resume_text: '',
  applied_patches: [],
  draft_patches: [],
  chat_history: [],
  streaming_message: '',
  websocket_client: null,
  websocket_connected: false,
  pending_questions: [],
  current_plan: [],
  is_processing: false,

  // Инициализация
  initialize: (resumeId: string, originalText: string) => {
    set({
      original_resume_text: originalText,
      current_resume_text: originalText,
      applied_patches: [],
      draft_patches: [],
      chat_history: [],
      streaming_message: '',
      pending_questions: [],
      current_plan: [],
      is_processing: false,
    });
    get().connectWebSocket(resumeId);
  },

  // WebSocket
  connectWebSocket: (resumeId: string) => {
    const client = new ResumeEditWebSocketClient();

    // Обработчики событий
    client.on<AssistantMessageData>('assistant_message', (data) => {
      get().addChatMessage({
        type: 'assistant',
        content: data.message,
        timestamp: new Date(),
      });
      set({ streaming_message: '', is_processing: false });
    });

    client.on<QuestionsData>('questions', (data) => {
      const questions = data.questions.map((q) => ({
        id: q.id,
        text: q.text,
        required: q.required,
        suggested_answers: q.suggested_answers,
        allow_multiple: q.allow_multiple,
      }));
      set({ pending_questions: questions });

      // Добавляем вопросы в чат
      data.questions.forEach((q) => {
        get().addChatMessage({
          type: 'question',
          content: q.text,
          questionId: q.id,
          timestamp: new Date(),
        });
      });
    });

    client.on<PatchesData>('patches', (data) => {
      const patches: ResumeEditPatch[] = data.patches.map((p) => ({
        id: p.id,
        type: p.type,
        start_line: p.start_line,
        end_line: p.end_line,
        old_text: p.old_text,
        new_text: p.new_text,
        reason: p.reason,
      }));
      const prevDrafts = get().draft_patches || [];
      const { merged, added, updated } = mergeDraftPatches(prevDrafts, patches);
      set({ draft_patches: merged });

      if (added > 0 || updated > 0) {
        const parts = [];
        if (added > 0) parts.push(`добавлено: ${added}`);
        if (updated > 0) parts.push(`обновлено: ${updated}`);
        get().addChatMessage({
          type: 'checkpoint',
          content: `Правки обновлены (${parts.join(', ')}). Всего на рассмотрении: ${merged.length}.`,
          timestamp: new Date(),
        });
      }
    });

    client.on<PlanData>('plan', (data) => {
      const prevPlan = get().current_plan;
      const nextPlan = data.plan || [];
      set({ current_plan: nextPlan });

      const systemMessages = buildPlanSystemMessages(prevPlan || [], nextPlan);
      systemMessages.forEach((content) => {
        get().addChatMessage({
          type: 'checkpoint',
          content,
          timestamp: new Date(),
        });
      });
    });

    client.on<StreamingData>('streaming', (data) => {
      if (data.is_complete) {
        set({ streaming_message: '' });
      } else {
        set((state) => ({
          streaming_message: (state.streaming_message || '') + data.chunk,
        }));
      }
    });

    client.on('error', (data: { message: string }) => {
      get().addChatMessage({
        type: 'system',
        content: `Ошибка: ${data.message}`,
        timestamp: new Date(),
      });
      set({ is_processing: false });
    });

    client.on<{ patch_id: string; message: string }>('patch_applied', (data) => {
      get().addChatMessage({
        type: 'checkpoint',
        content: data?.message || `Правка применена: ${data?.patch_id || ''}`,
        timestamp: new Date(),
      });
    });

    client.connect(resumeId);

    set({
      websocket_client: client,
      websocket_connected: true,
    });
  },

  disconnectWebSocket: () => {
    const client = get().websocket_client;
    if (client) {
      client.disconnect();
    }
    set({
      websocket_client: null,
      websocket_connected: false,
    });
  },

  // Отправка сообщения
  sendMessage: (message: string) => {
    if (get().is_processing) return;
    
    set({ is_processing: true });
    get().addChatMessage({
      type: 'user',
      content: message,
      timestamp: new Date(),
    });

    const client = get().websocket_client;
    if (client) {
      client.sendMessage(message, get().current_resume_text);
    }
  },

  // Ответ на вопрос
  answerQuestion: (questionId: string, answer: string) => {
    if (get().is_processing) return;
    
    set({ is_processing: true });
    
    const question = get().pending_questions.find((q) => q.id === questionId);
    if (question) {
      get().addChatMessage({
        type: 'user',
        content: `Ответ на вопрос: ${answer}`,
        timestamp: new Date(),
      });
    }

    const client = get().websocket_client;
    if (client) {
      // Получаем текущий текст резюме для отправки
      const resumeText = get().current_resume_text || get().original_resume_text;
      client.answerQuestion(questionId, answer, resumeText);
    }

    // Удаляем вопрос из pending
    set((state) => ({
      pending_questions: state.pending_questions.filter((q) => q.id !== questionId),
    }));
  },

  // Ответ на все вопросы одним сообщением
  answerAllQuestions: (answers: Array<{ questionId: string; answer: string }>) => {
    if (get().is_processing) return;

    set({ is_processing: true });
    
    const state = get();
    
    // Формируем сообщение со всеми ответами
    const answersText = answers
      .map((a) => {
        const question = state.pending_questions.find((q) => q.id === a.questionId);
        return question ? `Вопрос "${question.text}": ${a.answer}` : `Ответ: ${a.answer}`;
      })
      .join('\n');
    
    get().addChatMessage({
      type: 'user',
      content: `Ответы на вопросы:\n${answersText}`,
      timestamp: new Date(),
    });

    const client = state.websocket_client;
    if (client) {
      // Получаем текущий текст резюме для отправки
      const resumeText = state.current_resume_text || state.original_resume_text;
      client.answerAllQuestions(answers, resumeText);
    }

    // Очищаем все вопросы из pending
    set({
      pending_questions: [],
    });
  },

  // Применение patch
  applyPatch: (patchId: string) => {
    const state = get();
    const patch = state.draft_patches.find((p) => p.id === patchId);
    if (!patch) {
      console.warn(`Patch ${patchId} not found in draft_patches`);
      return;
    }

    const baseText = state.current_resume_text || state.original_resume_text;
    const newText = applyPatchToText(baseText, patch);
    if (newText === null) {
      get().addChatMessage({
        type: 'system',
        content:
          'Не удалось применить правку автоматически: не найден точный фрагмент в тексте. ' +
          'Попробуйте запросить правки заново или уточнить запрос.',
        timestamp: new Date(),
      });
      return;
    }
    
    set({
      current_resume_text: newText,
      applied_patches: [...state.applied_patches, patch],
      draft_patches: state.draft_patches.filter((p) => p.id !== patchId),
    });

    get().addChatMessage({
      type: 'checkpoint',
      content: `Правка применена локально: ${patch.reason || patch.id}`,
      timestamp: new Date(),
    });

    const client = state.websocket_client;
    if (client) {
      client.applyPatch(patchId);
    }
  },

  // Отклонение patch
  rejectPatch: (patchId: string) => {
    set({
      draft_patches: get().draft_patches.filter((p) => p.id !== patchId),
    });
  },

  // Сброс всех изменений
  resetAll: () => {
    set({
      current_resume_text: get().original_resume_text,
      applied_patches: [],
      draft_patches: [],
    });
  },

  // Сохранение черновика (локально)
  saveDraft: () => {
    // В MVP просто сохраняем в localStorage
    const state = get();
    localStorage.setItem(
      `resume_edit_draft_${state.original_resume_text.substring(0, 20)}`,
      JSON.stringify({
        current_text: state.current_resume_text,
        applied_patches: state.applied_patches,
      })
    );
  },

  // Установка стримингового сообщения
  setStreamingMessage: (message: string) => {
    set({ streaming_message: message });
  },

  // Добавление сообщения в чат
  addChatMessage: (message: ChatMessage) => {
    set((state) => ({
      chat_history: [...state.chat_history, message],
    }));
  },

  // Установка pending вопросов
  setPendingQuestions: (questions: ResumeEditQuestion[]) => {
    set({ pending_questions: questions });
  },

  // Установка draft patches
  setDraftPatches: (patches: ResumeEditPatch[]) => {
    set({ draft_patches: patches });
  },
}));

// Вспомогательная функция для применения patch к тексту
function applyPatchToText(text: string, patch: ResumeEditPatch): string | null {
  if (!text || typeof text !== 'string') return null;

  const lines = text.split('\n');
  const totalLines = lines.length;

  // Конвертируем из 1-based (от бэкенда) в 0-based (для массивов)
  const startLine0 = patch.start_line - 1;
  const endLine0 = patch.end_line - 1;

  // Проверка валидности номеров строк
  if (startLine0 < 0 || endLine0 >= totalLines || startLine0 > endLine0) {
    console.warn(
      `Invalid line numbers: start_line=${patch.start_line}, end_line=${patch.end_line}, total_lines=${totalLines}`
    );
    return null;
  }

  if (patch.type === 'insert') {
    // Вставка: вставляем new_text после строки start_line
    const insertLines = patch.new_text ? patch.new_text.split('\n') : [''];
    // Вставляем после строки start_line (то есть на позицию start_line + 1 в 0-based)
    lines.splice(startLine0 + 1, 0, ...insertLines);
    return lines.join('\n');
  } else if (patch.type === 'replace') {
    // Замена: заменяем строки с start_line по end_line на new_text
    const oldLines = lines.slice(startLine0, endLine0 + 1);
    const oldTextByLines = oldLines.join('\n');
    
    // Проверяем, что old_text соответствует тексту в указанных строках
    // Нормализуем пробелы в конце строк для сравнения
    const oldTextNormalized = patch.old_text.split('\n').map(line => line.trimEnd()).join('\n');
    const actualTextNormalized = oldTextByLines.split('\n').map(line => line.trimEnd()).join('\n');
    
    if (actualTextNormalized !== oldTextNormalized) {
      console.warn(
        `old_text doesn't match actual text in lines ${patch.start_line}-${patch.end_line}`
      );
      return null;
    }

    const newLines = patch.new_text ? patch.new_text.split('\n') : [''];
    lines.splice(startLine0, endLine0 - startLine0 + 1, ...newLines);
    return lines.join('\n');
  } else if (patch.type === 'delete') {
    // Удаление: удаляем строки с start_line по end_line
    const oldLines = lines.slice(startLine0, endLine0 + 1);
    const oldTextByLines = oldLines.join('\n');
    
    // Проверяем, что old_text соответствует тексту в указанных строках
    const oldTextNormalized = patch.old_text.split('\n').map(line => line.trimEnd()).join('\n');
    const actualTextNormalized = oldTextByLines.split('\n').map(line => line.trimEnd()).join('\n');
    
    if (actualTextNormalized !== oldTextNormalized) {
      console.warn(
        `old_text doesn't match actual text in lines ${patch.start_line}-${patch.end_line}`
      );
      return null;
    }

    lines.splice(startLine0, endLine0 - startLine0 + 1);
    return lines.join('\n');
  }

  return null;
}
