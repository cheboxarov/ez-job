import { Typography } from 'antd';
import { SEO } from '../components/SEO';

const { Title, Paragraph } = Typography;

export const RegisterPage = () => {
  return (
    <>
      <SEO 
        title="Регистрация"
        description="Регистрация в AutoOffer больше не нужна. Вход происходит через HeadHunter по номеру телефона. Начните использовать автоматизацию поиска работы уже сегодня."
        keywords="регистрация, autooffer, регистрация в системе, вход через headhunter"
        canonical="https://autoffer.ru/register"
      />
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
          Регистрация больше не нужна
              </Title>
        <Paragraph style={{ fontSize: 16, color: '#64748b', marginBottom: 0 }}>
          Вход в сервис теперь происходит только через HeadHunter по номеру телефона и коду из SMS.
          Просто перейдите на страницу входа и авторизуйтесь через HH.
        </Paragraph>
          </div>
        </div>
    </>
  );
};
