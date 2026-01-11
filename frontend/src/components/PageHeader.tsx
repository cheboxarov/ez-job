import { Breadcrumb, Button } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { HomeOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { Helmet } from 'react-helmet-async';
import { useEffect, useState } from 'react';
import styles from './PageHeader.module.css';

interface BreadcrumbItem {
  title: string;
  path?: string;
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  icon?: React.ReactNode;
}

const BASE_URL = 'https://autoffer.ru';

export const PageHeader = ({ 
  title, 
  subtitle, 
  breadcrumbs = [], 
  actions,
  icon
}: PageHeaderProps) => {
  const navigate = useNavigate();

  const breadcrumbItems = [
    { title: <Link to="/"><HomeOutlined /></Link> },
    ...breadcrumbs.map(item => ({
      title: item.path ? <Link to={item.path}>{item.title}</Link> : item.title
    })),
    { title: title }
  ];

  // Генерация структурированных данных BreadcrumbList
  const generateBreadcrumbSchema = () => {
    const itemListElement = [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Главная",
        "item": `${BASE_URL}/`
      },
      ...breadcrumbs.map((item, index) => ({
        "@type": "ListItem",
        "position": index + 2,
        "name": item.title,
        "item": item.path ? `${BASE_URL}${item.path}` : undefined
      })).filter(item => item.item !== undefined),
      {
        "@type": "ListItem",
        "position": breadcrumbs.length + 2,
        "name": title,
        "item": undefined // Текущая страница
      }
    ];

    return {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": itemListElement
    };
  };

  const breadcrumbSchema = generateBreadcrumbSchema();

  return (
    <>
      <Helmet>
        <script type="application/ld+json">
          {JSON.stringify(breadcrumbSchema)}
        </script>
      </Helmet>
      
      <header className={styles.header}>
        <div className={styles.headerTitle}>
          {breadcrumbs.length > 0 && (
            <Button 
              type="text" 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate(-1)}
              style={{ marginRight: 4 }}
            />
          )}
          <Breadcrumb items={breadcrumbItems} />
          {subtitle && (
            <span style={{ color: '#64748b', fontWeight: 400, marginLeft: 8, fontSize: 14 }}>
              / {subtitle}
            </span>
          )}
        </div>

        <div className={styles.headerActions}>
           {actions}
        </div>
      </header>
    </>
  );
};
