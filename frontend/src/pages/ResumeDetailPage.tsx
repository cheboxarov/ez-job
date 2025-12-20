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
} from '@ant-design/icons';
import { getResume, updateResume } from '../api/resumes';
import {
  getResumeFilterSettings,
  updateResumeFilterSettings,
  suggestResumeFilterSettings,
} from '../api/resumeFilterSettings';
import { getAreas, type HhArea } from '../api/dictionaries';
import { FilterSettingsForm } from '../components/FilterSettingsForm';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import type { Resume, ResumeFilterSettings, ResumeFilterSettingsUpdate } from '../types/api';

const { Text, Paragraph } = Typography;

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
  const [initialFilterValues, setInitialFilterValues] = useState<Record<string, unknown> | null>(
    null,
  );

  useEffect(() => {
    if (resumeId) {
      loadData();
      loadAreas();
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


  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка резюме..." />
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
              style={{ borderRadius: 10, height: 44 }}
            >
              История откликов
            </Button>
            <GradientButton
              icon={<SearchOutlined />}
              onClick={() => navigate(`/resumes/${resumeId}/vacancies`)}
            >
              Найти вакансии
            </GradientButton>
          </Space>
        }
      />

      <Row gutter={[24, 24]} style={{ alignItems: 'stretch' }}>
        {/* Left Column: Resume Content */}
        <Col xs={24} lg={15} xl={16} style={{ display: 'flex' }}>
          <Card
            title={
              <Space>
                <FileTextOutlined style={{ color: '#2563eb' }} />
                <span>Содержание резюме</span>
              </Space>
            }
            bordered={false}
            style={{
              borderRadius: 16,
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              width: '100%',
            }}
            styles={{
              body: {
                overflow: 'auto',
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
              }
            }}
          >
            <div
              style={{
                whiteSpace: 'pre-wrap',
                background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                border: '1px solid #e2e8f0',
                borderRadius: 12,
                padding: 24,
                fontSize: 14,
                lineHeight: 1.7,
                color: '#334155',
                fontFamily: 'Menlo, Monaco, Consolas, "Courier New", monospace',
                maxHeight: 'calc(100vh - 300px)',
                margin: 0,
                overflow: 'auto',
                boxSizing: 'border-box',
              }}
            >
              {resume?.content || 'Текст резюме отсутствует'}
            </div>
          </Card>
        </Col>

        {/* Right Column: Settings & Filters */}
        <Col xs={24} lg={9} xl={8}>
          <Space direction="vertical" size={20} style={{ width: '100%' }}>
            
            {/* Auto Reply Card */}
            <Card
              bordered={false}
              style={{
                borderRadius: 16,
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                background: resume?.is_auto_reply 
                  ? 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
                  : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: resume?.is_auto_reply 
                  ? '1px solid #86efac'
                  : '1px solid #e5e7eb',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              {/* Pulse animation when active */}
              {resume?.is_auto_reply && (
                <div
                  style={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    width: 8,
                    height: 8,
                    background: '#22c55e',
                    borderRadius: '50%',
                    animation: 'pulse 2s infinite',
                  }}
                />
              )}
              
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', gap: 14 }}>
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      background: resume?.is_auto_reply 
                        ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                        : 'linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%)',
                      borderRadius: 12,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: resume?.is_auto_reply 
                        ? '0 4px 12px rgba(34, 197, 94, 0.3)'
                        : 'none',
                    }}
                  >
                    <RobotOutlined style={{ fontSize: 22, color: 'white' }} />
                  </div>
                  <div>
                    <Text strong style={{ fontSize: 17, color: '#0f172a', display: 'block' }}>
                      Автоотклик
                    </Text>
                    <Paragraph type="secondary" style={{ fontSize: 13, marginBottom: 0, lineHeight: 1.5, marginTop: 4 }}>
                      {resume?.is_auto_reply 
                        ? 'Система автоматически откликается на подходящие вакансии'
                        : 'Включите для автоматического отклика на вакансии'}
                    </Paragraph>
                  </div>
                </div>
                <Switch
                  checked={resume?.is_auto_reply || false}
                  onChange={handleAutoReplyToggle}
                  loading={savingAutoReply}
                  disabled={savingAutoReply}
                  style={{ marginTop: 4 }}
                />
              </div>
            </Card>

            {/* User Parameters */}
            <Card
              title={
                <Space>
                  <ThunderboltOutlined style={{ color: '#f59e0b' }} />
                  <span>Дополнительные требования</span>
                  <Tooltip
                    title={
                      <div>
                        <div style={{ marginBottom: 8 }}>
                          Укажите специфичные требования к вакансиям, которые не могут быть выражены через стандартные фильтры.
                        </div>
                        <div>
                          <strong>Примеры:</strong>
                        </div>
                        <div>• Только удаленка, без гибрида</div>
                        <div>• Без тестовых заданий</div>
                        <div>• Без легаси кода</div>
                      </div>
                    }
                  >
                    <QuestionCircleOutlined style={{ color: '#94a3b8', cursor: 'help' }} />
                  </Tooltip>
                </Space>
              }
              size="small"
              bordered={false}
              style={{ borderRadius: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
            >
              <Form form={resumeForm} layout="vertical" requiredMark={false}>
                <Form.Item
                  name="user_parameters"
                  style={{ marginBottom: 12 }}
                >
                  <Input.TextArea
                    rows={3}
                    placeholder="Например: Только удаленка, без легаси кода..."
                    style={{ borderRadius: 10, resize: 'none' }}
                    maxLength={500}
                    showCount
                  />
                </Form.Item>
                <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
                  <Button
                    type="dashed"
                    block
                    onClick={handleResumeParamsSave}
                    loading={savingResumeParams}
                    style={{ borderRadius: 10, height: 40 }}
                  >
                    Сохранить требования
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            {/* Filters */}
            <Card
              title={
                <Space>
                  <SettingOutlined style={{ color: '#8b5cf6' }} />
                  <span>Настройки поиска</span>
                </Space>
              }
              bordered={false}
              style={{ borderRadius: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
              styles={{ body: { padding: '16px 20px' } }}
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

          </Space>
        </Col>
      </Row>
      
      {/* CSS for pulse animation */}
      <style>{`
        @keyframes pulse {
          0% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
          }
        }
      `}</style>
    </div>
  );
};
