import styles from '../pages/ResumeEditPage.module.css';

interface QuickActionsProps {
  onAction: (text: string) => void;
  disabled?: boolean;
}

const ACTIONS = [
  'Улучши формулировки',
  'Добавь достижения',
  'Исправь ошибки',
  'Сделай короче',
  'Добавь ключевые слова',
  'Перепиши в деловом стиле'
];

export const QuickActions = ({ onAction, disabled }: QuickActionsProps) => {
  return (
    <div className={styles.quickActions}>
      {ACTIONS.map((action) => (
        <button
          key={action}
          className={styles.actionChip}
          onClick={() => onAction(action)}
          disabled={disabled}
        >
          {action}
        </button>
      ))}
    </div>
  );
};
