import { Layout, Menu, Typography, message, Button } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  FileTextOutlined,
  LogoutOutlined,
  SettingOutlined,
  UserOutlined,
  SearchOutlined,
  CalendarOutlined,
  MessageOutlined,
  RocketOutlined,
  SendOutlined,
  BarChartOutlined,
  CrownOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';

const { Sider, Content, Footer } = Layout;
const { Title, Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      type: 'group' as const,
      label: <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1, color: '#9ca3af' }}>РАБОТА</span>,
      children: [
        {
          key: '/resumes',
          icon: <FileTextOutlined />,
          label: 'Мои резюме',
        },
        {
          key: 'events',
          icon: <CalendarOutlined />,
          label: 'События',
        },
        {
          key: 'statistics',
          icon: <BarChartOutlined />,
          label: 'Статистика',
        },
      ]
    },
    {
      type: 'group' as const,
      label: <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1, color: '#9ca3af', marginTop: 12 }}>ОБЩЕНИЕ</span>,
      children: [
        {
          key: 'chats',
          icon: <MessageOutlined />,
          label: 'Чаты',
        },
        {
          key: 'support',
          icon: <SendOutlined />,
          label: 'Поддержка',
        },
      ]
    },
    {
      type: 'group' as const,
      label: <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1, color: '#9ca3af', marginTop: 12 }}>АККАУНТ</span>,
      children: [
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Профиль',
        },
        {
          key: '/plans',
          icon: <CrownOutlined />,
          label: 'Планы',
        },
        {
          key: '/settings/hh-auth',
          icon: <SettingOutlined />,
          label: 'Настройки',
        },
      ]
    }
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'support') {
      window.open('https://t.me/wlovemm', '_blank');
      return;
    }
    if (key === 'events') {
      message.info('Раздел находится в разработке');
      return;
    }
    if (key === 'chats') {
      navigate('/chats');
      return;
    }
    if (key === 'statistics') {
      navigate('/statistics');
      return;
    }
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
            padding: '28px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 8,
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.2)',
            }}
          >
            <RocketOutlined style={{ color: 'white', fontSize: 22 }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <Title level={4} style={{ margin: 0, color: '#0f172a', fontSize: 22, fontWeight: 700, lineHeight: 1 }}>
              EzJob
            </Title>
            <Text type="secondary" style={{ fontSize: 11, fontWeight: 500, letterSpacing: 0.5 }}>
              Твой легкий оффер
            </Text>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100vh - 100px)',
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname === '/statistics' ? 'statistics' : location.pathname]}
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
      <Layout style={{ marginLeft: 260 }}>
        <Content style={{ padding: '32px 32px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
          {children}
        </Content>
        <Footer style={{ textAlign: 'center', background: 'transparent', color: '#94a3b8', fontSize: 13 }}>
          EzJob AI Assistant ©2025
        </Footer>
      </Layout>
    </Layout>
  );
};
