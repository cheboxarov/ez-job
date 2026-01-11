import styles from '../pages/ResumeEditPage.module.css';

export const TypingIndicator = () => {
  return (
    <div className={styles.typingIndicator}>
      <div className={styles.typingDot} />
      <div className={styles.typingDot} />
      <div className={styles.typingDot} />
    </div>
  );
};
