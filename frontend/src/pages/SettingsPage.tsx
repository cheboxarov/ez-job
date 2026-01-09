import { useEffect, useState } from 'react';
import {
  Card,
  Typography,
  message,
  Switch,
  Button,
  Space,
  Divider,
  Alert,
  Spin,
  Row,
  Col,
  Tooltip,
  Tabs,
} from 'antd';
import {
  MessageOutlined,
  CheckCircleOutlined,
  BellOutlined,
  LinkOutlined,
  CloseOutlined,
  SendOutlined,
  PhoneOutlined,
  FileTextOutlined,
  QuestionCircleOutlined,
  ThunderboltOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import {
  getTelegramSettings,
  updateTelegramSettings,
  generateTelegramLinkToken,
  unlinkTelegramAccount,
} from '../api/telegram';
import {
  getAutomationSettings,
  updateAutomationSettings,
} from '../api/automation';
import type {
  TelegramNotificationSettings,
  UpdateTelegramNotificationSettingsRequest,
  UserAutomationSettings,
  UpdateUserAutomationSettingsRequest,
} from '../types/api';

const { Text, Title, Paragraph } = Typography;

export const SettingsPage = () => {
  const [telegramSettings, setTelegramSettings] = useState<TelegramNotificationSettings | null>(null);
  const [automationSettings, setAutomationSettings] = useState<UserAutomationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generatingLink, setGeneratingLink] = useState(false);
  const [unlinking, setUnlinking] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const [telegramData, automationData] = await Promise.all([
        getTelegramSettings(),
        getAutomationSettings(),
      ]);
      setTelegramSettings(telegramData);
      setAutomationSettings(automationData);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при загрузке настроек');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTelegramSettings = async (updates: UpdateTelegramNotificationSettingsRequest) => {
    if (!telegramSettings) return;

    setSaving(true);
    try {
      const updated = await updateTelegramSettings(updates);
      setTelegramSettings(updated);
      message.success('Настройки обновлены');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при обновлении настроек');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateAutomationSettings = async (updates: UpdateUserAutomationSettingsRequest) => {
    if (!automationSettings) return;

    setSaving(true);
    try {
      const updated = await updateAutomationSettings(updates);
      setAutomationSettings(updated);
      message.success('Настройки обновлены');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при обновлении настроек');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleEnabled = async (checked: boolean) => {
    await handleUpdateTelegramSettings({ is_enabled: checked });
  };

  const handleToggleNotification = async (
    field: keyof UpdateTelegramNotificationSettingsRequest,
    checked: boolean
  ) => {
    await handleUpdateTelegramSettings({ [field]: checked });
  };

  const handleToggleAutoReply = async (checked: boolean) => {
    await handleUpdateAutomationSettings({ auto_reply_to_questions_in_chats: checked });
  };

  const handleGenerateLink = async () => {
    setGeneratingLink(true);
    try {
      const response = await generateTelegramLinkToken();
      window.open(response.link, '_blank');
      message.success('Ссылка для привязки сгенерирована. Откройте её в Telegram.');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при генерации ссылки');
    } finally {
      setGeneratingLink(false);
    }
  };

  const handleUnlink = async () => {
    setUnlinking(true);
    try {
      await unlinkTelegramAccount();
      await loadSettings();
      message.success('Telegram аккаунт отвязан');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при отвязке аккаунта');
    } finally {
      setUnlinking(false);
    }
  };

  if (loading) {
    return (
      <div>
        <PageHeader
          title="Настройки"
          subtitle="Управление уведомлениями и автоматизацией"
          icon={<BellOutlined />}
          breadcrumbs={[{ title: 'Профиль', path: '/profile' }, { title: 'Настройки' }]}
        />
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 400,
          }}
        >
          <Spin size="large" />
        </div>
      </div>
    );
  }

  if (!telegramSettings || !automationSettings) {
    return null;
  }

  const isLinked = telegramSettings.telegram_chat_id !== null;
  const isEnabled = telegramSettings.is_enabled && isLinked;

  const telegramTab = (
    <div style={{ 
      maxWidth: 800, 
      margin: '0 auto',
      padding: isMobile ? '0 16px' : '0 24px'
    }}>
      {/* Connection Status Card */}
      <Card
        bordered={true}
        style={{
          borderRadius: 20,
          border: '1px solid #e5e7eb',
          marginBottom: 24,
        }}
        styles={{
          header: {
            borderBottom: '1px solid #f1f5f9',
            padding: '20px 24px',
          },
          body: { padding: 24 },
        }}
      >
        <Row gutter={[24, 24]} align="middle">
          <Col xs={24} md={16}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div
                style={{
                  width: 56,
                  height: 56,
                  background: isLinked
                    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                    : 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
                  borderRadius: 14,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 24,
                  color: 'white',
                }}
              >
                {isLinked ? <CheckCircleOutlined /> : <MessageOutlined />}
              </div>
              <div>
                <Title level={4} style={{ margin: 0, marginBottom: 4 }}>
                  {isLinked ? 'Telegram аккаунт привязан' : 'Telegram аккаунт не привязан'}
                </Title>
                <Text type="secondary">
                  {isLinked
                    ? telegramSettings.telegram_username
                      ? `@${telegramSettings.telegram_username}`
                      : `Chat ID: ${telegramSettings.telegram_chat_id}`
                    : 'Привяжите Telegram для получения уведомлений'}
                </Text>
              </div>
            </div>
          </Col>
          <Col xs={24} md={8} style={{ display: 'flex', justifyContent: isMobile ? 'flex-start' : 'flex-end' }}>
            <Space>
              {!isLinked ? (
                <GradientButton
                  type="primary"
                  icon={<LinkOutlined />}
                  onClick={handleGenerateLink}
                  loading={generatingLink}
                >
                  Привязать Telegram
                </GradientButton>
              ) : (
                <Button
                  danger
                  icon={<CloseOutlined />}
                  onClick={handleUnlink}
                  loading={unlinking}
                >
                  Отвязать
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {!isLinked && (
        <Alert
          message="Для получения уведомлений привяжите Telegram аккаунт"
          description="Нажмите кнопку 'Привязать Telegram' и следуйте инструкциям в боте"
          type="info"
          showIcon
          style={{ marginBottom: 24, borderRadius: 12 }}
        />
      )}

      {/* Main Settings Card */}
      <Card
        bordered={true}
        style={{
          borderRadius: 20,
          border: '1px solid #e5e7eb',
          marginBottom: 24,
        }}
        styles={{
          header: {
            borderBottom: '1px solid #f1f5f9',
            padding: '20px 24px',
          },
          body: { padding: 24 },
        }}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <BellOutlined style={{ fontSize: 18, color: '#2563eb' }} />
            <Text strong style={{ fontSize: 16 }}>
              Уведомления
            </Text>
          </div>
        }
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Enable/Disable All */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '16px 20px',
              background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
              borderRadius: 12,
              border: '1px solid #e5e7eb',
            }}
          >
            <div>
              <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 4 }}>
                Включить уведомления
              </Text>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Общий переключатель для всех типов уведомлений
              </Text>
            </div>
            <Switch
              checked={isEnabled}
              onChange={handleToggleEnabled}
              disabled={!isLinked || saving}
              size="default"
            />
          </div>

          <Divider style={{ margin: '8px 0' }} />

          {/* Individual Notification Types */}
          <div>
            <Text strong style={{ fontSize: 14, display: 'block', marginBottom: 16 }}>
              Типы уведомлений:
            </Text>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              {/* Call Request */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: '#f8fafc',
                  borderRadius: 10,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <PhoneOutlined style={{ fontSize: 18, color: '#2563eb' }} />
                  <div>
                    <Text strong style={{ fontSize: 14, display: 'block' }}>
                      Собеседования
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Уведомления о назначенных собеседованиях
                    </Text>
                  </div>
                </div>
                <Switch
                  checked={telegramSettings.notify_call_request}
                  onChange={(checked) =>
                    handleToggleNotification('notify_call_request', checked)
                  }
                  disabled={!isEnabled || saving}
                />
              </div>

              {/* External Action */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: '#f8fafc',
                  borderRadius: 10,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <FileTextOutlined style={{ fontSize: 18, color: '#8b5cf6' }} />
                  <div>
                    <Text strong style={{ fontSize: 14, display: 'block' }}>
                      Требуемые действия
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Уведомления о формах и действиях для заполнения
                    </Text>
                  </div>
                </div>
                <Switch
                  checked={telegramSettings.notify_external_action}
                  onChange={(checked) =>
                    handleToggleNotification('notify_external_action', checked)
                  }
                  disabled={!isEnabled || saving}
                />
              </div>

              {/* Question Answered */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: '#f8fafc',
                  borderRadius: 10,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <QuestionCircleOutlined style={{ fontSize: 18, color: '#f59e0b' }} />
                  <div>
                    <Text strong style={{ fontSize: 14, display: 'block' }}>
                      Ответы на вопросы
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Уведомления об ответах на вопросы от работодателей
                    </Text>
                  </div>
                </div>
                <Switch
                  checked={telegramSettings.notify_question_answered}
                  onChange={(checked) =>
                    handleToggleNotification('notify_question_answered', checked)
                  }
                  disabled={!isEnabled || saving}
                />
              </div>

              {/* Message Suggestion */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: '#f8fafc',
                  borderRadius: 10,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <SendOutlined style={{ fontSize: 18, color: '#10b981' }} />
                  <div>
                    <Text strong style={{ fontSize: 14, display: 'block' }}>
                      Предложенные сообщения
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Уведомления о предложенных сообщениях для отправки
                    </Text>
                  </div>
                </div>
                <Switch
                  checked={telegramSettings.notify_message_suggestion}
                  onChange={(checked) =>
                    handleToggleNotification('notify_message_suggestion', checked)
                  }
                  disabled={!isEnabled || saving}
                />
              </div>

              {/* Vacancy Response */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: '#f8fafc',
                  borderRadius: 10,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <ThunderboltOutlined style={{ fontSize: 18, color: '#ef4444' }} />
                  <div>
                    <Text strong style={{ fontSize: 14, display: 'block' }}>
                      Отправленные отклики
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Уведомления об отправленных откликах на вакансии
                    </Text>
                  </div>
                </div>
                <Switch
                  checked={telegramSettings.notify_vacancy_response}
                  onChange={(checked) =>
                    handleToggleNotification('notify_vacancy_response', checked)
                  }
                  disabled={!isEnabled || saving}
                />
              </div>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );

  const automationTab = (
    <div style={{ 
      maxWidth: 800, 
      margin: '0 auto',
      padding: isMobile ? '0 16px' : '0 24px'
    }}>
      <Card
        bordered={true}
        style={{
          borderRadius: 20,
          border: '1px solid #e5e7eb',
          marginBottom: 24,
        }}
        styles={{
          header: {
            borderBottom: '1px solid #f1f5f9',
            padding: '20px 24px',
          },
          body: { padding: 24 },
        }}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <RobotOutlined style={{ fontSize: 18, color: '#8b5cf6' }} />
            <Text strong style={{ fontSize: 16 }}>
              Автоматизация
            </Text>
          </div>
        }
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '16px 20px',
              background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
              borderRadius: 12,
              border: '1px solid #e5e7eb',
            }}
          >
            <div>
              <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 4 }}>
                Автоматически отвечать на вопросы в чатах
              </Text>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Когда включено, система автоматически отправляет предложенные ответы на вопросы от работодателей
              </Text>
            </div>
            <Switch
              checked={automationSettings.auto_reply_to_questions_in_chats}
              onChange={handleToggleAutoReply}
              disabled={saving}
              size="default"
            />
          </div>
        </Space>
      </Card>
    </div>
  );

  return (
    <div>
      <PageHeader
        title="Настройки"
        subtitle="Управление уведомлениями и автоматизацией"
        icon={<BellOutlined />}
        breadcrumbs={[{ title: 'Профиль', path: '/profile' }, { title: 'Настройки' }]}
      />

      <div style={{ 
        maxWidth: 1000, 
        margin: '0 auto',
        padding: isMobile ? '0 16px' : '0 24px'
      }}>
        <Tabs
          defaultActiveKey="notifications"
          items={[
            {
              key: 'notifications',
              label: (
                <span>
                  <BellOutlined /> Уведомления
                </span>
              ),
              children: telegramTab,
            },
            {
              key: 'automation',
              label: (
                <span>
                  <RobotOutlined /> Автоматизация
                </span>
              ),
              children: automationTab,
            },
          ]}
          style={{
            background: 'transparent',
          }}
        />
      </div>
    </div>
  );
};
