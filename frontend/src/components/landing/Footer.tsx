import styles from '../../pages/LandingPage.module.css';

export const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.footerGrid}>
          <div className={styles.footerBrand}>
            <span className={styles.logo}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--landing-primary)' }}>
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
              AutoOffer
            </span>
            <p>
              Ваш AI-помощник для автоматического поиска работы на HeadHunter. Экономьте время, получайте больше офферов.
            </p>
          </div>
          
          <div className={styles.footerColumn}>
            <h4>Продукт</h4>
            <ul className={styles.footerList}>
              <li><a href="#features" className={styles.footerLink}>Возможности</a></li>
              <li><a href="#how-it-works" className={styles.footerLink}>Как это работает</a></li>
              <li><a href="#pricing" className={styles.footerLink}>Тарифы</a></li>
            </ul>
          </div>
          
          <div className={styles.footerColumn}>
            <h4>Поддержка</h4>
            <ul className={styles.footerList}>
              <li><a href="#" className={styles.footerLink}>Telegram чат</a></li>
              <li><a href="#" className={styles.footerLink}>База знаний</a></li>
              <li><a href="#" className={styles.footerLink}>Статус системы</a></li>
            </ul>
          </div>
          
          <div className={styles.footerColumn}>
            <h4>Компания</h4>
            <ul className={styles.footerList}>
              <li><a href="#" className={styles.footerLink}>О нас</a></li>
              <li><a href="#" className={styles.footerLink}>Конфиденциальность</a></li>
              <li><a href="#" className={styles.footerLink}>Оферта</a></li>
            </ul>
          </div>
        </div>
        
        <div className={styles.footerBottom}>
          &copy; {new Date().getFullYear()} AutoOffer. Все права защищены.
        </div>
      </div>
    </footer>
  );
};
