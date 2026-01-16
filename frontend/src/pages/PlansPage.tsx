import { useEffect, useState } from 'react';
import { Card, Typography, message, Row, Col, Spin, Button, Segmented, Space } from 'antd';
import { Link } from 'react-router-dom';
import { 
  CrownOutlined,
  UserOutlined,
  RocketOutlined,
  FireOutlined,
  CheckOutlined,
  ThunderboltOutlined,
  SafetyCertificateOutlined,
  FileDoneOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { getAllPlans, changePlan, getMySubscriptionPlan } from '../api/subscription';
import { PageHeader } from '../components/PageHeader';
import type { SubscriptionPlanResponse, UserSubscriptionResponse } from '../types/api';
import { useAuthStore } from '../stores/authStore';

const { Text, Title } = Typography;

type PeriodType = 'week' | 'month' | '2months';

const getPlanConfig = (planName: string) => {
  // Извлекаем базовое название плана (PLAN_1, PLAN_2, PLAN_3)
  const basePlanName = planName.replace(/_WEEK|_MONTH|_2MONTHS$/, '');
  
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
      features: [
        'Базовый поиск вакансий',
        'Ограниченный анализ резюме',
        'До 10 откликов за период',
      ],
    },
    PLAN_1: { 
      name: 'Стартовый', 
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
      lightBg: '#eff6ff',
      accentColor: '#2563eb',
      icon: <RocketOutlined />,
      description: 'Для активного поиска',
      features: [
        'AI-анализ резюме с рекомендациями',
        'Анализ чатов с работодателями',
        'Автоответы на вопросы в чатах',
        'Автоотклики на подходящие вакансии',
        'Уведомления о собеседованиях и событиях',
        'Генерация сопроводительных писем',
        'Умный поиск вакансий',
        'До 50 откликов за период',
      ],
    },
    PLAN_2: { 
      name: 'Продвинутый', 
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
      lightBg: '#f5f3ff',
      accentColor: '#7c3aed',
      icon: <FireOutlined />,
      description: 'Для профессионалов',
      features: [
        'Все функции Стартового',
        'Увеличенные лимиты откликов (до 100)',
        'Приоритетная обработка запросов',
        'Расширенная аналитика',
      ],
    },
    PLAN_3: { 
      name: 'Максимальный', 
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      lightBg: '#fffbeb',
      accentColor: '#d97706',
      icon: <CrownOutlined />,
      description: 'Максимум возможностей',
      features: [
        'Все функции Продвинутого',
        'Безлимитные отклики (до 200)',
        'VIP поддержка',
        'Максимальная скорость обработки',
      ],
    },
  };
  return configs[basePlanName] || configs.FREE;
};

export const PlansPage = () => {
  const { user } = useAuthStore();
  const [plans, setPlans] = useState<SubscriptionPlanResponse[]>([]);
  const [currentPlan, setCurrentPlan] = useState<UserSubscriptionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [changingPlan, setChangingPlan] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>('month');
  const isAdmin = user?.is_superuser === true;

  const getDurationDaysForPeriod = (period: PeriodType): number => {
    switch (period) {
      case 'week':
        return 7;
      case 'month':
        return 30;
      case '2months':
        return 60;
      default:
        return 30;
    }
  };

  const filteredPlans = plans.filter(plan => {
    if (plan.name === 'FREE') return false;
    return plan.duration_days === getDurationDaysForPeriod(selectedPeriod);
  });

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
        <div style={{ 
          marginBottom: 24, 
          display: 'flex', 
          justifyContent: 'center',
        }}>
          <Segmented
            value={selectedPeriod}
            onChange={(value) => setSelectedPeriod(value as PeriodType)}
            options={[
              { label: 'Неделя', value: 'week' },
              { label: 'Месяц', value: 'month' },
              { label: '2 месяца', value: '2months' },
            ]}
            size="large"
            style={{ background: '#f8fafc' }}
          />
        </div>

        <Row gutter={[24, 24]} justify="center">
          {filteredPlans.map((plan) => {
            const planConfig = getPlanConfig(plan.name);
            const isCurrentPlan = currentPlan?.plan_name === plan.name;
            const isLoading = changingPlan === plan.name;

            return (
              <Col xs={24} sm={12} lg={6} key={plan.id}>
                <Card
                  bordered={false}
                  style={{
                    borderRadius: 20,
                    overflow: 'visible',
                    border: isCurrentPlan 
                      ? `2px solid ${planConfig.accentColor}` 
                      : '1px solid #e5e7eb',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    background: isCurrentPlan ? planConfig.lightBg : 'white',
                    transition: 'all 0.2s ease',
                    boxShadow: 'none',
                    position: 'relative',
                  }}
                  styles={{ body: { padding: 0, flex: 1, display: 'flex', flexDirection: 'column' } }}
                >
                  {/* Badge "Активен" на границе карточки */}
                  {isCurrentPlan && (
                    <div
                      style={{
                        position: 'absolute',
                        top: -12,
                        right: 20,
                        background: planConfig.accentColor,
                        color: 'white',
                        fontSize: 11,
                        fontWeight: 600,
                        padding: '4px 10px',
                        borderRadius: 12,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                        zIndex: 10,
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
                      }}
                    >
                      <CheckOutlined style={{ fontSize: 10 }} />
                      Активен
                    </div>
                  )}

                  {/* Header */}
                  <div style={{ padding: '24px 24px 20px', borderBottom: '1px solid #f1f5f9' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
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
                      <div style={{ flex: 1 }}>
                        <Title level={4} style={{ margin: 0, fontWeight: 700, fontSize: 18 }}>
                          {planConfig.name}
                        </Title>
                        <Text type="secondary" style={{ fontSize: 13 }}>
                          {planConfig.description}
                        </Text>
                      </div>
                    </div>
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
                      marginBottom: 20,
                    }}>
                      <ThunderboltOutlined style={{ fontSize: 18, color: planConfig.accentColor }} />
                      <div>
                        <Text strong style={{ fontSize: 15, display: 'block', lineHeight: 1.2 }}>
                          {plan.response_limit} откликов
                        </Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          в день
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
                  {isAdmin && (
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
                  )}
                </Card>
              </Col>
            );
          })}
        </Row>

        {/* Ссылка на оферту */}
        <div style={{ 
          marginTop: 48, 
          padding: '24px', 
          textAlign: 'center',
          background: 'white',
          borderRadius: 20,
          border: '1px solid #e5e7eb'
        }}>
          <Title level={5} style={{ marginBottom: 16 }}>Юридическая информация</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 20 }}>
            Перед оплатой любого тарифного плана, пожалуйста, ознакомьтесь с условиями публичной оферты.
          </Text>
          <Space size="middle" wrap justify="center">
            <Link to="/offer">
              <Button icon={<FileDoneOutlined />}>
                Читать оферту
              </Button>
            </Link>
            <Button 
              icon={<DownloadOutlined />} 
              href="/oferta.docx" 
              download
            >
              Скачать оферту (.docx)
            </Button>
          </Space>
        </div>
      </div>
    </div>
  );
};

