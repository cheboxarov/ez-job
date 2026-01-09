import React, { useState, useRef, useEffect } from 'react';
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
  const [step, setStep] = useState<'phone' | 'code' | 'captcha'>('phone');
  const [intermediateCookies, setIntermediateCookies] = useState<Record<string, string> | null>(null);
  const [phoneNumber, setPhoneNumber] = useState<string>('');
  const [sendingCode, setSendingCode] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [captchaState, setCaptchaState] = useState<string | null>(null);
  const [captchaKey, setCaptchaKey] = useState<string | null>(null);
  const [captchaImage, setCaptchaImage] = useState<string | null>(null);
  const [loadingCaptcha, setLoadingCaptcha] = useState(false);
  const threeContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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

  const loadCaptcha = async (cookies: Record<string, string>) => {
    try {
      setLoadingCaptcha(true);
      const { getCaptchaKey, getCaptchaPicture } = await import('../api/hhAuth');
      
      // Получаем ключ капчи
      const keyResponse = await getCaptchaKey(cookies);
      setCaptchaKey(keyResponse.captchaKey);
      setIntermediateCookies(keyResponse.cookies);
      
      // Получаем картинку капчи
      const pictureResponse = await getCaptchaPicture(keyResponse.captchaKey, keyResponse.cookies);
      setCaptchaImage(`data:${pictureResponse.contentType};base64,${pictureResponse.imageBase64}`);
      setIntermediateCookies(pictureResponse.cookies);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при загрузке капчи');
      throw error;
    } finally {
      setLoadingCaptcha(false);
    }
  };

  const sendOtpRequest = async (
    cleanedPhone: string,
    captchaData?: { captchaText: string; captchaKey: string; captchaState: string }
  ) => {
    const { generateOtp } = await import('../api/hhAuth');
    const response = await generateOtp(cleanedPhone, intermediateCookies || undefined, captchaData);
    
    // Проверяем, требуется ли капча
    if (response.result?.hhcaptcha?.isBot === true) {
      setCaptchaState(response.result.hhcaptcha.captchaState);
      setPhoneNumber(cleanedPhone);
      setIntermediateCookies(response.cookies);
      setStep('captcha');
      // Загружаем капчу
      await loadCaptcha(response.cookies);
      return;
    }
    
    // Если капча не требуется, переходим к вводу кода
    setIntermediateCookies(response.cookies);
    setPhoneNumber(cleanedPhone);
    // Очищаем состояние капчи
    setCaptchaState(null);
    setCaptchaKey(null);
    setCaptchaImage(null);
    setStep('code');
    message.success('Код отправлен на ваш телефон');
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
      await sendOtpRequest(cleanedPhone);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при запросе кода');
    } finally {
      setSendingCode(false);
    }
  };

  const handleCaptchaSubmit = async (values: { captchaText: string }) => {
    if (!captchaKey || !captchaState || !intermediateCookies || !phoneNumber) {
      message.error('Ошибка: данные капчи не найдены');
      return;
    }
    
    try {
      setSendingCode(true);
      await sendOtpRequest(phoneNumber, {
        captchaText: values.captchaText.trim(),
        captchaKey: captchaKey,
        captchaState: captchaState,
      });
      // Если успешно, форма переключится на step 'code' или 'captcha' (если снова требуется)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Ошибка при отправке капчи';
      message.error(errorMessage);
      
      // Если ошибка связана с капчей, обновляем её
      if (intermediateCookies && (errorMessage.includes('капч') || errorMessage.includes('captcha') || errorMessage.includes('бот'))) {
        try {
          await loadCaptcha(intermediateCookies);
          form.setFieldsValue({ captchaText: '' }); // Очищаем поле ввода
        } catch (loadError) {
          // Ошибка уже обработана в loadCaptcha
        }
      }
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
        <div style={{ 
          maxWidth: 440, 
          width: '100%', 
          margin: '0 auto', 
          padding: isMobile ? '24px 16px' : '40px 24px', 
          boxSizing: 'border-box' 
        }}>
          
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
            onFinish={step === 'phone' ? handlePhoneSubmit : step === 'captcha' ? handleCaptchaSubmit : handleCodeSubmit}
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
                    style={{ borderRadius: 8, padding: '10px 12px', width: '100%', boxSizing: 'border-box' }}
                    onChange={handlePhoneChange}
                    maxLength={20}
                  />
                </Form.Item>
              </>
            ) : step === 'captcha' ? (
              <>
                <Form.Item
                  label={<span style={{ fontWeight: 500 }}>Подтвердите, что вы не робот</span>}
                >
                  {loadingCaptcha ? (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                      <Text type="secondary">Загрузка капчи...</Text>
                    </div>
                  ) : captchaImage ? (
                    <div style={{ marginBottom: 16 }}>
                      <img 
                        src={captchaImage} 
                        alt="Капча" 
                        style={{ 
                          width: '100%', 
                          maxWidth: 300, 
                          height: 'auto', 
                          border: '1px solid #e5e7eb',
                          borderRadius: 8,
                          display: 'block',
                          margin: '0 auto 12px'
                        }} 
                      />
                      <div style={{ textAlign: 'center' }}>
                        <Button
                          type="link"
                          size="small"
                          onClick={async () => {
                            if (intermediateCookies) {
                              try {
                                await loadCaptcha(intermediateCookies);
                              } catch (error) {
                                // Ошибка уже обработана в loadCaptcha
                              }
                            }
                          }}
                          disabled={loadingCaptcha}
                          style={{ padding: 0 }}
                        >
                          Обновить картинку
                        </Button>
                      </div>
                    </div>
                  ) : null}
                </Form.Item>
                <Form.Item
                  name="captchaText"
                  label={<span style={{ fontWeight: 500 }}>Введите текст с картинки</span>}
                  rules={[
                    { required: true, message: 'Пожалуйста, введите текст с картинки' },
                  ]}
                >
                  <Input
                    placeholder="Введите текст капчи"
                    style={{ borderRadius: 8, padding: '10px 12px', width: '100%', boxSizing: 'border-box' }}
                    autoFocus
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
                    style={{ borderRadius: 8, padding: '10px 12px', width: '100%', boxSizing: 'border-box' }}
                  />
                </Form.Item>
              </>
            )}

            <Form.Item style={{ marginBottom: 0 }}>
              <Button 
                type="primary" 
                htmlType="submit" 
                block 
                loading={step === 'phone' || step === 'captcha' ? sendingCode : loading}
                disabled={step === 'phone' || step === 'captcha' ? sendingCode || loadingCaptcha : loading}
                style={{ 
                  height: 48, 
                  fontSize: 16, 
                  fontWeight: 600, 
                  borderRadius: 8,
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  border: '1px solid #2563eb',
                  width: '100%',
                  boxSizing: 'border-box'
                }}
              >
                {step === 'phone' ? 'Получить код' : step === 'captcha' ? 'Отправить' : 'Войти'}
              </Button>
            </Form.Item>

            {(step === 'code' || step === 'captcha') && (
              <div style={{ textAlign: 'center', marginTop: 16 }}>
                <a
                  onClick={(e) => {
                    e.preventDefault();
                    form.resetFields();
                    setStep('phone');
                    setIntermediateCookies(null);
                    setPhoneNumber('');
                    setCaptchaState(null);
                    setCaptchaKey(null);
                    setCaptchaImage(null);
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
        {!isMobile && (
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
        )}
        
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
