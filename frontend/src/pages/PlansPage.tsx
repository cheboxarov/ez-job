import { useEffect, useState } from 'react';
import { Card, Typography, message, Row, Col, Spin, Button } from 'antd';
import { 
  CrownOutlined,
  UserOutlined,
  RocketOutlined,
  FireOutlined,
  CheckOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import { getAllPlans, changePlan, getMySubscriptionPlan } from '../api/subscription';
import { PageHeader } from '../components/PageHeader';
import type { SubscriptionPlanResponse, UserSubscriptionResponse } from '../types/api';

const { Text, Title } = Typography;

const getPlanConfig = (planName: string) => {
  const configs: Record<string, { 
    name: string; 
    gradient: string; 
    lightBg: string;
    accentColor: string;
    icon: React.ReactNode; 
    description: string;
    features: string[];
  }> = {
    FREE: { 
      name: 'Бесплатный', 
      gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
      lightBg: '#f8fafc',
      accentColor: '#64748b',
      icon: <UserOutlined />,
      description: 'Для знакомства с сервисом',
      features: ['Базовый поиск вакансий', 'AI-анализ совместимости', 'Ограниченные отклики'],
    },
    PLAN_1: { 
      name: 'Стартовый', 
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
      lightBg: '#eff6ff',
      accentColor: '#2563eb',
      icon: <RocketOutlined />,
      description: 'Для активного поиска',
      features: ['Расширенный поиск', 'Приоритетная обработка', 'Больше откликов в день'],
    },
    PLAN_2: { 
      name: 'Продвинутый', 
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
      lightBg: '#f5f3ff',
      accentColor: '#7c3aed',
      icon: <FireOutlined />,
      description: 'Для профессионалов',
      features: ['Все функции Стартового', 'Увеличенные лимиты', 'Приоритетная поддержка'],
    },
    PLAN_3: { 
      name: 'Максимальный', 
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      lightBg: '#fffbeb',
      accentColor: '#d97706',
      icon: <CrownOutlined />,
      description: 'Максимум возможностей',
      features: ['Безлимитный доступ', 'VIP поддержка', 'Эксклюзивные функции'],
    },
  };
  return configs[planName] || configs.FREE;
};

const formatResetPeriod = (seconds: number): string => {
  if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes} мин`;
  }
  
  if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600);
    return `${hours} ч`;
  }
  
  const days = Math.floor(seconds / 86400);
  if (days === 1) return '1 день';
  return `${days} дн`;
};

export const PlansPage = () => {
  const [plans, setPlans] = useState<SubscriptionPlanResponse[]>([]);
  const [currentPlan, setCurrentPlan] = useState<UserSubscriptionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [changingPlan, setChangingPlan] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [plansData, currentPlanData] = await Promise.all([
          getAllPlans(),
          getMySubscriptionPlan(),
        ]);
        setPlans(plansData.plans);
        setCurrentPlan(currentPlanData);
      } catch (error: any) {
        message.error(error.response?.data?.detail || 'Ошибка при загрузке планов');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleChangePlan = async (planName: string) => {
    if (currentPlan?.plan_name === planName) {
      message.info('Этот план уже активен');
      return;
    }

    setChangingPlan(planName);
    try {
      const updatedSubscription = await changePlan(planName);
      setCurrentPlan(updatedSubscription);
      const planConfig = getPlanConfig(planName);
      message.success(`План "${planConfig.name}" успешно активирован!`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при смене плана');
    } finally {
      setChangingPlan(null);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: 400,
        background: '#f8fafc',
        borderRadius: 24,
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Тарифные планы"
        subtitle="Выберите подходящий тариф для эффективного поиска работы"
        icon={<CrownOutlined />}
        breadcrumbs={[{ title: 'Планы' }]}
      />

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <Row gutter={[24, 24]}>
          {plans.map((plan) => {
            const planConfig = getPlanConfig(plan.name);
            const isCurrentPlan = currentPlan?.plan_name === plan.name;
            const isLoading = changingPlan === plan.name;

            return (
              <Col xs={24} sm={12} lg={6} key={plan.id}>
                <Card
                  bordered={false}
                  style={{
                    borderRadius: 20,
                    overflow: 'hidden',
                    border: isCurrentPlan 
                      ? `2px solid ${planConfig.accentColor}` 
                      : '1px solid #e5e7eb',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    background: isCurrentPlan ? planConfig.lightBg : 'white',
                    transition: 'all 0.2s ease',
                    boxShadow: 'none',
                  }}
                  styles={{ body: { padding: 0, flex: 1, display: 'flex', flexDirection: 'column' } }}
                >
                  {/* Header */}
                  <div style={{ padding: '24px 24px 20px', borderBottom: '1px solid #f1f5f9' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                      <div
                        style={{
                          width: 44,
                          height: 44,
                          background: planConfig.gradient,
                          borderRadius: 12,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 20,
                          color: 'white',
                        }}
                      >
                        {planConfig.icon}
                      </div>
                      {isCurrentPlan && (
                        <div
                          style={{
                            marginLeft: 'auto',
                            background: planConfig.accentColor,
                            color: 'white',
                            fontSize: 11,
                            fontWeight: 600,
                            padding: '4px 10px',
                            borderRadius: 12,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <CheckOutlined style={{ fontSize: 10 }} />
                          Активен
                        </div>
                      )}
                    </div>
                    
                    <Title level={4} style={{ margin: '0 0 4px', fontWeight: 700, fontSize: 18 }}>
                      {planConfig.name}
                    </Title>
                    <Text type="secondary" style={{ fontSize: 13 }}>
                      {planConfig.description}
                    </Text>
                  </div>

                  {/* Price */}
                  <div style={{ padding: '20px 24px', background: planConfig.lightBg }}>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
                      <Text style={{ fontSize: 36, fontWeight: 800, color: '#0f172a', lineHeight: 1 }}>
                        {plan.price === 0 ? '0' : plan.price}
                      </Text>
                      <Text style={{ fontSize: 16, fontWeight: 600, color: '#64748b' }}>
                        {plan.price === 0 ? '₽' : '₽'}
                      </Text>
                    </div>
                    {plan.duration_days > 0 && (
                      <Text type="secondary" style={{ fontSize: 13 }}>
                        за {plan.duration_days} {plan.duration_days === 1 ? 'день' : plan.duration_days < 5 ? 'дня' : 'дней'}
                      </Text>
                    )}
                    {plan.duration_days === 0 && (
                      <Text type="secondary" style={{ fontSize: 13 }}>
                        навсегда
                      </Text>
                    )}
                  </div>

                  {/* Stats */}
                  <div style={{ padding: '20px 24px', flex: 1 }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 10, 
                      padding: '12px 14px',
                      background: '#f8fafc',
                      borderRadius: 12,
                      marginBottom: 12,
                    }}>
                      <ThunderboltOutlined style={{ fontSize: 18, color: planConfig.accentColor }} />
                      <div>
                        <Text strong style={{ fontSize: 15, display: 'block', lineHeight: 1.2 }}>
                          {plan.response_limit} откликов
                        </Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          за период
                        </Text>
                      </div>
                    </div>

                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 10, 
                      padding: '12px 14px',
                      background: '#f8fafc',
                      borderRadius: 12,
                      marginBottom: 20,
                    }}>
                      <ClockCircleOutlined style={{ fontSize: 18, color: planConfig.accentColor }} />
                      <div>
                        <Text strong style={{ fontSize: 15, display: 'block', lineHeight: 1.2 }}>
                          Сброс: {formatResetPeriod(plan.reset_period_seconds)}
                        </Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          период обновления
                        </Text>
                      </div>
                    </div>

                    {/* Features list */}
                    <div style={{ marginTop: 'auto' }}>
                      {planConfig.features.map((feature, index) => (
                        <div 
                          key={index} 
                          style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: 8, 
                            marginBottom: 8,
                          }}
                        >
                          <SafetyCertificateOutlined style={{ fontSize: 14, color: planConfig.accentColor }} />
                          <Text style={{ fontSize: 13, color: '#475569' }}>{feature}</Text>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Button */}
                  <div style={{ padding: '0 24px 24px' }}>
                    <Button
                      type={isCurrentPlan ? 'default' : 'primary'}
                      block
                      size="large"
                      loading={isLoading}
                      disabled={isCurrentPlan}
                      onClick={() => handleChangePlan(plan.name)}
                      style={{
                        height: 46,
                        fontSize: 15,
                        fontWeight: 600,
                        borderRadius: 12,
                        background: isCurrentPlan ? '#f1f5f9' : planConfig.gradient,
                        border: 'none',
                        color: isCurrentPlan ? '#64748b' : 'white',
                      }}
                    >
                      {isCurrentPlan ? 'Текущий план' : 'Выбрать план'}
                    </Button>
                  </div>
                </Card>
              </Col>
            );
          })}
        </Row>
      </div>
    </div>
  );
};

