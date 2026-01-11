import { Card, List, Button, Space, Typography, Tag, Empty } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { useResumeEditStore, type ResumeEditPatch } from '../stores/resumeEditStore';

const { Text, Paragraph } = Typography;

interface ResumeEditPatchesPanelProps {
  patches: ResumeEditPatch[];
}

export const ResumeEditPatchesPanel = ({ patches }: ResumeEditPatchesPanelProps) => {
  const { applyPatch, rejectPatch } = useResumeEditStore();

  if (patches.length === 0) {
    return (
      <Card title="Предложенные изменения" style={{ height: '100%' }}>
        <Empty description="Нет предложенных изменений" />
      </Card>
    );
  }

  const getPatchTypeColor = (type: string) => {
    switch (type) {
      case 'replace':
        return 'orange';
      case 'insert':
        return 'green';
      case 'delete':
        return 'red';
      default:
        return 'default';
    }
  };

  const getPatchTypeLabel = (type: string) => {
    switch (type) {
      case 'replace':
        return 'Замена';
      case 'insert':
        return 'Вставка';
      case 'delete':
        return 'Удаление';
      default:
        return type;
    }
  };

  return (
    <Card title="Предложенные изменения" style={{ height: '100%' }}>
      <List
        dataSource={patches}
        renderItem={(patch) => (
          <List.Item
            actions={[
              <Button
                key="apply"
                type="primary"
                icon={<CheckOutlined />}
                size="small"
                onClick={() => applyPatch(patch.id)}
              >
                Применить
              </Button>,
              <Button
                key="reject"
                danger
                icon={<CloseOutlined />}
                size="small"
                onClick={() => rejectPatch(patch.id)}
              >
                Отклонить
              </Button>,
            ]}
          >
            <List.Item.Meta
              title={
                <Space>
                  <Tag color={getPatchTypeColor(patch.type)}>
                    {getPatchTypeLabel(patch.type)}
                  </Tag>
                  <Text strong style={{ fontSize: 12 }}>
                    {patch.reason}
                  </Text>
                </Space>
              }
              description={
                <div>
                  {patch.type === 'replace' && (
                    <div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Было:
                      </Text>
                      <div
                        style={{
                          background: '#fff1f0',
                          padding: 8,
                          borderRadius: 4,
                          marginTop: 4,
                          fontSize: 12,
                        }}
                      >
                        {patch.old_text.substring(0, 100)}
                        {patch.old_text.length > 100 ? '...' : ''}
                      </div>
                      <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
                        Станет:
                      </Text>
                      <div
                        style={{
                          background: '#f6ffed',
                          padding: 8,
                          borderRadius: 4,
                          marginTop: 4,
                          fontSize: 12,
                        }}
                      >
                        {patch.new_text?.substring(0, 100)}
                        {patch.new_text && patch.new_text.length > 100 ? '...' : ''}
                      </div>
                    </div>
                  )}
                  {patch.type === 'insert' && (
                    <div
                      style={{
                        background: '#f6ffed',
                        padding: 8,
                        borderRadius: 4,
                        fontSize: 12,
                      }}
                    >
                      {patch.new_text?.substring(0, 100)}
                      {patch.new_text && patch.new_text.length > 100 ? '...' : ''}
                    </div>
                  )}
                  {patch.type === 'delete' && (
                    <div
                      style={{
                        background: '#fff1f0',
                        padding: 8,
                        borderRadius: 4,
                        fontSize: 12,
                      }}
                    >
                      {patch.old_text.substring(0, 100)}
                      {patch.old_text.length > 100 ? '...' : ''}
                    </div>
                  )}
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
};
