/**
 * Утилиты для работы с Яндекс.Метрикой
 */

declare global {
  interface Window {
    ym?: (
      counterId: number,
      method: string,
      target: string,
      params?: Record<string, any>
    ) => void;
  }
}

/**
 * Инициализирует Яндекс.Метрику
 * @param counterId - ID счетчика Яндекс.Метрики
 */
export function initYandexMetrika(counterId: number): void {
  if (typeof window === 'undefined' || window.ym) {
    return;
  }

  // Функция для инициализации метрики (должна быть загружена из index.html)
  // Эта функция вызывается только для проверки наличия ym
}

/**
 * Отправляет событие в Яндекс.Метрику
 * @param counterId - ID счетчика
 * @param eventName - Название события
 * @param params - Дополнительные параметры события
 */
export function trackEvent(
  counterId: number,
  eventName: string,
  params?: Record<string, any>
): void {
  if (typeof window !== 'undefined' && window.ym) {
    window.ym(counterId, 'reachGoal', eventName, params);
  }
}

/**
 * Отслеживает просмотр страницы (для SPA навигации)
 * @param counterId - ID счетчика
 * @param url - URL страницы
 * @param title - Заголовок страницы
 */
export function trackPageView(
  counterId: number,
  url: string,
  title?: string
): void {
  if (typeof window !== 'undefined' && window.ym) {
    window.ym(counterId, 'hit', url, {
      title: title || document.title,
      referer: document.referrer,
    });
  }
}
