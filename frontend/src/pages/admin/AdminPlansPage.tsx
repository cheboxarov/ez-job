import { useState, useEffect } from 'react';
import {
  Table,
  Typography,
  Button,
  Modal,
  Form,
  InputNumber,
  Input,
  Switch,
  Space,
  Tag,
  message,
  Row,
  Col,
} from 'antd';
import { PlusOutlined, EditOutlined, StopOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { adminApi } from '../../api/admin';
import type { AdminPlan, AdminPlanUpsertRequest } from '../../types/admin';

const { Title } = Typography;

export const AdminPlansPage = () => {
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPlan, setEditingPlan] = useState<AdminPlan | null>(null);
  const [form] = Form.useForm();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    loadPlans();
  }, [page, pageSize]);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const loadPlans = async () => {
    setLoading(true);
    try {
      const response = await adminApi.getPlans({
        page,
        page_size: pageSize,
      });
      setPlans(response.plans);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка загрузки планов');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingPlan(null);
    form.resetFields();
    form.setFieldsValue({
      is_active: true,
    });
    setModalVisible(true);
  };

  const handleEdit = (plan: AdminPlan) => {
    setEditingPlan(plan);
    form.setFieldsValue({
      name: plan.name,
      response_limit: plan.response_limit,
      reset_period_seconds: plan.reset_period_seconds,
      duration_days: plan.duration_days,
      price: plan.price,
    });
    setModalVisible(true);
  };

  const handleDeactivate = async (planId: string) => {
    try {
      await adminApi.deactivatePlan(planId);
      message.success('План деактивирован');
      await loadPlans();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка деактивации плана');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const data: AdminPlanUpsertRequest = {
        name: values.name,
        response_limit: values.response_limit,
        reset_period_seconds: values.reset_period_seconds,
        duration_days: values.duration_days,
        price: values.price,
        is_active: values.is_active !== undefined ? values.is_active : true,
      };

      if (editingPlan) {
        await adminApi.updatePlan(editingPlan.id, data);
        message.success('План успешно обновлён');
      } else {
        await adminApi.createPlan(data);
        message.success('План успешно создан');
      }

      setModalVisible(false);
      form.resetFields();
      await loadPlans();
    } catch (error: any) {
      if (error.errorFields) {
        return; // Validation errors
      }
      message.error(error.response?.data?.detail || 'Ошибка сохранения плана');
    }
  };

  const formatResetPeriod = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    if (days === 1) return '1 день';
    return `${days} дн`;
  };

  const columns: ColumnsType<AdminPlan> = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      align: 'center',
    },
    {
      title: 'Лимит откликов',
      dataIndex: 'response_limit',
      key: 'response_limit',
      align: 'center',
    },
    {
      title: 'Период сброса',
      dataIndex: 'reset_period_seconds',
      key: 'reset_period_seconds',
      align: 'center',
      render: (seconds: number) => formatResetPeriod(seconds),
      responsive: ['md'],
    },
    {
      title: 'Длительность (дней)',
      dataIndex: 'duration_days',
      key: 'duration_days',
      align: 'center',
      render: (days: number) => (days === 0 ? 'Бессрочно' : days),
      responsive: ['md'],
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      key: 'price',
      align: 'center',
      render: (price: number) => `${price} ₽`,
    },
    {
      title: 'Действия',
      key: 'actions',
      align: 'center',
      render: (_: any, record: AdminPlan) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Редактировать
          </Button>
          <Button
            type="link"
            danger
            icon={<StopOutlined />}
            onClick={() => handleDeactivate(record.id)}
          >
            Деактивировать
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
        <Col xs={24} md={18}>
          <Title level={2} style={{ margin: 0 }}>
            Управление планами
          </Title>
        </Col>
        <Col xs={24} md={6} style={{ textAlign: 'right' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
            block={isMobile}
          >
            Создать план
          </Button>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={plans}
        loading={loading}
        rowKey="id"
        scroll={{ x: true }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (total) => `Всего: ${total}`,
          onChange: (newPage, newPageSize) => {
            setPage(newPage);
            setPageSize(newPageSize);
          },
        }}
      />

      <Modal
        title={editingPlan ? 'Редактировать план' : 'Создать план'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        okText="Сохранить"
        cancelText="Отмена"
        width={isMobile ? '95%' : 600}
        style={{ maxWidth: '95vw' }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="Название"
            rules={[{ required: true, message: 'Введите название плана' }]}
          >
            <Input placeholder="FREE, PLAN_1, PLAN_2..." />
          </Form.Item>
          <Form.Item
            name="response_limit"
            label="Лимит откликов"
            rules={[{ required: true, message: 'Введите лимит откликов' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="reset_period_seconds"
            label="Период сброса (секунды)"
            rules={[{ required: true, message: 'Введите период сброса' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="duration_days"
            label="Длительность (дней, 0 = бессрочно)"
            rules={[{ required: true, message: 'Введите длительность' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="price"
            label="Цена (₽)"
            rules={[{ required: true, message: 'Введите цену' }]}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
          {editingPlan && (
            <Form.Item name="is_active" label="Активен" valuePropName="checked">
              <Switch />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};
