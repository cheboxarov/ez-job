import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

const features = [
  {
    number: "01",
    title: "AI-фильтрация",
    description: "Умный алгоритм анализирует вакансии на соответствие вашему опыту и стоп-словам, отсеивая нерелевантные предложения."
  },
  {
    number: "02",
    title: "Генерация писем",
    description: "GPT создает уникальные сопроводительные письма для каждой вакансии, подчеркивая именно те навыки, которые нужны работодателю."
  },
  {
    number: "03",
    title: "Авто-отклики",
    description: "Система работает 24/7, отправляя отклики сразу после публикации вакансии, чтобы вы были в топе кандидатов."
  },
  {
    number: "04",
    title: "Безопасность",
    description: "Эмуляция действий реального пользователя и работа через официальное API HeadHunter гарантируют безопасность вашего аккаунта."
  },
  {
    number: "05",
    title: "Гибкие настройки",
    description: "Настройте фильтры по зарплате, графику, локации и ключевым словам. Исключайте конкретные компании или фразы."
  },
  {
    number: "06",
    title: "Аналитика",
    description: "Следите за статистикой просмотров и приглашений в реальном времени через удобный дашборд."
  }
];

export const Features = () => {
  return (
    <section className={styles.section} id="features">
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Что делает вас уникальным кандидатом?</h2>
          <p className={styles.sectionSubtitle}>Шесть мощных инструментов, которые превращают поиск работы в автоматизированный процесс</p>
        </div>
        
        <div className={styles.featuresGrid}>
          {features.map((feature, index) => (
            <motion.div 
              key={index}
              className={styles.featureCard}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className={styles.featureNumber}>{feature.number}</div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDescription}>{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
