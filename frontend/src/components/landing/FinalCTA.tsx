import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

export const FinalCTA = () => {
  const navigate = useNavigate();

  return (
    <section className={styles.finalCta}>
      <div className={styles.container}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
        >
          <h2 className={styles.finalCtaTitle}>Хватит откладывать карьеру на потом</h2>
          <p className={styles.finalCtaSubtitle}>
            Присоединяйтесь к кандидатам, которые уже автоматизировали поиск работы и освободили 40+ часов в неделю для жизни.
          </p>
          
          <div className={styles.finalCtaButtons}>
            <button 
              className={styles.primaryButton}
              onClick={() => navigate('/login')}
              style={{ fontSize: '18px', padding: '20px 40px' }}
            >
              Запустить автопилот
            </button>
            <a 
              href="#features" 
              className={styles.secondaryButton}
              style={{ fontSize: '18px', padding: '20px 40px' }}
            >
              Узнать больше
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
