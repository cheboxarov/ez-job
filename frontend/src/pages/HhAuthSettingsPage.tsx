import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export const HhAuthSettingsPage = () => {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#ffffff',
        padding: '40px 16px',
      }}
    >
      <div
        style={{
          maxWidth: 480,
          width: '100%',
          textAlign: 'center',
        }}
      >
        <Title level={2} style={{ marginBottom: 16, color: '#0f172a' }}>
          Настройки HeadHunter больше не требуются
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#64748b', marginBottom: 0 }}>
          Авторизация в HH теперь используется только на странице входа. Дополнительные настройки
          больше не нужны.
        </Paragraph>
      </div>
    </div>
  );
};
