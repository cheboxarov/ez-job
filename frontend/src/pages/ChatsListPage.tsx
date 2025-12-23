import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Spin, Alert, Badge, Avatar } from 'antd';
import { MessageOutlined, ClockCircleOutlined, ArrowRightOutlined } from '@ant-design/icons';
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
    if (text.length > 120) {
      return text.substring(0, 120) + '...';
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
      <PageHeader
        title="Непрочитанные чаты"
        subtitle="Диалоги с работодателями, требующие вашего внимания"
        icon={<MessageOutlined />}
        breadcrumbs={[{ title: 'Чаты' }]}
      />

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

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {!loading && chats.length === 0 && !error && (
          <EmptyState
            icon={<MessageOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            title="Нет непрочитанных чатов"
            description="Когда появятся новые сообщения, они отобразятся здесь"
          />
        )}

        {chats.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => navigate(`/chats/${chat.id}`)}
                style={{
                  display: 'flex',
                  cursor: 'pointer',
                  borderRadius: 16,
                  background: '#ffffff',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                  overflow: 'hidden',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.12)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                {/* Left gradient strip */}
                <div
                  style={{
                    width: 6,
                    background: chat.unread_count > 0
                      ? 'linear-gradient(180deg, #2563eb 0%, #7c3aed 100%)'
                      : 'linear-gradient(180deg, #e2e8f0 0%, #cbd5e1 100%)',
                    flexShrink: 0,
                  }}
                />

                <div style={{ flex: 1, padding: '20px 24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <Badge count={chat.unread_count > 0 ? chat.unread_count : 0} overflowCount={99}>
                        <div
                          style={{
                            width: 44,
                            height: 44,
                            background: chat.unread_count > 0
                              ? 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)'
                              : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                            borderRadius: 12,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <MessageOutlined style={{ 
                            fontSize: 20, 
                            color: chat.unread_count > 0 ? '#2563eb' : '#64748b' 
                          }} />
                        </div>
                      </Badge>
                      <div>
                        <Text strong style={{ fontSize: 16, color: '#0f172a', display: 'block' }}>
                          {chat.display_info?.title || `Чат #${chat.id}`}
                        </Text>
                        {chat.display_info?.subtitle && (
                          <Text type="secondary" style={{ fontSize: 13 }}>
                            {chat.display_info.subtitle}
                          </Text>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {chat.last_message && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <ClockCircleOutlined style={{ marginRight: 4 }} />
                          {formatTime(chat.last_message.creation_time)}
                        </Text>
                      )}
                      <ArrowRightOutlined style={{ color: '#94a3b8', fontSize: 14 }} />
                    </div>
                  </div>

                  {chat.last_message && (
                    <Paragraph
                      ellipsis={{ rows: 2, expandable: false }}
                      style={{ margin: 0, color: '#475569', fontSize: 14, lineHeight: 1.6 }}
                    >
                      {getLastMessagePreview(chat)}
                    </Paragraph>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
