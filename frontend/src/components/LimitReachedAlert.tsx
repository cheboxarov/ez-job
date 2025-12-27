import { Button, Typography } from 'antd';
import { LockOutlined, CrownOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Text, Title } = Typography;

interface LimitReachedAlertProps {
  limit: number;
  count: number;
}

export const LimitReachedAlert = ({ limit, count }: LimitReachedAlertProps) => {
  const navigate = useNavigate();

  const handleUnlock = () => {
    navigate('/plans');
  };

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
        borderRadius: 20,
        padding: '24px 28px',
        marginBottom: 24,
        border: '1px solid #fcd34d',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative background elements */}
      <div
        style={{
          position: 'absolute',
          top: -20,
          right: -20,
          width: 120,
          height: 120,
          background: 'radial-gradient(circle, rgba(251, 191, 36, 0.2) 0%, transparent 70%)',
          borderRadius: '50%',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: -30,
          left: '30%',
          width: 80,
          height: 80,
          background: 'radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%)',
          borderRadius: '50%',
        }}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 20, position: 'relative', flexWrap: 'wrap' }}>
        {/* Icon */}
        <div
          style={{
            width: 56,
            height: 56,
            background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            borderRadius: 16,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #f59e0b',
            flexShrink: 0,
          }}
        >
          <LockOutlined style={{ fontSize: 26, color: 'white' }} />
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 200 }}>
          <Title level={5} style={{ margin: 0, color: '#92400e', fontSize: 17, fontWeight: 700 }}>
            Достигнут лимит откликов
          </Title>
          <Text style={{ color: '#a16207', fontSize: 14, lineHeight: 1.5, display: 'block', marginTop: 4 }}>
            Использовано <Text strong style={{ color: '#92400e' }}>{count} из {limit}</Text> откликов. 
            Обновите план для продолжения.
          </Text>
        </div>

        {/* Progress indicator */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          padding: '8px 16px',
          background: 'rgba(255, 255, 255, 0.6)',
          borderRadius: 12,
          flexShrink: 0,
        }}>
          <Text style={{ fontSize: 24, fontWeight: 800, color: '#d97706', lineHeight: 1 }}>
            {count}/{limit}
          </Text>
          <Text style={{ fontSize: 11, color: '#a16207', textTransform: 'uppercase', letterSpacing: 0.5 }}>
            откликов
          </Text>
        </div>

        {/* Button */}
        <Button
          type="primary"
          size="large"
          icon={<CrownOutlined />}
          onClick={handleUnlock}
          style={{
            height: 48,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            border: '1px solid #f59e0b',
            fontWeight: 600,
            fontSize: 15,
            paddingLeft: 20,
            paddingRight: 20,
          }}
        >
          Разблокировать
        </Button>
      </div>

      {/* Bottom hint */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 6, 
        marginTop: 16,
        paddingTop: 16,
        borderTop: '1px solid rgba(251, 191, 36, 0.3)',
      }}>
        <ThunderboltOutlined style={{ color: '#d97706', fontSize: 14 }} />
        <Text style={{ fontSize: 13, color: '#a16207' }}>
          Перейдите на план с большим лимитом, чтобы отправлять больше откликов
        </Text>
      </div>
    </div>
  );
};
