import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Typography, Spin, Alert, Card } from 'antd';
import { 
  FileTextOutlined, 
  SendOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { VacancyResponsesList } from '../components/VacancyResponsesList';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import { getResume } from '../api/resumes';
import type { Resume } from '../types/api';

const { Title, Text } = Typography;

export const ResumeResponsesPage = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (resumeId) {
      loadResume();
    }
  }, [resumeId]);

  const loadResume = async () => {
    if (!resumeId) return;
    setLoading(true);
    setError(null);
    try {
      const resumeData = await getResume(resumeId);
      setResume(resumeData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке резюме');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка данных..." />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <PageHeader
          title="История откликов"
          icon={<SendOutlined />}
          breadcrumbs={[
            { title: 'Мои резюме', path: '/resumes' },
            { title: 'Отклики' }
          ]}
        />
        <Alert
          message="Ошибка загрузки"
          description={error}
          type="error"
          showIcon
          style={{ borderRadius: 12 }}
        />
        <Button
          type="primary"
          onClick={() => navigate(`/resumes/${resumeId}`)}
          style={{ marginTop: 16, borderRadius: 10 }}
        >
          Вернуться к резюме
        </Button>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="История откликов"
        subtitle="Все отправленные отклики по данному резюме"
        icon={<SendOutlined />}
        breadcrumbs={[
          { title: 'Мои резюме', path: '/resumes' },
          { title: 'Резюме', path: `/resumes/${resumeId}` },
          { title: 'Отклики' }
        ]}
        actions={
          <GradientButton
            icon={<FileTextOutlined />}
            onClick={() => navigate(`/resumes/${resumeId}/vacancies`)}
          >
            Подходящие вакансии
          </GradientButton>
        }
      />

      <div style={{ maxWidth: '100%', margin: '0 auto' }}>
        {!resume?.headhunter_hash ? (
          <Card
            bordered={false}
            style={{
              borderRadius: 16,
              border: '1px solid #e5e7eb',
            }}
          >
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div
                style={{
                  width: 80,
                  height: 80,
                  background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                  borderRadius: 20,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px',
                }}
              >
                <ExclamationCircleOutlined style={{ fontSize: 36, color: '#d97706' }} />
              </div>
              <Title level={4} style={{ marginBottom: 12, color: '#0f172a' }}>
                Резюме не импортировано из HeadHunter
              </Title>
              <Text type="secondary" style={{ fontSize: 15, display: 'block', marginBottom: 24, maxWidth: 500, margin: '0 auto 24px' }}>
                Для просмотра откликов необходимо импортировать резюме из HeadHunter. 
                После импорта здесь будет отображаться история всех отправленных откликов.
              </Text>
              <Button
                onClick={() => navigate('/resumes')}
                style={{ borderRadius: 10, height: 44 }}
              >
                Перейти к резюме
              </Button>
            </div>
          </Card>
        ) : (
          <VacancyResponsesList resumeHash={resume.headhunter_hash} />
        )}
      </div>
    </div>
  );
};
