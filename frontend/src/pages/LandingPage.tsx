import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { SEO } from '../components/SEO';
import { Header } from '../components/landing/Header';
import { Hero } from '../components/landing/Hero';
import { Features } from '../components/landing/Features';
import { HowItWorks } from '../components/landing/HowItWorks';
import { Pricing } from '../components/landing/Pricing';
import { FinalCTA } from '../components/landing/FinalCTA';
import { Footer } from '../components/landing/Footer';
import { ThreeBackground } from '../components/landing/ThreeBackground';
import styles from './LandingPage.module.css';

export const LandingPage = () => {
  const navigate = useNavigate();
  const { token } = useAuthStore();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    if (token) {
      navigate('/resumes', { replace: true });
    }
  }, [token, navigate]);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  if (token) {
    return null;
  }

  return (
    <div className={styles.landing}>
      <SEO 
        canonical="https://autooffer.ru/"
        keywords="поиск работы, headhunter, hh.ru, автоотклики, вакансии, резюме, сопроводительное письмо"
      />
      
      {!isMobile && <ThreeBackground />}
      
      <Header />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Pricing />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
};
