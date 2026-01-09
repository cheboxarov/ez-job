import { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Space,
  DatePicker,
  Select,
  Button,
  Row,
  Col,
  Statistic,
  message,
  Spin,
  InputNumber,
  Modal,
  Form,
} from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import dayjs, { type Dayjs } from 'dayjs';
import { adminApi } from '../../api/admin';
import type { CombinedMetricsResponse, AdminPlan } from '../../types/admin';
import { tokenPricingUtils, type TokenPricing } from '../../utils/tokenPricing';

const { Title } = Typography;
const { RangePicker } = DatePicker;

export const AdminMetricsDashboardPage = () => {
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<CombinedMetricsResponse | null>(null);
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(30, 'day'),
    dayjs(),
  ]);
  const [selectedPlan, setSelectedPlan] = useState<string>('');
  const [timeStep, setTimeStep] = useState<'day' | 'week' | 'month'>('day');
  const [pricing, setPricing] = useState<TokenPricing>(tokenPricingUtils.getPricing());
  const [pricingModalVisible, setPricingModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    loadPlans();
  }, []);

  useEffect(() => {
    loadMetrics();
  }, [dateRange, selectedPlan, timeStep]);

  useEffect(() => {
    const savedPricing = tokenPricingUtils.getPricing();
    setPricing(savedPricing);
  }, []);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const loadPlans = async () => {
    try {
      const response = await adminApi.getPlans({ page: 1, page_size: 100 });
      setPlans(response.plans);
    } catch (error: any) {
      console.error('Ошибка загрузки планов:', error);
    }
  };

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const params: any = {
        start_date: dateRange[0].toISOString(),
        end_date: dateRange[1].toISOString(),
        time_step: timeStep,
      };

      if (selectedPlan) {
        params.plan_id = selectedPlan;
      }

      const data = await adminApi.getCombinedMetrics(params);
      setMetrics(data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка загрузки метрик');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePricing = () => {
    form.validateFields().then((values) => {
      const newPricing: TokenPricing = {
        inputPricePerMillion: values.inputPrice || 0,
        outputPricePerMillion: values.outputPrice || 0,
      };
      tokenPricingUtils.setPricing(newPricing);
      setPricing(newPricing);
      setPricingModalVisible(false);
      message.success('Настройки стоимости сохранены');
    });
  };

  const openPricingModal = () => {
    form.setFieldsValue({
      inputPrice: pricing.inputPricePerMillion,
      outputPrice: pricing.outputPricePerMillion,
    });
    setPricingModalVisible(true);
  };

  const formatDate = (dateStr: string) => {
    const date = dayjs(dateStr);
    if (timeStep === 'day') return date.format('DD.MM');
    if (timeStep === 'week') return `Неделя ${date.format('DD.MM')}`;
    return date.format('MMM YYYY');
  };

  // Приблизительный расчет стоимости на основе total_tokens
  // Используем соотношение 60/40 для prompt/completion
  const calculateCostFromTotalTokens = (totalTokens: number): number => {
    const promptTokens = Math.round(totalTokens * 0.6);
    const completionTokens = Math.round(totalTokens * 0.4);
    return tokenPricingUtils.calculateCost(promptTokens, completionTokens, pricing) || 0;
  };

  const llmChartData =
    metrics?.llm_metrics.metrics_by_period.map((m) => {
      const cost = calculateCostFromTotalTokens(m.total_tokens);
      return {
      period: formatDate(m.period_start),
      calls: m.calls_count,
      tokens: m.total_tokens,
      users: m.unique_users,
        cost: cost,
      };
    }) || [];

  const totalCost = metrics
    ? calculateCostFromTotalTokens(metrics.llm_metrics.total_metrics.total_tokens)
    : 0;
  const avgCostPerCall =
    metrics && metrics.llm_metrics.total_metrics.calls_count > 0
      ? totalCost / metrics.llm_metrics.total_metrics.calls_count
      : 0;

  const responsesChartData =
    metrics?.responses_metrics.metrics_by_period.map((m) => ({
      period: formatDate(m.period_start),
      responses: m.responses_count,
      users: m.unique_users,
    })) || [];

  if (loading && !metrics) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: isMobile ? '0 16px' : '0 24px' }}>
      <Title level={isMobile ? 3 : 2}>Метрики</Title>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={24} md={8} lg={6}>
              <RangePicker
                value={dateRange}
                onChange={(dates) => {
                  if (dates) {
                    setDateRange(dates as [Dayjs, Dayjs]);
                  }
                }}
                format="DD.MM.YYYY"
                style={{ width: '100%' }}
              />
            </Col>
            <Col xs={24} sm={12} md={6} lg={5}>
              <Select
                placeholder="План"
                value={selectedPlan || undefined}
                onChange={setSelectedPlan}
                allowClear
                style={{ width: '100%' }}
              >
                {plans.map((plan) => (
                  <Select.Option key={plan.id} value={plan.id}>
                    {plan.name}
                  </Select.Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={6} lg={4}>
              <Select
                value={timeStep}
                onChange={setTimeStep}
                style={{ width: '100%' }}
              >
                <Select.Option value="day">По дням</Select.Option>
                <Select.Option value="week">По неделям</Select.Option>
                <Select.Option value="month">По месяцам</Select.Option>
              </Select>
            </Col>
            <Col xs={24} sm={24} md={6} lg={5}>
              <Button
                icon={<SettingOutlined />}
                onClick={openPricingModal}
                style={{ width: '100%' }}
              >
                Настройки стоимости
              </Button>
            </Col>
          </Row>
        </Card>

        {metrics && (
          <>
            <Row gutter={16}>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Всего вызовов LLM"
                    value={metrics.llm_metrics.total_metrics.calls_count}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Всего токенов"
                    value={metrics.llm_metrics.total_metrics.total_tokens}
                    formatter={(value) => value?.toLocaleString()}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Общая стоимость"
                    value={totalCost}
                    formatter={(value) => tokenPricingUtils.formatCost(value as number)}
                    precision={2}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Средняя стоимость за вызов"
                    value={avgCostPerCall}
                    formatter={(value) => tokenPricingUtils.formatCost(value as number)}
                    precision={4}
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Средние токены на пользователя"
                    value={metrics.llm_metrics.total_metrics.avg_tokens_per_user.toFixed(0)}
                    formatter={(value) => value?.toLocaleString()}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Уникальных пользователей (LLM)"
                    value={metrics.llm_metrics.total_metrics.unique_users}
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Всего откликов"
                    value={metrics.responses_metrics.total_metrics.responses_count}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Средние отклики на пользователя"
                    value={metrics.responses_metrics.total_metrics.avg_responses_per_user.toFixed(1)}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Уникальных пользователей (отклики)"
                    value={metrics.responses_metrics.total_metrics.unique_users}
                  />
                </Card>
              </Col>
            </Row>

            <Card title="Вызовы LLM по периодам">
              <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
                <BarChart data={llmChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="calls" fill="#8884d8" name="Вызовы" />
                  <Bar dataKey="users" fill="#82ca9d" name="Пользователи" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Токены LLM по периодам">
              <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
                <LineChart data={llmChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip
                    formatter={(value: number, name: string) => {
                      if (name === 'Стоимость') {
                        return tokenPricingUtils.formatCost(value);
                      }
                      return value.toLocaleString();
                    }}
                  />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="tokens"
                    stroke="#8884d8"
                    name="Токены"
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="cost"
                    stroke="#82ca9d"
                    name="Стоимость"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Отклики по периодам">
              <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
                <BarChart data={responsesChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="responses" fill="#ffc658" name="Отклики" />
                  <Bar dataKey="users" fill="#82ca9d" name="Пользователи" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </>
        )}
      </Space>

      <Modal
        title="Настройки стоимости токенов"
        open={pricingModalVisible}
        onOk={handleSavePricing}
        onCancel={() => setPricingModalVisible(false)}
        okText="Сохранить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="Стоимость входных токенов за млн"
            name="inputPrice"
            rules={[{ required: true, message: 'Укажите стоимость' }]}
          >
            <InputNumber
              min={0}
              step={0.01}
              style={{ width: '100%' }}
              prefix="$"
              placeholder="0.00"
            />
          </Form.Item>
          <Form.Item
            label="Стоимость выходных токенов за млн"
            name="outputPrice"
            rules={[{ required: true, message: 'Укажите стоимость' }]}
          >
            <InputNumber
              min={0}
              step={0.01}
              style={{ width: '100%' }}
              prefix="$"
              placeholder="0.00"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
