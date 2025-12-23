import { Form, Input, Button, Typography, message, Row, Col, Divider } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { 
  RocketOutlined, 
  MailOutlined, 
  LockOutlined, 
  GoogleOutlined,
  SearchOutlined,
  FileTextOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
  SafetyOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import type { RegisterRequest } from '../types/api';

const { Title, Text } = Typography;

// Компонент карточки Bento
const BentoCard = ({ 
  icon, 
  title, 
  description, 
  gridArea,
  large = false 
}: { 
  icon: React.ReactNode; 
  title: string; 
  description: string;
  gridArea: string;
  large?: boolean;
}) => (
  <div
    style={{
      gridArea,
      background: 'rgba(255, 255, 255, 0.08)',
      backdropFilter: 'blur(12px)',
      borderRadius: 20,
      padding: large ? '32px 28px' : '24px 20px',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      transition: 'all 0.3s ease',
      cursor: 'default',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.12)';
      e.currentTarget.style.transform = 'translateY(-2px)';
      e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.15)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = 'none';
    }}
  >
    <div style={{ 
      fontSize: large ? 36 : 28, 
      color: '#fff',
      opacity: 0.9
    }}>
      {icon}
    </div>
    <div>
      <div style={{ 
        fontSize: large ? 20 : 16, 
        fontWeight: 600, 
        color: '#fff',
        marginBottom: 4
      }}>
        {title}
      </div>
      <div style={{ 
        fontSize: large ? 15 : 13, 
        color: 'rgba(255,255,255,0.7)',
        lineHeight: 1.5
      }}>
        {description}
      </div>
    </div>
  </div>
);

// Компонент статистики
const StatItem = ({ value, label }: { value: string; label: string }) => (
  <div style={{ textAlign: 'center' }}>
    <div style={{ 
      fontSize: 32, 
      fontWeight: 700, 
      color: '#fff',
      lineHeight: 1
    }}>
      {value}
    </div>
    <div style={{ 
      fontSize: 13, 
      color: 'rgba(255,255,255,0.7)',
      marginTop: 4
    }}>
      {label}
    </div>
  </div>
);

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, loading, token } = useAuthStore();

  if (token) {
    navigate('/resumes');
    return null;
  }

  const onFinish = async (values: any) => {
    try {
      const registerData: RegisterRequest = {
        email: values.email,
        password: values.password,
      };
      await register(registerData);
      message.success('Регистрация успешна');
      navigate('/resumes');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка регистрации');
    }
  };

  return (
    <Row style={{ minHeight: '100vh', background: '#ffffff' }}>
      {/* Левая часть - Форма */}
      <Col xs={24} md={12} lg={10} xl={8} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{ maxWidth: 440, width: '100%', margin: '0 auto', padding: '40px 24px' }}>
          
          {/* Логотип */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 40 }}>
            <div
              style={{
                width: 36,
                height: 36,
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(37, 99, 235, 0.2)',
              }}
            >
              <RocketOutlined style={{ color: 'white', fontSize: 18 }} />
            </div>
            <Title level={4} style={{ margin: 0, color: '#0f172a', fontWeight: 700, lineHeight: 1 }}>
              AutoOffer
            </Title>
          </div>

          <Title level={2} style={{ marginBottom: 8, color: '#1e293b' }}>
            Создать аккаунт
          </Title>
          <Text type="secondary" style={{ fontSize: 16, display: 'block', marginBottom: 32 }}>
            Начните свой путь к успешной карьере
          </Text>

          <Form
            name="register"
            onFinish={onFinish}
            layout="vertical"
            requiredMark={false}
            size="large"
          >
            <Form.Item
              name="email"
              label={<span style={{ fontWeight: 500 }}>Email</span>}
              rules={[
                { required: true, message: 'Пожалуйста, введите email' },
                { type: 'email', message: 'Некорректный email' },
              ]}
            >
              <Input 
                prefix={<MailOutlined style={{ color: '#94a3b8' }} />} 
                placeholder="name@example.com" 
                style={{ borderRadius: 8, padding: '10px 12px' }}
              />
            </Form.Item>

            <Form.Item
              name="password"
              label={<span style={{ fontWeight: 500 }}>Пароль</span>}
              rules={[
                { required: true, message: 'Пожалуйста, введите пароль' },
                { min: 6, message: 'Пароль должен быть не менее 6 символов' },
              ]}
            >
              <Input.Password 
                prefix={<LockOutlined style={{ color: '#94a3b8' }} />} 
                placeholder="Придумайте пароль" 
                style={{ borderRadius: 8, padding: '10px 12px' }}
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              label={<span style={{ fontWeight: 500 }}>Подтвердите пароль</span>}
              dependencies={['password']}
              rules={[
                { required: true, message: 'Пожалуйста, подтвердите пароль' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Пароли не совпадают'));
                  },
                }),
              ]}
            >
              <Input.Password 
                prefix={<LockOutlined style={{ color: '#94a3b8' }} />} 
                placeholder="Повторите пароль" 
                style={{ borderRadius: 8, padding: '10px 12px' }}
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 12 }}>
              <Button 
                type="primary" 
                htmlType="submit" 
                block 
                loading={loading}
                style={{ 
                  height: 48, 
                  fontSize: 16, 
                  fontWeight: 600, 
                  borderRadius: 8,
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  border: 'none',
                  boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)'
                }}
              >
                Зарегистрироваться
              </Button>
            </Form.Item>

            <div style={{ position: 'relative', margin: '32px 0', textAlign: 'center' }}>
              <Divider style={{ margin: 0, color: '#94a3b8', fontSize: 14 }}>или</Divider>
            </div>

            <Button 
              block 
              icon={<GoogleOutlined />} 
              style={{ 
                height: 48, 
                borderRadius: 8, 
                fontWeight: 500,
                borderColor: '#e2e8f0',
                color: '#475569'
              }}
              onClick={() => message.info('Регистрация через Google скоро будет доступна')}
            >
              Регистрация через Google
            </Button>

            <div style={{ textAlign: 'center', marginTop: 32, color: '#64748b' }}>
              Уже есть аккаунт?{' '}
              <a href="/login" style={{ color: '#2563eb', fontWeight: 600 }}>
                Войти
              </a>
            </div>
          </Form>
        </div>
      </Col>

      {/* Правая часть - Bento Grid */}
      <Col xs={0} md={12} lg={14} xl={16} style={{ position: 'relative', overflow: 'hidden' }}>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '40px 60px',
          }}
        >
          {/* Декоративные элементы */}
          <div style={{
            position: 'absolute',
            width: 500,
            height: 500,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, rgba(59,130,246,0) 70%)',
            top: '-10%',
            right: '-10%',
            pointerEvents: 'none',
          }} />
          <div style={{
            position: 'absolute',
            width: 400,
            height: 400,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(147,51,234,0.1) 0%, rgba(147,51,234,0) 70%)',
            bottom: '10%',
            left: '5%',
            pointerEvents: 'none',
          }} />

          <div style={{ maxWidth: 580, width: '100%', zIndex: 1 }}>
            {/* Заголовок */}
            <div style={{ marginBottom: 32, textAlign: 'center' }}>
              <Title style={{ color: 'white', marginBottom: 8, fontSize: 36 }}>
                Присоединяйся к нам
              </Title>
              <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 16 }}>
                Создай аккаунт за пару минут и начни получать офферы
              </Text>
            </div>

            {/* Статистика */}
            <div 
              style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 48,
                marginBottom: 32,
                padding: '24px 32px',
                background: 'rgba(255,255,255,0.05)',
                borderRadius: 16,
                border: '1px solid rgba(255,255,255,0.08)'
              }}
            >
              <StatItem value="1000+" label="Пользователей" />
              <StatItem value="50K+" label="Вакансий" />
              <StatItem value="24/7" label="Автоматизация" />
            </div>

            {/* Bento Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gridTemplateRows: 'auto auto auto',
                gridTemplateAreas: `
                  "main main"
                  "fast secure"
                  "free free"
                `,
                gap: 16,
              }}
            >
              <BentoCard
                gridArea="main"
                icon={<ThunderboltOutlined />}
                title="Быстрый старт"
                description="Импортируй резюме с hh.ru в один клик и начни получать отклики уже сегодня"
                large
              />
              <BentoCard
                gridArea="fast"
                icon={<CheckCircleOutlined />}
                title="Без лишних шагов"
                description="Простая регистрация — только email и пароль"
              />
              <BentoCard
                gridArea="secure"
                icon={<SafetyOutlined />}
                title="Безопасность"
                description="Твои данные надёжно защищены"
              />
              <BentoCard
                gridArea="free"
                icon={<RocketOutlined />}
                title="Бесплатный старт"
                description="Попробуй все возможности платформы без оплаты — автоотклики, аналитика и умный поиск"
              />
            </div>
          </div>
        </div>
      </Col>
    </Row>
  );
};
