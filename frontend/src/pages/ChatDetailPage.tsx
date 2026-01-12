import { useEffect, useState, useMemo, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Typography, Spin, Alert, Button, Input } from 'antd';
import { MessageOutlined, SendOutlined } from '@ant-design/icons';
import { getChat, sendChatMessage } from '../api/chats';
import { getAgentActions } from '../api/agentActions';
import { ActionCard } from '../components/ActionCard';
import { FileAttachment } from '../components/FileAttachment';
import { MarkdownMessage } from '../components/MarkdownMessage';
import { PageHeader } from '../components/PageHeader';
import { useWindowSize } from '../hooks/useWindowSize';
import type { ChatDetailedResponse, ChatMessage, AgentAction } from '../types/api';

const { TextArea } = Input;
const { Text } = Typography;

export const ChatDetailPage = () => {
  const navigate = useNavigate();
  const { chatId } = useParams<{ chatId: string }>();
  const windowSize = useWindowSize();
  const [chat, setChat] = useState<ChatDetailedResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messageText, setMessageText] = useState('');
  const [sending, setSending] = useState(false);
  const [actions, setActions] = useState<AgentAction[]>([]);
  const [loadingActions, setLoadingActions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const isMobile = useMemo(() => windowSize.width < 768, [windowSize.width]);

  useEffect(() => {
    if (chatId) {
      loadChat(parseInt(chatId, 10));
    }
  }, [chatId]);

  const loadChat = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getChat(id);
      setChat(data);
      await loadActions(id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке чата');
    } finally {
      setLoading(false);
    }
  };

  const loadActions = async (chatId: number) => {
    setLoadingActions(true);
    try {
      const response = await getAgentActions({
        types: ['send_message'],
        entity_type: 'hh_dialog',
        entity_id: chatId,
      });
      setActions(response.items);
    } catch (err: any) {
      console.error('Ошибка при загрузке actions:', err);
    } finally {
      setLoadingActions(false);
    }
  };

  const actionsByMessageId = useMemo(() => {
    const map = new Map<number, AgentAction[]>();
    actions.forEach((action) => {
      const messageTo = action.data.message_to;
      if (messageTo !== undefined) {
        if (!map.has(messageTo)) {
          map.set(messageTo, []);
        }
        map.get(messageTo)!.push(action);
      }
    });
    return map;
  }, [actions]);

  const handleSendMessage = async () => {
    if (!messageText.trim() || !chatId) return;

    setSending(true);
    try {
      await sendChatMessage(parseInt(chatId, 10), messageText);
      setMessageText('');
      await loadChat(parseInt(chatId, 10));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при отправке сообщения');
    } finally {
      setSending(false);
    }
  };

  const formatTimeShort = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `${hours}:${minutes}`;
    } catch {
      return timeStr;
    }
  };

  const isUserMessage = (message: ChatMessage) => {
    if (!chat) return false;
    return message.participant_id === chat.current_participant_id;
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [chat?.messages?.items.length]);

  if (loading && !chat) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Загрузка чата..." />
      </div>
    );
  }

  if (error && !chat) {
    return (
      <div>
        <PageHeader
          title="Ошибка загрузки чата"
          icon={<MessageOutlined />}
          breadcrumbs={[
            { title: 'Чаты', path: '/chats' },
            { title: 'Ошибка' }
          ]}
        />
        <Alert
          message="Ошибка"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/chats')}>
              Вернуться к списку
            </Button>
          }
        />
      </div>
    );
  }

  if (!chat) {
    return null;
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      overflow: 'hidden',
    }}>
      {/* Header - фиксированная высота */}
      <div style={{ flexShrink: 0 }}>
        <PageHeader
          title={`Чат #${chat.id}`}
          icon={<MessageOutlined />}
          breadcrumbs={[
            { title: 'Чаты', path: '/chats' },
            { title: `Чат #${chat.id}` }
          ]}
        />
      </div>

      {/* Messages area - занимает оставшееся пространство и скроллится */}
      <div
        style={{
          flex: 1,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          padding: isMobile ? '16px' : '24px',
          paddingBottom: 0,
        }}
      >
        <div
          style={{
            flex: 1,
            padding: isMobile ? '16px' : '24px',
            background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
            borderRadius: 20,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            marginBottom: isMobile ? 12 : 16,
          }}
        >
          <div
            ref={messagesEndRef}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 16,
              flex: 1,
              overflowY: 'auto',
              overflowX: 'hidden',
              paddingRight: 4,
            }}
          >
            {chat.messages && chat.messages.items.length > 0 ? (
              chat.messages.items.map((message: ChatMessage) => {
                const hasText = Boolean(message.text?.trim());
                const hasFiles = Boolean(message.files && message.files.length > 0);
                if (!hasText && !hasFiles) {
                  return null;
                }
                const isUser = isUserMessage(message);
                return (
                  <div
                    key={message.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: isUser ? 'flex-end' : 'flex-start',
                    }}
                  >
                    {/* Sender name */}
                    <Text 
                      type="secondary" 
                      style={{ 
                        fontSize: 12, 
                        marginBottom: 6,
                        marginLeft: isUser ? 0 : 16,
                        marginRight: isUser ? 16 : 0,
                      }}
                    >
                      {message.participant_display?.name || 'Участник'}
                    </Text>
                    
                    {/* Message bubble */}
                    <div
                      style={{
                        maxWidth: isMobile ? '90%' : '75%',
                        padding: '14px 18px',
                        borderRadius: isUser 
                          ? '20px 20px 4px 20px' 
                          : '20px 20px 20px 4px',
                        background: isUser
                          ? 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)'
                          : '#ffffff',
                        color: isUser ? '#ffffff' : '#0f172a',
                        border: isUser ? '1px solid #2563eb' : '1px solid #e5e7eb',
                        position: 'relative',
                        fontSize: 15,
                        lineHeight: 1.5,
                      }}
                    >
                      {hasText && (
                        <MarkdownMessage content={message.text} variant={isUser ? 'user' : 'assistant'} />
                      )}

                      {hasFiles && (
                        <div
                          style={{
                            marginTop: hasText ? 12 : 0,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 8,
                          }}
                        >
                          {message.files!.map((file, index) => (
                            <FileAttachment
                              key={file.upload_id || `${message.id}-${index}`}
                              file={file}
                              variant={isUser ? 'user' : 'assistant'}
                            />
                          ))}
                        </div>
                      )}
                      
                      <Text 
                        style={{ 
                          fontSize: 11, 
                          marginTop: 8,
                          display: 'block',
                          textAlign: 'right',
                          color: isUser ? 'rgba(255,255,255,0.7)' : '#94a3b8',
                        }}
                      >
                        {formatTimeShort(message.creation_time)}
                      </Text>
                    </div>

                    {/* Action cards for this message */}
                    {actionsByMessageId.has(message.id) && (
                      <div style={{ 
                        marginTop: 8,
                        maxWidth: isMobile ? '90%' : '75%',
                        width: '100%',
                      }}>
                        {actionsByMessageId.get(message.id)!.map((action) => (
                          <ActionCard
                            key={action.id}
                            action={action}
                            chatId={parseInt(chatId || '0', 10)}
                            onSent={() => {
                              if (chatId) {
                                loadChat(parseInt(chatId, 10));
                              }
                            }}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <div
                style={{
                  textAlign: 'center',
                  padding: '60px 20px',
                  color: '#94a3b8',
                }}
              >
                <MessageOutlined style={{ fontSize: 48, marginBottom: 16, opacity: 0.5 }} />
                <Text type="secondary" style={{ fontSize: 16, display: 'block' }}>
                  В этом чате пока нет сообщений
                </Text>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Message input - фиксированная высота, всегда внизу */}
      <div
        style={{
          flexShrink: 0,
          background: '#ffffff',
          borderRadius: 16,
          padding: isMobile ? '12px 16px' : '16px 20px',
          border: '1px solid #e5e7eb',
          margin: isMobile ? '0 16px 16px' : '0 24px 24px',
        }}
      >
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
          <TextArea
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            placeholder="Введите сообщение..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            onPressEnter={(e) => {
              if (e.shiftKey) return;
              e.preventDefault();
              handleSendMessage();
            }}
            disabled={sending}
            style={{
              flex: 1,
              borderRadius: 12,
              resize: 'none',
              fontSize: 15,
            }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            loading={sending}
            disabled={!messageText.trim()}
            style={{
              height: 44,
              width: 44,
              borderRadius: 12,
              background: messageText.trim()
                ? 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)'
                : undefined,
              border: messageText.trim() ? '1px solid #2563eb' : undefined,
            }}
          />
        </div>
      </div>
    </div>
  );
};
