import { Typography } from 'antd';

const { Title, Text } = Typography;

interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 40px',
        textAlign: 'center',
        background: 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)',
        borderRadius: 20,
        border: '1px dashed #e2e8f0',
      }}
    >
      <div
        style={{
          width: 80,
          height: 80,
          background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
          borderRadius: 20,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 24,
          fontSize: 36,
          color: '#94a3b8',
        }}
      >
        {icon}
      </div>
      
      <Title level={4} style={{ margin: 0, marginBottom: 8, color: '#334155' }}>
        {title}
      </Title>
      
      {description && (
        <Text type="secondary" style={{ fontSize: 15, maxWidth: 400, lineHeight: 1.6 }}>
          {description}
        </Text>
      )}
      
      {action && (
        <div style={{ marginTop: 24 }}>
          {action}
        </div>
      )}
    </div>
  );
};
