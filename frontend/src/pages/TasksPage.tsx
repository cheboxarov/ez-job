import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Spin, Alert, Tag, Button, Radio, Space, Tooltip } from 'antd';
import {
  FormOutlined,
  ProfileOutlined,
  LinkOutlined,
  MessageOutlined,
  CheckOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import { useTasksStore } from '../stores/tasksStore';
import type { AgentAction, EventStatus } from '../types/api';

const { Text, Paragraph } = Typography;

const STATUS_OPTIONS: { value: EventStatus | 'all'; label: string }[] = [
  { value: 'pending', label: 'Ожидают' },
  { value: 'completed', label: 'Выполненные' },
  { value: 'declined', label: 'Отклоненные' },
  { value: 'all', label: 'Все' },
];

const getTaskTypeLabel = (eventType?: string) => {
  switch (eventType) {
    case 'fill_form':
      return 'Заполнить форму';
    case 'test_task':
      return 'Тестовое задание';
    default:
      return 'Задание';
  }
};

const getTaskTypeIcon = (eventType?: string) => {
  switch (eventType) {
    case 'fill_form':
      return <FormOutlined />;
    case 'test_task':
      return <ProfileOutlined />;
    default:
      return <ProfileOutlined />;
  }
};

const getStatusLabel = (status?: EventStatus) => {
  switch (status) {
    case 'completed':
      return 'Выполнено';
    case 'declined':
      return 'Отклонено';
    default:
      return 'Ожидает';
  }
};

const getStatusColor = (status?: EventStatus) => {
  switch (status) {
    case 'completed':
      return 'green';
    case 'declined':
      return 'red';
    default:
      return 'gold';
  }
};

const normalizeStatus = (status?: EventStatus) => status || 'pending';

export const TasksPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<{ id: string; status: EventStatus } | null>(null);
  const { tasks, loading, statusFilter, fetchTasks, setStatusFilter, updateTaskStatus } =
    useTasksStore();

  useEffect(() => {
    const loadTasks = async () => {
      setError(null);
      try {
        await fetchTasks();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка при загрузке заданий');
      }
    };
    loadTasks();
  }, [statusFilter, fetchTasks]);

  const handleOpenChat = (task: AgentAction) => {
    const dialogId = task.data?.dialog_id || task.entity_id;
    navigate(`/chats/${dialogId}`);
  };

  const handleOpenLink = (link: string) => {
    window.open(link, '_blank', 'noopener,noreferrer');
  };

  const handleStatusUpdate = async (taskId: string, status: EventStatus) => {
    setUpdating({ id: taskId, status });
    try {
      await updateTaskStatus(taskId, status);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении статуса');
    } finally {
      setUpdating(null);
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка заданий..." />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Задания"
        subtitle="Все запросы на формы и тестовые задания"
        icon={<ProfileOutlined />}
        breadcrumbs={[{ title: 'Задания' }]}
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
            <Text type="secondary">Статус</Text>
            <Radio.Group
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              {STATUS_OPTIONS.map((option) => (
                <Radio.Button key={option.value} value={option.value}>
                  {option.label}
                </Radio.Button>
              ))}
            </Radio.Group>
          </Space>
        </div>

        {!loading && tasks.length === 0 && !error && (
          <EmptyState
            icon={<ProfileOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            title="Нет заданий"
            description="Когда работодатели пришлют формы или тестовые, они появятся здесь"
          />
        )}

        {tasks.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {tasks.map((task) => {
              const eventType = task.data?.event_type;
              const status = normalizeStatus(task.data?.status);
              const link = task.data?.link;
              const linkLabel = eventType === 'fill_form' ? 'Перейти к форме' : 'Перейти к заданию';
              return (
                <div
                  key={task.id}
                  style={{
                    display: 'flex',
                    borderRadius: 16,
                    background: '#ffffff',
                    border: '1px solid #e5e7eb',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: 6,
                      background:
                        eventType === 'fill_form'
                          ? 'linear-gradient(180deg, #f59e0b 0%, #d97706 100%)'
                          : 'linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%)',
                      flexShrink: 0,
                    }}
                  />

                  <div style={{ flex: 1, padding: '20px 24px' }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        gap: 16,
                        marginBottom: 12,
                        flexWrap: 'wrap',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div
                          style={{
                            width: 40,
                            height: 40,
                            borderRadius: 10,
                            background:
                              eventType === 'fill_form'
                                ? 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                                : 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 18,
                            color: eventType === 'fill_form' ? '#b45309' : '#2563eb',
                          }}
                        >
                          {getTaskTypeIcon(eventType)}
                        </div>
                        <div>
                          <Text strong style={{ fontSize: 16, color: '#0f172a', display: 'block' }}>
                            {getTaskTypeLabel(eventType)}
                          </Text>
                          <Tag color={getStatusColor(status)} style={{ marginTop: 6 }}>
                            {getStatusLabel(status)}
                          </Tag>
                        </div>
                      </div>

                      <Space size={8} wrap>
                        {link && (
                          <Tooltip title="Открыть ссылку">
                            <Button
                              icon={<LinkOutlined />}
                              onClick={() => handleOpenLink(link)}
                            >
                              {linkLabel}
                            </Button>
                          </Tooltip>
                        )}
                        <Button icon={<MessageOutlined />} onClick={() => handleOpenChat(task)}>
                          Открыть чат
                        </Button>
                      </Space>
                    </div>

                    {task.data?.message && (
                      <Paragraph
                        style={{ marginBottom: 16, color: '#475569', fontSize: 14, lineHeight: 1.6 }}
                      >
                        {task.data.message}
                      </Paragraph>
                    )}

                    <Space size={12} wrap>
                      <Button
                        type="primary"
                        icon={<CheckOutlined />}
                        disabled={status !== 'pending'}
                        loading={updating?.id === task.id && updating.status === 'completed'}
                        onClick={() => handleStatusUpdate(task.id, 'completed')}
                      >
                        Выполнено
                      </Button>
                      <Button
                        danger
                        icon={<CloseOutlined />}
                        disabled={status !== 'pending'}
                        loading={updating?.id === task.id && updating.status === 'declined'}
                        onClick={() => handleStatusUpdate(task.id, 'declined')}
                      >
                        Отказаться
                      </Button>
                    </Space>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
