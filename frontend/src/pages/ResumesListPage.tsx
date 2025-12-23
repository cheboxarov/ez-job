import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Typography, Alert, Modal, Tag } from 'antd';
import { 
  FileTextOutlined, 
  RobotOutlined, 
  CheckCircleOutlined,
  ArrowRightOutlined,
  LockOutlined
} from '@ant-design/icons';
import { listResumes, importResumesFromHH } from '../api/resumes';
import { getDailyResponses } from '../api/subscription';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import { LimitReachedAlert } from '../components/LimitReachedAlert';
import type { Resume } from '../types/api';

const { Text } = Typography;

export const ResumesListPage = () => {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dailyResponses, setDailyResponses] = useState<{ count: number; limit: number } | null>(null);

  useEffect(() => {
    const initializePage = async () => {
      // Сначала загружаем резюме
      await loadResumes();
      // Затем импортируем из HH
      await importFromHH();
      // И снова загружаем резюме
      await loadResumes();
      // Загружаем лимиты
      await loadDailyResponses();
    };
    
    initializePage();
  }, []);

  const loadResumes = async () => {
    setError(null);
    try {
      const response = await listResumes();
      setResumes(response.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке резюме');
    }
  };

  const loadDailyResponses = async () => {
    try {
      const response = await getDailyResponses();
      setDailyResponses({ count: response.count, limit: response.limit });
    } catch (err) {
      // Игнорируем ошибки загрузки лимитов
      setDailyResponses(null);
    }
  };

  const importFromHH = async () => {
    try {
      await importResumesFromHH();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка при импорте резюме из HeadHunter';
      if (err.response?.status === 400 && errorMessage.includes('HH auth data')) {
        // Тихо игнорируем ошибку отсутствия авторизации
        return;
      }
      // Тихо игнорируем другие ошибки импорта
    }
  };

  const getResumePreview = (content: string) => {
    const maxLength = 180;
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  return (
    <div>
      <PageHeader
        title="Мои резюме"
        subtitle="Управляйте своими резюме и настройками автооткликов"
        icon={<FileTextOutlined />}
        breadcrumbs={[{ title: 'Мои резюме' }]}
      />

      {error && (
        <Alert
          message="Ошибка загрузки"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24, borderRadius: 12 }}
          closable
          onClose={() => setError(null)}
        />
      )}

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {dailyResponses && 
         dailyResponses.count >= dailyResponses.limit && 
         dailyResponses.limit < 200 && (
          <LimitReachedAlert 
            limit={dailyResponses.limit} 
            count={dailyResponses.count} 
          />
        )}

        {resumes.length === 0 && (
        <EmptyState
          icon={<FileTextOutlined />}
          title="У вас пока нет резюме"
          description="Резюме будут автоматически импортированы из HeadHunter при наличии настроенной авторизации"
        />
      )}

      {resumes.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {resumes.map((resume) => (
            <Card
              key={resume.id}
              hoverable
              onClick={() => navigate(`/resumes/${resume.id}`)}
              style={{
                borderRadius: 16,
                border: 'none',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                cursor: 'pointer',
                overflow: 'hidden',
                transition: 'all 0.2s ease',
              }}
              styles={{ body: { padding: 0 } }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.12)';
                e.currentTarget.style.transform = 'translateY(-2px)';
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
                    width: 6,
                    background: dailyResponses && 
                               dailyResponses.count >= dailyResponses.limit && 
                               dailyResponses.limit < 200
                      ? 'linear-gradient(180deg, #f59e0b 0%, #d97706 100%)'
                      : resume.is_auto_reply 
                        ? 'linear-gradient(180deg, #22c55e 0%, #16a34a 100%)'
                        : 'linear-gradient(180deg, #e2e8f0 0%, #cbd5e1 100%)',
                    flexShrink: 0,
                  }}
                />
                
                <div style={{ flex: 1, padding: '24px 28px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div
                        style={{
                          width: 44,
                          height: 44,
                          background: dailyResponses && 
                                     dailyResponses.count >= dailyResponses.limit && 
                                     dailyResponses.limit < 200
                            ? 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                            : resume.is_auto_reply 
                              ? 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)'
                              : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                          borderRadius: 12,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: dailyResponses && 
                                    dailyResponses.count >= dailyResponses.limit && 
                                    dailyResponses.limit < 200
                            ? '0 2px 8px rgba(251, 191, 36, 0.25)'
                            : 'none',
                        }}
                      >
                        {dailyResponses && 
                         dailyResponses.count >= dailyResponses.limit && 
                         dailyResponses.limit < 200 ? (
                          <LockOutlined style={{ fontSize: 20, color: '#d97706' }} />
                        ) : (
                          <FileTextOutlined style={{ 
                            fontSize: 20, 
                            color: resume.is_auto_reply ? '#16a34a' : '#64748b' 
                          }} />
                        )}
                      </div>
                      <div>
                        <Text strong style={{ fontSize: 17, color: '#0f172a' }}>
                          Резюме
                        </Text>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4, flexWrap: 'wrap' }}>
                          {resume.is_auto_reply && (
                            <Tag 
                              color="success" 
                              icon={<CheckCircleOutlined />}
                              style={{ borderRadius: 6, margin: 0 }}
                            >
                              Автоотклик активен
                            </Tag>
                          )}
                          {dailyResponses && 
                           dailyResponses.count >= dailyResponses.limit && 
                           dailyResponses.limit < 200 && (
                            <Tag 
                              icon={<LockOutlined />}
                              style={{ 
                                borderRadius: 20, 
                                margin: 0,
                                padding: '2px 10px',
                                background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                                border: '1px solid #fbbf24',
                                color: '#92400e',
                                fontWeight: 600,
                                fontSize: 12,
                                boxShadow: '0 2px 4px rgba(251, 191, 36, 0.2)',
                              }}
                            >
                              Лимит исчерпан
                            </Tag>
                          )}
                        </div>
                      </div>
                    </div>
                    <ArrowRightOutlined style={{ color: '#94a3b8', fontSize: 16 }} />
                  </div>
                  
                  <Text style={{ 
                    color: '#475569', 
                    fontSize: 14, 
                    lineHeight: 1.7,
                    display: 'block'
                  }}>
                    {getResumePreview(resume.content)}
                  </Text>
                  
                  {resume.user_parameters && (
                    <div style={{ 
                      marginTop: 16, 
                      paddingTop: 16, 
                      borderTop: '1px solid #f1f5f9',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8
                    }}>
                      <RobotOutlined style={{ color: '#94a3b8', fontSize: 14 }} />
                      <Text type="secondary" style={{ fontSize: 13 }}>
                        Доп. требования: {resume.user_parameters.substring(0, 60)}
                        {resume.user_parameters.length > 60 ? '...' : ''}
                      </Text>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
        )}
      </div>
    </div>
  );
};
