import { Modal, Steps, Typography, Tag } from 'antd';
import { 
  CheckCircleOutlined, 
  ClockCircleOutlined, 
  LoadingOutlined 
} from '@ant-design/icons';
import { useResumeEditStore } from '../stores/resumeEditStore';

const { Text } = Typography;

interface ResumeEditPlanModalProps {
  open: boolean;
  onClose: () => void;
}

export const ResumeEditPlanModal = ({ open, onClose }: ResumeEditPlanModalProps) => {
  const { current_plan } = useResumeEditStore();

  if (!current_plan || current_plan.length === 0) {
    return null;
  }

  // Определяем текущий шаг для Steps
  const currentStepIndex = current_plan.findIndex(t => t.status === 'in_progress');
  const completedCount = current_plan.filter(t => t.status === 'completed').length;
  const progressPercent = Math.round((completedCount / current_plan.length) * 100);

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Text strong>План действий</Text>
          <Tag color={progressPercent === 100 ? 'success' : 'blue'}>
            {progressPercent}%
          </Tag>
        </div>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={600}
      styles={{
        body: { padding: '24px' }
      }}
    >
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
    </Modal>
  );
};
