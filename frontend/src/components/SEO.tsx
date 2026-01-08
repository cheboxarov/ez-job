import { Helmet, HelmetProvider } from 'react-helmet-async';
import { useLocation } from 'react-router-dom';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonical?: string;
  ogImage?: string;
  ogType?: 'website' | 'article' | 'product';
  noIndex?: boolean;
  structuredData?: Record<string, any>;
}

const DEFAULT_TITLE = 'AutoOffer — Автоматизация поиска работы на HeadHunter';
const DEFAULT_DESCRIPTION = 'Умный помощник для поиска работы. Автоматические отклики на вакансии, AI-генерация сопроводительных писем, аналитика откликов.';
const BASE_URL = 'https://autoffer.ru';

export const SEO = ({
  title,
  description = DEFAULT_DESCRIPTION,
  keywords,
  canonical,
  ogImage = 'https://autoffer.ru/og-image.png',
  ogType = 'website',
  noIndex = false,
  structuredData,
}: SEOProps) => {
  const location = useLocation();
  const fullTitle = title ? `${title} | AutoOffer` : DEFAULT_TITLE;
  
  // Автоматическое определение canonical URL
  const canonicalUrl = canonical || `${BASE_URL}${location.pathname}${location.search}`;
  
  // Open Graph URL
  const ogUrl = canonicalUrl;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      {keywords && <meta name="keywords" content={keywords} />}
      {noIndex && <meta name="robots" content="noindex, nofollow" />}
      
      {/* Open Graph */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={ogUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:site_name" content="AutoOffer" />
      <meta property="og:locale" content="ru_RU" />
      
      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:title" content={fullTitle} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={ogImage} />
      
      {/* Canonical */}
      <link rel="canonical" href={canonicalUrl} />
      
      {/* Структурированные данные */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
};

export { HelmetProvider };
