import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Typography, Spin, Alert, Badge, Avatar } from 'antd';
import { MessageOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { listChats } from '../api/chats';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import type { ChatListItem } from '../types/api';

const { Text, Paragraph } = Typography;

export const ChatsListPage = () => {
  const navigate = useNavigate();
  const [chats, setChats] = useState<ChatListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listChats();
      setChats(response.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке чатов');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr: string | null | undefined) => {
    if (!timeStr) return '';
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

  const getLastMessagePreview = (chat: ChatListItem) => {
    if (!chat.last_message) return 'Нет сообщений';
    const text = chat.last_message.text || '';
    if (text.length > 100) {
      return text.substring(0, 100) + '...';
    }
    return text;
  };

  if (loading && chats.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка чатов..." />
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Непрочитанные чаты" />

      {error && (
        <Alert
          message="Ошибка"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: 24 }}
        />
      )}

      {!loading && chats.length === 0 && !error && (
        <EmptyState
          icon={<MessageOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
          title="Нет непрочитанных чатов"
          description="Когда появятся новые сообщения, они отобразятся здесь"
        />
      )}

      {chats.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {chats.map((chat) => (
            <Card
              key={chat.id}
              hoverable
              onClick={() => navigate(`/chats/${chat.id}`)}
              style={{
                cursor: 'pointer',
                borderRadius: 12,
                border: '1px solid #f0f0f0',
                transition: 'all 0.2s',
              }}
              bodyStyle={{ padding: 16 }}
            >
              <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                <Badge count={chat.unread_count > 0 ? chat.unread_count : 0} overflowCount={99}>
                  <Avatar
                    size={48}
                    icon={<MessageOutlined />}
                    style={{ backgroundColor: '#1890ff' }}
                  />
                </Badge>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <Text strong style={{ fontSize: 16 }}>
                      {chat.display_info?.title || `Чат #${chat.id}`}
                    </Text>
                    {chat.last_message && (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {formatTime(chat.last_message.creation_time)}
                      </Text>
                    )}
                  </div>

                  {chat.display_info?.subtitle && (
                    <Text type="secondary" style={{ fontSize: 14, display: 'block', marginBottom: 4 }}>
                      {chat.display_info.subtitle}
                    </Text>
                  )}

                  {chat.last_message && (
                    <Paragraph
                      ellipsis={{ rows: 2, expandable: false }}
                      style={{ margin: 0, color: '#595959', fontSize: 14 }}
                    >
                      {getLastMessagePreview(chat)}
                    </Paragraph>
                  )}

                  <div style={{ display: 'flex', gap: 16, marginTop: 8, alignItems: 'center' }}>
                    {chat.last_activity_time && (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        <ClockCircleOutlined /> {formatTime(chat.last_activity_time)}
                      </Text>
                    )}
                    {chat.unread_count > 0 && (
                      <Badge
                        count={chat.unread_count}
                        overflowCount={99}
                        style={{ backgroundColor: '#1890ff' }}
                      />
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

