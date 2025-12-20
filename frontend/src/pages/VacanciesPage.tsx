import { useEffect, useState } from 'react';
import {
  Form,
  Button,
  Select,
  Slider,
  Card,
  Typography,
  Spin,
  Alert,
  Row,
  Col,
  Space,
  Input,
  Checkbox,
  InputNumber,
  TreeSelect,
  Tooltip,
} from 'antd';
import { 
  FilterOutlined, 
  SearchOutlined, 
  SaveOutlined, 
  ExperimentOutlined,
  DollarOutlined,
  EnvironmentOutlined,
  FieldTimeOutlined
} from '@ant-design/icons';
import { VacancyCard } from '../components/VacancyCard';
import { PageHeader } from '../components/PageHeader';
import { EmptyState } from '../components/EmptyState';
import { GradientButton } from '../components/GradientButton';
import { getRelevantVacancies } from '../api/vacancies';
import {
  getUserFilterSettings,
  updateUserFilterSettings,
  suggestUserFilterSettings,
} from '../api/filterSettings';
import { getAreas, type HhArea } from '../api/dictionaries';
import { useVacanciesStore } from '../stores/vacanciesStore';
import type { VacancyRequest, UserFilterSettings } from '../types/api';

const { Text } = Typography;

const FILTER_COMPARE_KEYS: (keyof UserFilterSettings)[] = [
  'text',
  'experience',
  'employment',
  'schedule',
  'professional_role',
  'area',
  'salary',
  'currency',
  'only_with_salary',
  'order_by',
];

export const VacanciesPage = () => {
  const { vacancies, setVacancies } = useVacanciesStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [areasTree, setAreasTree] = useState<any[]>([]);
  const [, setSavedSettingsSnapshot] = useState<Partial<UserFilterSettings> | null>(null);
  const [initialFilterValues, setInitialFilterValues] = useState<Record<string, unknown> | null>(
    null,
  );
  const [isDirty, setIsDirty] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const settings = await getUserFilterSettings();
        setSavedSettingsSnapshot(settings);
        form.setFieldsValue({
          text: settings.text || '',
          experience: settings.experience || [],
          employment: settings.employment || [],
          schedule: settings.schedule || [],
          professional_role: settings.professional_role || [],
          area: settings.area || '',
          salary: settings.salary ?? null,
          currency: settings.currency || 'RUR',
          only_with_salary: settings.only_with_salary,
          order_by: settings.order_by || undefined,
        });
        const current = form.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
        setInitialFilterValues(current);
        setIsDirty(false);
      } catch (e) {
        // игнорируем, фильтры просто будут дефолтными
      }
    };
    loadSettings();
  }, [form]);

  useEffect(() => {
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

    loadAreas();
  }, []);

  const handleValuesChange = () => {
    const current = form.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
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

  const handleFind = async () => {
    const values = await form.validateFields();
    setLoading(true);
    setError(null);
    try {
      const request: VacancyRequest = {
        min_confidence_for_cover_letter: values.min_confidence_for_cover_letter || 0.7,
        order_by: values.order_by || null,
      };
      const response = await getRelevantVacancies(request);
      
      const sortedVacancies = [...response.items].sort((a, b) => b.confidence - a.confidence);
      setVacancies(sortedVacancies);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при получении вакансий');
      setVacancies([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    setLoading(true);
    setError(null);
    try {
      const saved = await updateUserFilterSettings({
        text: values.text || null,
        experience: values.experience || null,
        employment: values.employment || null,
        schedule: values.schedule || null,
        professional_role: values.professional_role || null,
        area: values.area || null,
        salary: values.salary ?? null,
        currency: values.currency || null,
        only_with_salary: values.only_with_salary ?? false,
        order_by: values.order_by || null,
      });
      setSavedSettingsSnapshot(saved);
      const current = form.getFieldsValue(FILTER_COMPARE_KEYS as string[]);
      setInitialFilterValues(current);
      setIsDirty(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при сохранении фильтров');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggest = async () => {
    setLoading(true);
    setError(null);
    try {
      const suggested = await suggestUserFilterSettings();
      form.setFieldsValue({
        text: suggested.text ?? '',
        salary: suggested.salary ?? null,
        currency: suggested.currency ?? 'RUR',
      });
      handleValuesChange();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при генерации фильтров');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Поиск вакансий"
        subtitle="Настройте фильтры и найдите подходящие вакансии"
        icon={<SearchOutlined />}
        breadcrumbs={[{ title: 'Поиск вакансий' }]}
      />

      <Row gutter={[24, 24]}>
        {/* Фильтры */}
        <Col xs={24} md={8} lg={6}>
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <FilterOutlined style={{ color: 'white', fontSize: 14 }} />
                </div>
                <span style={{ fontWeight: 600 }}>Фильтры</span>
              </div>
            }
            extra={
              <Space size="small">
                {isDirty && (
                  <Tooltip title="Сохранить фильтры">
                    <Button
                      type="text"
                      icon={<SaveOutlined />}
                      onClick={handleSave}
                      loading={loading}
                    />
                  </Tooltip>
                )}
                <Tooltip title="AI-генерация фильтров">
                  <Button
                    type="text"
                    icon={<ExperimentOutlined />}
                    onClick={handleSuggest}
                    loading={loading}
                  />
                </Tooltip>
              </Space>
            }
            bordered={false}
            style={{ 
              position: 'sticky', 
              top: 24, 
              maxHeight: 'calc(100vh - 48px)', 
              overflowY: 'auto',
              borderRadius: 16,
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }}
          >
            <Form
              id="vacancies-filters-form"
              form={form}
              layout="vertical"
              onValuesChange={handleValuesChange}
              initialValues={{
                min_confidence_for_cover_letter: 0.7,
                only_with_salary: false,
              }}
            >
              <Form.Item 
                name="text" 
                label={
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <SearchOutlined style={{ color: '#64748b' }} />
                    Ключевые слова
                  </span>
                }
              >
                <Input placeholder="Например: Python разработчик" style={{ borderRadius: 10 }} />
              </Form.Item>

              <Form.Item
                name="min_confidence_for_cover_letter"
                label="Порог совпадения (AI)"
                tooltip="Минимальная оценка соответствия для генерации письма"
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  marks={{
                    0: '0',
                    0.5: '0.5',
                    1: '1',
                  }}
                />
              </Form.Item>

              <Form.Item 
                name="order_by" 
                label={
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <FieldTimeOutlined style={{ color: '#64748b' }} />
                    Сортировка
                  </span>
                }
              >
                <Select placeholder="По релевантности" allowClear style={{ borderRadius: 10 }}>
                  <Select.Option value="publication_time">По дате публикации</Select.Option>
                  <Select.Option value="salary_desc">По убыванию зарплаты</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item 
                name="area" 
                label={
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <EnvironmentOutlined style={{ color: '#64748b' }} />
                    Регион
                  </span>
                }
              >
                <TreeSelect
                  showSearch
                  allowClear
                  style={{ width: '100%' }}
                  treeData={areasTree}
                  placeholder="Выберите регион"
                  treeNodeFilterProp="title"
                />
              </Form.Item>

              <Form.Item 
                label={
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <DollarOutlined style={{ color: '#64748b' }} />
                    Зарплата
                  </span>
                }
              >
                <Space.Compact style={{ width: '100%' }}>
                  <Form.Item name="salary" noStyle>
                    <InputNumber style={{ width: '70%', borderRadius: '10px 0 0 10px' }} placeholder="Минимум" />
                  </Form.Item>
                  <Form.Item name="currency" noStyle initialValue="RUR">
                    <Select style={{ width: '30%' }}>
                      <Select.Option value="RUR">₽</Select.Option>
                      <Select.Option value="USD">$</Select.Option>
                      <Select.Option value="EUR">€</Select.Option>
                    </Select>
                  </Form.Item>
                </Space.Compact>
              </Form.Item>

              <Form.Item name="only_with_salary" valuePropName="checked">
                <Checkbox>Только с указанной зарплатой</Checkbox>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        {/* Список вакансий */}
        <Col xs={24} md={16} lg={18}>
          <div style={{ display: 'flex', flexDirection: 'column', minHeight: 'calc(100vh - 200px)' }}>
            {vacancies.length > 0 && (
              <div
                style={{
                  marginBottom: 20,
                  display: 'flex',
                  justifyContent: 'flex-end',
                  alignItems: 'center',
                }}
              >
                <div 
                  style={{ 
                    padding: '8px 16px', 
                    background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                    borderRadius: 20,
                  }}
                >
                  <Text strong style={{ fontSize: 14, color: '#475569' }}>
                    Найдено: {vacancies.length}
                  </Text>
                </div>
              </div>
            )}

            {loading && (
              <div style={{ textAlign: 'center', padding: '80px 0' }}>
                <Spin size="large" tip="Анализируем вакансии..." />
              </div>
            )}

            {error && (
              <Alert
                message="Ошибка загрузки"
                description={error}
                type="error"
                showIcon
                style={{ marginBottom: 24, borderRadius: 12 }}
              />
            )}

            {!loading && !error && vacancies.length > 0 && (
              <div>
                {vacancies.map((vacancy) => (
                  <VacancyCard key={vacancy.vacancy_id} vacancy={vacancy} />
                ))}
              </div>
            )}

            {!loading && !error && vacancies.length === 0 && (
              <EmptyState
                icon={<SearchOutlined />}
                title="Пока пусто"
                description="Настройте параметры поиска слева для получения результатов"
              />
            )}
          </div>
        </Col>
      </Row>
    </div>
  );
};
