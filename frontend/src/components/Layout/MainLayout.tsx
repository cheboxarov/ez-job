import { Layout, Menu, Button, Badge } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  FileTextOutlined,
  LogoutOutlined,
  SettingOutlined,
  UserOutlined,
  CalendarOutlined,
  MessageOutlined,
  SendOutlined,
  BarChartOutlined,
  CrownOutlined,
  } from '@ant-design/icons';
import { useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useAgentActionsStore } from '../../stores/agentActionsStore';
import { Logo } from '../Logo';

const { Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const { logout } = useAuthStore();
  const { unreadCount, fetchUnreadCount } = useAgentActionsStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchUnreadCount();
  }, [fetchUnreadCount]);

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
          icon: (
            <Badge
              dot={unreadCount > 0}
              offset={[4, 0]}
              style={{ boxShadow: 'none' }}
            >
              <CalendarOutlined />
            </Badge>
          ),
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
        // Страница настроек HH сейчас не используется
      ]
    }
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'support') {
      window.open('https://t.me/wlovemm', '_blank');
      return;
    }
    if (key === 'events') {
      navigate('/events');
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
            padding: '16px 20px',
            marginBottom: 8,
          }}
        >
          <Logo />
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
            selectedKeys={[
              location.pathname === '/statistics' ? 'statistics' : 
              location.pathname === '/events' ? 'events' : 
              location.pathname
            ]}
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
      <Layout style={{ marginLeft: 260, background: '#fafbfc' }}>
        <Content style={{ padding: '32px 32px', width: '100%' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};
