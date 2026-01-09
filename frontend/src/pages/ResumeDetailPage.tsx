import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  message,
  Space,
  Spin,
  Alert,
  Switch,
  Row,
  Col,
  Divider,
  Slider,
} from 'antd';
import {
  ArrowLeftOutlined,
  SearchOutlined,
  RobotOutlined,
  SettingOutlined,
  FileTextOutlined,
  SendOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { getResume, updateResume, evaluateResume } from '../api/resumes';
import {
  getResumeFilterSettings,
  updateResumeFilterSettings,
  suggestResumeFilterSettings,
} from '../api/resumeFilterSettings';
import { getAreas, type HhArea } from '../api/dictionaries';
import { useDailyResponsesStore } from '../stores/dailyResponsesStore';
import { FilterSettingsForm } from '../components/FilterSettingsForm';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import { LimitReachedAlert } from '../components/LimitReachedAlert';
import { ResumeContent } from '../components/ResumeContent';
import { ResumeEvaluation } from '../components/ResumeEvaluation';
import { useWindowSize } from '../hooks/useWindowSize';
import type { Resume, ResumeFilterSettings, ResumeFilterSettingsUpdate } from '../types/api';

const { Text, Title } = Typography;

const FILTER_COMPARE_KEYS: (keyof ResumeFilterSettings)[] = [
  'text',
  'experience',
  'employment',
  'schedule',
  'professional_role',
  'area',
  'salary',
  'currency',
  'only_with_salary',
];

export const ResumeDetailPage = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [resumeForm] = Form.useForm();
  const [filterForm] = Form.useForm();

  const [resume, setResume] = useState<Resume | null>(null);
  const [filterSettings, setFilterSettings] = useState<ResumeFilterSettings | null>(null);
  const [areasTree, setAreasTree] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingResumeParams, setSavingResumeParams] = useState(false);
  const [savingFilters, setSavingFilters] = useState(false);
  const [savingAutoReply, setSavingAutoReply] = useState(false);
  const [savingAutolikeThreshold, setSavingAutolikeThreshold] = useState(false);
  const [localAutolikeThreshold, setLocalAutolikeThreshold] = useState<number | null>(null);
  const autolikeThresholdTimeoutRef = useRef<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResult, setEvaluationResult] = useState<any | null>(null);
  const [evaluationLoading, setEvaluationLoading] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [resumeParamsDirty, setResumeParamsDirty] = useState(false);
  const [initialFilterValues, setInitialFilterValues] = useState<Record<string, unknown> | null>(
    null,
  );
  const { count, limit, remaining, loading: dailyResponsesLoading, fetchDailyResponses } = useDailyResponsesStore();
  const { isMobile } = useWindowSize();

  useEffect(() => {
    if (resumeId) {
      loadData();
      loadAreas();
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

  useEffect(() => {
    if (resume?.autolike_threshold !== undefined) {
      setLocalAutolikeThreshold(null);
    }
  }, [resume?.autolike_threshold]);

  const loadData = async () => {
    if (!resumeId) return;
    setLoading(true);
    setError(null);
    try {
      const [resumeData, settingsData] = await Promise.all([
        getResume(resumeId),
        getResumeFilterSettings(resumeId).catch(() => null),
      ]);

      setResume(resumeData);
      setFilterSettings(settingsData);

      resumeForm.setFieldsValue({
        user_parameters: resumeData.user_parameters || '',
      });
      setResumeParamsDirty(false);

      if (settingsData) {
        filterForm.setFieldsValue({
          text: settingsData.text || '',
          experience: settingsData.experience || [],
          employment: settingsData.employment || [],
          schedule: settingsData.schedule || [],
          professional_role: settingsData.professional_role || [],
          area: settingsData.area || '',
          salary: settingsData.salary ?? null,
          currency: settingsData.currency || 'RUR',
          only_with_salary: settingsData.only_with_salary,
        });
        const current = filterForm.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
        setInitialFilterValues(current);
      }
      setIsDirty(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const loadAreas = async () => {
    try {
      const areas = await getAreas();
      const mapToTreeData = (nodes: HhArea[]): any[] =>
        nodes.map((node) => ({
          title: node.name,
          value: node.id,
          key: node.id,
          children: node.areas && node.areas.length ? mapToTreeData(node.areas) : undefined,
        }));
      setAreasTree(mapToTreeData(areas));
    } catch {
      setAreasTree([]);
    }
  };


  const handleResumeParamsSave = async () => {
    if (!resumeId) return;
    const values = await resumeForm.validateFields();
    setSavingResumeParams(true);
    try {
      const updated = await updateResume(resumeId, {
        user_parameters: values.user_parameters?.trim() || null,
      });
      setResume(updated);
      setResumeParamsDirty(false);
      message.success('Параметры сохранены');
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при сохранении параметров');
    } finally {
      setSavingResumeParams(false);
    }
  };

  const handleAutoReplyToggle = async (checked: boolean) => {
    if (!resumeId) return;
    setSavingAutoReply(true);
    try {
      const updated = await updateResume(resumeId, {
        is_auto_reply: checked,
      });
      setResume(updated);
      message.success(
        checked
          ? 'Автоотклик включен'
          : 'Автоотклик выключен',
      );
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при обновлении автоотклика');
      if (resume) {
        setResume({ ...resume, is_auto_reply: !checked });
      }
    } finally {
      setSavingAutoReply(false);
    }
  };

  const saveAutolikeThreshold = async (value: number) => {
    if (!resumeId) return;
    setSavingAutolikeThreshold(true);
    try {
      const updated = await updateResume(resumeId, {
        autolike_threshold: value,
      });
      setResume(updated);
      setLocalAutolikeThreshold(null);
      message.success(`Порог автолика установлен: ${value}%`);
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при обновлении порога автолика');
    } finally {
      setSavingAutolikeThreshold(false);
    }
  };

  const handleAutolikeThresholdChange = (value: number) => {
    setLocalAutolikeThreshold(value);
    
    if (autolikeThresholdTimeoutRef.current) {
      clearTimeout(autolikeThresholdTimeoutRef.current);
    }
    
    autolikeThresholdTimeoutRef.current = setTimeout(() => {
      saveAutolikeThreshold(value);
    }, 500);
  };

  useEffect(() => {
    return () => {
      if (autolikeThresholdTimeoutRef.current) {
        clearTimeout(autolikeThresholdTimeoutRef.current);
      }
    };
  }, []);

  const handleFilterSave = async (values: ResumeFilterSettingsUpdate) => {
    if (!resumeId) return;
    setSavingFilters(true);
    try {
      const saved = await updateResumeFilterSettings(resumeId, values);
      setFilterSettings(saved);
      const current = filterForm.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
      setInitialFilterValues(current);
      setIsDirty(false);
      message.success('Настройки фильтров сохранены');
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при сохранении фильтров');
    } finally {
      setSavingFilters(false);
    }
  };

  const handleFilterSuggest = async () => {
    if (!resumeId) return;
    setSavingFilters(true);
    try {
      const suggested = await suggestResumeFilterSettings(resumeId);
      filterForm.setFieldsValue({
        text: suggested.text ?? '',
        salary: suggested.salary ?? null,
        currency: suggested.currency || 'RUR',
      });
      handleFilterValuesChange();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при генерации фильтров');
    } finally {
      setSavingFilters(false);
    }
  };

  const handleFilterValuesChange = () => {
    const current = filterForm.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
    if (!initialFilterValues) {
      setIsDirty(true);
      return;
    }
    const dirty = FILTER_COMPARE_KEYS.some((key) => {
      const prev = initialFilterValues[key];
      const curr = current[key as string];
      return (prev ?? null) !== (curr ?? null);
    });
    setIsDirty(dirty);
  };

  const handleResumeParamsChange = () => {
    const current = (resumeForm.getFieldValue('user_parameters') ?? '').trim();
    const initial = (resume?.user_parameters ?? '').trim();
    setResumeParamsDirty(current !== initial);
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
        subtitle="Настройте параметры автоотклика и фильтры поиска"
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

        <Row gutter={24} style={{ alignItems: 'flex-start' }}>
          {/* Основной контент */}
          <Col xs={24} lg={16} xl={17}>
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

          {/* Правый сайдбар */}
          <Col xs={24} lg={8} xl={7}>
            <div style={{ 
              position: 'sticky',
              top: 24,
              maxHeight: 'calc(100vh - 48px)',
              overflowY: 'auto',
            }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Карточка автоотклика */}
              <Card
                bordered={true}
                style={{
                  borderRadius: 20,
                  border: resume?.is_auto_reply 
                    ? '2px solid #86efac'
                    : '1px solid #e5e7eb',
                  background: resume?.is_auto_reply 
                    ? 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
                    : 'linear-gradient(135deg, #ffffff 0%, #fafafa 100%)',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                styles={{ 
                  body: { 
                    padding: 20,
                  } 
                }}
              >
                {resume?.is_auto_reply && (
                  <div
                    style={{
                      position: 'absolute',
                      top: -30,
                      right: -30,
                      width: 100,
                      height: 100,
                      background: 'radial-gradient(circle, rgba(34, 197, 94, 0.15) 0%, transparent 70%)',
                      borderRadius: '50%',
                    }}
                  />
                )}
                
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', position: 'relative', marginBottom: resume?.is_auto_reply ? 16 : 0 }}>
                  <div style={{ display: 'flex', gap: 12, flex: 1 }}>
                    <div
                      style={{
                        width: 44,
                        height: 44,
                        background: resume?.is_auto_reply 
                          ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                          : 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
                        borderRadius: 12,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: resume?.is_auto_reply ? '1px solid #22c55e' : '1px solid #64748b',
                        flexShrink: 0,
                      }}
                    >
                      <RobotOutlined style={{ fontSize: 20, color: 'white' }} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4, flexWrap: 'wrap' }}>
                        <Title level={5} style={{ margin: 0, fontWeight: 700, color: '#0f172a', fontSize: 15 }}>
                          Автоотклик
                        </Title>
                        {resume?.is_auto_reply && (
                          <div
                            style={{
                              padding: '2px 6px',
                              background: 'rgba(34, 197, 94, 0.15)',
                              borderRadius: 8,
                              fontSize: 10,
                              fontWeight: 600,
                              color: '#16a34a',
                            }}
                          >
                            Активен
                          </div>
                        )}
                      </div>
                      <Text style={{ fontSize: 12, color: '#64748b', lineHeight: 1.4, display: 'block' }}>
                        {resume?.is_auto_reply 
                          ? 'Автоматические отклики на подходящие вакансии'
                          : 'Включите для автоматического отклика'}
                      </Text>
                    </div>
                  </div>
                  <Switch
                    checked={resume?.is_auto_reply || false}
                    onChange={handleAutoReplyToggle}
                    loading={savingAutoReply}
                    disabled={savingAutoReply}
                    style={{ marginTop: 2, flexShrink: 0 }}
                  />
                </div>

                {resume?.is_auto_reply && (
                  <>
                    <Divider style={{ margin: '16px 0 12px', borderColor: 'rgba(34, 197, 94, 0.2)' }} />
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ marginBottom: 6 }}>
                        <Text style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>
                          Порог автолика
                        </Text>
                      </div>
                      <Slider
                        min={0}
                        max={100}
                        value={localAutolikeThreshold ?? resume?.autolike_threshold ?? 50}
                        onChange={handleAutolikeThresholdChange}
                        disabled={savingAutolikeThreshold}
                        marks={{
                          0: '0%',
                          50: '50%',
                          100: '100%',
                        }}
                        tooltip={{ formatter: (value) => `${value}%` }}
                        style={{ marginBottom: 24 }}
                      />
                      <Text style={{ fontSize: 11, color: '#94a3b8', marginTop: 4, display: 'block' }}>
                        Отклики на вакансии с оценкой {localAutolikeThreshold ?? resume?.autolike_threshold ?? 50}% и выше
                      </Text>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <div
                        style={{
                          flex: 1,
                          padding: '10px 12px',
                          background: 'rgba(255, 255, 255, 0.7)',
                          borderRadius: 10,
                          border: '1px solid rgba(34, 197, 94, 0.15)',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <CheckCircleOutlined style={{ color: '#16a34a', fontSize: 14 }} />
                          <div>
                            <Text style={{ fontSize: 16, fontWeight: 700, color: '#16a34a', display: 'block', lineHeight: 1 }}>
                              {count}
                            </Text>
                            <Text style={{ fontSize: 10, color: '#64748b' }}>сегодня</Text>
                          </div>
                        </div>
                      </div>
                      <div
                        style={{
                          flex: 1,
                          padding: '10px 12px',
                          background: 'rgba(255, 255, 255, 0.7)',
                          borderRadius: 10,
                          border: '1px solid rgba(34, 197, 94, 0.15)',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <ClockCircleOutlined style={{ color: '#64748b', fontSize: 14 }} />
                          <div>
                            <Text style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', display: 'block', lineHeight: 1 }}>
                              {remaining}
                            </Text>
                            <Text style={{ fontSize: 10, color: '#64748b' }}>осталось</Text>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </Card>

              {/* Карточка дополнительных требований */}
              <Card
                bordered={true}
                style={{ 
                  borderRadius: 20, 
                  border: '1px solid #e5e7eb',
                }}
                styles={{ 
                  header: { 
                    borderBottom: '1px solid #f1f5f9',
                    padding: '14px 18px',
                  },
                  body: { 
                    padding: 18,
                  } 
                }}
                title={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                        borderRadius: 8,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <ThunderboltOutlined style={{ fontSize: 14, color: '#2563eb' }} />
                    </div>
                    <Text strong style={{ fontSize: 14 }}>Дополнительные требования</Text>
                  </div>
                }
              >
                <Form 
                  form={resumeForm} 
                  layout="vertical" 
                  requiredMark={false}
                  onValuesChange={handleResumeParamsChange}
                >
                  <Form.Item
                    name="user_parameters"
                    style={{ marginBottom: 12 }}
                  >
                    <Input.TextArea
                      placeholder="Например: Только удаленка, без легаси кода..."
                      style={{ 
                        borderRadius: 10, 
                        resize: 'none',
                        border: '1px solid #e5e7eb',
                        minHeight: 120
                      }}
                      maxLength={500}
                      showCount
                    />
                  </Form.Item>
                  
                  {!resumeParamsDirty && (
                    <div>
                      <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 4 }}>
                        Примеры:
                      </Text>
                      <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: '#94a3b8' }}>
                        <li>Только удаленка, без гибрида</li>
                        <li>Без тестовых заданий</li>
                        <li>Без легаси кода</li>
                      </ul>
                    </div>
                  )}

                  {resumeParamsDirty && (
                    <Button
                      type="primary"
                      block
                      onClick={handleResumeParamsSave}
                      loading={savingResumeParams}
                      style={{ 
                        borderRadius: 10, 
                        height: 38,
                        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                        border: 'none',
                        fontWeight: 600,
                        marginTop: 12,
                      }}
                    >
                      Сохранить требования
                    </Button>
                  )}
                </Form>
              </Card>

              {/* Карточка настроек поиска */}
              <Card
                bordered={true}
                style={{ 
                  borderRadius: 20, 
                  border: '1px solid #e5e7eb',
                }}
                styles={{ 
                  header: { 
                    borderBottom: '1px solid #f1f5f9',
                    padding: '14px 18px',
                  },
                  body: { padding: 18 } 
                }}
                title={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                        borderRadius: 8,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <SettingOutlined style={{ fontSize: 14, color: '#2563eb' }} />
                    </div>
                    <Text strong style={{ fontSize: 14 }}>Настройки поиска</Text>
                  </div>
                }
              >
                <Form
                  form={filterForm}
                  layout="vertical"
                  onValuesChange={handleFilterValuesChange}
                  initialValues={{
                    only_with_salary: false,
                    ...filterSettings,
                  }}
                >
                  <FilterSettingsForm
                    form={filterForm}
                    initialValues={filterSettings}
                    areasTree={areasTree}
                    loading={savingFilters}
                    isDirty={isDirty}
                    onSave={handleFilterSave}
                    onSuggest={handleFilterSuggest}
                    onValuesChange={handleFilterValuesChange}
                  />
                </Form>
              </Card>
            </div>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};
