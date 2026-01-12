import { useState, useEffect, type Key } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Table,
  Typography,
  Space,
  DatePicker,
  Select,
  Input,
  Button,
  Drawer,
  Tag,
  Descriptions,
  message,
  Row,
  Col,
  Grid,
} from 'antd';
import { SearchOutlined, EyeOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { type Dayjs } from 'dayjs';
import { adminApi } from '../../api/admin';
import type { LlmCall } from '../../types/admin';
import { tokenPricingUtils } from '../../utils/tokenPricing';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

export const AdminLlmCallsPage = () => {
  const { xs } = Grid.useBreakpoint();
  const [searchParams, setSearchParams] = useSearchParams();
  const [calls, setCalls] = useState<LlmCall[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedCall, setSelectedCall] = useState<LlmCall | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<Key[]>([]);
  const [selectedRows, setSelectedRows] = useState<LlmCall[]>([]);

  // Filters
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null]>([null, null]);
  const [userId, setUserId] = useState<string>('');
  const [agentName, setAgentName] = useState<string>('');
  const [status, setStatus] = useState<string>('');

  // Читаем user_id из query параметров при монтировании и применяем фильтр
  useEffect(() => {
    const userIdFromQuery = searchParams.get('user_id');
    if (userIdFromQuery) {
      setUserId(userIdFromQuery);
      // Фильтр применится автоматически через loadCalls в следующем useEffect
    }
  }, [searchParams.get('user_id')]);

  useEffect(() => {
    loadCalls();
  }, [page, pageSize, userId]);

  const loadCalls = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
      };

      if (dateRange[0] && dateRange[1]) {
        params.start_date = dateRange[0].toISOString();
        params.end_date = dateRange[1].toISOString();
      }
      if (userId) params.user_id = userId;
      if (agentName) params.agent_name = agentName;
      if (status) params.status = status;

      const response = await adminApi.getLlmCalls(params);
      setCalls(response.items);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Ошибка загрузки вызовов LLM');
    } finally {
      setLoading(false);
    }
  };

  const handleViewCall = (call: LlmCall) => {
    setSelectedCall(call);
    setDrawerVisible(true);
  };

  const handleFilter = () => {
    setPage(1);
    loadCalls();
  };

  const handleCopySelected = async () => {
    if (selectedRows.length === 0) return;
    const payload = selectedRows.map((call) => ({
      id: call.id,
      call_id: call.call_id,
      attempt_number: call.attempt_number,
      agent_name: call.agent_name,
      model: call.model,
      user_id: call.user_id,
      status: call.status,
      temperature: call.temperature,
      response_format: call.response_format,
      duration_ms: call.duration_ms,
      prompt_tokens: call.prompt_tokens,
      completion_tokens: call.completion_tokens,
      total_tokens: call.total_tokens,
      response_size_bytes: call.response_size_bytes,
      cost_usd: call.cost_usd,
      context: call.context,
      created_at: call.created_at,
      error_type: call.error_type,
      error_message: call.error_message,
      prompt: call.prompt,
      response: call.response,
    }));
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
      message.success(`Скопировано вызовов: ${selectedRows.length}`);
    } catch (error) {
      console.error('Ошибка копирования:', error);
      message.error('Не удалось скопировать данные');
    }
  };

  const columns: ColumnsType<LlmCall> = [
    {
      title: 'Дата',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm:ss'),
      sorter: true,
    },
    {
      title: 'Агент',
      dataIndex: 'agent_name',
      key: 'agent_name',
    },
    {
      title: 'Модель',
      dataIndex: 'model',
      key: 'model',
    },
    {
      title: 'Пользователь',
      dataIndex: 'user_id',
      key: 'user_id',
      render: (userId: string | null) => userId || '-',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>{status}</Tag>
      ),
    },
    {
      title: 'Токены',
      key: 'tokens',
      render: (_: any, record: LlmCall) =>
        record.total_tokens ? record.total_tokens.toLocaleString() : '-',
    },
    {
      title: 'Стоимость',
      key: 'cost',
      render: (_: any, record: LlmCall) => {
        if (record.cost_usd !== null && record.cost_usd !== undefined) {
          return tokenPricingUtils.formatCost(record.cost_usd);
        }
        return '—';
      },
    },
    {
      title: 'Длительность',
      dataIndex: 'duration_ms',
      key: 'duration_ms',
      render: (ms: number | null) => (ms ? `${(ms / 1000).toFixed(2)}s` : '-'),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: LlmCall) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewCall(record)}
        >
          Просмотр
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: xs ? '0 16px' : '0 24px' }}>
      <Title level={2}>LLM вызовы</Title>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <RangePicker
              value={dateRange}
              onChange={(dates) => setDateRange(dates as [Dayjs | null, Dayjs | null])}
              showTime
              format="DD.MM.YYYY HH:mm"
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Input
              placeholder="ID пользователя"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Input
              placeholder="Агент"
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Select
              placeholder="Статус"
              value={status || undefined}
              onChange={setStatus}
              allowClear
              style={{ width: '100%' }}
            >
              <Select.Option value="success">Успех</Select.Option>
              <Select.Option value="error">Ошибка</Select.Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Button type="primary" icon={<SearchOutlined />} onClick={handleFilter} style={{ width: '100%' }}>
              Применить фильтры
            </Button>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Button
              onClick={handleCopySelected}
              disabled={selectedRows.length === 0}
              style={{ width: '100%' }}
            >
              Скопировать выбранные
            </Button>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={calls}
          loading={loading}
          rowKey="id"
          rowSelection={{
            selectedRowKeys,
            onChange: (keys, rows) => {
              setSelectedRowKeys(keys);
              setSelectedRows(rows);
            },
          }}
          scroll={{ x: true }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Всего: ${total}`,
            onChange: (newPage, newPageSize) => {
              setPage(newPage);
              setPageSize(newPageSize);
            },
          }}
        />
      </Space>

      <Drawer
        title="Детали вызова LLM"
        placement="right"
        width={xs ? '100%' : '90%'}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        styles={{
          body: {
            padding: xs ? '16px' : '24px',
          },
        }}
      >
        {selectedCall && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions column={1} bordered>
              <Descriptions.Item label="ID">{selectedCall.id}</Descriptions.Item>
              <Descriptions.Item label="Call ID">{selectedCall.call_id}</Descriptions.Item>
              <Descriptions.Item label="Агент">{selectedCall.agent_name}</Descriptions.Item>
              <Descriptions.Item label="Модель">{selectedCall.model}</Descriptions.Item>
              <Descriptions.Item label="Пользователь">
                {selectedCall.user_id || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color={selectedCall.status === 'success' ? 'green' : 'red'}>
                  {selectedCall.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Температура">{selectedCall.temperature}</Descriptions.Item>
              <Descriptions.Item label="Токены промпта">
                {selectedCall.prompt_tokens?.toLocaleString() || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Токены ответа">
                {selectedCall.completion_tokens?.toLocaleString() || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Всего токенов">
                {selectedCall.total_tokens?.toLocaleString() || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Стоимость">
                {selectedCall.cost_usd !== null && selectedCall.cost_usd !== undefined
                  ? tokenPricingUtils.formatCost(selectedCall.cost_usd)
                  : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Длительность">
                {selectedCall.duration_ms ? `${(selectedCall.duration_ms / 1000).toFixed(2)}s` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Дата создания">
                {dayjs(selectedCall.created_at).format('DD.MM.YYYY HH:mm:ss')}
              </Descriptions.Item>
              {selectedCall.error_type && (
                <Descriptions.Item label="Тип ошибки">{selectedCall.error_type}</Descriptions.Item>
              )}
              {selectedCall.error_message && (
                <Descriptions.Item label="Сообщение об ошибке">
                  <div
                    style={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      maxWidth: '100%',
                    }}
                  >
                    {selectedCall.error_message}
                  </div>
                </Descriptions.Item>
              )}
            </Descriptions>

            <div>
              <Title level={4}>Промпт</Title>
              <pre
                style={{
                  background: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  overflowX: 'auto',
                  overflowY: 'auto',
                  maxHeight: '400px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  wordWrap: 'break-word',
                  overflowWrap: 'anywhere',
                  maxWidth: '100%',
                  fontSize: '12px',
                  lineHeight: '1.5',
                }}
              >
                {JSON.stringify(selectedCall.prompt, null, 2)}
              </pre>
            </div>

            <div>
              <Title level={4}>Ответ</Title>
              <pre
                style={{
                  background: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  overflowX: 'auto',
                  overflowY: 'auto',
                  maxHeight: '500px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  wordWrap: 'break-word',
                  overflowWrap: 'anywhere',
                  maxWidth: '100%',
                  fontSize: '12px',
                  lineHeight: '1.5',
                }}
              >
                {selectedCall.response}
              </pre>
            </div>
          </Space>
        )}
      </Drawer>
    </div>
  );
};
