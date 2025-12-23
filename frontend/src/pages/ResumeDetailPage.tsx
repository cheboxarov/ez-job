import { useEffect, useState } from 'react';
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
  Tooltip,
  Divider,
} from 'antd';
import {
  ArrowLeftOutlined,
  SearchOutlined,
  RobotOutlined,
  SettingOutlined,
  FileTextOutlined,
  QuestionCircleOutlined,
  SendOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { getResume, updateResume } from '../api/resumes';
import {
  getResumeFilterSettings,
  updateResumeFilterSettings,
  suggestResumeFilterSettings,
} from '../api/resumeFilterSettings';
import { getAreas, type HhArea } from '../api/dictionaries';
import { getDailyResponses } from '../api/subscription';
import { FilterSettingsForm } from '../components/FilterSettingsForm';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import { LimitReachedAlert } from '../components/LimitReachedAlert';
import { ResumeContent } from '../components/ResumeContent';
import type { Resume, ResumeFilterSettings, ResumeFilterSettingsUpdate } from '../types/api';

const { Text, Paragraph, Title } = Typography;

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
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [resumeParamsDirty, setResumeParamsDirty] = useState(false);
  const [initialFilterValues, setInitialFilterValues] = useState<Record<string, unknown> | null>(
    null,
  );
  const [dailyResponses, setDailyResponses] = useState<{ count: number; limit: number } | null>(null);

  useEffect(() => {
    if (resumeId) {
      loadData();
      loadAreas();
      loadDailyResponses();
    }
  }, [resumeId]);

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

  const loadDailyResponses = async () => {
    try {
      const response = await getDailyResponses();
      setDailyResponses({ count: response.count, limit: response.limit });
    } catch (err) {
      setDailyResponses(null);
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
          <Space size="middle">
            <Button
              icon={<SendOutlined />}
              size="large"
              onClick={() => navigate(`/resumes/${resumeId}/responses`)}
              disabled={!resume?.headhunter_hash}
              style={{ borderRadius: 10, height: 44, border: '1px solid #e5e7eb' }}
            >
              История откликов
            </Button>
            <GradientButton
              icon={<SearchOutlined />}
              onClick={() => navigate(`/resumes/${resumeId}/vacancies`)}
            >
              Подходящие вакансии
            </GradientButton>
          </Space>
        }
      />

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {dailyResponses && 
         dailyResponses.count >= dailyResponses.limit && 
         dailyResponses.limit < 200 && (
          <LimitReachedAlert 
            limit={dailyResponses.limit} 
            count={dailyResponses.count} 
          />
        )}

        <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={8}>
            <Card
              bordered={true}
              style={{
                borderRadius: 20,
                border: resume?.is_auto_reply 
                  ? '2px solid #86efac'
                  : '1px solid #e5e7eb',
                boxShadow: resume?.is_auto_reply 
                  ? '0 4px 20px rgba(34, 197, 94, 0.15)'
                  : '0 2px 8px rgba(0,0,0,0.06)',
                background: resume?.is_auto_reply 
                  ? 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
                  : 'linear-gradient(135deg, #ffffff 0%, #fafafa 100%)',
                overflow: 'hidden',
                position: 'relative',
                height: '100%',
              }}
              styles={{ 
                body: { 
                  padding: 24,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: '100%',
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
              
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', position: 'relative' }}>
                <div style={{ display: 'flex', gap: 16 }}>
                  <div
                    style={{
                      width: 52,
                      height: 52,
                      background: resume?.is_auto_reply 
                        ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                        : 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
                      borderRadius: 14,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: resume?.is_auto_reply 
                        ? '0 4px 12px rgba(34, 197, 94, 0.35)'
                        : '0 2px 6px rgba(100, 116, 139, 0.2)',
                      flexShrink: 0,
                    }}
                  >
                    <RobotOutlined style={{ fontSize: 24, color: 'white' }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <Title level={5} style={{ margin: 0, fontWeight: 700, color: '#0f172a' }}>
                        Автоотклик
                      </Title>
                      {resume?.is_auto_reply && (
                        <div
                          style={{
                            padding: '2px 8px',
                            background: 'rgba(34, 197, 94, 0.15)',
                            borderRadius: 12,
                            fontSize: 11,
                            fontWeight: 600,
                            color: '#16a34a',
                          }}
                        >
                          Активен
                        </div>
                      )}
                    </div>
                    <Text style={{ fontSize: 13, color: '#64748b', lineHeight: 1.5, display: 'block' }}>
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
                  style={{ marginTop: 4, flexShrink: 0 }}
                />
              </div>

              {resume?.is_auto_reply && dailyResponses && (
                <>
                  <Divider style={{ margin: '20px 0 16px', borderColor: 'rgba(34, 197, 94, 0.2)' }} />
                  <div style={{ display: 'flex', gap: 12 }}>
                    <div
                      style={{
                        flex: 1,
                        padding: '12px 14px',
                        background: 'rgba(255, 255, 255, 0.7)',
                        borderRadius: 12,
                        border: '1px solid rgba(34, 197, 94, 0.15)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <CheckCircleOutlined style={{ color: '#16a34a', fontSize: 16 }} />
                        <div>
                          <Text style={{ fontSize: 18, fontWeight: 700, color: '#16a34a', display: 'block', lineHeight: 1 }}>
                            {dailyResponses.count}
                          </Text>
                          <Text style={{ fontSize: 11, color: '#64748b' }}>сегодня</Text>
                        </div>
                      </div>
                    </div>
                    <div
                      style={{
                        flex: 1,
                        padding: '12px 14px',
                        background: 'rgba(255, 255, 255, 0.7)',
                        borderRadius: 12,
                        border: '1px solid rgba(34, 197, 94, 0.15)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <ClockCircleOutlined style={{ color: '#64748b', fontSize: 16 }} />
                        <div>
                          <Text style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', display: 'block', lineHeight: 1 }}>
                            {dailyResponses.limit - dailyResponses.count}
                          </Text>
                          <Text style={{ fontSize: 11, color: '#64748b' }}>осталось</Text>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            <Card
              bordered={true}
              style={{ 
                borderRadius: 20, 
                border: '1px solid #e5e7eb',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                height: '100%',
                display: 'flex',
                flexDirection: 'column'
              }}
              styles={{ 
                header: { 
                  borderBottom: '1px solid #f1f5f9',
                  padding: '16px 20px',
                },
                body: { 
                  padding: 20,
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column'
                } 
              }}
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                      borderRadius: 10,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <ThunderboltOutlined style={{ fontSize: 16, color: '#2563eb' }} />
                  </div>
                  <Text strong style={{ fontSize: 15 }}>Дополнительные требования</Text>
                </div>
              }
            >
              <Form 
                form={resumeForm} 
                layout="vertical" 
                requiredMark={false}
                onValuesChange={handleResumeParamsChange}
                style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              >
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <Form.Item
                    name="user_parameters"
                    style={{ marginBottom: 12, flex: 1 }}
                  >
                    <Input.TextArea
                      placeholder="Например: Только удаленка, без легаси кода..."
                      style={{ 
                        borderRadius: 12, 
                        resize: 'none',
                        border: '1px solid #e5e7eb',
                        height: '100%',
                        minHeight: 200
                      }}
                      maxLength={500}
                      showCount
                    />
                  </Form.Item>
                  
                  {!resumeParamsDirty && (
                    <div style={{ marginTop: 'auto', paddingTop: 12 }}>
                      <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>
                        Примеры:
                      </Text>
                      <ul style={{ margin: 0, paddingLeft: 20, fontSize: 12, color: '#94a3b8' }}>
                        <li>Только удаленка, без гибрида</li>
                        <li>Без тестовых заданий</li>
                        <li>Без легаси кода</li>
                      </ul>
                    </div>
                  )}
                </div>

                {resumeParamsDirty && (
                  <Button
                    type="primary"
                    block
                    onClick={handleResumeParamsSave}
                    loading={savingResumeParams}
                    style={{ 
                      borderRadius: 12, 
                      height: 42,
                      background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                      border: 'none',
                      fontWeight: 600,
                      marginTop: 24,
                    }}
                  >
                    Сохранить требования
                  </Button>
                )}
              </Form>
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            <Card
              bordered={true}
              style={{ 
                borderRadius: 20, 
                border: '1px solid #e5e7eb',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                height: '100%',
              }}
              styles={{ 
                header: { 
                  borderBottom: '1px solid #f1f5f9',
                  padding: '16px 20px',
                },
                body: { padding: 20 } 
              }}
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                      borderRadius: 10,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <SettingOutlined style={{ fontSize: 16, color: '#2563eb' }} />
                  </div>
                  <Text strong style={{ fontSize: 15 }}>Настройки поиска</Text>
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
          </Col>
        </Row>

        <Row gutter={[24, 24]}>
          <Col xs={24}>
            <div
              style={{
                background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                border: '1px solid #e2e8f0',
                borderRadius: 14,
                padding: 24,
                fontSize: 14,
                lineHeight: 1.8,
                color: '#334155',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                margin: 0,
                boxSizing: 'border-box',
              }}
            >
              {resume?.content ? (
                <ResumeContent content={resume.content} />
              ) : (
                <Text type="secondary">Текст резюме отсутствует</Text>
              )}
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};
