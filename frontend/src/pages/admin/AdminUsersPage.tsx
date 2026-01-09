import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Input, Typography, Space, Tag, Button, Row, Col } from 'antd';
import { SearchOutlined, UserOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { adminApi } from '../../api/admin';
import type { AdminUser } from '../../types/admin';

const { Title } = Typography;

export const AdminUsersPage = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [phoneSearch, setPhoneSearch] = useState('');

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await adminApi.getUsers({
        page,
        page_size: pageSize,
        phone: phoneSearch || undefined,
      });
      setUsers(response.items);
      setTotal(response.total);
    } catch (error: any) {
      console.error('Ошибка загрузки пользователей:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [page, pageSize]);

  const handleSearch = () => {
    setPage(1);
    loadUsers();
  };

  const columns: ColumnsType<AdminUser> = [
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: (email: string | null) => email || '-',
    },
    {
      title: 'Телефон',
      dataIndex: 'phone',
      key: 'phone',
      render: (phone: string | null) => phone || '-',
    },
    {
      title: 'Статус',
      key: 'status',
      render: (_: any, record: AdminUser) => (
        <Space>
          {record.is_active ? (
            <Tag color="green">Активен</Tag>
          ) : (
            <Tag color="red">Неактивен</Tag>
          )}
          {record.is_verified && <Tag color="blue">Подтверждён</Tag>}
          {record.is_superuser && <Tag color="purple">Админ</Tag>}
        </Space>
      ),
    },
    {
      title: 'Дата создания',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string | null) =>
        date ? new Date(date).toLocaleDateString('ru-RU') : '-',
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: AdminUser) => (
        <Button
          type="link"
          onClick={() => navigate(`/admin/users/${record.id}`)}
        >
          Подробнее
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Пользователи</Title>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={16} md={12} lg={10}>
          <Input
            placeholder="Поиск по телефону"
            prefix={<SearchOutlined />}
            value={phoneSearch}
            onChange={(e) => setPhoneSearch(e.target.value)}
            onPressEnter={handleSearch}
              style={{ width: '100%' }}
          />
          </Col>
          <Col xs={24} sm={8} md={6} lg={4}>
            <Button type="primary" onClick={handleSearch} style={{ width: '100%' }}>
            Найти
          </Button>
          </Col>
        </Row>
        <Table
          columns={columns}
          dataSource={users}
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
      </Space>
    </div>
  );
};
