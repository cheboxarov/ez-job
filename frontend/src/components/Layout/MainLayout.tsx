import { Layout, Menu, Button, Badge, Drawer, Grid } from 'antd';
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
  SafetyOutlined,
  MenuOutlined,
  ProfileOutlined,
  } from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useAgentActionsStore } from '../../stores/agentActionsStore';
import { useTasksStore } from '../../stores/tasksStore';
import { Logo } from '../Logo';

const { Sider, Content } = Layout;
const { useBreakpoint } = Grid;

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const { logout, user } = useAuthStore();
  const { unreadCount, fetchUnreadCount } = useAgentActionsStore();
  const { pendingCount, fetchPendingCount } = useTasksStore();
  const navigate = useNavigate();
  const location = useLocation();
  const screens = useBreakpoint();
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Если экраны определились (screens не пустой объект)
    if (Object.keys(screens).length > 0) {
      // Считаем мобильным если нет md (т.е. меньше 768px)
      setIsMobile(!screens.md);
    }
  }, [screens]);

  useEffect(() => {
    fetchUnreadCount();
  }, [fetchUnreadCount]);

  useEffect(() => {
    fetchPendingCount();
  }, [fetchPendingCount]);

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
          key: 'tasks',
          icon: (
            <Badge
              count={pendingCount > 0 ? pendingCount : 0}
              offset={[8, 0]}
              size="small"
            >
              <ProfileOutlined />
            </Badge>
          ),
          label: 'Задания',
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
          key: '/settings',
          icon: <SettingOutlined />,
          label: 'Настройки',
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

  // Добавляем группу админки только для суперпользователей
  if (user?.is_superuser) {
    menuItems.push({
      type: 'group' as const,
      label: <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1, color: '#9ca3af', marginTop: 12 }}>АДМИНИСТРИРОВАНИЕ</span>,
      children: [
        {
          key: '/admin/users',
          icon: <SafetyOutlined />,
          label: 'Админ панель',
        },
      ]
    });
  }

  const handleMenuClick = ({ key }: { key: string }) => {
    if (isMobile) {
      setDrawerVisible(false);
    }
    
    if (key === 'support') {
      window.open('https://t.me/wlovemm', '_blank');
      return;
    }
    if (key === 'events') {
      navigate('/events');
      return;
    }
    if (key === 'tasks') {
      navigate('/tasks');
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
    if (key === '/admin/users') {
      navigate('/admin/users');
      return;
    }
    navigate(key);
  };

  const SidebarContent = () => (
    <>
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
          selectedKeys={[
            location.pathname === '/statistics' ? 'statistics' : 
            location.pathname === '/events' ? 'events' : 
            location.pathname === '/tasks' ? 'tasks' :
            location.pathname.startsWith('/settings') ? '/settings' :
            location.pathname.startsWith('/admin') ? '/admin/users' :
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
    </>
  );

  return (
    <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
      {!isMobile ? (
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
          <SidebarContent />
        </Sider>
      ) : (
        <Drawer
          placement="left"
          closable={false}
          onClose={() => setDrawerVisible(false)}
          open={drawerVisible}
          styles={{ body: { padding: 0 } }}
          width={260}
        >
          <SidebarContent />
        </Drawer>
      )}

      <Layout style={{ marginLeft: isMobile ? 0 : 260, background: 'transparent' }}>
        {isMobile && (
          <div style={{ 
            padding: '16px 24px', 
            background: '#fff', 
            borderBottom: '1px solid #f1f5f9', 
            display: 'flex', 
            alignItems: 'center',
            position: 'sticky',
            top: 0,
            zIndex: 900
          }}>
            <Button 
              type="text" 
              icon={<MenuOutlined />} 
              onClick={() => setDrawerVisible(true)}
              style={{ marginRight: 16 }}
            />
            <Logo />
          </div>
        )}
        <Content style={{ padding: isMobile ? '16px' : '20px 24px', width: '100%' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};
