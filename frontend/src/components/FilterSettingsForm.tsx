import { Form, Input, Select, Checkbox, InputNumber, TreeSelect, Button, Space, Tooltip, Row, Col } from 'antd';
import { SaveOutlined, ExperimentOutlined } from '@ant-design/icons';
import type { ResumeFilterSettings, ResumeFilterSettingsUpdate } from '../types/api';

interface FilterSettingsFormProps {
  form: any;
  initialValues?: ResumeFilterSettings | null;
  areasTree: any[];
  loading?: boolean;
  isDirty?: boolean;
  onSave: (values: ResumeFilterSettingsUpdate) => Promise<void>;
  onSuggest: () => Promise<void>;
  onValuesChange?: () => void;
}

export const FilterSettingsForm = ({
  form,
  areasTree,
  loading = false,
  isDirty = false,
  onSave,
  onSuggest,
}: FilterSettingsFormProps) => {
  const handleSave = async () => {
    const values = await form.validateFields();
    await onSave({
      text: values.text || null,
      experience: values.experience || null,
      employment: values.employment || null,
      schedule: values.schedule || null,
      professional_role: values.professional_role || null,
      area: values.area || null,
      salary: values.salary ?? null,
      currency: values.currency || null,
      only_with_salary: values.only_with_salary ?? false,
      period: values.period || null,
      date_from: values.date_from || null,
      date_to: values.date_to || null,
    });
  };

  return (
    <>
      <Form.Item 
        name="text" 
        label="Ключевые слова"
        tooltip="Поиск по вакансиям (аналог поисковой строки)"
        style={{ marginBottom: 16 }}
      >
        <Input placeholder="Python, Django, React..." style={{ borderRadius: 6 }} />
      </Form.Item>

      <Form.Item 
        name="area" 
        label="Регион"
        style={{ marginBottom: 16 }}
      >
        <TreeSelect
          showSearch
          allowClear
          style={{ width: '100%' }}
          treeData={areasTree}
          placeholder="Выберите город/регион"
          treeNodeFilterProp="title"
          treeDefaultExpandAll={false}
        />
      </Form.Item>

      <Form.Item 
        label="Зарплата"
        style={{ marginBottom: 16 }}
      >
        <Space.Compact style={{ width: '100%' }}>
          <Form.Item name="salary" noStyle>
            <InputNumber style={{ width: '65%' }} placeholder="От..." min={0} />
          </Form.Item>
          <Form.Item name="currency" noStyle initialValue="RUR">
            <Select style={{ width: '35%' }}>
              <Select.Option value="RUR">₽</Select.Option>
              <Select.Option value="USD">$</Select.Option>
              <Select.Option value="EUR">€</Select.Option>
            </Select>
          </Form.Item>
        </Space.Compact>
      </Form.Item>

      <Form.Item name="only_with_salary" valuePropName="checked" style={{ marginBottom: 24 }}>
        <Checkbox>Только с указанной зарплатой</Checkbox>
      </Form.Item>

      <Row gutter={[8, 8]}>
        <Col span={24}>
          <Button
            block
            icon={<ExperimentOutlined />}
            onClick={onSuggest}
            loading={loading}
          >
            Сгенерировать настройки
          </Button>
        </Col>
        {isDirty && (
          <Col span={24}>
            <Button
              type="primary"
              block
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={loading}
              style={{ marginTop: 8 }}
            >
              Сохранить изменения
            </Button>
          </Col>
        )}
      </Row>
    </>
  );
};
