import { useEffect, useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Alert, Space } from 'antd';
import { 
  SaveOutlined, 
  ReloadOutlined, 
  SettingOutlined,
  PhoneOutlined,
  SafetyOutlined,
  CheckCircleOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { getHhAuth, generateOtp, loginByCode, deleteHhAuth } from '../api/hhAuth';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';

const { Text, Paragraph } = Typography;

export const HhAuthSettingsPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'phone' | 'code'>('phone');
  const [intermediateCookies, setIntermediateCookies] = useState<Record<string, string> | null>(null);
  const [phoneNumber, setPhoneNumber] = useState<string>('');
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    loadCurrentData();
  }, []);

  const loadCurrentData = async () => {
    setLoadingData(true);
    setError(null);
    try {
      const data = await getHhAuth();
      setIsAuthorized(true);
      form.setFieldsValue({
        phone: '',
        code: '',
      });
    } catch (err: any) {
      if (err.response?.status === 404) {
        setIsAuthorized(false);
        setError(null);
      } else {
        setError(err.response?.data?.detail || 'Ошибка при загрузке данных');
        setIsAuthorized(false);
      }
    } finally {
      setLoadingData(false);
    }
  };

  const handleGenerateOtp = async (values: { phone: string }) => {
    setLoading(true);
    setError(null);
    try {
      const phone = values.phone.trim();
      if (!phone.startsWith('+7') || phone.length !== 12) {
        setError('Номер телефона должен быть в формате +7XXXXXXXXXX');
        return;
      }

      const response = await generateOtp(phone);
      setIntermediateCookies(response.cookies);
      setPhoneNumber(phone);
      setStep('code');
      message.success('Код отправлен на ваш телефон');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка при запросе кода';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginByCode = async (values: { code: string }) => {
    if (!intermediateCookies || !phoneNumber) {
      setError('Ошибка: промежуточные данные не найдены. Начните заново.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const code = values.code.trim();
      if (!code || code.length < 4) {
        setError('Код должен содержать не менее 4 символов');
        return;
      }

      await loginByCode(phoneNumber, code, intermediateCookies);
      setIsAuthorized(true);
      setStep('phone');
      setIntermediateCookies(null);
      setPhoneNumber('');
      form.resetFields();
      message.success('Авторизация успешна! Данные сохранены.');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка при входе по коду';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep('phone');
    setIntermediateCookies(null);
    setPhoneNumber('');
    form.resetFields();
    setError(null);
  };

  const handleLogout = async () => {
    setLoading(true);
    setError(null);
    try {
      await deleteHhAuth();
      setIsAuthorized(false);
      setStep('phone');
      setIntermediateCookies(null);
      setPhoneNumber('');
      form.resetFields();
      message.success('Вы вышли из HeadHunter. Данные авторизации удалены.');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка при выходе из HeadHunter';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Настройки HeadHunter"
        subtitle="Настройте авторизацию для работы с hh.ru API"
        icon={<SettingOutlined />}
        breadcrumbs={[{ title: 'Настройки HH' }]}
      />

      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        {error && (
          <Alert
            message="Ошибка"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 24, borderRadius: 12 }}
          />
        )}

        {isAuthorized && (
          <Alert
            message="Авторизация настроена"
            description={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Вы успешно авторизованы в HeadHunter. Данные сохранены и готовы к использованию.</span>
                <Button
                  danger
                  icon={<LogoutOutlined />}
                  onClick={handleLogout}
                  loading={loading}
                  size="small"
                  style={{ marginLeft: 16 }}
                >
                  Выйти из HH
                </Button>
              </div>
            }
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            style={{ marginBottom: 24, borderRadius: 12 }}
          />
        )}

        <Card
          bordered={false}
          style={{
            borderRadius: 16,
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          }}
        >
          {step === 'phone' ? (
            <div>
              <div style={{ marginBottom: 24 }}>
                <Text strong style={{ fontSize: 16 }}>
                  Вход по номеру телефона
                </Text>
                <Paragraph type="secondary" style={{ marginTop: 8, marginBottom: 0 }}>
                  Введите номер телефона для получения SMS кода
                </Paragraph>
              </div>

              <Form
                form={form}
                layout="vertical"
                onFinish={handleGenerateOtp}
                requiredMark={false}
                size="large"
              >
                <Form.Item
                  name="phone"
                  label="Номер телефона"
                  rules={[
                    { required: true, message: 'Введите номер телефона' },
                    {
                      pattern: /^\+7\d{10}$/,
                      message: 'Номер должен быть в формате +7XXXXXXXXXX',
                    },
                  ]}
                >
                  <Input
                    prefix={<PhoneOutlined />}
                    placeholder="+7XXXXXXXXXX"
                    style={{ borderRadius: 10 }}
                  />
                </Form.Item>

                <Form.Item style={{ marginBottom: 0 }}>
                  <GradientButton
                    htmlType="submit"
                    icon={<PhoneOutlined />}
                    loading={loading}
                    block
                  >
                    Запросить код
                  </GradientButton>
                </Form.Item>
              </Form>
            </div>
          ) : (
            <div>
              <div style={{ marginBottom: 24 }}>
                <Text strong style={{ fontSize: 16 }}>
                  Введите код из SMS
                </Text>
                <Paragraph type="secondary" style={{ marginTop: 8, marginBottom: 0 }}>
                  Код был отправлен на номер {phoneNumber}
                </Paragraph>
              </div>

              <Form
                form={form}
                layout="vertical"
                onFinish={handleLoginByCode}
                requiredMark={false}
                size="large"
              >
                <Form.Item
                  name="code"
                  label="Код подтверждения"
                  rules={[
                    { required: true, message: 'Введите код из SMS' },
                    { min: 4, message: 'Код должен содержать не менее 4 символов' },
                  ]}
                >
                  <Input
                    prefix={<SafetyOutlined />}
                    placeholder="Введите код"
                    style={{ borderRadius: 10 }}
                    maxLength={10}
                  />
                </Form.Item>

                <Form.Item style={{ marginBottom: 0 }}>
                  <Space size="middle" style={{ width: '100%' }}>
                    <GradientButton
                      htmlType="submit"
                      icon={<CheckCircleOutlined />}
                      loading={loading}
                      style={{ flex: 1 }}
                    >
                      Войти
                    </GradientButton>
                    <Button
                      onClick={handleReset}
                      disabled={loading}
                      style={{ borderRadius: 10 }}
                    >
                      Назад
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
