import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from '../../pages/LandingPage.module.css';

export const Header = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`${styles.header} ${scrolled ? styles.headerScrolled : ''}`}>
      <div className={styles.container}>
        <div className={styles.headerInner}>
          <a href="/" className={styles.logo}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--landing-primary)' }}>
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            AutoOffer
          </a>

          <div className={styles.navLinks}>
            <a href="#features" className={styles.navLink}>Возможности</a>
            <a href="#how-it-works" className={styles.navLink}>Как это работает</a>
            <a href="#pricing" className={styles.navLink}>Тарифы</a>
          </div>

          <button 
            className={styles.headerButton}
            onClick={() => navigate('/login')}
          >
            Войти
          </button>
        </div>
      </div>
    </nav>
  );
};
