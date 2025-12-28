import React from 'react';
import { Modal, Progress, Typography, Tag, Empty, Spin, Collapse } from 'antd';
import { 
  CheckCircleFilled, 
  WarningFilled, 
  CloseCircleFilled,
  BulbOutlined,
  RocketOutlined,
  StarFilled,
  CaretRightOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface Remark {
  rule: string;
  comment: string;
  improvement: string;
}

interface ResumeEvaluationResult {
  conf: number;
  remarks: Remark[];
  summary?: string;
}

interface ResumeEvaluationModalProps {
  visible: boolean;
  onCancel: () => void;
  loading: boolean;
  result: ResumeEvaluationResult | null;
}

const getScoreData = (conf: number) => {
  if (conf >= 0.85) return {
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    bgGradient: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
    color: '#059669',
    icon: <RocketOutlined style={{ fontSize: 28 }} />,
    label: 'Отличное резюме!',
    emoji: '🚀',
  };
  if (conf >= 0.7) return {
    gradient: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    bgGradient: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
    color: '#16a34a',
    icon: <CheckCircleFilled style={{ fontSize: 28 }} />,
    label: 'Хорошая работа!',
    emoji: '✨',
  };
  if (conf >= 0.5) return {
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    bgGradient: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
    color: '#d97706',
    icon: <WarningFilled style={{ fontSize: 28 }} />,
    label: 'Есть над чем работать',
    emoji: '💡',
  };
  return {
    gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    bgGradient: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
    color: '#dc2626',
    icon: <CloseCircleFilled style={{ fontSize: 28 }} />,
    label: 'Требует доработки',
    emoji: '🔧',
  };
};

export const ResumeEvaluationModal: React.FC<ResumeEvaluationModalProps> = ({
  visible,
  onCancel,
  loading,
  result,
}) => {
  const scoreData = result ? getScoreData(result.conf) : null;

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={720}
      destroyOnClose
      centered
      closable={!loading}
      maskClosable={!loading}
      styles={{ 
        body: { padding: 0 },
      }}
      className="resume-evaluation-modal"
    >
      {loading ? (
        <div style={{ 
          padding: '80px 40px',
          textAlign: 'center',
          background: 'transparent',
        }}>
          <Title level={3} style={{ margin: '0 0 12px', color: '#1e293b', fontWeight: 600 }}>
            Анализируем ваше резюме
          </Title>
          <Text style={{ color: '#64748b', fontSize: 16 }}>
            ИИ проверяет соответствие правилам HH.ru...
          </Text>
          <div style={{ marginTop: 32 }}>
            <Spin size="large" />
          </div>
        </div>
      ) : result && scoreData ? (
        <div style={{ borderRadius: 24, overflow: 'hidden' }}>
          {/* Header with score */}
          <div style={{
            background: scoreData.bgGradient,
            padding: '40px 40px 48px',
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 24
          }}>
            {/* Decorative circles */}
            <div style={{
              position: 'absolute',
              top: -60,
              right: -60,
              width: 200,
              height: 200,
              borderRadius: '50%',
              background: scoreData.gradient,
              opacity: 0.1,
            }} />
            <div style={{
              position: 'absolute',
              bottom: -40,
              left: -40,
              width: 120,
              height: 120,
              borderRadius: '50%',
              background: scoreData.gradient,
              opacity: 0.08,
            }} />

            <div style={{ 
              display: 'flex', 
              alignItems: 'flex-start',
              gap: 32,
              position: 'relative',
              zIndex: 1,
            }}>
              {/* Score circle */}
              <div style={{
                flexShrink: 0,
                width: 140,
                height: 140,
                borderRadius: '50%',
                background: 'white',
                boxShadow: '0 8px 32px -8px rgba(0,0,0,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
              }}>
                <Progress
                  type="circle"
                  percent={Math.round(result.conf * 100)}
                  strokeColor={scoreData.gradient}
                  strokeWidth={8}
                  size={130}
                  format={(percent) => (
                    <div style={{ lineHeight: 1.1 }}>
                      <div style={{ fontSize: 36, fontWeight: 700, color: scoreData.color }}>
                        {percent}
                      </div>
                      <div style={{ fontSize: 14, color: '#94a3b8', fontWeight: 500 }}>
                        из 100
                      </div>
                    </div>
                  )}
                />
              </div>

              {/* Score info */}
              <div style={{ flex: 1, paddingTop: 8 }}>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 16px',
                  background: scoreData.gradient,
                  borderRadius: 100,
                  color: 'white',
                  fontWeight: 600,
                  fontSize: 14,
                  marginBottom: 16,
                  boxShadow: `0 4px 16px -4px ${scoreData.color}66`,
                }}>
                  {scoreData.label}
                </div>
                <Paragraph style={{ 
                  margin: 0, 
                  color: '#475569', 
                  fontSize: 16,
                  lineHeight: 1.7,
                }}>
                  {result.summary}
                </Paragraph>
              </div>
            </div>
          </div>

          {/* Remarks section */}
          <div style={{ padding: '32px 40px 40px' }}>
            {result.remarks.length > 0 ? (
              <>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 12, 
                  marginBottom: 20,
                }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <BulbOutlined style={{ fontSize: 18, color: '#64748b' }} />
                  </div>
                  <div>
                    <Title level={5} style={{ margin: 0, color: '#1e293b' }}>
                      Рекомендации по улучшению
                    </Title>
                    <Text style={{ color: '#94a3b8', fontSize: 13 }}>
                      {result.remarks.length} {result.remarks.length === 1 ? 'замечание' : 
                        result.remarks.length < 5 ? 'замечания' : 'замечаний'}
                    </Text>
                  </div>
                </div>

                <Collapse
                  ghost
                  expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} style={{ fontSize: 14, color: '#94a3b8' }} />}
                  style={{ display: 'flex', flexDirection: 'column', gap: 12 }}
                >
                  {result.remarks.map((remark, index) => (
                    <Panel
                      key={index}
                      header={
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center',
                          gap: 16,
                          flex: 1
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                            <Tag 
                              style={{ 
                                margin: 0,
                                borderRadius: 6,
                                background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
                                border: 'none',
                                color: '#2563eb',
                                fontWeight: 500,
                                fontSize: 12,
                                padding: '2px 10px',
                              }}
                            >
                              {remark.rule}
                            </Tag>

                          </div>
                        </div>
                      }
                      style={{
                        background: '#fafafa',
                        borderRadius: 16,
                        border: '1px solid #f1f5f9',
                        overflow: 'hidden',
                        marginBottom: 0, // override default collapse margin
                      }}
                    >
                      <div style={{ paddingLeft: 44 }}>
                        <Text style={{ 
                          display: 'block',
                          color: '#475569',
                          fontSize: 14,
                          lineHeight: 1.6,
                          marginBottom: 12,
                        }}>
                          {remark.comment}
                        </Text>
                        <div style={{
                          background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                          borderRadius: 10,
                          padding: '12px 16px',
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 10,
                        }}>
                          <StarFilled style={{ 
                            fontSize: 12, 
                            color: '#22c55e',
                            marginTop: 3,
                          }} />
                          <Text style={{ 
                            color: '#166534',
                            fontSize: 13,
                            lineHeight: 1.5,
                          }}>
                            {remark.improvement}
                          </Text>
                        </div>
                      </div>
                    </Panel>
                  ))}
                </Collapse>
              </>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '40px 20px',
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                borderRadius: 20,
              }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>🎉</div>
                <Title level={4} style={{ margin: '0 0 8px', color: '#166534' }}>
                  Превосходно!
                </Title>
                <Text style={{ color: '#15803d', fontSize: 15 }}>
                  Ваше резюме полностью оптимизировано и готово к работе
                </Text>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div style={{ padding: '60px 40px', textAlign: 'center' }}>
          <Empty 
            description={
              <Text style={{ color: '#94a3b8' }}>
                Нет данных для отображения
              </Text>
            } 
          />
        </div>
      )}
    </Modal>
  );
};
