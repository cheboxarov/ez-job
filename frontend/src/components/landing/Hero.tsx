import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

export const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className={styles.hero}>
      <motion.div 
        className={styles.heroContentWrapper}
        initial={{ opacity: 0, x: -100 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <motion.h1
          className={styles.heroTitle}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
        >
          <span className={styles.heroTitleAccent}>Хватит тратить время</span> <span className={styles.heroTitleDarkBlue}>на</span><br />
          поиск работы
        </motion.h1>

        <motion.p
          className={styles.heroSubtitle}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
        >
          Наймите своего ИИ-агента, который будет мониторить HeadHunter, фильтровать вакансии, отправлять персонализированные отклики, автоматически отвечать на вопросы в чатах и проходить тесты 24/7.
        </motion.p>

        <motion.div
          className={styles.heroButtons}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
        >
          <button 
            className={styles.primaryButton}
            onClick={() => navigate('/login')}
          >
            Попробовать бесплатно
          </button>
          
          <a href="#how-it-works" className={styles.secondaryButton}>
            Как это работает ↓
          </a>
        </motion.div>

        <motion.div 
          className={styles.heroStats}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.6 }}
        >
          <div className={styles.heroStatItem}>
            <span className={styles.heroStatIcon}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </span>
            500+ пользователей
          </div>
          <div className={styles.heroStatItem}>
            <span className={styles.heroStatIcon}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </span>
            10K+ откликов
          </div>
          <div className={styles.heroStatItem}>
            <span className={styles.heroStatIcon}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </span>
            98% довольны
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
};
