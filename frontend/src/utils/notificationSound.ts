/** Утилита для воспроизведения звука уведомлений. */

let audioContext: AudioContext | null = null;

/**
 * Инициализирует AudioContext (вызывается при первом использовании).
 */
function initAudioContext(): AudioContext {
  if (!audioContext) {
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  }
  return audioContext;
}

/**
 * Воспроизводит короткий звук уведомления.
 * Использует Web Audio API для генерации простого тонального сигнала.
 */
export function playNotificationSound(): void {
  try {
    const ctx = initAudioContext();
    
    // Создаём осциллятор для генерации звука
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    // Подключаем осциллятор к gain node, затем к выходу
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    // Настройки звука: частота 800 Гц (приятный тон)
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    // Настройки громкости: плавное нарастание и затухание
    gainNode.gain.setValueAtTime(0, ctx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.01);
    gainNode.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.15);
    
    // Воспроизводим звук 150 мс
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.15);
  } catch (error) {
    // Игнорируем ошибки воспроизведения звука (например, если пользователь не взаимодействовал со страницей)
    console.warn('Не удалось воспроизвести звук уведомления:', error);
  }
}
