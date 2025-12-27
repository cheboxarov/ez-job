import { useEffect, useState } from 'react';
import { Card, Typography, Spin, Alert, Pagination, Space, Button, Divider, theme } from 'antd';
import { LinkOutlined, FileTextOutlined, CalendarOutlined } from '@ant-design/icons';
import { getVacancyResponses } from '../api/vacancies';
import type { VacancyResponseItem, VacancyResponsesListResponse } from '../types/api';

const { Title, Text, Paragraph } = Typography;

interface VacancyResponsesListProps {
  resumeHash: string;
}

export const VacancyResponsesList = ({ resumeHash }: VacancyResponsesListProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [responses, setResponses] = useState<VacancyResponseItem[]>([]);
  const [pagination, setPagination] = useState({
    total: 0,
    offset: 0,
    limit: 50,
    current: 1,
  });

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const loadResponses = async (page: number = 1) => {
    if (!resumeHash) return;

    setLoading(true);
    setError(null);

    const offset = (page - 1) * pagination.limit;

    try {
      const data: VacancyResponsesListResponse = await getVacancyResponses({
        resume_hash: resumeHash,
        offset,
        limit: pagination.limit,
      });

      setResponses(data.items);
      setPagination({
        total: data.total,
        offset: data.offset,
        limit: data.limit,
        current: page,
      });
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || 'Ошибка при загрузке откликов';
      setError(errorMessage);
      setResponses([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResponses(1);
  }, [resumeHash]);

  const handlePageChange = (page: number) => {
    loadResponses(page);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading && responses.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <Spin size="large" tip="Загрузка откликов..." />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Ошибка загрузки"
        description={error}
        type="error"
        showIcon
        style={{ marginBottom: 24 }}
        closable
        onClose={() => setError(null)}
      />
    );
  }

  if (responses.length === 0 && !loading) {
    return (
      <Card
        bordered={false}
        style={{
          borderRadius: borderRadiusLG,
          border: '1px solid #e5e7eb',
        }}
      >
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <FileTextOutlined style={{ fontSize: 48, color: '#d1d5db', marginBottom: 16 }} />
          <Title level={4} style={{ marginBottom: 8 }}>
            Откликов пока нет
          </Title>
          <Text type="secondary" style={{ fontSize: 16 }}>
            Отправленные отклики на вакансии появятся здесь
          </Text>
        </div>
      </Card>
    );
  }

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {responses.map((response) => (
          <Card
            key={response.id}
            bordered={false}
            style={{
              borderRadius: borderRadiusLG,
              border: '1px solid #e5e7eb',
            }}
            actions={[
              response.vacancy_url ? (
                <Button
                  type="link"
                  icon={<LinkOutlined />}
                  href={response.vacancy_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  key="open"
                >
                  Открыть вакансию на HeadHunter
                </Button>
              ) : null,
            ].filter(Boolean)}
          >
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: 16,
                  marginBottom: 8,
                }}
              >
                <div style={{ flex: 1 }}>
                  <Title level={5} style={{ margin: 0, marginBottom: 4 }}>
                    {response.vacancy_url ? (
                      <a 
                        href={response.vacancy_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: 'inherit', textDecoration: 'none' }}
                        className="hover:underline"
                        onMouseEnter={(e) => (e.currentTarget.style.textDecoration = 'underline')}
                        onMouseLeave={(e) => (e.currentTarget.style.textDecoration = 'none')}
                      >
                        {response.vacancy_name}
                      </a>
                    ) : (
                      response.vacancy_name
                    )}
                  </Title>
                </div>
                <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                  <Space>
                    <CalendarOutlined style={{ color: 'rgba(0, 0, 0, 0.45)' }} />
                    <Text type="secondary" style={{ fontSize: 13 }}>
                      {formatDate(response.created_at)}
                    </Text>
                  </Space>
                </div>
              </div>
            </div>

            <Divider style={{ margin: '12px 0' }} />

            <div style={{ position: 'relative' }}>
              <Text strong style={{ fontSize: 14, display: 'block', marginBottom: 8 }}>
                Сопроводительное письмо
              </Text>
              <div 
                style={{ 
                  background: '#f9fafb', 
                  borderRadius: 8, 
                  padding: '16px',
                  borderLeft: '4px solid #1890ff'
                }}
              >
                <Paragraph
                  ellipsis={{
                    rows: 3,
                    expandable: true,
                    symbol: 'Показать полностью',
                  }}
                  style={{ 
                    margin: 0, 
                    fontSize: 14, 
                    lineHeight: 1.6,
                    color: '#374151'
                  }}
                >
                  {response.cover_letter}
                </Paragraph>
              </div>
            </div>
          </Card>
        ))}
      </Space>

      {pagination.total > pagination.limit && (
        <div
          style={{
            marginTop: 24,
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <Pagination
            current={pagination.current}
            total={pagination.total}
            pageSize={pagination.limit}
            onChange={handlePageChange}
            showSizeChanger={false}
            showTotal={(total, range) =>
              `${range[0]}-${range[1]} из ${total} откликов`
            }
          />
        </div>
      )}
    </div>
  );
};
