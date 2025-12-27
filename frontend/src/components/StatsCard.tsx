import { Typography } from 'antd';

const { Text } = Typography;

interface StatsCardProps {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

const colorMap = {
  blue: {
    bg: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
    icon: '#2563eb',
    border: '#bfdbfe',
  },
  green: {
    bg: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
    icon: '#16a34a',
    border: '#bbf7d0',
  },
  purple: {
    bg: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
    icon: '#9333ea',
    border: '#e9d5ff',
  },
  orange: {
    bg: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
    icon: '#ea580c',
    border: '#fde68a',
  },
};

export const StatsCard = ({ icon, value, label, color = 'blue' }: StatsCardProps) => {
  const colors = colorMap[color];
  
  return (
    <div
      style={{
        padding: '20px 24px',
        background: colors.bg,
        borderRadius: 16,
        border: `1px solid ${colors.border}`,
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        flex: 1,
        minWidth: 180,
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          background: 'white',
          borderRadius: 12,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 22,
          color: colors.icon,
        }}
      >
        {icon}
      </div>
      
      <div>
        <div style={{ fontSize: 28, fontWeight: 700, color: '#0f172a', lineHeight: 1 }}>
          {value}
        </div>
        <Text type="secondary" style={{ fontSize: 13 }}>
          {label}
        </Text>
      </div>
    </div>
  );
};
