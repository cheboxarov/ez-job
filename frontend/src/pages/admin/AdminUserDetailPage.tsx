import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Typography,
  Space,
  Tag,
  Switch,
  Button,
  Select,
  Modal,
  message,
  Spin,
  Descriptions,
  Divider,
  Row,
  Col,
} from 'antd';
import {
  UserOutlined,
  DeleteOutlined,
  SaveOutlined,
  ArrowLeftOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import { adminApi } from '../../api/admin';
import type { AdminUserDetailResponse, AdminPlan } from '../../types/admin';

const { Title, Text } = Typography;

export const AdminUserDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [userData, setUserData] = useState<AdminUserDetailResponse | null>(null);
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [isVerified, setIsVerified] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string>('');
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);

  useEffect(() => {
    if (id) {
      loadUserData();
      loadPlans();
    }
  }, [id]);

  const loadUserData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await adminApi.getUserDetail(id);
      setUserData(data);
      setIsActive(data.is_active);
      setIsVerified(data.is_verified);
      setSelectedPlan(data.subscription?.plan_id || '');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка загрузки данных пользователя');
    } finally {
      setLoading(false);
    }
  };

  const loadPlans = async () => {
    try {
      const response = await adminApi.getPlans({ page: 1, page_size: 100 });
      setPlans(response.plans);
    } catch (error: any) {
      console.error('Ошибка загрузки планов:', error);
    }
  };

  const handleSaveFlags = async () => {
    if (!id) return;
    setSaving(true);
    try {
      await adminApi.updateUserFlags(id, {
        is_active: isActive,
        is_verified: isVerified,
      });
      message.success('Флаги успешно обновлены');
      await loadUserData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка обновления флагов');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePlan = async () => {
    if (!id || !selectedPlan) return;
    const plan = plans.find((p) => p.id === selectedPlan);
    if (!plan) return;

    setSaving(true);
    try {
      await adminApi.changeUserPlan(id, {
        plan_name: plan.name,
      });
      message.success(`План изменён на "${plan.name}"`);
      await loadUserData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка смены плана');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    setSaving(true);
    try {
      await adminApi.deleteUser(id);
      message.success('Пользователь успешно удалён');
      navigate('/admin/users');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка удаления пользователя');
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!userData) {
    return <div>Пользователь не найден</div>;
  }

  const hasChanges =
    isActive !== userData.is_active ||
    isVerified !== userData.is_verified ||
    selectedPlan !== userData.subscription?.plan_id;

  return (
    <div style={{ padding: '0 16px' }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/admin/users')}>
            Назад к списку
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            Пользователь: {userData.email || userData.phone || userData.id}
          </Title>
        </Space>

        <Card title="Основная информация">
          <Descriptions column={{ xs: 1, sm: 1, md: 2, lg: 2 }}>
            <Descriptions.Item label="ID">{userData.id}</Descriptions.Item>
            <Descriptions.Item label="Email">{userData.email || '-'}</Descriptions.Item>
            <Descriptions.Item label="Телефон">{userData.phone || '-'}</Descriptions.Item>
            <Descriptions.Item label="Статус">
              <Space>
                {userData.is_active ? (
                  <Tag color="green">Активен</Tag>
                ) : (
                  <Tag color="red">Неактивен</Tag>
                )}
                {userData.is_verified && <Tag color="blue">Подтверждён</Tag>}
                {userData.is_superuser && <Tag color="purple">Админ</Tag>}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="Текущий план">
              {userData.subscription?.plan_name || 'Нет плана'}
            </Descriptions.Item>
          </Descriptions>
          <div style={{ marginTop: 16 }}>
            <Button
              type="default"
              icon={<ApiOutlined />}
              onClick={() => navigate(`/admin/llm-calls?user_id=${userData.id}`)}
            >
              Посмотреть LLM вызовы этого пользователя
            </Button>
          </div>
        </Card>

        <Card title="Управление флагами">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space wrap>
              <Text>Активен:</Text>
              <Switch checked={isActive} onChange={setIsActive} />
            </Space>
            <Space wrap>
              <Text>Подтверждён:</Text>
              <Switch checked={isVerified} onChange={setIsVerified} />
            </Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveFlags}
              loading={saving}
              disabled={!hasChanges || (isActive === userData.is_active && isVerified === userData.is_verified)}
            >
              Сохранить изменения
            </Button>
          </Space>
        </Card>

        <Card title="Управление планом">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space wrap style={{ width: '100%' }}>
              <Text>План:</Text>
              <Select
                style={{ width: '100%', maxWidth: 300 }}
                value={selectedPlan}
                onChange={setSelectedPlan}
                placeholder="Выберите план"
              >
                {plans.map((plan) => (
                  <Select.Option key={plan.id} value={plan.id}>
                    {plan.name} ({plan.price} ₽)
                  </Select.Option>
                ))}
              </Select>
            </Space>
            <Button
              type="primary"
              onClick={handleChangePlan}
              loading={saving}
              disabled={!selectedPlan || selectedPlan === userData.subscription?.plan_id}
            >
              Изменить план
            </Button>
          </Space>
        </Card>

        <Divider />

        <Card title="Опасная зона" style={{ borderColor: '#ff4d4f' }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={24} md={8}>
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={() => setDeleteModalVisible(true)}
                style={{ width: '100%' }}
              >
                Удалить пользователя
              </Button>
            </Col>
            <Col xs={24} sm={24} md={16}>
              <Text type="secondary">
                Это действие удалит пользователя и все связанные данные без возможности восстановления.
              </Text>
            </Col>
          </Row>
        </Card>
      </Space>

      <Modal
        title="Подтверждение удаления"
        open={deleteModalVisible}
        onOk={handleDelete}
        onCancel={() => setDeleteModalVisible(false)}
        okText="Удалить"
        cancelText="Отмена"
        okButtonProps={{ danger: true }}
        confirmLoading={saving}
      >
        <p>Вы уверены, что хотите удалить пользователя {userData.email || userData.phone}?</p>
        <p style={{ color: '#ff4d4f' }}>
          Это действие нельзя отменить. Будут удалены все связанные данные: резюме, отклики, настройки и т.д.
        </p>
      </Modal>
    </div>
  );
};
