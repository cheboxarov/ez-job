import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Spin, Alert, Select, Tag, Button } from 'antd';
import { CalendarOutlined, MessageOutlined, ArrowRightOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import { useAgentActionsStore } from '../stores/agentActionsStore';
import { useEventsStore } from '../stores/eventsStore';

const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

type EventGroup = 'today' | 'yesterday' | 'thisWeek' | 'earlier';

interface GroupedEvents {
  group: EventGroup;
  label: string;
  events: AgentAction[];
}

const getEventGroup = (date: Date): EventGroup => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const thisWeekStart = new Date(today);
  thisWeekStart.setDate(today.getDate() - today.getDay());

  const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  if (eventDate.getTime() === today.getTime()) {
    return 'today';
  } else if (eventDate.getTime() === yesterday.getTime()) {
    return 'yesterday';
  } else if (eventDate >= thisWeekStart) {
    return 'thisWeek';
  } else {
    return 'earlier';
  }
};

const formatDateTime = (dateStr: string): string => {
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    
    const day = date.getDate();
    const month = date.toLocaleDateString('ru-RU', { month: 'short' });
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${day} ${month}, ${hours}:${minutes}`;
  } catch {
    return dateStr;
  }
};

const getEventTypeLabel = (type: string): string => {
  switch (type) {
    case 'send_message':
      return 'Отправка сообщения';
    case 'create_event':
      return 'Создание события';
    default:
      return type;
  }
};

const getEventTypeIcon = (type: string) => {
  switch (type) {
    case 'send_message':
      return <MessageOutlined />;
    case 'create_event':
      return <CalendarOutlined />;
    default:
      return <CalendarOutlined />;
  }
};

const getEventSubtypeLabel = (eventType?: string): string => {
  switch (eventType) {
    case 'call_request':
      return 'Запрос на созвон';
    case 'external_action_request':
      return 'Требуется действие';
    default:
      return eventType || '';
  }
};

const getEventSubtypeColor = (eventType?: string): string => {
  switch (eventType) {
    case 'call_request':
      return 'blue';
    case 'external_action_request':
      return 'orange';
    default:
      return 'default';
  }
};

export const EventsPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const { markAllAsRead, fetchUnreadCount } = useAgentActionsStore();
  const { events, loading, fetchEvents } = useEventsStore();

  useEffect(() => {
    const loadEvents = async () => {
      setError(null);
      try {
        await fetchEvents(filterType);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка при загрузке событий');
      }
    };
    loadEvents();
  }, [filterType, fetchEvents]);

  useEffect(() => {
    const markAndRefresh = async () => {
      await markAllAsRead();
      await fetchUnreadCount();
    };
    markAndRefresh();
  }, [markAllAsRead, fetchUnreadCount]);

  const groupedEvents = useMemo<GroupedEvents[]>(() => {
    const groups: Record<EventGroup, AgentAction[]> = {
      today: [],
      yesterday: [],
      thisWeek: [],
      earlier: [],
    };

    events.forEach((event) => {
      const group = getEventGroup(new Date(event.created_at));
      groups[group].push(event);
    });

    const result: GroupedEvents[] = [];

    if (groups.today.length > 0) {
      result.push({ group: 'today', label: 'Сегодня', events: groups.today });
    }
    if (groups.yesterday.length > 0) {
      result.push({ group: 'yesterday', label: 'Вчера', events: groups.yesterday });
    }
    if (groups.thisWeek.length > 0) {
      result.push({ group: 'thisWeek', label: 'На этой неделе', events: groups.thisWeek });
    }
    if (groups.earlier.length > 0) {
      result.push({ group: 'earlier', label: 'Ранее', events: groups.earlier });
    }

    return result;
  }, [events]);

  const handleEventClick = (event: AgentAction) => {
    navigate(`/chats/${event.entity_id}`);
  };

  if (loading && events.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка событий..." />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="События"
        subtitle="История действий агентов"
        icon={<CalendarOutlined />}
        breadcrumbs={[{ title: 'События' }]}
        actions={
          <Select
            value={filterType}
            onChange={setFilterType}
            style={{ width: 200 }}
            placeholder="Фильтр по типу"
          >
            <Option value="all">Все события</Option>
            <Option value="send_message">Отправка сообщений</Option>
            <Option value="create_event">Создание событий</Option>
          </Select>
        }
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
        {!loading && events.length === 0 && !error && (
          <EmptyState
            icon={<CalendarOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            title="Нет событий"
            description="Когда агенты выполнят действия, они отобразятся здесь"
          />
        )}

        {!loading && groupedEvents.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            {groupedEvents.map((group) => (
              <div key={group.group}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 12, 
                  marginBottom: 16 
                }}>
                  <Title level={4} style={{ margin: 0, color: '#0f172a', fontSize: 18, fontWeight: 600 }}>
                    {group.label}
                  </Title>
                  <Tag style={{ 
                    borderRadius: 20, 
                    padding: '2px 10px',
                    background: '#f1f5f9',
                    border: 'none',
                    color: '#64748b',
                    fontWeight: 500,
                  }}>
                    {group.events.length}
                  </Tag>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  {group.events.map((event) => (
                    <div
                      key={event.id}
                      onClick={() => handleEventClick(event)}
                      style={{
                        display: 'flex',
                        cursor: 'pointer',
                        borderRadius: 16,
                        background: '#ffffff',
                        border: '1px solid #e5e7eb',
                        overflow: 'hidden',
                        transition: 'all 0.2s ease',
                      }}
                      onMouseEnter={(e) => {
                        const stripColor = event.type === 'send_message' ? '#2563eb' : '#7c3aed';
                        e.currentTarget.style.borderColor = stripColor;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                    >
                      {/* Left gradient strip */}
                      <div
                        style={{
                          width: 6,
                          background: event.type === 'send_message'
                            ? 'linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%)'
                            : 'linear-gradient(180deg, #7c3aed 0%, #6d28d9 100%)',
                          flexShrink: 0,
                        }}
                      />

                      <div style={{ flex: 1, padding: '20px 24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <div
                              style={{
                                width: 40,
                                height: 40,
                                borderRadius: 10,
                                background: event.type === 'send_message'
                                  ? 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)'
                                  : 'linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 18,
                                color: event.type === 'send_message' ? '#2563eb' : '#7c3aed',
                              }}
                            >
                              {getEventTypeIcon(event.type)}
                            </div>
                            <div>
                              <Text strong style={{ fontSize: 16, color: '#0f172a', display: 'block' }}>
                                {getEventTypeLabel(event.type)}
                              </Text>
                              {event.type === 'create_event' && event.data.event_type && (
                                <Tag 
                                  color={getEventSubtypeColor(event.data.event_type)}
                                  style={{ marginTop: 4, borderRadius: 6 }}
                                >
                                  {getEventSubtypeLabel(event.data.event_type)}
                                </Tag>
                              )}
                            </div>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              <ClockCircleOutlined style={{ marginRight: 4 }} />
                              {formatDateTime(event.created_at)}
                            </Text>
                            <ArrowRightOutlined style={{ color: '#94a3b8', fontSize: 14 }} />
                          </div>
                        </div>

                        {event.type === 'send_message' && event.data.message_text && (
                          <Paragraph
                            ellipsis={{ rows: 2, expandable: false }}
                            style={{ margin: 0, color: '#475569', fontSize: 14, lineHeight: 1.6 }}
                          >
                            {event.data.message_text}
                          </Paragraph>
                        )}

                        {event.type === 'create_event' && event.data.message && (
                          <Paragraph
                            ellipsis={{ rows: 2, expandable: false }}
                            style={{ margin: 0, color: '#475569', fontSize: 14, lineHeight: 1.6 }}
                          >
                            {event.data.message}
                          </Paragraph>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
