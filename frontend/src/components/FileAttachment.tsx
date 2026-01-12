import { Button, Typography } from 'antd';
import {
  DownloadOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  FileOutlined,
  FilePdfOutlined,
  FilePptOutlined,
  FileTextOutlined,
  FileWordOutlined,
} from '@ant-design/icons';
import type { ChatFile } from '../types/api';

const { Text } = Typography;

interface FileAttachmentProps {
  file: ChatFile;
  variant?: 'user' | 'assistant';
}

const getFileIcon = (contentType: string, title: string, color: string) => {
  const signature = `${contentType} ${title}`.toLowerCase();
  if (signature.includes('pdf')) {
    return <FilePdfOutlined style={{ color }} />;
  }
  if (signature.includes('word') || signature.includes('document') || signature.includes('.doc')) {
    return <FileWordOutlined style={{ color }} />;
  }
  if (signature.includes('excel') || signature.includes('sheet') || signature.includes('.xls')) {
    return <FileExcelOutlined style={{ color }} />;
  }
  if (signature.includes('powerpoint') || signature.includes('presentation') || signature.includes('.ppt')) {
    return <FilePptOutlined style={{ color }} />;
  }
  if (signature.includes('image') || signature.includes('.png') || signature.includes('.jpg')) {
    return <FileImageOutlined style={{ color }} />;
  }
  if (signature.includes('text') || signature.includes('.txt')) {
    return <FileTextOutlined style={{ color }} />;
  }
  return <FileOutlined style={{ color }} />;
};

export const FileAttachment = ({ file, variant = 'assistant' }: FileAttachmentProps) => {
  const isUser = variant === 'user';
  const iconColor = isUser ? '#e2e8f0' : '#475569';

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '10px 12px',
        borderRadius: 12,
        background: isUser ? 'rgba(255,255,255,0.18)' : '#f1f5f9',
        border: isUser ? '1px solid rgba(255,255,255,0.2)' : '1px solid #e2e8f0',
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: 8,
          background: isUser ? 'rgba(255,255,255,0.2)' : '#e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {getFileIcon(file.content_type || '', file.title || '', iconColor)}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <Text
          ellipsis
          style={{
            display: 'block',
            color: isUser ? '#ffffff' : '#0f172a',
            fontWeight: 500,
          }}
        >
          {file.title || 'Файл'}
        </Text>
        <Text
          style={{
            fontSize: 12,
            color: isUser ? 'rgba(255,255,255,0.7)' : '#64748b',
          }}
        >
          {file.content_type || 'application/octet-stream'}
        </Text>
      </div>
      <Button
        type="link"
        icon={<DownloadOutlined />}
        href={file.url}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: isUser ? '#ffffff' : '#2563eb', padding: 0 }}
      >
        Скачать
      </Button>
    </div>
  );
};
