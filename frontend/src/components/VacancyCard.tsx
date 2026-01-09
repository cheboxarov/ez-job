import { useState } from 'react';
import { Card, Typography, Tag, Tooltip, Button, message, Modal } from 'antd';
import { 
  CheckCircleFilled, 
  LinkOutlined, 
  SendOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { ConfidenceBadge } from './ConfidenceBadge';
import { respondToVacancy } from '../api/vacancies';
import { useWindowSize } from '../hooks/useWindowSize';
import type { VacancyListItem } from '../types/api';

const { Title, Text } = Typography;

interface VacancyCardProps {
  vacancy: VacancyListItem;
  resumeId?: string;
  onRespondSuccess?: () => void;
}

export const VacancyCard = ({ vacancy, resumeId, onRespondSuccess }: VacancyCardProps) => {
  const { isMobile } = useWindowSize();
  const [responding, setResponding] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);

  const handleCardClick = () => {
    if (isMobile) {
      setModalVisible(true);
    } else if (vacancy.alternate_url) {
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

  // Мобильная упрощенная версия
  if (isMobile) {
    return (
      <>
        <Card
          onClick={handleCardClick}
          style={{
            marginBottom: 12,
            border: '1px solid #e5e7eb',
            borderRadius: 12,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            overflow: 'hidden',
          }}
          styles={{ body: { padding: 0 } }}
          hoverable
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = isHighMatch ? '#22c55e' : '#2563eb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#e5e7eb';
          }}
        >
          <div style={{ display: 'flex' }}>
            {/* Left gradient strip */}
            <div
              style={{
                width: 4,
                background: isHighMatch 
                  ? 'linear-gradient(180deg, #22c55e 0%, #16a34a 100%)'
                  : 'linear-gradient(180deg, #3b82f6 0%, #2563eb 100%)',
                flexShrink: 0,
              }}
            />
            
            <div style={{ flex: 1, padding: '16px' }}>
              {/* Header - только название и зарплата */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div style={{ flex: 1, marginRight: 8 }}>
                  <Title
                    level={5}
                    style={{
                      margin: 0,
                      fontSize: 16,
                      lineHeight: 1.3,
                      color: '#0f172a',
                      fontWeight: 600,
                      marginBottom: 6,
                    }}
                  >
                    {vacancy.name}
                  </Title>
                  <Text
                    strong
                    style={{
                      fontSize: 16,
                      color: isHighMatch ? '#16a34a' : '#2563eb',
                      display: 'block',
                    }}
                  >
                    {formatSalary()}
                  </Text>
                </div>
                <ConfidenceBadge confidence={vacancy.confidence} reason={vacancy.reason} />
              </div>

              {/* Минимум информации - компания и локация */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                {vacancy.company_name && (
                  <Text style={{ fontSize: 13, color: '#64748b' }}>
                    {vacancy.company_name}
                  </Text>
                )}
                {(vacancy.area_name || vacancy.address_city) && (
                  <Text style={{ fontSize: 13, color: '#64748b', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <EnvironmentOutlined style={{ fontSize: 12 }} />
                    {vacancy.address_city || vacancy.area_name}
                  </Text>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Модальное окно с детальной информацией */}
        <Modal
          title={null}
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          footer={null}
          width="100%"
          style={{ 
            top: 0,
            paddingBottom: 0,
            maxWidth: '100%',
            margin: 0,
            height: '100vh',
          }}
          styles={{ 
            body: { 
              padding: 0,
              height: '100vh',
              maxHeight: '100vh',
              overflowY: 'auto',
              borderRadius: 0,
            },
            content: { 
              padding: 0,
              borderRadius: 0,
              height: '100vh',
              maxHeight: '100vh',
            },
            wrap: {
              top: 0,
            },
            mask: {
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
            }
          }}
          closeIcon={null}
          centered={false}
        >
          <div style={{ 
            padding: '20px 16px', 
            paddingTop: '56px', 
            position: 'relative',
            minHeight: '100vh',
            background: '#ffffff',
          }}>
            {/* Кнопка закрытия */}
            <div 
              onClick={() => setModalVisible(false)}
              style={{
                position: 'fixed',
                top: 16,
                right: 16,
                zIndex: 1001,
                width: 36,
                height: 36,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'rgba(255, 255, 255, 0.95)',
                borderRadius: '50%',
                cursor: 'pointer',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
              }}
            >
              <CloseOutlined style={{ fontSize: 18, color: '#64748b' }} />
            </div>
            {/* Header модалки */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div style={{ flex: 1, marginRight: 12 }}>
                  <Title
                    level={4}
                    style={{
                      margin: 0,
                      fontSize: 20,
                      lineHeight: 1.3,
                      color: '#0f172a',
                      fontWeight: 600,
                      marginBottom: 8,
                    }}
                  >
                    {vacancy.name}
                  </Title>
                  <Text
                    strong
                    style={{
                      fontSize: 22,
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
                      maxWidth: '100%',
                      wordBreak: 'break-word',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
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
                      maxWidth: '100%',
                      wordBreak: 'break-word',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'normal',
                    }}
                  >
                    {role}
                  </Tag>
                ))}
              </div>
            </div>

            {/* Snippets */}
            {(vacancy.snippet_requirement || vacancy.snippet_responsibility) && (
              <div style={{ marginBottom: 20, padding: 16, background: '#f8fafc', borderRadius: 12 }}>
                {vacancy.snippet_responsibility && (
                  <Text style={{ fontSize: 14, color: '#475569', display: 'block', marginBottom: 12, lineHeight: 1.6 }}>
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
            <div style={{ marginBottom: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                {vacancy.company_name && (
                  <>
                    <Text style={{ fontSize: 16, fontWeight: 600, color: '#0f172a' }}>
                      {vacancy.company_name}
                    </Text>
                    <CheckCircleFilled style={{ color: '#2563eb', fontSize: 14 }} />
                  </>
                )}
              </div>
              {(vacancy.area_name || vacancy.address_city) && (
                <Text style={{ fontSize: 14, color: '#64748b', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <EnvironmentOutlined />
                  {vacancy.address_city || vacancy.area_name}
                  {vacancy.address_street && `, ${vacancy.address_street}`}
                </Text>
              )}
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {resumeId && (
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  loading={responding}
                  onClick={handleRespond}
                  block
                  size="large"
                  style={{
                    borderRadius: 10,
                    height: 48,
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                    border: '1px solid #2563eb',
                  }}
                >
                  Откликнуться
                </Button>
              )}
              {vacancy.alternate_url && (
                <Button
                  icon={<LinkOutlined />}
                  onClick={() => window.open(vacancy.alternate_url, '_blank', 'noopener,noreferrer')}
                  block
                  size="large"
                  style={{
                    borderRadius: 10,
                    height: 48,
                    fontWeight: 600,
                  }}
                >
                  Открыть на hh.ru
                </Button>
              )}
            </div>
          </div>
        </Modal>
      </>
    );
  }

  // Десктопная версия (без изменений)
  return (
    <Card
      onClick={hasLink ? handleCardClick : undefined}
      style={{
        marginBottom: 16,
        border: '1px solid #e5e7eb',
        borderRadius: 16,
        cursor: hasLink ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        overflow: 'hidden',
      }}
      styles={{ body: { padding: 0 } }}
      hoverable={hasLink}
      onMouseEnter={(e) => {
        if (hasLink) {
          e.currentTarget.style.borderColor = isHighMatch ? '#22c55e' : '#2563eb';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = '#e5e7eb';
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
                  maxWidth: '100%',
                  wordBreak: 'break-word',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
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
                  maxWidth: '100%',
                  wordBreak: 'break-word',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'normal',
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
                  border: '1px solid #2563eb',
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
