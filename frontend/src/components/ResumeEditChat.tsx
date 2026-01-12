import { useEffect, useRef, useState } from 'react';
import { Input, Button, Checkbox, Badge, Tooltip } from 'antd';
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
  CopyOutlined,
  LikeOutlined,
  DislikeOutlined,
  UnorderedListOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'motion/react';
import { useResumeEditStore } from '../stores/resumeEditStore';
import { TypingIndicator } from './TypingIndicator';
import { QuickActions } from './QuickActions';
import { ResumeEditPlanModal } from './ResumeEditPlanModal';
import { MarkdownMessage } from './MarkdownMessage';
import styles from '../pages/ResumeEditPage.module.css';

const { TextArea } = Input;

export const ResumeEditChat = () => {
  const [messageText, setMessageText] = useState('');
  const [questionAnswers, setQuestionAnswers] = useState<Record<string, string | string[]>>({});
  const [planModalOpen, setPlanModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  
  const {
    chat_history,
    streaming_message,
    websocket_connected,
    pending_questions,
    current_plan,
    is_processing,
    sendMessage,
    answerAllQuestions,
    stopGeneration,
  } = useResumeEditStore();

  // Автоскролл к концу сообщений
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [chat_history, streaming_message, pending_questions]);

  // Сброс ответов на вопросы
  useEffect(() => {
    if (pending_questions.length === 0) {
      setQuestionAnswers({});
    } else {
      const newAnswers: Record<string, string | string[]> = {};
      pending_questions.forEach((q) => {
        if (!(q.id in questionAnswers)) {
          newAnswers[q.id] = q.allow_multiple ? [] : '';
        } else {
          newAnswers[q.id] = questionAnswers[q.id];
        }
      });
      setQuestionAnswers(newAnswers);
    }
  }, [pending_questions]);

  const handleSend = (text: string = messageText) => {
    if (!text.trim()) return;
    sendMessage(text);
    setMessageText('');
  };

  const handleQuickAction = (action: string) => {
    handleSend(action);
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    setQuestionAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  const handleMultipleAnswerChange = (questionId: string, checkedValues: string[]) => {
    setQuestionAnswers((prev) => ({ ...prev, [questionId]: checkedValues }));
  };

  const handleAdditionalAnswerChange = (questionId: string, additionalText: string) => {
    const question = pending_questions.find((q) => q.id === questionId);
    if (!question?.allow_multiple) {
      handleAnswerChange(questionId, additionalText);
      return;
    }

    if (additionalText.trim()) {
      const textParts = additionalText.split(',').map(s => s.trim()).filter(s => s);
      setQuestionAnswers((prev) => ({ ...prev, [questionId]: textParts }));
    } else {
      const currentAnswers = questionAnswers[questionId];
      const selectedAnswers = Array.isArray(currentAnswers) ? currentAnswers : [];
      setQuestionAnswers((prev) => ({ ...prev, [questionId]: selectedAnswers }));
    }
  };

  const handleSendAllAnswers = () => {
    const requiredQuestions = pending_questions.filter((q) => q.required);
    const missingAnswers = requiredQuestions.filter((q) => {
      const answer = questionAnswers[q.id];
      if (q.allow_multiple) {
        return !Array.isArray(answer) || answer.length === 0;
      } else {
        return !answer || (typeof answer === 'string' && !answer.trim());
      }
    });

    if (missingAnswers.length > 0) return;

    const answers: Array<{ questionId: string; answer: string }> = [];
    pending_questions.forEach((q) => {
      const answer = questionAnswers[q.id];
      if (!answer) return;

      let answerText: string;
      if (q.allow_multiple && Array.isArray(answer)) {
        answerText = answer.filter(a => a.trim()).join(', ');
      } else if (typeof answer === 'string') {
        answerText = answer.trim();
      } else {
        return;
      }

      if (answerText) {
        answers.push({ questionId: q.id, answer: answerText });
      }
    });

    if (answers.length > 0) {
      answerAllQuestions(answers);
    }
    setQuestionAnswers({});
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Получаем текущую активную задачу
  const activeTask = current_plan.find(t => t.status === 'in_progress');
  const hasPlan = current_plan && current_plan.length > 0;

  return (
    <div className={styles.chatSection}>
      <div className={styles.chatHeader}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
          <Badge status={websocket_connected ? 'success' : 'error'} />
          <span style={{ fontWeight: 600 }}>AI Ассистент</span>
          {hasPlan && activeTask && (
            <span style={{ 
              fontSize: 12, 
              color: 'var(--text-secondary)', 
              marginLeft: 8,
              display: 'flex',
              alignItems: 'center',
              gap: 4
            }}>
              <LoadingOutlined style={{ fontSize: 10 }} />
              {activeTask.title}
            </span>
          )}
        </div>
        {hasPlan && (
          <Button
            type="text"
            icon={<UnorderedListOutlined />}
            onClick={() => setPlanModalOpen(true)}
            size="small"
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 4,
              color: 'var(--text-secondary)'
            }}
          >
            План
          </Button>
        )}
      </div>

      <ResumeEditPlanModal 
        open={planModalOpen} 
        onClose={() => setPlanModalOpen(false)} 
      />

      <div className={styles.chatMessages} ref={messagesContainerRef}>
        {chat_history.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-secondary)' }}>
            <div className={`${styles.avatar} ${styles.botAvatar}`} style={{ width: 64, height: 64, margin: '0 auto 16px', fontSize: 32 }}>
              <RobotOutlined />
            </div>
            <p>Начните диалог с агентом.<br/>Опишите, какие изменения вы хотите внести в резюме.</p>
          </div>
        )}

        <AnimatePresence>
          {chat_history.map((msg) => {
            const isUser = msg.type === 'user';
            const isQuestion = msg.type === 'question';
            const isCheckpoint = msg.type === 'checkpoint';
            const bubbleClass = isUser ? styles.userBubble : isQuestion ? styles.questionBubble : styles.botBubble;
            const avatarClass = isUser ? styles.userAvatar : styles.botAvatar;
            const icon = isUser ? <UserOutlined /> : <RobotOutlined />;

            if (isCheckpoint) {
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={styles.checkpointRow}
                >
                  <div className={styles.checkpointCard}>
                    <div className={styles.checkpointIcon}>
                      <CheckCircleOutlined />
                    </div>
                    <div className={styles.checkpointContent}>{msg.content}</div>
                  </div>
                </motion.div>
              );
            }

            return (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={`${styles.message} ${isUser ? styles.messageUser : styles.messageBot}`}
              >
                <div className={`${styles.avatar} ${avatarClass}`}>
                  {icon}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxWidth: '100%' }}>
                  <div className={`${styles.messageBubble} ${bubbleClass}`}>
                    <MarkdownMessage content={msg.content} variant={isUser ? 'user' : 'assistant'} />
                    
                    {!isUser && !isQuestion && (
                      <div style={{ display: 'flex', gap: 8, marginTop: 8, opacity: 0.7, justifyContent: 'flex-end' }}>
                        <Tooltip title="Копировать">
                          <CopyOutlined onClick={() => copyToClipboard(msg.content)} style={{ cursor: 'pointer' }} />
                        </Tooltip>
                        <Tooltip title="Хороший ответ">
                          <LikeOutlined style={{ cursor: 'pointer' }} />
                        </Tooltip>
                        <Tooltip title="Плохой ответ">
                          <DislikeOutlined style={{ cursor: 'pointer' }} />
                        </Tooltip>
                      </div>
                    )}
                  </div>

                  {/* Рендеринг инпутов для вопросов */}
                  {isQuestion && msg.questionId && (() => {
                    const question = pending_questions.find((q) => q.id === msg.questionId);
                    if (!question) return null; // Вопрос уже отвечен или не найден

                    const suggestedAnswers = question.suggested_answers || [];
                    const allowMultiple = question.allow_multiple || false;
                    const currentAnswer = questionAnswers[msg.questionId];
                    const selectedValues = allowMultiple && Array.isArray(currentAnswer) ? currentAnswer : [];
                    const textValue = allowMultiple ? '' : (typeof currentAnswer === 'string' ? currentAnswer : '');
                    
                    const hasStandardAnswers = suggestedAnswers.some(
                      (a) => a.toLowerCase().includes('не знаю') || a.toLowerCase().includes('не трогай')
                    );

                    return (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        style={{ marginTop: 8, background: 'rgba(255,255,255,0.5)', padding: 12, borderRadius: 8 }}
                      >
                         {suggestedAnswers.length > 0 && (
                          <div style={{ marginBottom: 12 }}>
                            <span style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>
                              {allowMultiple ? 'Выберите варианты:' : 'Варианты ответов:'}
                            </span>
                            {allowMultiple ? (
                              <Checkbox.Group
                                value={selectedValues}
                                onChange={(checked) => handleMultipleAnswerChange(msg.questionId!, checked as string[])}
                                style={{ display: 'flex', flexDirection: 'column', gap: 8 }}
                              >
                                {suggestedAnswers.map((answer, idx) => (
                                  <Checkbox key={idx} value={answer} style={{ fontSize: 13 }}>{answer}</Checkbox>
                                ))}
                              </Checkbox.Group>
                            ) : (
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                {suggestedAnswers.map((answer, idx) => (
                                  <Button
                                    key={idx}
                                    size="small"
                                    onClick={() => handleAnswerChange(msg.questionId!, answer)}
                                    style={{ fontSize: 12 }}
                                  >
                                    {answer}
                                  </Button>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {!hasStandardAnswers && !allowMultiple && (
                          <div style={{ marginBottom: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                            <Button size="small" onClick={() => handleAnswerChange(msg.questionId!, 'не знаю, придумай сам')}>
                              Не знаю
                            </Button>
                            <Button size="small" onClick={() => handleAnswerChange(msg.questionId!, 'не трогай эту секцию')}>
                              Не трогать
                            </Button>
                          </div>
                        )}

                        <TextArea
                          value={allowMultiple ? (Array.isArray(currentAnswer) ? currentAnswer.join(', ') : '') : textValue}
                          onChange={(e) => {
                            if (allowMultiple) {
                              handleAdditionalAnswerChange(msg.questionId!, e.target.value);
                            } else {
                              handleAnswerChange(msg.questionId!, e.target.value);
                            }
                          }}
                          placeholder={allowMultiple ? "Или введите свои ответы..." : "Или введите свой ответ..."}
                          autoSize={{ minRows: 2, maxRows: 4 }}
                        />
                        {allowMultiple && selectedValues.length > 0 && (
                          <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-secondary)' }}>
                            Выбрано: {selectedValues.join(', ')}
                          </div>
                        )}
                      </motion.div>
                    );
                  })()}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {streaming_message && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`${styles.message} ${styles.messageBot}`}
          >
            <div className={`${styles.avatar} ${styles.botAvatar}`}>
              <RobotOutlined />
            </div>
            <div className={`${styles.messageBubble} ${styles.botBubble}`}>
              <MarkdownMessage content={streaming_message} variant="assistant" />
              <div style={{ marginTop: 8 }}>
                <TypingIndicator />
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {pending_questions.length > 0 ? (
        <div style={{ padding: 16, borderTop: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.8)' }}>
           <Button
            type="primary"
            block
            onClick={handleSendAllAnswers}
            disabled={pending_questions.some((q) => {
               const answer = questionAnswers[q.id];
               if (q.allow_multiple) {
                 return !Array.isArray(answer) || answer.length === 0;
               } else {
                 return !answer || (typeof answer === 'string' && !answer.trim());
               }
            })}
          >
            Отправить ответы ({pending_questions.length})
          </Button>
        </div>
      ) : (
        <>
          <QuickActions onAction={handleQuickAction} disabled={!websocket_connected || is_processing || !!streaming_message} />
          <div className={styles.chatInputArea}>
            {is_processing || streaming_message ? (
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ 
                  flex: 1, 
                  padding: '12px 16px', 
                  background: 'rgba(0, 0, 0, 0.02)', 
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  color: 'var(--text-secondary)'
                }}>
                  <LoadingOutlined style={{ fontSize: 16 }} />
                  <span>Генерация ответа...</span>
                </div>
                <Button
                  type="primary"
                  danger
                  shape="circle"
                  icon={<StopOutlined />}
                  size="large"
                  onClick={() => stopGeneration()}
                />
              </div>
            ) : (
              <div style={{ display: 'flex', gap: 12 }}>
                <TextArea
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Опишите желаемые изменения..."
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  style={{ borderRadius: 12, resize: 'none' }}
                />
                <Button
                  type="primary"
                  shape="circle"
                  icon={<SendOutlined />}
                  size="large"
                  onClick={() => handleSend()}
                  disabled={!websocket_connected || !messageText.trim()}
                />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
