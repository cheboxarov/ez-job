import React, { useState, useRef } from 'react';
import { Form, Input, Button, Typography, message, Row, Col } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { ThreeBackgroundContainer } from '../components/landing/ThreeBackgroundContainer';
import { Logo } from '../components/Logo';
import { SEO } from '../components/SEO';
import { 
  PhoneOutlined,
  ThunderboltOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

export const LoginPage = () => {
  const navigate = useNavigate();
  const { loginWithHhOtp, loading, token } = useAuthStore();
  const [form] = Form.useForm();
  const [step, setStep] = useState<'phone' | 'code'>('phone');
  const [intermediateCookies, setIntermediateCookies] = useState<Record<string, string> | null>(null);
  const [phoneNumber, setPhoneNumber] = useState<string>('');
  const [sendingCode, setSendingCode] = useState(false);
  const threeContainerRef = useRef<HTMLDivElement>(null);

  if (token) {
    navigate('/resumes');
    return null;
  }

  const formatPhoneInput = (value: string): string => {
    // Удаляем все символы кроме цифр, +, -, (, ), пробелов
    let cleaned = value.replace(/[^\d+\-()\s]/g, '');
    
    // Если начинается с 8, заменяем на +7
    if (cleaned.startsWith('8')) {
      cleaned = '+7' + cleaned.slice(1);
    }
    
    // Если начинается с 7, добавляем +
    if (cleaned.startsWith('7') && !cleaned.startsWith('+7')) {
      cleaned = '+' + cleaned;
    }
    
    // Если не начинается с +7, добавляем +7
    if (!cleaned.startsWith('+7') && cleaned.length > 0) {
      // Если уже есть +, но не +7, заменяем
      if (cleaned.startsWith('+')) {
        cleaned = '+7' + cleaned.slice(1);
      } else {
        cleaned = '+7' + cleaned;
      }
    }
    
    return cleaned;
  };

  const cleanPhoneNumber = (phone: string): string => {
    // Удаляем все символы кроме цифр и +
    return phone.replace(/[^\d+]/g, '');
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const formatted = formatPhoneInput(value);
    form.setFieldsValue({ phone: formatted });
  };

  const handlePhoneSubmit = async (values: { phone: string }) => {
    try {
      // Очищаем номер от всех символов кроме цифр и +
      const cleanedPhone = cleanPhoneNumber(values.phone);
      
      if (!cleanedPhone.startsWith('+7') || cleanedPhone.length !== 12) {
        message.error('Номер телефона должен быть в формате +7XXXXXXXXXX');
        return;
      }
      setSendingCode(true);
      // Запрашиваем OTP через backend (используем тот же роутер, что и в настройках)
      const { generateOtp } = await import('../api/hhAuth');
      const response = await generateOtp(cleanedPhone);
      setIntermediateCookies(response.cookies);
      setPhoneNumber(cleanedPhone);
      setStep('code');
      message.success('Код отправлен на ваш телефон');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при запросе кода');
    } finally {
      setSendingCode(false);
    }
  };

  const handleCodeSubmit = async (values: { code: string }) => {
    try {
      if (!intermediateCookies || !phoneNumber) {
        message.error('Ошибка: промежуточные данные не найдены. Начните заново.');
        return;
      }
      const code = values.code.trim();
      if (!code || code.length < 4) {
        message.error('Код должен содержать не менее 4 символов');
        return;
      }

      await loginWithHhOtp({ phone: phoneNumber, code, cookies: intermediateCookies });
      message.success('Успешный вход');
      navigate('/resumes');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка входа');
    }
  };

  return (
    <>
      <SEO 
        title="Вход в систему"
        description="Войдите в AutoOffer для управления автооткликами на вакансии HeadHunter. Авторизация через номер телефона и код из SMS."
        keywords="войти, авторизация, вход в систему, autooffer, headhunter, вход"
        canonical="https://autoffer.ru/login"
      />
      <Row style={{ minHeight: '100vh', background: '#ffffff' }}>
        {/* Левая часть - Форма */}
        <Col xs={24} md={12} lg={10} xl={8} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{ maxWidth: 440, width: '100%', margin: '0 auto', padding: '40px 24px' }}>
          
          {/* Кнопка назад */}
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/')}
            style={{
              color: '#64748b',
              padding: '4px 8px',
              marginBottom: 24,
              fontSize: 14,
              height: 'auto',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            Назад
          </Button>
          
          {/* Логотип */}
          <div style={{ marginBottom: 40 }}>
            <Logo />
          </div>

          <Title level={2} style={{ marginBottom: 8, color: '#1e293b' }}>
            С возвращением!
          </Title>
          <Text type="secondary" style={{ fontSize: 16, display: 'block', marginBottom: 32 }}>
            Введите свои данные для входа в систему
          </Text>

          <Form
            form={form}
            name="login"
            onFinish={step === 'phone' ? handlePhoneSubmit : handleCodeSubmit}
            layout="vertical"
            requiredMark={false}
            size="large"
          >
            {step === 'phone' ? (
              <>
                <Form.Item
                  name="phone"
                  label={
                    <span style={{ fontWeight: 500 }}>
                      Номер телефона{' '}
                      <span style={{ color: '#2563eb' }}>HeadHunter</span>
                    </span>
                  }
                  rules={[
                    { required: true, message: 'Пожалуйста, введите номер телефона' },
                    {
                      validator: (_, value) => {
                        if (!value) {
                          return Promise.resolve();
                        }
                        const cleaned = cleanPhoneNumber(value);
                        if (cleaned.startsWith('+7') && cleaned.length === 12) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('Номер должен быть в формате +7XXXXXXXXXX'));
                      },
                    },
                  ]}
                >
                  <Input 
                    prefix={<PhoneOutlined style={{ color: '#94a3b8' }} />} 
                    placeholder="+7 ХХХ ХХХ ХХ ХХ" 
                    style={{ borderRadius: 8, padding: '10px 12px' }}
                    onChange={handlePhoneChange}
                    maxLength={20}
                  />
                </Form.Item>
              </>
            ) : (
              <>
                <Form.Item
                  name="code"
                  label={<span style={{ fontWeight: 500 }}>Код из SMS</span>}
                  rules={[
                    { required: true, message: 'Пожалуйста, введите код' },
                    { min: 4, message: 'Код должен содержать не менее 4 символов' },
                  ]}
                >
                  <Input
                    prefix={<ThunderboltOutlined style={{ color: '#94a3b8' }} />}
                    placeholder="Введите код"
                    style={{ borderRadius: 8, padding: '10px 12px' }}
                  />
                </Form.Item>
              </>
            )}

            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                block 
                loading={step === 'phone' ? sendingCode : loading}
                disabled={step === 'phone' ? sendingCode : loading}
                style={{ 
                  height: 48, 
                  fontSize: 16, 
                  fontWeight: 600, 
                  borderRadius: 8,
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  border: '1px solid #2563eb'
                }}
              >
                {step === 'phone' ? 'Получить код' : 'Войти'}
              </Button>
            </Form.Item>

            {step === 'code' && (
              <div style={{ textAlign: 'center', marginTop: 16 }}>
                <a
                  onClick={(e) => {
                    e.preventDefault();
                    form.resetFields();
                    setStep('phone');
                    setIntermediateCookies(null);
                    setPhoneNumber('');
                  }}
                  style={{ color: '#2563eb', fontWeight: 500 }}
                >
                  Изменить номер телефона
                </a>
              </div>
            )}
          </Form>
        </div>
      </Col>

      {/* Правая часть - Bento Grid */}
      <Col xs={0} md={12} lg={14} xl={16} style={{ position: 'relative', overflow: 'hidden' }}>
        {/* 3D Background - контейнер */}
        <div 
          ref={threeContainerRef}
          style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%',
            zIndex: 0,
            overflow: 'hidden'
          }}
        >
          <ThreeBackgroundContainer containerRef={threeContainerRef} />
        </div>
        
        <div
          style={{
            position: 'relative',
            zIndex: 1,
            width: '100%',
            height: '100%',
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 58, 95, 0.7) 50%, rgba(30, 64, 175, 0.7) 100%)',
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
        </div>
        </Col>
    </Row>
    </>
  );
};
