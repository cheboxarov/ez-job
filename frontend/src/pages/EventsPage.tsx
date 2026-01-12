import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Spin, Alert, Tag, Button, Radio, Checkbox, Space } from 'antd';
import {
  CalendarOutlined,
  MessageOutlined,
  ArrowRightOutlined,
  ClockCircleOutlined,
  LinkOutlined,
  ProfileOutlined,
} from '@ant-design/icons';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import { useAgentActionsStore } from '../stores/agentActionsStore';
import { useEventsStore } from '../stores/eventsStore';
import type { AgentAction } from '../types/api';

const { Text, Title, Paragraph } = Typography;

const EVENT_TYPES = [
  { value: 'send_message', label: 'Отправка сообщений', icon: <MessageOutlined /> },
  { value: 'create_event', label: 'Создание событий', icon: <CalendarOutlined /> },
];

const EVENT_SUBTYPES = [
  { value: 'call_request', label: 'Запрос на созвон', color: 'blue' },
  { value: 'fill_form', label: 'Заполнение формы', color: 'gold' },
  { value: 'test_task', label: 'Тестовое задание', color: 'geekblue' },
  { value: 'external_action_request', label: 'Требуется действие', color: 'orange' },
  { value: 'question_answered', label: 'Ответ на вопрос', color: 'green' },
];

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
    case 'fill_form':
      return 'Заполнение формы';
    case 'test_task':
      return 'Тестовое задание';
    case 'external_action_request':
      return 'Требуется действие';
    case 'question_answered':
      return 'Ответ на вопрос';
    default:
      return eventType || '';
  }
};

const getEventSubtypeColor = (eventType?: string): string => {
  switch (eventType) {
    case 'call_request':
      return 'blue';
    case 'fill_form':
      return 'gold';
    case 'test_task':
      return 'geekblue';
    case 'external_action_request':
      return 'orange';
    case 'question_answered':
      return 'green';
    default:
      return 'default';
  }
};

const isTaskEventType = (eventType?: string) =>
  eventType === 'fill_form' || eventType === 'test_task';

const getEventStatusLabel = (status?: string): string => {
  switch (status) {
    case 'completed':
      return 'Выполнено';
    case 'declined':
      return 'Отклонено';
    default:
      return 'Ожидает';
  }
};

const getEventStatusColor = (status?: string): string => {
  switch (status) {
    case 'completed':
      return 'green';
    case 'declined':
      return 'red';
    default:
      return 'gold';
  }
};

export const EventsPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const { markAllAsRead, fetchUnreadCount } = useAgentActionsStore();
  const {
    events,
    loading,
    fetchEvents,
    filterMode,
    selectedTypes,
    selectedEventTypes,
    setFilterMode,
    toggleType,
    toggleEventType,
    clearFilters,
  } = useEventsStore();

  useEffect(() => {
    const loadEvents = async () => {
      setError(null);
      try {
        await fetchEvents();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка при загрузке событий');
      }
    };
    loadEvents();
  }, [filterMode, selectedTypes, selectedEventTypes, fetchEvents]);

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

  const handleOpenTaskLink = (event: React.MouseEvent, link: string) => {
    event.stopPropagation();
    window.open(link, '_blank', 'noopener,noreferrer');
  };

  const handleOpenTasksPage = (event: React.MouseEvent) => {
    event.stopPropagation();
    navigate('/tasks');
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
        <div
          style={{
            marginBottom: 24,
            padding: '16px 20px',
            background: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: 12,
          }}
        >
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            <Radio.Group
              value={filterMode}
              onChange={(event) => setFilterMode(event.target.value as 'include' | 'exclude')}
            >
              <Radio.Button value="include">Показать только</Radio.Button>
              <Radio.Button value="exclude">Исключить</Radio.Button>
            </Radio.Group>

            <div>
              <Text type="secondary">Типы событий</Text>
              <div style={{ marginTop: 8 }}>
                <Space wrap size={12}>
                  {EVENT_TYPES.map((type) => (
                    <Checkbox
                      key={type.value}
                      checked={selectedTypes.includes(type.value)}
                      onChange={() => toggleType(type.value)}
                    >
                      <Space size={6}>
                        {type.icon}
                        {type.label}
                      </Space>
                    </Checkbox>
                  ))}
                </Space>
              </div>
            </div>

            <div>
              <Text type="secondary">Подтипы create_event</Text>
              <div style={{ marginTop: 8 }}>
                <Space wrap size={12}>
                  {EVENT_SUBTYPES.map((subtype) => (
                    <Checkbox
                      key={subtype.value}
                      checked={selectedEventTypes.includes(subtype.value)}
                      onChange={() => toggleEventType(subtype.value)}
                    >
                      <Tag color={subtype.color} style={{ marginInlineEnd: 0 }}>
                        {subtype.label}
                      </Tag>
                    </Checkbox>
                  ))}
                </Space>
              </div>
            </div>

            <div>
              <Button onClick={clearFilters}>Сбросить фильтры</Button>
            </div>
          </Space>
        </div>

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
                                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 4 }}>
                                  <Tag
                                    color={getEventSubtypeColor(event.data.event_type)}
                                    style={{ borderRadius: 6, marginInlineEnd: 0 }}
                                  >
                                    {getEventSubtypeLabel(event.data.event_type)}
                                  </Tag>
                                  {isTaskEventType(event.data.event_type) && (
                                    <Tag
                                      color={getEventStatusColor(event.data.status)}
                                      style={{ borderRadius: 6, marginInlineEnd: 0 }}
                                    >
                                      {getEventStatusLabel(event.data.status)}
                                    </Tag>
                                  )}
                                </div>
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

                        {event.type === 'create_event' && isTaskEventType(event.data.event_type) && (
                          <Space size={8} style={{ marginTop: 12, flexWrap: 'wrap' }}>
                            {event.data.link && (
                              <Button
                                size="small"
                                icon={<LinkOutlined />}
                                onClick={(e) => handleOpenTaskLink(e, event.data.link)}
                              >
                                {event.data.event_type === 'fill_form'
                                  ? 'Перейти к форме'
                                  : 'Перейти к заданию'}
                              </Button>
                            )}
                            <Button
                              size="small"
                              icon={<ProfileOutlined />}
                              onClick={handleOpenTasksPage}
                            >
                              К заданиям
                            </Button>
                          </Space>
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
