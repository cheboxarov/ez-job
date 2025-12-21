import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Typography, Spin, Alert, Button, Avatar, Tag, Divider } from 'antd';
import { ArrowLeftOutlined, MessageOutlined, UserOutlined } from '@ant-design/icons';
import { getChat } from '../api/chats';
import { PageHeader } from '../components/PageHeader';
import type { ChatDetailedResponse, ChatMessage } from '../types/api';

const { Title, Text, Paragraph } = Typography;

export const ChatDetailPage = () => {
  const navigate = useNavigate();
  const { chatId } = useParams<{ chatId: string }>();
  const [chat, setChat] = useState<ChatDetailedResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (chatId) {
      loadChat(parseInt(chatId, 10));
    }
  }, [chatId]);

  const loadChat = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getChat(id);
      setChat(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке чата');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      return date.toLocaleString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return timeStr;
    }
  };

  const formatTimeShort = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'только что';
      if (diffMins < 60) return `${diffMins} мин назад`;
      if (diffHours < 24) return `${diffHours} ч назад`;
      if (diffDays < 7) return `${diffDays} дн назад`;
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    } catch {
      return timeStr;
    }
  };

  if (loading && !chat) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка чата..." />
      </div>
    );
  }

  if (error && !chat) {
    return (
      <div>
        <PageHeader title="Ошибка загрузки чата" />
        <Alert
          message="Ошибка"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/chats')}>
              Вернуться к списку
            </Button>
          }
        />
      </div>
    );
  }

  if (!chat) {
    return null;
  }

  return (
    <div>
      <PageHeader
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/chats')}
              style={{ marginRight: 8 }}
            >
              Назад
            </Button>
            <div>
              <Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 700, color: '#0f172a' }}>
                {chat.id ? `Чат #${chat.id}` : 'Чат'}
              </Title>
            </div>
          </div>
        }
      />

      <Card
        style={{
          borderRadius: 16,
          border: '1px solid #f0f0f0',
          marginBottom: 24,
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Avatar size={48} icon={<MessageOutlined />} style={{ backgroundColor: '#1890ff' }} />
              <div>
                <Text strong style={{ fontSize: 18, display: 'block' }}>
                  Чат #{chat.id}
                </Text>
                <Text type="secondary" style={{ fontSize: 14 }}>
                  Тип: {chat.type}
                </Text>
              </div>
            </div>
            {chat.unread_count > 0 && (
              <Tag color="blue" style={{ fontSize: 14, padding: '4px 12px' }}>
                {chat.unread_count} непрочитанных
              </Tag>
            )}
          </div>

          <Divider style={{ margin: '8px 0' }} />

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                Создан
              </Text>
              <Text style={{ fontSize: 14 }}>{formatTime(chat.creation_time)}</Text>
            </div>
            {chat.last_activity_time && (
              <div>
                <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                  Последняя активность
                </Text>
                <Text style={{ fontSize: 14 }}>{formatTime(chat.last_activity_time)}</Text>
              </div>
            )}
            {chat.participants_ids && chat.participants_ids.length > 0 && (
              <div>
                <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                  Участников
                </Text>
                <Text style={{ fontSize: 14 }}>{chat.participants_ids.length}</Text>
              </div>
            )}
          </div>
        </div>
      </Card>

      {chat.messages && chat.messages.items.length > 0 ? (
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <MessageOutlined />
              <span>Сообщения ({chat.messages.items.length})</span>
              {chat.messages.has_more && (
                <Tag color="default" style={{ marginLeft: 8 }}>
                  Есть еще сообщения
                </Tag>
              )}
            </div>
          }
          style={{
            borderRadius: 16,
            border: '1px solid #f0f0f0',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {chat.messages.items.map((message: ChatMessage) => (
              <Card
                key={message.id}
                size="small"
                style={{
                  borderRadius: 12,
                  border: '1px solid #f0f0f0',
                  backgroundColor: message.hidden ? '#fafafa' : '#ffffff',
                }}
                bodyStyle={{ padding: 16 }}
              >
                <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                  <Avatar
                    size={40}
                    icon={
                      message.participant_display?.is_bot ? (
                        <UserOutlined />
                      ) : (
                        <UserOutlined />
                      )
                    }
                    style={{
                      backgroundColor: message.participant_display?.is_bot ? '#52c41a' : '#1890ff',
                    }}
                  />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <Text strong style={{ fontSize: 14 }}>
                        {message.participant_display?.name || `Участник #${message.participant_id || '?'}`}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {formatTimeShort(message.creation_time)}
                      </Text>
                    </div>
                    {message.hidden && (
                      <Tag color="default" style={{ marginBottom: 8, fontSize: 11 }}>
                        Скрыто
                      </Tag>
                    )}
                    <Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {message.text}
                    </Paragraph>
                    {message.workflow_transition && (
                      <div style={{ marginTop: 8, padding: 8, backgroundColor: '#f5f5f5', borderRadius: 6 }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          Workflow: {message.workflow_transition.applicant_state}
                        </Text>
                      </div>
                    )}
                    <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        {formatTime(message.creation_time)}
                      </Text>
                      {message.type && (
                        <Tag color="default" style={{ fontSize: 11 }}>
                          {message.type}
                        </Tag>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Card>
      ) : (
        <Card
          style={{
            borderRadius: 16,
            border: '1px dashed #d9d9d9',
            textAlign: 'center',
            padding: '40px 20px',
          }}
        >
          <MessageOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
          <Text type="secondary" style={{ fontSize: 16 }}>
            В этом чате пока нет сообщений
          </Text>
        </Card>
      )}
    </div>
  );
};

