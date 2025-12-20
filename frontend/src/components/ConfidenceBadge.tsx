import { Tag, Tooltip } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';

interface ConfidenceBadgeProps {
  confidence: number;
  reason?: string | null;
}

export const ConfidenceBadge = ({ confidence, reason }: ConfidenceBadgeProps) => {
  let color = '#ef4444'; // red-500
  let bgColor = '#fef2f2'; // red-50
  let borderColor = '#fecaca'; // red-200
  let matchText = 'низкий матч';

  if (confidence >= 0.75) {
    color = '#10b981'; // emerald-500
    bgColor = '#ecfdf5'; // emerald-50
    borderColor = '#a7f3d0'; // emerald-200
    matchText = 'высокий матч';
  } else if (confidence >= 0.5) {
    color = '#f59e0b'; // amber-500
    bgColor = '#fffbeb'; // amber-50
    borderColor = '#fde68a'; // amber-200
    matchText = 'средний матч';
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 12px',
          borderRadius: 9999,
          backgroundColor: bgColor,
          border: `1px solid ${borderColor}`,
          color: color,
          fontSize: 13,
          fontWeight: 500,
          whiteSpace: 'nowrap',
        }}
      >
        <span style={{ fontWeight: 700 }}>{Math.round(confidence * 100)}%</span>
        <span>·</span>
        <span>{matchText}</span>
      </div>
      
      {reason && (
        <Tooltip title={reason} overlayStyle={{ maxWidth: 300 }}>
          <QuestionCircleOutlined style={{ color: '#9ca3af', fontSize: 16, cursor: 'help' }} />
        </Tooltip>
      )}
    </div>
  );
};

