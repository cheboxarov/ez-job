import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card, Typography, Spin, Alert, Space } from 'antd';
import { 
  SearchOutlined, 
  SettingOutlined, 
  FileTextOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { VacancyCard } from '../components/VacancyCard';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import { GradientButton } from '../components/GradientButton';
import { useWindowSize } from '../hooks/useWindowSize';
import { getRelevantVacancyList } from '../api/vacancies';
import { getResumeFilterSettings } from '../api/resumeFilterSettings';
import { getResume } from '../api/resumes';
import { useVacanciesStore } from '../stores/vacanciesStore';
import type { VacanciesListRequest, ResumeFilterSettings, Resume } from '../types/api';

const { Title, Text } = Typography;

export const ResumeVacanciesPage = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const { isMobile } = useWindowSize();
  const { vacancies, setVacancies } = useVacanciesStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHhAuthMissing, setIsHhAuthMissing] = useState(false);
  const [filterSettings, setFilterSettings] = useState<ResumeFilterSettings | null>(null);
  const [resume, setResume] = useState<Resume | null>(null);
  const [loadingResume, setLoadingResume] = useState(false);

  useEffect(() => {
    if (resumeId) {
      loadResume();
      loadSettingsAndSearch();
    }
  }, [resumeId]);

  const loadResume = async () => {
    if (!resumeId) return;
    setLoadingResume(true);
    try {
      const resumeData = await getResume(resumeId);
      setResume(resumeData);
    } catch (err) {
      console.error('Ошибка загрузки резюме:', err);
    } finally {
      setLoadingResume(false);
    }
  };

  const loadSettingsAndSearch = async () => {
    if (!resumeId) return;
    
    setLoading(true);
    setError(null);
    
    let settings: ResumeFilterSettings | null = null;
    try {
      settings = await getResumeFilterSettings(resumeId);
      setFilterSettings(settings);
    } catch (e) {
      setFilterSettings(null);
    }
    
    try {
      const request: VacanciesListRequest = {
        resume_id: resumeId,
        page_indices: null,
        min_confidence: null,
        order_by: settings?.order_by || null,
      };
      const response = await getRelevantVacancyList(request);
      const sortedVacancies = [...response.items].sort((a, b) => b.confidence - a.confidence);
      setVacancies(sortedVacancies);
      setIsHhAuthMissing(false);
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || '';
      const isMissingAuth = err.response?.status === 400 && 
        (errorDetail === 'HH auth data not set' || errorDetail.includes('HH auth data'));
      
      if (isMissingAuth) {
        setIsHhAuthMissing(true);
        setError(null);
      } else {
        setIsHhAuthMissing(false);
        setError(errorDetail || 'Ошибка при получении вакансий');
      }
      setVacancies([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Поиск вакансий"
        subtitle="Вакансии, подобранные на основе вашего резюме"
        icon={<SearchOutlined />}
        breadcrumbs={[
          { title: 'Мои резюме', path: '/resumes' },
          { title: 'Резюме', path: `/resumes/${resumeId}` },
          { title: 'Вакансии' }
        ]}
        actions={
          <Space size="middle" wrap={isMobile} style={{ width: isMobile ? '100%' : 'auto' }}>
            {vacancies.length > 0 && (
              <div 
                style={{ 
                  padding: isMobile ? '6px 12px' : '8px 16px', 
                  background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                  borderRadius: 20,
                  border: '1px solid #86efac',
                }}
              >
                <Text strong style={{ fontSize: isMobile ? 12 : 14, color: '#16a34a' }}>
                  Найдено: {vacancies.length}
                </Text>
              </div>
            )}
            <Button
              icon={<FileTextOutlined />}
              size={isMobile ? 'middle' : 'large'}
              onClick={() => navigate(`/resumes/${resumeId}/responses`)}
              disabled={!resume?.headhunter_hash || loadingResume}
              loading={loadingResume}
              style={{ 
                borderRadius: 10, 
                height: isMobile ? 36 : 44,
                width: isMobile ? '100%' : 'auto'
              }}
            >
              История откликов
            </Button>
          </Space>
        }
      />

      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: isMobile ? 'auto' : 'calc(100vh - 200px)',
        padding: isMobile ? '0 16px' : '0'
      }}>

        {loading && (
          <div style={{ textAlign: 'center', padding: isMobile ? '60px 0' : '100px 0' }}>
            <Spin size="large" tip="Анализируем вакансии с помощью AI..." />
          </div>
        )}

        {isHhAuthMissing && (
          <Card
            bordered={false}
            style={{
              marginBottom: 24,
              background: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
              border: '1px solid #fcd34d',
              borderRadius: 16,
            }}
          >
            <div style={{ textAlign: 'center', padding: '32px' }}>
              <div
                style={{
                  width: 64,
                  height: 64,
                  background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                  borderRadius: 16,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 20px',
                }}
              >
                <ExclamationCircleOutlined style={{ fontSize: 28, color: 'white' }} />
              </div>
              <Title level={4} style={{ marginBottom: 8, color: '#92400e' }}>
                Требуется авторизация HeadHunter
              </Title>
              <Text style={{ fontSize: 15, display: 'block', marginBottom: 20, color: '#a16207' }}>
                Для поиска вакансий необходимо указать headers и cookies HeadHunter
              </Text>
              <GradientButton
                icon={<SettingOutlined />}
                onClick={() => navigate('/settings/hh-auth')}
              >
                Настроить HeadHunter
              </GradientButton>
            </div>
          </Card>
        )}

        {error && !isHhAuthMissing && (
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

        {!loading && !error && !isHhAuthMissing && vacancies.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 0 : 0 }}>
            {vacancies.map((vacancy) => (
              <VacancyCard
                key={vacancy.vacancy_id}
                vacancy={vacancy}
                resumeId={resumeId}
              />
            ))}
          </div>
        )}

        {!loading && !error && !isHhAuthMissing && vacancies.length === 0 && (
          <EmptyState
            icon={<SearchOutlined />}
            title="Вакансии не найдены"
            description="Попробуйте изменить настройки фильтрации на странице редактирования резюме"
            action={
              <Button
                icon={<SettingOutlined />}
                onClick={() => navigate(`/resumes/${resumeId}`)}
                style={{ borderRadius: 10, height: 44 }}
              >
                Настроить фильтры
              </Button>
            }
          />
        )}
      </div>
    </div>
  );
};
