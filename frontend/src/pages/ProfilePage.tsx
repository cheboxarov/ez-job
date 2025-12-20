import { useEffect } from 'react';
import { Form, Input, Button, Card, Typography, message, Space } from 'antd';
import { 
  UserOutlined, 
  MailOutlined, 
  FileTextOutlined, 
  SettingOutlined,
  SaveOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../stores/authStore';
import { updateUser } from '../api/users';
import { PageHeader } from '../components/PageHeader';
import { GradientButton } from '../components/GradientButton';
import type { UpdateUserRequest } from '../types/api';

const { Text } = Typography;

export const ProfilePage = () => {
  const { user, fetchCurrentUser } = useAuthStore();
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        email: user.email,
        resume_text: user.resume_text || '',
        user_filter_params: user.user_filter_params || '',
      });
    }
  }, [user, form]);

  const onFinish = async (values: any) => {
    if (!user) return;

    try {
      const updateData: UpdateUserRequest = {
        resume_text: values.resume_text?.trim() || null,
        user_filter_params: values.user_filter_params?.trim() || null,
      };
      await updateUser(user.id, updateData);
      await fetchCurrentUser();
      message.success('Профиль успешно обновлен');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка при обновлении профиля');
    }
  };

  if (!user) {
    return null;
  }

  // Get user initials for avatar
  const getInitials = (email: string) => {
    return email.substring(0, 2).toUpperCase();
  };

  return (
    <div>
      <PageHeader
        title="Настройки профиля"
        subtitle="Управляйте информацией о себе и настройками аккаунта"
        icon={<UserOutlined />}
        breadcrumbs={[{ title: 'Профиль' }]}
      />

      <div style={{ maxWidth: 800 }}>
        {/* User Info Card */}
        <Card
          bordered={false}
          style={{
            borderRadius: 16,
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            marginBottom: 24,
            overflow: 'hidden',
          }}
          styles={{ body: { padding: 0 } }}
        >
          <div 
            style={{ 
              padding: '32px 28px',
              background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
              display: 'flex',
              alignItems: 'center',
              gap: 20,
            }}
          >
            <div
              style={{
                width: 72,
                height: 72,
                background: 'rgba(255,255,255,0.2)',
                borderRadius: 16,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 28,
                fontWeight: 700,
                color: 'white',
                backdropFilter: 'blur(10px)',
                border: '2px solid rgba(255,255,255,0.3)',
              }}
            >
              {getInitials(user.email)}
            </div>
            <div>
              <Text style={{ fontSize: 22, fontWeight: 600, color: 'white', display: 'block' }}>
                {user.email}
              </Text>
              <Text style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
                Пользователь EzJob
              </Text>
            </div>
          </div>
        </Card>

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          requiredMark={false}
          size="large"
        >
          {/* Email Section */}
          <Card
            bordered={false}
            style={{
              borderRadius: 16,
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              marginBottom: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <MailOutlined style={{ fontSize: 18, color: '#2563eb' }} />
              </div>
              <div>
                <Text strong style={{ fontSize: 16, display: 'block' }}>Контактные данные</Text>
                <Text type="secondary" style={{ fontSize: 13 }}>Email нельзя изменить</Text>
              </div>
            </div>
            
            <Form.Item name="email" style={{ marginBottom: 0 }}>
              <Input 
                disabled 
                placeholder="Email" 
                style={{ borderRadius: 10, background: '#f8fafc' }}
                prefix={<MailOutlined style={{ color: '#94a3b8' }} />}
              />
            </Form.Item>
          </Card>

          {/* Resume Section */}
          <Card
            bordered={false}
            style={{
              borderRadius: 16,
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              marginBottom: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <FileTextOutlined style={{ fontSize: 18, color: '#16a34a' }} />
              </div>
              <div>
                <Text strong style={{ fontSize: 16, display: 'block' }}>Текст резюме</Text>
                <Text type="secondary" style={{ fontSize: 13 }}>Основная информация о вас для AI-анализа</Text>
              </div>
            </div>

            <Form.Item name="resume_text" style={{ marginBottom: 0 }}>
              <Input.TextArea 
                rows={6} 
                placeholder="Опишите свой опыт, навыки и желаемую позицию..." 
                style={{ borderRadius: 10 }}
              />
            </Form.Item>
          </Card>

          {/* Filter Params Section */}
          <Card
            bordered={false}
            style={{
              borderRadius: 16,
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              marginBottom: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <SettingOutlined style={{ fontSize: 18, color: '#9333ea' }} />
              </div>
              <div>
                <Text strong style={{ fontSize: 16, display: 'block' }}>Дополнительные параметры</Text>
                <Text type="secondary" style={{ fontSize: 13 }}>Специфичные требования к вакансиям</Text>
              </div>
            </div>

            <Form.Item name="user_filter_params" style={{ marginBottom: 0 }}>
              <Input.TextArea 
                rows={3} 
                placeholder="Например: нужна исключительно удаленка без гибрида" 
                style={{ borderRadius: 10 }}
              />
            </Form.Item>
          </Card>

          <Form.Item>
            <GradientButton
              htmlType="submit"
              icon={<SaveOutlined />}
              style={{ width: 200 }}
            >
              Сохранить изменения
            </GradientButton>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};
