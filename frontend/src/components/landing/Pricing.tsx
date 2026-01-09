import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import styles from '../../pages/LandingPage.module.css';

type PeriodType = 'week' | 'month' | '2months';

const plansByPeriod: Record<PeriodType, Array<{
  name: string;
  subtitle: string;
  price: string;
  period: string;
  responses: string;
  responsesLabel: string;
  resetPeriod: string;
  features: string[];
  isPopular: boolean;
  accent: string;
}>> = {
  week: [
    {
      name: "Стартовый",
      subtitle: "Для активного поиска",
      price: "350",
      period: "за 7 дней",
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
      price: "700",
      period: "за 7 дней",
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
      price: "1050",
      period: "за 7 дней",
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
  ],
  month: [
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
  ],
  '2months': [
    {
      name: "Стартовый",
      subtitle: "Для активного поиска",
      price: "1800",
      period: "за 60 дней",
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
      price: "3600",
      period: "за 60 дней",
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
      price: "5400",
      period: "за 60 дней",
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
  ]
};

export const Pricing = () => {
  const navigate = useNavigate();
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>('month');
  const plans = plansByPeriod[selectedPeriod];

  return (
    <section className={styles.section} id="pricing">
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Инвестиция в вашу карьеру</h2>
          <p className={styles.sectionSubtitle}>Выберите тариф, который подходит именно вам</p>
        </div>
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          marginBottom: 40,
        }}>
          <div style={{
            display: 'inline-flex',
            background: 'rgba(37, 99, 235, 0.08)',
            borderRadius: '12px',
            padding: '4px',
            gap: '4px',
          }}>
            {(['week', 'month', '2months'] as PeriodType[]).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  background: selectedPeriod === period 
                    ? 'linear-gradient(135deg, var(--landing-primary), var(--landing-accent))'
                    : 'transparent',
                  color: selectedPeriod === period ? 'white' : 'var(--landing-text-muted)',
                  fontSize: '14px',
                  fontWeight: selectedPeriod === period ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                {period === 'week' ? 'Неделя' : period === 'month' ? 'Месяц' : '2 месяца'}
              </button>
            ))}
          </div>
        </div>
        
        <div className={styles.pricingGrid}>
          {plans.map((plan, index) => (
            <motion.div 
              key={index}
              className={`${styles.pricingCard} ${plan.isPopular ? styles.pricingCardPopular : ''}`}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-100px' }}
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
