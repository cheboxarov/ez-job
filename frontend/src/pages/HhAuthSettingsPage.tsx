import { useEffect, useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Alert, Space, Steps } from 'antd';
import { 
  SaveOutlined, 
  ReloadOutlined, 
  SettingOutlined,
  ChromeOutlined,
  CodeOutlined,
  CopyOutlined,
  CheckCircleOutlined,
  LinkOutlined
} from '@ant-design/icons';
import { getHhAuth, updateHhAuth } from '../api/hhAuth';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';

const { Text, Paragraph } = Typography;
const { TextArea } = Input;

export const HhAuthSettingsPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCurrentData();
  }, []);

  const loadCurrentData = async () => {
    setLoadingData(true);
    setError(null);
    try {
      const data = await getHhAuth();
      form.setFieldsValue({
        headers: JSON.stringify(data.headers, null, 2),
        cookies: JSON.stringify(data.cookies, null, 2),
      });
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError(null);
      } else {
        setError(err.response?.data?.detail || 'Ошибка при загрузке данных');
      }
    } finally {
      setLoadingData(false);
    }
  };

  const validateJson = (_: any, value: string) => {
    if (!value || value.trim() === '') {
      return Promise.reject(new Error('Поле обязательно для заполнения'));
    }
    try {
      const parsed = JSON.parse(value);
      if (typeof parsed !== 'object' || Array.isArray(parsed)) {
        return Promise.reject(new Error('Должен быть JSON-объект (не массив)'));
      }
      for (const [key, val] of Object.entries(parsed)) {
        if (typeof val !== 'string') {
          return Promise.reject(
            new Error(`Значение для ключа "${key}" должно быть строкой`)
          );
        }
      }
      return Promise.resolve();
    } catch (e) {
      return Promise.reject(new Error('Некорректный JSON'));
    }
  };

  const onFinish = async (values: { headers: string; cookies: string }) => {
    setLoading(true);
    setError(null);
    try {
      const headers = JSON.parse(values.headers);
      const cookies = JSON.parse(values.cookies);

      await updateHhAuth({ headers, cookies });
      message.success('Данные авторизации успешно сохранены');
    } catch (err: any) {
      if (err instanceof SyntaxError) {
        setError('Ошибка парсинга JSON. Проверьте формат данных.');
      } else {
        setError(err.response?.data?.detail || 'Ошибка при сохранении данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      title: 'Откройте hh.ru',
      description: 'Войдите в свой аккаунт HeadHunter',
      icon: <LinkOutlined />,
    },
    {
      title: 'Откройте DevTools',
      description: 'Нажмите F12 или Cmd+Option+I',
      icon: <ChromeOutlined />,
    },
    {
      title: 'Перейдите в Network',
      description: 'Выберите любой запрос к hh.ru',
      icon: <CodeOutlined />,
    },
    {
      title: 'Скопируйте данные',
      description: 'Headers и Cookies из запроса',
      icon: <CopyOutlined />,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Настройки HeadHunter"
        subtitle="Настройте авторизацию для работы с hh.ru API"
        icon={<SettingOutlined />}
        breadcrumbs={[{ title: 'Настройки HH' }]}
      />

      <div style={{ maxWidth: 900 }}>
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

        {/* Instructions Card */}
        <Card
          bordered={false}
          style={{
            borderRadius: 16,
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            marginBottom: 24,
            background: 'linear-gradient(135deg, #fefce8 0%, #fef9c3 100%)',
            border: '1px solid #fde047',
          }}
        >
          <div style={{ marginBottom: 20 }}>
            <Text strong style={{ fontSize: 16, color: '#854d0e' }}>
              Как получить данные авторизации?
            </Text>
          </div>
          
          <Steps
            direction="horizontal"
            size="small"
            items={steps.map((step, index) => ({
              title: <Text style={{ fontSize: 13, fontWeight: 500 }}>{step.title}</Text>,
              description: <Text type="secondary" style={{ fontSize: 12 }}>{step.description}</Text>,
              icon: (
                <div
                  style={{
                    width: 32,
                    height: 32,
                    background: 'white',
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ca8a04',
                    fontSize: 14,
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                >
                  {step.icon}
                </div>
              ),
            }))}
          />
        </Card>

        {/* Form Card */}
        <Card
          bordered={false}
          style={{
            borderRadius: 16,
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          }}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            requiredMark={false}
            size="large"
          >
            <Form.Item
              name="headers"
              label={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
                      borderRadius: 6,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <CodeOutlined style={{ fontSize: 14, color: '#2563eb' }} />
                  </div>
                  <span style={{ fontWeight: 500 }}>Headers (JSON)</span>
                </div>
              }
              rules={[{ validator: validateJson }]}
              tooltip="JSON-объект с заголовками для запросов к HH API"
            >
              <TextArea
                rows={10}
                placeholder='{"accept": "application/json", "user-agent": "...", ...}'
                style={{ 
                  fontFamily: 'Menlo, Monaco, Consolas, monospace', 
                  fontSize: 13,
                  borderRadius: 10,
                  background: '#f8fafc',
                }}
              />
            </Form.Item>

            <Form.Item
              name="cookies"
              label={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                      borderRadius: 6,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <CodeOutlined style={{ fontSize: 14, color: '#16a34a' }} />
                  </div>
                  <span style={{ fontWeight: 500 }}>Cookies (JSON)</span>
                </div>
              }
              rules={[{ validator: validateJson }]}
              tooltip="JSON-объект с cookies для запросов к HH API"
            >
              <TextArea
                rows={10}
                placeholder='{"hhtoken": "...", "hhuid": "...", ...}'
                style={{ 
                  fontFamily: 'Menlo, Monaco, Consolas, monospace', 
                  fontSize: 13,
                  borderRadius: 10,
                  background: '#f8fafc',
                }}
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Space size="middle">
                <GradientButton
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  Сохранить
                </GradientButton>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadCurrentData}
                  loading={loadingData}
                  style={{ borderRadius: 10, height: 44 }}
                >
                  Загрузить текущие
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      </div>
    </div>
  );
};
