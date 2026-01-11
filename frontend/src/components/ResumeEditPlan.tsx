import { useState, useEffect } from 'react';
import { Card, Steps, Typography, Collapse, Tag } from 'antd';
import { 
  CheckCircleOutlined, 
  ClockCircleOutlined, 
  LoadingOutlined, 
  UnorderedListOutlined 
} from '@ant-design/icons';
import { useResumeEditStore } from '../stores/resumeEditStore';
import { motion, AnimatePresence } from 'motion/react';

const { Text } = Typography;
const { Panel } = Collapse;

export const ResumeEditPlan = () => {
  const { current_plan } = useResumeEditStore();
  const [activeKeys, setActiveKeys] = useState<string[]>(['plan']);

  // Автоматически разворачиваем панель при появлении/обновлении плана
  useEffect(() => {
    if (current_plan.length > 0) {
      setActiveKeys(['plan']);
    }
  }, [current_plan.length]);

  if (!current_plan || current_plan.length === 0) {
    return null;
  }

  // Определяем текущий шаг для Steps
  const currentStepIndex = current_plan.findIndex(t => t.status === 'in_progress');
  // Если нет активного, но есть выполненные -> все выполнены или ждем
  const completedCount = current_plan.filter(t => t.status === 'completed').length;
  
  // Вычисляем процент выполнения
  const progressPercent = Math.round((completedCount / current_plan.length) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      style={{ marginBottom: 16 }}
    >
      <Collapse 
        activeKey={activeKeys} 
        onChange={(keys) => setActiveKeys(keys as string[])}
        ghost
        style={{ background: 'white', borderRadius: 12, border: '1px solid #e5e7eb', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}
        expandIconPosition="end"
      >
        <Panel 
          header={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <UnorderedListOutlined style={{ color: '#1890ff' }} />
                <Text strong>План действий</Text>
                <Tag color={progressPercent === 100 ? 'success' : 'blue'}>
                  {progressPercent}%
                </Tag>
              </div>
            </div>
          } 
          key="plan"
        >
          <div style={{ padding: '0 8px 8px' }}>
            <Steps
              direction="vertical"
              size="small"
              current={currentStepIndex !== -1 ? currentStepIndex : (completedCount === current_plan.length ? current_plan.length : 0)}
              items={current_plan.map((task) => {
                let status: 'wait' | 'process' | 'finish' | 'error' = 'wait';
                let icon = <ClockCircleOutlined />;
                
                if (task.status === 'completed') {
                  status = 'finish';
                  icon = <CheckCircleOutlined />;
                } else if (task.status === 'in_progress') {
                  status = 'process';
                  icon = <LoadingOutlined />;
                }

                return {
                  title: (
                    <Text 
                      strong={task.status === 'in_progress'} 
                      delete={task.status === 'completed'}
                      style={{ color: task.status === 'completed' ? '#9ca3af' : 'inherit' }}
                    >
                      {task.title}
                    </Text>
                  ),
                  description: task.description,
                  status,
                  icon
                };
              })}
            />
          </div>
        </Panel>
      </Collapse>
    </motion.div>
  );
};
