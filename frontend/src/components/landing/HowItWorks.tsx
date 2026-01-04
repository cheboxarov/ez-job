import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

const steps = [
  {
    title: "01. Подключение",
    description: "Авторизуйтесь через HeadHunter в один клик. Мы не храним ваши пароли, работа идет через безопасный токен."
  },
  {
    title: "02. Настройка фильтров",
    description: "Укажите желаемую должность, зарплату и локацию. Добавьте стоп-слова, чтобы исключить неподходящие вакансии."
  },
  {
    title: "03. AI анализирует",
    description: "Система сканирует новые вакансии каждые 10 минут, проверяя их на соответствие вашим критериям и опыту."
  },
  {
    title: "04. Авто-отклик",
    description: "Бот генерирует персонализированное письмо и отправляет отклик. Если в вакансии есть тест, он автоматически решается. Вы получаете уведомление о приглашении."
  }
];

export const HowItWorks = () => {
  return (
    <section className={styles.section} id="how-it-works">
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Настроил за 5 минут — работает месяцами</h2>
          <p className={styles.sectionSubtitle}>Четыре простых шага от регистрации до первых собеседований</p>
        </div>
        
        <div className={styles.stepsGrid}>
          {steps.map((step, index) => (
            <motion.div 
              key={index}
              className={styles.step}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className={styles.stepLine}></div>
              <h3 className={styles.stepTitle}>{step.title}</h3>
              <p className={styles.stepDescription}>{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
