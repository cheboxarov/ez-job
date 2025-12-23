import { useState } from 'react';
import { Button, Typography, message, Tooltip } from 'antd';
import { SendOutlined, RobotOutlined } from '@ant-design/icons';
import { sendChatMessage } from '../api/chats';
import type { AgentAction } from '../types/api';

const { Paragraph, Text } = Typography;

interface ActionCardProps {
  action: AgentAction;
  chatId: number;
  onSent?: () => void;
}

export const ActionCard = ({ action, chatId, onSent }: ActionCardProps) => {
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!action.data.message_text) {
      message.error('Текст сообщения отсутствует');
      return;
    }

    setSending(true);
    try {
      await sendChatMessage(chatId, action.data.message_text);
      message.success('Сообщение отправлено');
      onSent?.();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Ошибка при отправке сообщения');
    } finally {
      setSending(false);
    }
  };

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
              border: 'none',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
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
