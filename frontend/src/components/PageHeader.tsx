import { Typography, Breadcrumb } from 'antd';
import { Link } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

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

export const PageHeader = ({ 
  title, 
  subtitle, 
  breadcrumbs = [], 
  actions,
  icon
}: PageHeaderProps) => {
  const breadcrumbItems = [
    { title: <Link to="/"><HomeOutlined /></Link> },
    ...breadcrumbs.map(item => ({
      title: item.path ? <Link to={item.path}>{item.title}</Link> : item.title
    }))
  ];

  return (
    <div
      style={{
        width: '100%',
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        marginBottom: 20,
        padding: '16px 20px',
        background: '#ffffff',
        borderRadius: 16,
        border: '1px solid #e5e7eb',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Gradient accent */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: 4,
          background: 'linear-gradient(180deg, #2563eb 0%, #7c3aed 100%)',
          borderRadius: '16px 0 0 16px',
        }}
      />
      
      <Breadcrumb items={breadcrumbItems} />
      
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16 
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div>
            <Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 700, color: '#0f172a' }}>
              {title}
            </Title>
            {subtitle && (
              <Text type="secondary" style={{ fontSize: 14, marginTop: 2, display: 'block' }}>
                {subtitle}
              </Text>
            )}
          </div>
        </div>
        
        {actions && (
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};
