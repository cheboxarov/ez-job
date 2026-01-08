import { useState, useEffect } from 'react';
import { Button, Typography, message, Tooltip } from 'antd';
import { SendOutlined, RobotOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { executeAgentAction } from '../api/agentActions';
import type { AgentAction } from '../types/api';

const { Paragraph, Text } = Typography;

interface ActionCardProps {
  action: AgentAction;
  chatId: number;
  onSent?: () => void;
}

export const ActionCard = ({ action, chatId, onSent }: ActionCardProps) => {
  const [sending, setSending] = useState(false);
  const [isSent, setIsSent] = useState(action.data.sended === true);

  useEffect(() => {
    setIsSent(action.data.sended === true);
  }, [action.data.sended]);

  const handleSend = async () => {
    if (!action.data.message_text) {
      message.error('Текст сообщения отсутствует');
      return;
    }

    setSending(true);
    try {
      const updatedAction = await executeAgentAction(action.id);
      setIsSent(true);
      message.success('Сообщение отправлено');
      onSent?.();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при отправке сообщения');
    } finally {
      setSending(false);
    }
  };

  // Не показываем кнопку если уже отправлено
  if (isSent) {
    return (
      <div
        style={{
          marginTop: 8,
          padding: '12px 14px',
          borderRadius: 16,
          background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
          border: '1px dashed #86efac',
          position: 'relative',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <div
            style={{
              width: 24,
              height: 24,
              borderRadius: 6,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <CheckCircleOutlined style={{ color: '#fff', fontSize: 12 }} />
          </div>
          
          <div style={{ flex: 1, minWidth: 0 }}>
            <Text 
              type="secondary" 
              style={{ 
                fontSize: 11, 
                display: 'block', 
                marginBottom: 4,
                color: '#047857',
                fontWeight: 500,
              }}
            >
              Сообщение отправлено
            </Text>
            <Paragraph
              ellipsis={{ rows: 3, expandable: true, symbol: 'ещё' }}
              style={{
                margin: 0,
                fontSize: 13,
                lineHeight: 1.5,
                color: '#065f46',
              }}
            >
              {action.data.message_text}
            </Paragraph>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        marginTop: 8,
        padding: '12px 14px',
        borderRadius: 16,
        background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        border: '1px dashed #7dd3fc',
        position: 'relative',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        <div
          style={{
            width: 24,
            height: 24,
            borderRadius: 6,
            background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <RobotOutlined style={{ color: '#fff', fontSize: 12 }} />
        </div>
        
        <div style={{ flex: 1, minWidth: 0 }}>
          <Text 
            type="secondary" 
            style={{ 
              fontSize: 11, 
              display: 'block', 
              marginBottom: 4,
              color: '#0369a1',
              fontWeight: 500,
            }}
          >
            Предложенный ответ
          </Text>
          <Paragraph
            ellipsis={{ rows: 3, expandable: true, symbol: 'ещё' }}
            style={{
              margin: 0,
              fontSize: 13,
              lineHeight: 1.5,
              color: '#0c4a6e',
            }}
          >
            {action.data.message_text}
          </Paragraph>
        </div>

        <Tooltip title="Отправить">
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={sending}
            size="small"
            style={{
              borderRadius: 8,
              background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
              border: '1px solid #0ea5e9',
              width: 32,
              height: 32,
              padding: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          />
        </Tooltip>
      </div>
    </div>
  );
};
