import { Layout, Menu, Button } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  UserOutlined,
  CrownOutlined,
  ApiOutlined,
  BarChartOutlined,
  LogoutOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';
import { Logo } from '../Logo';

const { Sider, Content, Header } = Layout;

interface AdminLayoutProps {
  children: React.ReactNode;
}

export const AdminLayout = ({ children }: AdminLayoutProps) => {
  const { logout, user } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleBackToApp = () => {
    navigate('/resumes');
  };

  const menuItems = [
    {
      key: '/admin/users',
      icon: <UserOutlined />,
      label: 'Пользователи',
    },
    {
      key: '/admin/plans',
      icon: <CrownOutlined />,
      label: 'Планы',
    },
    {
      key: '/admin/llm-calls',
      icon: <ApiOutlined />,
      label: 'LLM вызовы',
    },
    {
      key: '/admin/metrics',
      icon: <BarChartOutlined />,
      label: 'Метрики',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f8fafc' }}>
      <Sider
        width={260}
        style={{
          background: '#ffffff',
          boxShadow: '4px 0 24px 0 rgba(0, 0, 0, 0.02)',
          borderRight: '1px solid #f1f5f9',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          height: '100vh',
          overflow: 'auto',
          zIndex: 1000,
        }}
      >
        <div
          style={{
            padding: '16px 20px 0 20px',
            marginBottom: 0,
          }}
        >
          <Logo />
        </div>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100vh - 84px)',
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{
              borderRight: 0,
              background: 'transparent',
              flex: 1,
              padding: '0 12px',
              fontSize: 14,
              fontWeight: 500,
            }}
          />
          
          <div style={{ padding: '16px 24px', borderTop: '1px solid #f1f5f9' }}>
            <Button 
              type="text" 
              icon={<ArrowLeftOutlined />} 
              onClick={handleBackToApp}
              style={{ width: '100%', textAlign: 'left', paddingLeft: 12, height: 40, marginBottom: 8 }}
            >
              Вернуться в приложение
            </Button>
            <Button 
              type="text" 
              danger 
              icon={<LogoutOutlined />} 
              onClick={handleLogout}
              style={{ width: '100%', textAlign: 'left', paddingLeft: 12, height: 40 }}
            >
              Выйти
            </Button>
          </div>
        </div>
      </Sider>
      <Layout style={{ marginLeft: 260, background: '#fafbfc' }}>
        <Header
          style={{
            background: '#ffffff',
            padding: '0 24px',
            borderBottom: '1px solid #f1f5f9',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>Админ-панель</h2>
          {user && (
            <span style={{ color: '#64748b', fontSize: 14 }}>
              {user.email}
            </span>
          )}
        </Header>
        <Content style={{ padding: '20px 24px', width: '100%' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};
