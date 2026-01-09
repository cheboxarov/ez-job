import { useEffect, useState } from 'react';
import { Card, Typography, Spin, message } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getResponsesStatistics } from '../api/vacancies';
import { PageHeader } from '../components/PageHeader';
import { useWindowSize } from '../hooks/useWindowSize';
import type { StatisticsResponse } from '../types/api';

const { Title, Text } = Typography;

export const StatisticsPage = () => {
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { isMobile } = useWindowSize();

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const data = await getResponsesStatistics(7);
      setStatistics(data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при загрузке статистики');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleDateString('ru-RU', { month: 'short' });
    return `${day} ${month}`;
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: 400,
      }}>
        <Spin size="large" />
      </div>
    );
  }

  const chartData = statistics?.data.map(item => ({
    date: formatDate(item.date),
    count: item.count,
    fullDate: item.date,
  })) || [];

  const totalResponses = statistics?.data.reduce((sum, item) => sum + item.count, 0) || 0;

  return (
    <div>
      <PageHeader
        title="Статистика откликов"
        subtitle="Количество отправленных откликов за последние 7 дней"
        icon={<BarChartOutlined />}
        breadcrumbs={[{ title: 'Статистика' }]}
      />

      <div style={{ 
        maxWidth: 1200, 
        margin: '0 auto',
        padding: isMobile ? '0 16px' : '0 24px',
      }}>
        <Card
          bordered={false}
          style={{
            borderRadius: 20,
            border: '1px solid #e5e7eb',
            marginBottom: isMobile ? 16 : 24,
          }}
        >
          <div style={{ marginBottom: isMobile ? 16 : 24 }}>
            <Title level={4} style={{ marginBottom: 8, color: '#0f172a' }}>
              Отклики за 7 дней
            </Title>
            <Text type="secondary" style={{ fontSize: 14 }}>
              Всего отправлено: <Text strong style={{ color: '#2563eb' }}>{totalResponses}</Text> откликов
            </Text>
          </div>

          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={isMobile ? 280 : 400}>
              <LineChart
                data={chartData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  stroke="#64748b"
                  style={{ fontSize: 12 }}
                />
                <YAxis 
                  stroke="#64748b"
                  style={{ fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: 8,
                  }}
                  labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                  formatter={(value: number) => [`${value} откликов`, 'Количество']}
                />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#2563eb" 
                  strokeWidth={3}
                  dot={{ fill: '#2563eb', r: 6 }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: isMobile ? '40px 16px' : '60px 20px',
              color: '#94a3b8',
            }}>
              <Text style={{ fontSize: 15 }}>
                Нет данных за выбранный период
              </Text>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
