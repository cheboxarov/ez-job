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
  Slider,
  Tag,
  Tabs,
} from 'antd';
import {
  RobotOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { getResume, updateResume } from '../api/resumes';
import {
  getResumeFilterSettings,
  updateResumeFilterSettings,
  suggestResumeFilterSettings,
} from '../api/resumeFilterSettings';
import { getAreas, type HhArea } from '../api/dictionaries';
import { useDailyResponsesStore } from '../stores/dailyResponsesStore';
import { FilterSettingsForm } from '../components/FilterSettingsForm';
import { PageHeader } from '../components/PageHeader';
import { LimitReachedAlert } from '../components/LimitReachedAlert';
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

export const ResumeAutolikePage = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [filterForm] = Form.useForm();

  const [resume, setResume] = useState<Resume | null>(null);
  const [filterSettings, setFilterSettings] = useState<ResumeFilterSettings | null>(null);
  const [areasTree, setAreasTree] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingAutoReply, setSavingAutoReply] = useState(false);
  const [localAutolikeThreshold, setLocalAutolikeThreshold] = useState<number | null>(null);
  const [localAutoReply, setLocalAutoReply] = useState<boolean | null>(null);
  const autolikeThresholdTimeoutRef = useRef<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [initialFilterValues, setInitialFilterValues] = useState<Record<string, unknown> | null>(
    null,
  );
  const [requirements, setRequirements] = useState<string[]>([]);
  const [newRequirement, setNewRequirement] = useState('');
  const [initialRequirements, setInitialRequirements] = useState<string[]>([]);
  const [initialAutolikeThreshold, setInitialAutolikeThreshold] = useState<number | null>(null);
  const [initialAutoReply, setInitialAutoReply] = useState<boolean | null>(null);
  const { count, limit, remaining, loading: dailyResponsesLoading, fetchDailyResponses } = useDailyResponsesStore();
  const { isMobile } = useWindowSize();

  useEffect(() => {
    if (resumeId) {
      loadData();
      loadAreas();
      fetchDailyResponses();
    }
  }, [resumeId, fetchDailyResponses]);

  useEffect(() => {
    if (resume?.autolike_threshold !== undefined) {
      if (localAutolikeThreshold === null) {
        setInitialAutolikeThreshold(resume.autolike_threshold);
      }
    }
  }, [resume?.autolike_threshold]);

  useEffect(() => {
    if (resume?.is_auto_reply !== undefined) {
      if (localAutoReply === null) {
        setInitialAutoReply(resume.is_auto_reply);
      }
    }
  }, [resume?.is_auto_reply]);

  // Отслеживаем изменения для показа кнопки сохранения
  useEffect(() => {
    if (resume) {
      checkDirty();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requirements, localAutolikeThreshold, localAutoReply]);

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

      // Загружаем требования из user_parameters (разбиваем по |)
      const loadRequirements = (userParams: string | null): string[] => {
        if (!userParams) return [];
        if (!userParams.includes('|')) {
          return userParams.trim() ? [userParams.trim()] : [];
        }
        return userParams.split('|').filter(r => r.trim()).map(r => r.trim());
      };
      
      const loadedRequirements = loadRequirements(resumeData.user_parameters);
      setRequirements(loadedRequirements);
      setInitialRequirements(loadedRequirements);
      setInitialAutolikeThreshold(resumeData.autolike_threshold ?? 50);
      setInitialAutoReply(resumeData.is_auto_reply ?? false);

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

  const checkDirty = () => {
    if (!resume) {
      setIsDirty(false);
      return;
    }

    // Проверяем изменения в требованиях
    const requirementsChanged = JSON.stringify(requirements) !== JSON.stringify(initialRequirements);
    
    // Проверяем изменения в пороге автолика
    const currentThreshold = localAutolikeThreshold ?? (resume?.autolike_threshold ?? 50);
    const thresholdChanged = currentThreshold !== (initialAutolikeThreshold ?? 50);
    
    // Проверяем изменения в тумблере автоотклика
    const currentAutoReply = localAutoReply !== null ? localAutoReply : (resume?.is_auto_reply ?? false);
    const autoReplyChanged = currentAutoReply !== (initialAutoReply ?? false);
    
    // Проверяем изменения в фильтрах
    const current = filterForm.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
    const filtersChanged = initialFilterValues ? 
      FILTER_COMPARE_KEYS.some((key) => {
        const prev = initialFilterValues[key];
        const curr = current[key as string];
        return (prev ?? null) !== (curr ?? null);
      }) : false;

    setIsDirty(requirementsChanged || thresholdChanged || autoReplyChanged || filtersChanged);
  };

  const handleAutoReplyToggle = (checked: boolean) => {
    setLocalAutoReply(checked);
  };

  const handleAutolikeThresholdChange = (value: number) => {
    setLocalAutolikeThreshold(value);
    if (autolikeThresholdTimeoutRef.current) {
      clearTimeout(autolikeThresholdTimeoutRef.current);
    }
    autolikeThresholdTimeoutRef.current = window.setTimeout(() => {
      checkDirty();
    }, 300);
  };

  const handleAddRequirement = () => {
    const trimmed = newRequirement.trim();
    if (!trimmed) {
      message.warning('Введите требование');
      return;
    }
    if (trimmed.length > 100) {
      message.warning('Максимальная длина требования - 100 символов');
      return;
    }
    if (requirements.includes(trimmed)) {
      message.warning('Такое требование уже добавлено');
      return;
    }
    const updated = [...requirements, trimmed];
    setRequirements(updated);
    setNewRequirement('');
    // checkDirty будет вызван через useEffect
  };

  const handleRemoveRequirement = (index: number) => {
    const updated = requirements.filter((_, i) => i !== index);
    setRequirements(updated);
    // checkDirty будет вызван через useEffect
  };

  const handleFilterValuesChange = () => {
    checkDirty();
  };

  const handleFilterSuggest = async () => {
    if (!resumeId) return;
    setSaving(true);
    try {
      const suggested = await suggestResumeFilterSettings(resumeId);
      filterForm.setFieldsValue({
        text: suggested.text ?? '',
        salary: suggested.salary ?? null,
        currency: suggested.currency || 'RUR',
      });
      checkDirty();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при генерации фильтров');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAll = async () => {
    if (!resumeId) return;
    setSaving(true);
    try {
      // Сохраняем требования
      const saveRequirements = (reqs: string[]): string | null => {
        const filtered = reqs.filter(r => r.trim());
        return filtered.length > 0 ? filtered.join('|') : null;
      };
      
      const userParamsString = saveRequirements(requirements);
      
      // Сохраняем резюме (требования + порог автолика + тумблер автоотклика)
      const resumeUpdate: any = {
        user_parameters: userParamsString,
      };
      
      if (localAutolikeThreshold !== null) {
        resumeUpdate.autolike_threshold = localAutolikeThreshold;
      }
      
      if (localAutoReply !== null) {
        resumeUpdate.is_auto_reply = localAutoReply;
      }
      
      const updatedResume = await updateResume(resumeId, resumeUpdate);
      setResume(updatedResume);
      
      // Обновляем requirements на основе сохраненных данных
      const loadRequirements = (userParams: string | null): string[] => {
        if (!userParams) return [];
        if (!userParams.includes('|')) {
          return userParams.trim() ? [userParams.trim()] : [];
        }
        return userParams.split('|').filter(r => r.trim()).map(r => r.trim());
      };
      const savedRequirements = loadRequirements(updatedResume.user_parameters);
      setRequirements(savedRequirements);
      setInitialRequirements(savedRequirements);
      setLocalAutolikeThreshold(null);
      setInitialAutolikeThreshold(updatedResume.autolike_threshold ?? 50);
      setLocalAutoReply(null);
      setInitialAutoReply(updatedResume.is_auto_reply ?? false);
      
      // Сохраняем фильтры
      const filterValues = await filterForm.validateFields();
      const filterUpdate: ResumeFilterSettingsUpdate = {
        text: filterValues.text || null,
        experience: filterValues.experience || null,
        employment: filterValues.employment || null,
        schedule: filterValues.schedule || null,
        professional_role: filterValues.professional_role || null,
        area: filterValues.area || null,
        salary: filterValues.salary ?? null,
        currency: filterValues.currency || null,
        only_with_salary: filterValues.only_with_salary ?? false,
        period: filterValues.period || null,
        date_from: filterValues.date_from || null,
        date_to: filterValues.date_to || null,
      };
      
      await updateResumeFilterSettings(resumeId, filterUpdate);
      const updatedSettings = await getResumeFilterSettings(resumeId);
      setFilterSettings(updatedSettings);
      
      const current = filterForm.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
      setInitialFilterValues(current);
      
      setIsDirty(false);
      message.success('Все изменения сохранены');
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при сохранении');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error && !resume) {
    return (
      <div style={{ padding: '24px', maxWidth: 800, margin: '0 auto' }}>
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

  const currentThreshold = localAutolikeThreshold ?? resume?.autolike_threshold ?? 50;

  return (
    <div style={{ paddingBottom: 40, minHeight: '100vh' }}>
      <PageHeader
        title="Настройки автолика"
        subtitle="Настройте параметры автоматического отклика на вакансии"
        icon={<RobotOutlined />}
        breadcrumbs={[
          { title: 'Мои резюме', path: '/resumes' },
          { title: 'Настройки автолика' }
        ]}
      />

      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : '0 24px' }}>
        {/* Навигация табами */}
        <Tabs
          activeKey="autolike"
          onChange={(key) => {
            if (key === 'resume') {
              navigate(`/resumes/${resumeId}`);
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

        {!dailyResponsesLoading && count >= limit && limit > 0 && limit < 200 && (
          <LimitReachedAlert 
            limit={limit} 
            count={count} 
          />
        )}

        {/* Верхняя секция: Автоотклик + Статистика */}
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
            marginBottom: 24,
          }}
          styles={{ 
            body: { 
              padding: 24,
            } 
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
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
                }}
              >
                <RobotOutlined style={{ fontSize: 20, color: 'white' }} />
              </div>
              <div>
                <Title level={4} style={{ margin: 0, fontWeight: 700, color: '#0f172a' }}>
                  Автоотклик
                </Title>
                <Text style={{ fontSize: 13, color: '#64748b' }}>
                  {resume?.is_auto_reply 
                    ? 'Автоматические отклики на подходящие вакансии'
                    : 'Включите для автоматического отклика'}
                </Text>
              </div>
            </div>
            <Switch
              checked={localAutoReply !== null ? localAutoReply : (resume?.is_auto_reply || false)}
              onChange={handleAutoReplyToggle}
              disabled={saving}
              size="default"
            />
          </div>

          {/* Статистика */}
          <div style={{ display: 'flex', gap: 12 }}>
            <div
              style={{
                flex: 1,
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.7)',
                borderRadius: 12,
                border: '1px solid rgba(34, 197, 94, 0.15)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircleOutlined style={{ color: '#16a34a', fontSize: 18 }} />
                <div>
                  <Text style={{ fontSize: 24, fontWeight: 700, color: '#16a34a', display: 'block', lineHeight: 1 }}>
                    {count}
                  </Text>
                  <Text style={{ fontSize: 12, color: '#64748b' }}>сегодня</Text>
                </div>
              </div>
            </div>
            <div
              style={{
                flex: 1,
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.7)',
                borderRadius: 12,
                border: '1px solid rgba(34, 197, 94, 0.15)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <ClockCircleOutlined style={{ color: '#64748b', fontSize: 18 }} />
                <div>
                  <Text style={{ fontSize: 24, fontWeight: 700, color: '#0f172a', display: 'block', lineHeight: 1 }}>
                    {remaining}
                  </Text>
                  <Text style={{ fontSize: 12, color: '#64748b' }}>осталось</Text>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Шаг 1: Настройки поиска */}
        <Card
          bordered={true}
          style={{ 
            borderRadius: 20, 
            border: '1px solid #e5e7eb',
            marginBottom: 24,
          }}
          styles={{ 
            header: { 
              borderBottom: '1px solid #f1f5f9',
              padding: '18px 24px',
            },
            body: { padding: 24 } 
          }}
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <SettingOutlined style={{ fontSize: 16, color: '#2563eb' }} />
              </div>
              <Title level={4} style={{ margin: 0, fontWeight: 600 }}>
                Шаг 1: Настройки поиска
              </Title>
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
              loading={saving}
              isDirty={false}
              onSave={async () => {}}
              onSuggest={handleFilterSuggest}
              onValuesChange={handleFilterValuesChange}
            />
          </Form>
        </Card>

        {/* Шаг 2: Дополнительные требования */}
        <Card
          bordered={true}
          style={{ 
            borderRadius: 20, 
            border: '1px solid #e5e7eb',
            marginBottom: 24,
          }}
          styles={{ 
            header: { 
              borderBottom: '1px solid #f1f5f9',
              padding: '18px 24px',
            },
            body: { padding: 24 } 
          }}
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ThunderboltOutlined style={{ fontSize: 16, color: '#2563eb' }} />
              </div>
              <Title level={4} style={{ margin: 0, fontWeight: 600 }}>
                Шаг 2: Дополнительные требования
              </Title>
            </div>
          }
        >
          {/* Список существующих требований */}
          {requirements.length > 0 && (
            <div 
              style={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: 8, 
                marginBottom: 16 
              }}
            >
              {requirements.map((req, index) => (
                <Tag
                  key={index}
                  closable
                  onClose={() => handleRemoveRequirement(index)}
                  style={{ 
                    background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
                    border: 'none',
                    color: '#2563eb',
                    padding: '8px 14px',
                    fontSize: 14,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  {req}
                </Tag>
              ))}
            </div>
          )}

          {/* Большое поле для добавления нового требования */}
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <Input.TextArea
              placeholder="Добавить требование..."
              value={newRequirement}
              onChange={(e) => setNewRequirement(e.target.value)}
              maxLength={100}
              rows={3}
              style={{ 
                borderRadius: 10,
                border: '1px solid #e5e7eb',
                resize: 'none',
              }}
              showCount
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddRequirement}
              style={{ 
                borderRadius: 10,
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                border: 'none',
              }}
            >
              Добавить
            </Button>
          </Space>

          {requirements.length === 0 && (
            <div style={{ marginTop: 16 }}>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                Примеры:
              </Text>
              <ul style={{ margin: 0, paddingLeft: 20, fontSize: 12, color: '#94a3b8' }}>
                <li>Только удаленка, без гибрида</li>
                <li>Без тестовых заданий</li>
                <li>Без легаси кода</li>
              </ul>
            </div>
          )}
        </Card>

        {/* Шаг 3: Автолик */}
        <Card
          bordered={true}
          style={{ 
            borderRadius: 20, 
            border: '1px solid #e5e7eb',
            marginBottom: 24,
          }}
          styles={{ 
            header: { 
              borderBottom: '1px solid #f1f5f9',
              padding: '18px 24px',
            },
            body: { padding: 24 } 
          }}
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <RobotOutlined style={{ fontSize: 16, color: '#2563eb' }} />
              </div>
              <Title level={4} style={{ margin: 0, fontWeight: 600 }}>
                Шаг 3: Автолик
              </Title>
            </div>
          }
        >
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text style={{ fontSize: 14, color: '#64748b', fontWeight: 500, display: 'block', marginBottom: 12 }}>
                Порог автолика
              </Text>
              <Slider
                min={0}
                max={100}
                value={currentThreshold}
                onChange={handleAutolikeThresholdChange}
                marks={{
                  0: '0%',
                  50: '50%',
                  100: '100%',
                }}
                tooltip={{ formatter: (value) => `${value}%` }}
              />
            </div>
            <Text style={{ fontSize: 13, color: '#94a3b8', display: 'block' }}>
              Отклики на вакансии с оценкой {currentThreshold}% и выше
            </Text>
          </div>
        </Card>

        {/* Кнопка сохранения */}
        {isDirty && (
          <Card
            bordered={false}
            style={{ 
              borderRadius: 20,
              background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
            }}
            styles={{ 
              body: { padding: 24 } 
            }}
          >
            <Button
              type="primary"
              size="large"
              icon={<SaveOutlined />}
              onClick={handleSaveAll}
              loading={saving}
              block
              style={{ 
                borderRadius: 12,
                height: 48,
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                border: 'none',
                fontWeight: 600,
                fontSize: 16,
              }}
            >
              Сохранить все изменения
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
};
