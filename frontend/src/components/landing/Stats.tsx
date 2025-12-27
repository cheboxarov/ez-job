import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

const stats = [
  {
    value: "40+",
    label: "Часов экономии в неделю"
  },
  {
    value: "24/7",
    label: "Поиск вакансий нон-стоп"
  },
  {
    value: "3x",
    label: "Выше шанс на собеседование"
  },
  {
    value: "100%",
    label: "Автоматизация рутины"
  }
];

export const Stats = () => {
  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.statsGrid}>
          {stats.map((stat, index) => (
            <motion.div 
              key={index}
              className={styles.statItem}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <span className={styles.statValue}>{stat.value}</span>
              <span className={styles.statLabel}>{stat.label}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
