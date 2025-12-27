import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

const plans = [
  {
    name: "Стартовый",
    subtitle: "Для активного поиска",
    price: "990",
    period: "за 30 дней",
    responses: "50",
    responsesLabel: "откликов за период",
    resetPeriod: "1 день",
    features: [
      "Расширенный поиск",
      "Приоритетная обработка",
      "Больше откликов в день"
    ],
    isPopular: false,
    accent: "blue"
  },
  {
    name: "Продвинутый",
    subtitle: "Для профессионалов",
    price: "1990",
    period: "за 30 дней",
    responses: "100",
    responsesLabel: "откликов за период",
    resetPeriod: "1 день",
    features: [
      "Все функции Стартового",
      "Увеличенные лимиты",
      "Приоритетная поддержка"
    ],
    isPopular: false,
    accent: "purple"
  },
  {
    name: "Максимальный",
    subtitle: "Максимум возможностей",
    price: "2990",
    period: "за 30 дней",
    responses: "200",
    responsesLabel: "откликов за период",
    resetPeriod: "1 день",
    features: [
      "Безлимитный доступ",
      "VIP поддержка",
      "Эксклюзивные функции"
    ],
    isPopular: true,
    accent: "gold"
  }
];

export const Pricing = () => {
  const navigate = useNavigate();

  return (
    <section className={styles.section} id="pricing">
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Инвестиция в вашу карьеру</h2>
          <p className={styles.sectionSubtitle}>Выберите тариф, который подходит именно вам</p>
        </div>
        
        <div className={styles.pricingGrid}>
          {plans.map((plan, index) => (
            <motion.div 
              key={index}
              className={`${styles.pricingCard} ${plan.isPopular ? styles.pricingCardPopular : ''}`}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              {plan.isPopular && (
                <div className={styles.pricingBadge}>Популярный</div>
              )}
              
              <div className={styles.pricingHeader}>
                <h3 className={styles.pricingName}>{plan.name}</h3>
                <p className={styles.pricingSubtitle}>{plan.subtitle}</p>
              </div>

              <div className={styles.pricingPrice}>
                <span className={styles.pricingAmount}>{plan.price}</span>
                <span className={styles.pricingCurrency}>₽</span>
                <span className={styles.pricingPeriod}>{plan.period}</span>
              </div>

              <div className={styles.pricingResponses}>
                <div className={styles.responsesValue}>{plan.responses}</div>
                <div className={styles.responsesLabel}>{plan.responsesLabel}</div>
              </div>

              <div className={styles.pricingReset}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="23 4 23 10 17 10"></polyline>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                <span>Сброс: <strong>{plan.resetPeriod}</strong></span>
                <span className={styles.resetSubtext}>период обновления</span>
              </div>

              <ul className={styles.pricingFeatures}>
                {plan.features.map((feature, i) => (
                  <li key={i}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <button 
                className={plan.isPopular ? styles.pricingButtonPrimary : styles.pricingButton}
                onClick={() => navigate('/login')}
              >
                Выбрать план
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
