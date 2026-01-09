import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Button,
  Card,
  Typography,
  Space,
  Spin,
  Alert,
  Row,
  Col,
  Tabs,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { getResume, evaluateResume } from '../api/resumes';
import { useDailyResponsesStore } from '../stores/dailyResponsesStore';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import { LimitReachedAlert } from '../components/LimitReachedAlert';
import { ResumeContent } from '../components/ResumeContent';
import { ResumeEvaluation } from '../components/ResumeEvaluation';
import { useWindowSize } from '../hooks/useWindowSize';
import type { Resume } from '../types/api';

const { Text } = Typography;

export const ResumeDetailPage = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResult, setEvaluationResult] = useState<any | null>(null);
  const [evaluationLoading, setEvaluationLoading] = useState(false);
  const { count, limit, loading: dailyResponsesLoading, fetchDailyResponses } = useDailyResponsesStore();
  const { isMobile } = useWindowSize();

  useEffect(() => {
    if (resumeId) {
      loadData();
      fetchDailyResponses();
    }
  }, [resumeId, fetchDailyResponses]);

  // Автоматический запуск анализа при загрузке резюме
  useEffect(() => {
    if (resume?.content && !evaluationLoading && !evaluationResult && !loading) {
      handleEvaluateResume();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resume?.content, loading]);

  const loadData = async () => {
    if (!resumeId) return;
    setLoading(true);
    setError(null);
    try {
      const resumeData = await getResume(resumeId);
      setResume(resumeData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };



  const handleEvaluateResume = async () => {
    if (!resumeId) return;
    setEvaluationLoading(true);
    try {
      const result = await evaluateResume(resumeId);
      setEvaluationResult(result);
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при анализе резюме');
    } finally {
      setEvaluationLoading(false);
    }
  };


  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: 400,
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
        borderRadius: 24,
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error && !resume) {
    return (
      <div style={{ padding: '24px', maxWidth: 800, margin: '0 auto' }}>
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/resumes')}
          style={{ marginBottom: 16 }}
        >
          Назад к списку
        </Button>
        <Alert
          message="Ошибка загрузки"
          description={error}
          type="error"
          showIcon
          style={{ borderRadius: 12 }}
        />
      </div>
    );
  }

  return (
    <div style={{ paddingBottom: 40, minHeight: '100vh' }}>
      <PageHeader
        title="Просмотр резюме"
        subtitle="Оценка и текст резюме"
        icon={<FileTextOutlined />}
        breadcrumbs={[
          { title: 'Мои резюме', path: '/resumes' },
          { title: 'Текущее резюме' }
        ]}
        actions={
          <Space size="middle" wrap style={{ width: isMobile ? '100%' : 'auto', justifyContent: isMobile ? 'stretch' : 'flex-start' }}>
            <Button
              icon={<SendOutlined />}
              size="large"
              onClick={() => navigate(`/resumes/${resumeId}/responses`)}
              disabled={!resume?.headhunter_hash}
              style={{ borderRadius: 10, height: 44, border: '1px solid #e5e7eb', width: isMobile ? '100%' : 'auto' }}
            >
              История откликов
            </Button>
            <GradientButton
              icon={<SearchOutlined />}
              onClick={() => navigate(`/resumes/${resumeId}/vacancies`)}
              style={{ width: isMobile ? '100%' : 'auto' }}
            >
              Подходящие вакансии
            </GradientButton>
          </Space>
        }
      />

      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : '0 24px' }}>
        {!dailyResponsesLoading && count >= limit && limit > 0 && limit < 200 && (
          <LimitReachedAlert 
            limit={limit} 
            count={count} 
          />
        )}

        {/* Навигация табами */}
        <Tabs
          activeKey="resume"
          onChange={(key) => {
            if (key === 'autolike') {
              navigate(`/resumes/${resumeId}/autolike`);
            }
          }}
          items={[
            {
              key: 'resume',
              label: 'Резюме',
            },
            {
              key: 'autolike',
              label: 'Автолик',
            },
          ]}
          style={{ marginBottom: 24 }}
        />

        <Row gutter={24} style={{ alignItems: 'flex-start' }}>
          {/* Основной контент */}
          <Col xs={24}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {/* Секция анализа резюме */}
              {(evaluationLoading || evaluationResult) && (
                <ResumeEvaluation
                  loading={evaluationLoading}
                  result={evaluationResult}
                />
              )}

              {/* Секция отображения резюме */}
              <Card
                bordered={false}
                style={{
                  borderRadius: 20,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                }}
                styles={{
                  body: {
                    padding: isMobile ? 20 : 32,
                  }
                }}
              >
                <div
                  style={{
                    fontSize: 14,
                    lineHeight: 1.8,
                    color: '#334155',
                    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                  }}
                >
                  {resume?.content ? (
                    <ResumeContent content={resume.content} />
                  ) : (
                    <Text type="secondary">Текст резюме отсутствует</Text>
                  )}
                </div>
              </Card>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};
