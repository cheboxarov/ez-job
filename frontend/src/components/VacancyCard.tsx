import { useState } from 'react';
import { Card, Typography, Tag, Tooltip, Button, message } from 'antd';
import { 
  CheckCircleFilled, 
  LinkOutlined, 
  SendOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { ConfidenceBadge } from './ConfidenceBadge';
import { respondToVacancy } from '../api/vacancies';
import type { VacancyListItem } from '../types/api';

const { Title, Text } = Typography;

interface VacancyCardProps {
  vacancy: VacancyListItem;
  resumeId?: string;
  onRespondSuccess?: () => void;
}

export const VacancyCard = ({ vacancy, resumeId, onRespondSuccess }: VacancyCardProps) => {
  const [responding, setResponding] = useState(false);

  const handleCardClick = () => {
    if (vacancy.alternate_url) {
      window.open(vacancy.alternate_url, '_blank', 'noopener,noreferrer');
    }
  };

  const handleRespond = async (e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!resumeId) {
      message.error('Не указан ID резюме');
      return;
    }

    setResponding(true);
    try {
      await respondToVacancy({
        vacancy_id: vacancy.vacancy_id,
        resume_id: resumeId,
        letter: '1',
      });
      message.success('Отклик успешно отправлен');
      onRespondSuccess?.();
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || 'Ошибка при отправке отклика';
      message.error(errorDetail);
    } finally {
      setResponding(false);
    }
  };

  const formatSalary = () => {
    if (!vacancy.salary_from && !vacancy.salary_to) {
      return 'Уровень дохода не указан';
    }
    const parts: string[] = [];
    if (vacancy.salary_from) parts.push(`от ${vacancy.salary_from.toLocaleString('ru-RU')}`);
    if (vacancy.salary_to) parts.push(`до ${vacancy.salary_to.toLocaleString('ru-RU')}`);
    const currency = vacancy.salary_currency === 'RUR' ? '₽' : vacancy.salary_currency || '';
    return `${parts.join(' ')} ${currency}`.trim();
  };

  const isHighMatch = vacancy.confidence >= 0.75;
  const hasLink = Boolean(vacancy.alternate_url);

  return (
    <Card
      onClick={hasLink ? handleCardClick : undefined}
      style={{
        marginBottom: 16,
        border: 'none',
        borderRadius: 16,
        cursor: hasLink ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        overflow: 'hidden',
      }}
      styles={{ body: { padding: 0 } }}
      hoverable={hasLink}
      onMouseEnter={(e) => {
        if (hasLink) {
          e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.12)';
          e.currentTarget.style.transform = 'translateY(-2px)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <div style={{ display: 'flex' }}>
        {/* Left gradient strip */}
        <div
          style={{
            width: 5,
            background: isHighMatch 
              ? 'linear-gradient(180deg, #22c55e 0%, #16a34a 100%)'
              : 'linear-gradient(180deg, #3b82f6 0%, #2563eb 100%)',
            flexShrink: 0,
          }}
        />
        
        <div style={{ flex: 1, padding: '24px 28px' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
            <div style={{ flex: 1, marginRight: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <Title
                  level={4}
                  style={{
                    margin: 0,
                    fontSize: 19,
                    lineHeight: 1.3,
                    color: '#0f172a',
                    fontWeight: 600,
                  }}
                >
                  {vacancy.name}
                </Title>
                {hasLink && (
                  <Tooltip title="Открыть на hh.ru">
                    <LinkOutlined style={{ color: '#94a3b8', fontSize: 15 }} />
                  </Tooltip>
                )}
              </div>
              <Text
                strong
                style={{
                  fontSize: 20,
                  color: isHighMatch ? '#16a34a' : '#2563eb',
                  display: 'block',
                }}
              >
                {formatSalary()}
              </Text>
            </div>
            <ConfidenceBadge confidence={vacancy.confidence} reason={vacancy.reason} />
          </div>

          {/* Tags */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
            {vacancy.schedule_name && (
              <Tag 
                icon={<ClockCircleOutlined />}
                style={{ 
                  background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)', 
                  border: 'none', 
                  color: '#475569', 
                  padding: '4px 12px', 
                  fontSize: 13,
                  borderRadius: 8,
                }}
              >
                {vacancy.schedule_name}
              </Tag>
            )}
            {vacancy.professional_roles?.map((role, i) => (
              <Tag 
                key={i} 
                style={{ 
                  background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)', 
                  border: 'none', 
                  color: '#2563eb', 
                  padding: '4px 12px', 
                  fontSize: 13,
                  borderRadius: 8,
                }}
              >
                {role}
              </Tag>
            ))}
          </div>

          {/* Snippets */}
          {(vacancy.snippet_requirement || vacancy.snippet_responsibility) && (
            <div style={{ marginBottom: 16, padding: 16, background: '#f8fafc', borderRadius: 12 }}>
              {vacancy.snippet_responsibility && (
                <Text style={{ fontSize: 14, color: '#475569', display: 'block', marginBottom: 8, lineHeight: 1.6 }}>
                  <strong style={{ color: '#334155' }}>Обязанности:</strong> {vacancy.snippet_responsibility.replace(/<[^>]*>/g, '')}
                </Text>
              )}
              {vacancy.snippet_requirement && (
                <Text style={{ fontSize: 14, color: '#475569', display: 'block', lineHeight: 1.6 }}>
                  <strong style={{ color: '#334155' }}>Требования:</strong> {vacancy.snippet_requirement.replace(/<[^>]*>/g, '')}
                </Text>
              )}
            </div>
          )}

          {/* Company Info */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {vacancy.company_name && (
                <>
                  <Text style={{ fontSize: 15, fontWeight: 600, color: '#0f172a' }}>
                    {vacancy.company_name}
                  </Text>
                  <CheckCircleFilled style={{ color: '#2563eb', fontSize: 14 }} />
                </>
              )}
              {(vacancy.area_name || vacancy.address_city) && (
                <Text style={{ fontSize: 14, color: '#64748b', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <EnvironmentOutlined />
                  {vacancy.address_city || vacancy.area_name}
                  {vacancy.address_street && `, ${vacancy.address_street}`}
                </Text>
              )}
            </div>

            {/* Action Button */}
            {resumeId && (
              <Button
                type="primary"
                icon={<SendOutlined />}
                loading={responding}
                onClick={handleRespond}
                style={{
                  borderRadius: 10,
                  height: 40,
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  border: 'none',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                }}
              >
                Откликнуться
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};
