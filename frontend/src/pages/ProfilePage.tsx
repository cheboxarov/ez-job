import { useEffect, useState } from 'react';
import { Card, Typography, message, Row, Col, Progress, Spin, Tooltip } from 'antd';
import { 
  UserOutlined, 
  MailOutlined, 
  CrownOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CalendarOutlined,
  RocketOutlined,
  FireOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../stores/authStore';
import { useDailyResponsesStore } from '../stores/dailyResponsesStore';
import { getMySubscriptionPlan } from '../api/subscription';
import { PageHeader } from '../components/PageHeader';
import { useWindowSize } from '../hooks/useWindowSize';
import type { UserSubscriptionResponse } from '../types/api';

const { Text, Title } = Typography;

const formatTimeUntilReset = (seconds: number | null): string => {
  if (seconds === null || seconds <= 0) return 'Скоро';
  
  if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes} мин`;
  }
  
  if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600);
    return `${hours} ч`;
  }
  
  const days = Math.floor(seconds / 86400);
  return `${days} дн`;
};

const formatDateTime = (dateString: string | null): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const ProfilePage = () => {
  const { user } = useAuthStore();
  const [subscriptionData, setSubscriptionData] = useState<UserSubscriptionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { count, limit, remaining, secondsUntilReset, fetchDailyResponses } = useDailyResponsesStore();
  const { isMobile } = useWindowSize();

  useEffect(() => {
    const loadSubscriptionData = async () => {
      setLoading(true);
      try {
        const subscription = await getMySubscriptionPlan();
        setSubscriptionData(subscription);
        // Загружаем daily responses через store
        await fetchDailyResponses();
      } catch (error: any) {
        message.error(error.response?.data?.detail || 'Ошибка при загрузке данных подписки');
      } finally {
        setLoading(false);
      }
    };

    loadSubscriptionData();
  }, [fetchDailyResponses]);

  if (!user) return null;

  const getInitials = (phone: string | undefined | null, email: string) => {
    const source = phone && phone.length >= 4 ? phone.replace('+', '') : email;
    return source.substring(0, 2).toUpperCase();
  };

  const getPlanConfig = (planName: string) => {
    // Извлекаем базовое название плана (PLAN_1, PLAN_2, PLAN_3)
    const basePlanName = planName.replace(/_WEEK|_MONTH|_2MONTHS$/, '');
    
    const configs: Record<string, { name: string; gradient: string; icon: React.ReactNode; badge: string }> = {
      FREE: { 
        name: 'Бесплатный', 
        gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
        icon: <UserOutlined />,
        badge: 'Базовый'
      },
      PLAN_1: { 
        name: 'Стартовый', 
        gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        icon: <RocketOutlined />,
        badge: 'Популярный'
      },
      PLAN_2: { 
        name: 'Продвинутый', 
        gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
        icon: <FireOutlined />,
        badge: 'Про'
      },
      PLAN_3: { 
        name: 'Максимальный', 
        gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        icon: <CrownOutlined />,
        badge: 'VIP'
      },
    };
    return configs[basePlanName] || configs.FREE;
  };

  const getProgressColor = (percentage: number): string => {
    if (percentage < 50) return '#22c55e';
    if (percentage < 80) return '#f59e0b';
    return '#ef4444';
  };

  const usagePercentage = subscriptionData && subscriptionData.response_limit > 0
    ? Math.round((subscriptionData.responses_count / subscriptionData.response_limit) * 100)
    : 0;

  const planConfig = subscriptionData ? getPlanConfig(subscriptionData.plan_name) : getPlanConfig('FREE');

  // Вычисляем период обновления лимита в днях
  const getResetPeriodText = () => {
    if (!subscriptionData) return 'Лимит/день';
    const days = Math.floor(subscriptionData.reset_period_seconds / 86400);
    if (days === 1) {
      return 'Лимит/день';
    }
    // Правильное склонение для дней
    const daysText = days === 1 ? 'день' : days < 5 ? 'дня' : 'дней';
    return `Лимит/${days} ${daysText}`;
  };

  const getLimitText = () => {
    if (!subscriptionData) return 'откликов/день';
    const days = Math.floor(subscriptionData.reset_period_seconds / 86400);
    if (days === 1) {
      return 'откликов/день';
    }
    const daysText = days === 1 ? 'день' : days < 5 ? 'дня' : 'дней';
    return `откликов/${days} ${daysText}`;
  };

  return (
    <div>
      <PageHeader
        title="Профиль"
        subtitle="Ваш аккаунт и информация о подписке"
        icon={<UserOutlined />}
        breadcrumbs={[{ title: 'Профиль' }]}
      />

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: isMobile ? '0 16px' : '0 24px' }}>
        {loading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: 400,
            background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
            borderRadius: 24,
          }}>
            <Spin size="large" />
          </div>
        ) : subscriptionData ? (
          <>
            {/* Hero Card - User + Subscription */}
            <Card
              bordered={true}
                    style={{
                      borderRadius: 24,
                      overflow: 'hidden',
                      marginBottom: 24,
                      border: '1px solid #e5e7eb',
                    }}
              styles={{ body: { padding: 0 } }}
            >
              {/* Top gradient section */}
              <div
                style={{
                  background: planConfig.gradient,
                  padding: isMobile ? '24px 16px 60px' : '40px 40px 80px',
                  position: 'relative',
                }}
              >
                {/* Decorative circles */}
                <div style={{
                  position: 'absolute',
                  top: -50,
                  right: -50,
                  width: isMobile ? 150 : 200,
                  height: isMobile ? 150 : 200,
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '50%',
                }} />
                <div style={{
                  position: 'absolute',
                  bottom: -30,
                  left: '30%',
                  width: isMobile ? 80 : 100,
                  height: isMobile ? 80 : 100,
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: '50%',
                }} />
                
                <Row align="middle" gutter={24}>
                  <Col>
                    <div
                      style={{
                        width: isMobile ? 64 : 88,
                        height: isMobile ? 64 : 88,
                        background: 'rgba(255,255,255,0.2)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: 20,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: isMobile ? 24 : 32,
                        fontWeight: 700,
                        color: 'white',
                        border: '3px solid rgba(255,255,255,0.3)',
                      }}
                      >
                      {getInitials(user.phone, user.email)}
                    </div>
                  </Col>
                  <Col flex="auto">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                      <Title level={2} style={{ margin: 0, color: 'white', fontWeight: 700 }}>
                        {user.phone ?? 'Телефон не указан'}
                      </Title>
                      <div
                        style={{
                          padding: '4px 12px',
                          background: 'rgba(255,255,255,0.2)',
                          borderRadius: 20,
                          fontSize: 12,
                          fontWeight: 600,
                          color: 'white',
                          backdropFilter: 'blur(4px)',
                        }}
                      >
                        {planConfig.badge}
                      </div>
                    </div>
                    {user.hh_user_id && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 12 }}>
                          ID HH: {user.hh_user_id}
                        </Text>
                      </div>
                    )}
                  </Col>
                </Row>
              </div>

              {/* Plan info card overlapping */}
              <div style={{ padding: isMobile ? '0 16px' : '0 32px', marginTop: isMobile ? -32 : -48 }}>
                <Card
                  bordered={true}
                    style={{
                      borderRadius: 20,
                      border: '1px solid #e5e7eb',
                      background: 'white',
                    }}
                >
                  <Row gutter={[32, 24]} align="middle">
                    <Col xs={24} md={8}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <div
                          style={{
                            width: 56,
                            height: 56,
                            background: planConfig.gradient,
                            borderRadius: 14,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 24,
                            color: 'white',
                          }}
                        >
                          {planConfig.icon}
                        </div>
                        <div>
                          <Text type="secondary" style={{ fontSize: 13 }}>Ваш тариф</Text>
                          <Title level={4} style={{ margin: 0, fontWeight: 700 }}>
                            {planConfig.name}
                          </Title>
                        </div>
                      </div>
                    </Col>
                    
                    <Col xs={24} md={8}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <CalendarOutlined style={{ fontSize: 20, color: '#64748b' }} />
                        <div>
                          <Text type="secondary" style={{ fontSize: 13, display: 'block' }}>Статус</Text>
                          <Text strong style={{ fontSize: 15 }}>
                            {subscriptionData.days_remaining !== null && subscriptionData.days_remaining > 0
                              ? `Осталось ${subscriptionData.days_remaining} ${subscriptionData.days_remaining === 1 ? 'день' : subscriptionData.days_remaining < 5 ? 'дня' : 'дней'}`
                              : subscriptionData.expires_at === null && subscriptionData.plan_name === 'FREE'
                              ? 'Бессрочно'
                              : 'Активна'}
                          </Text>
                        </div>
                      </div>
                    </Col>
                    
                    <Col xs={24} md={8}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <CheckCircleOutlined style={{ fontSize: 20, color: '#22c55e' }} />
                        <div>
                          <Text type="secondary" style={{ fontSize: 13, display: 'block' }}>Лимит</Text>
                          <Text strong style={{ fontSize: 15 }}>
                            {subscriptionData.response_limit} {getLimitText()}
                          </Text>
                        </div>
                      </div>
                    </Col>
                  </Row>
                </Card>
              </div>

              <div style={{ height: 32 }} />
            </Card>

            {/* Stats Grid */}
            <Row gutter={isMobile ? [16, 16] : [20, 20]} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={12} lg={6}>
                <Tooltip title="Количество откликов, отправленных сегодня">
                  <Card
                    bordered={true}
                    hoverable
                    style={{
                      borderRadius: 20,
                      border: '1px solid #e5e7eb',
                      height: '100%',
                      cursor: 'default',
                      transition: 'all 0.2s ease',
                      boxShadow: 'none',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#2563eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <div
                        style={{
                          width: 64,
                          height: 64,
                          background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                          borderRadius: 16,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          margin: '0 auto 16px',
                        }}
                      >
                        <ThunderboltOutlined style={{ fontSize: 28, color: '#2563eb' }} />
                      </div>
                      <Title level={2} style={{ margin: '0 0 4px', fontWeight: 800, color: '#2563eb' }}>
                        {count}
                      </Title>
                      <Text type="secondary" style={{ fontSize: 14 }}>Откликов отправлено</Text>
                    </div>
                  </Card>
                </Tooltip>
              </Col>

              <Col xs={24} sm={12} lg={6}>
                <Tooltip title="Оставшееся количество откликов на сегодня">
                  <Card
                    bordered={true}
                    hoverable
                    style={{
                      borderRadius: 20,
                      border: '1px solid #e5e7eb',
                      height: '100%',
                      cursor: 'default',
                      transition: 'all 0.2s ease',
                      boxShadow: 'none',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#2563eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <div
                        style={{
                          width: 64,
                          height: 64,
                          background: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
                          borderRadius: 16,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          margin: '0 auto 16px',
                        }}
                      >
                        <CheckCircleOutlined style={{ fontSize: 28, color: '#16a34a' }} />
                      </div>
                      <Title level={2} style={{ margin: '0 0 4px', fontWeight: 800, color: '#16a34a' }}>
                        {remaining}
                      </Title>
                      <Text type="secondary" style={{ fontSize: 14 }}>Осталось</Text>
                    </div>
                  </Card>
                </Tooltip>
              </Col>

              <Col xs={24} sm={12} lg={6}>
                <Tooltip title="Дневной лимит откликов по вашему тарифу">
                  <Card
                    bordered={true}
                    hoverable
                    style={{
                      borderRadius: 20,
                      border: '1px solid #e5e7eb',
                      height: '100%',
                      cursor: 'default',
                      transition: 'all 0.2s ease',
                      boxShadow: 'none',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#2563eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <div
                        style={{
                          width: 64,
                          height: 64,
                          background: 'linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%)',
                          borderRadius: 16,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          margin: '0 auto 16px',
                        }}
                      >
                        <CrownOutlined style={{ fontSize: 28, color: '#9333ea' }} />
                      </div>
                      <Title level={2} style={{ margin: '0 0 4px', fontWeight: 800, color: '#9333ea' }}>
                        {subscriptionData.response_limit}
                      </Title>
                      <Text type="secondary" style={{ fontSize: 14 }}>{getResetPeriodText()}</Text>
                    </div>
                  </Card>
                </Tooltip>
              </Col>

              <Col xs={24} sm={12} lg={6}>
                <Tooltip title="Время до обновления дневного лимита">
                  <Card
                    bordered={true}
                    hoverable
                    style={{
                      borderRadius: 20,
                      border: '1px solid #e5e7eb',
                      height: '100%',
                      cursor: 'default',
                      transition: 'all 0.2s ease',
                      boxShadow: 'none',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#2563eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <div
                        style={{
                          width: 64,
                          height: 64,
                          background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                          borderRadius: 16,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          margin: '0 auto 16px',
                        }}
                      >
                        <ClockCircleOutlined style={{ fontSize: 28, color: '#d97706' }} />
                      </div>
                      <Title level={2} style={{ margin: '0 0 4px', fontWeight: 800, color: '#d97706' }}>
                        {formatTimeUntilReset(secondsUntilReset)}
                      </Title>
                      <Text type="secondary" style={{ fontSize: 14 }}>До обновления</Text>
                    </div>
                  </Card>
                </Tooltip>
              </Col>
            </Row>

            {/* Usage Progress Card */}
            <Card
              bordered={true}
              style={{
                borderRadius: 20,
                border: '1px solid #e5e7eb',
              }}
              styles={{ body: { padding: isMobile ? 16 : 24 } }}
            >
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <Text strong style={{ fontSize: 16 }}>Использование лимита</Text>
                  <Text style={{ fontSize: 20, fontWeight: 700, color: getProgressColor(usagePercentage) }}>
                    {usagePercentage}%
                  </Text>
                </div>
                <Progress
                  percent={usagePercentage}
                  strokeColor={{
                    '0%': usagePercentage < 50 ? '#22c55e' : usagePercentage < 80 ? '#f59e0b' : '#ef4444',
                    '100%': usagePercentage < 50 ? '#16a34a' : usagePercentage < 80 ? '#d97706' : '#dc2626',
                  }}
                  trailColor="#f1f5f9"
                  showInfo={false}
                  strokeWidth={12}
                  style={{ marginBottom: 8 }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary" style={{ fontSize: 13 }}>
                    Использовано: <Text strong>{subscriptionData.responses_count}</Text>
                  </Text>
                  <Text type="secondary" style={{ fontSize: 13 }}>
                    Всего: <Text strong>{subscriptionData.response_limit}</Text>
                  </Text>
                </div>
              </div>
              
              {subscriptionData.next_reset_at && (
                <div
                  style={{
                    padding: isMobile ? '12px 16px' : '16px 20px',
                    background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                    borderRadius: 14,
                    border: '1px solid #e5e7eb',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                  }}
                >
                  <ClockCircleOutlined style={{ fontSize: 20, color: '#64748b' }} />
                  <div>
                    <Text type="secondary" style={{ fontSize: 13 }}>
                      Лимит обновится: <Text strong>{formatDateTime(subscriptionData.next_reset_at)}</Text>
                    </Text>
                  </div>
                </div>
              )}
            </Card>
          </>
        ) : null}
      </div>
    </div>
  );
};
