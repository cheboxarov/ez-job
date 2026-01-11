import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Space, Spin, Alert, Breadcrumb } from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  UndoOutlined,
  DownloadOutlined,
  FilePdfOutlined
} from '@ant-design/icons';
import { getResume } from '../api/resumes';
import { ResumeEditChat } from '../components/ResumeEditChat';
import { ResumeEditPreview } from '../components/ResumeEditPreview';
import { useResumeEditStore } from '../stores/resumeEditStore';
import type { Resume } from '../types/api';
import styles from './ResumeEditPage.module.css';

export const ResumeEditPage = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    initialize,
    disconnectWebSocket,
    resetAll,
    saveDraft,
    applied_patches,
    draft_patches
  } = useResumeEditStore();

  useEffect(() => {
    if (resumeId) {
      loadResume();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [resumeId]);

  const loadResume = async () => {
    if (!resumeId) return;
    setLoading(true);
    setError(null);
    try {
      const resumeData = await getResume(resumeId);
      setResume(resumeData);
      if (resumeData.content) {
        initialize(resumeId, resumeData.content);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке резюме');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = () => {
    // TODO: Реализовать экспорт
    console.log('Export to PDF');
  };

  if (loading) {
    return (
      <div className={styles.container} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" tip="Загрузка резюме..." />
      </div>
    );
  }

  if (error && !resume) {
    return (
      <div className={styles.container} style={{ padding: '24px' }}>
        <Alert message="Ошибка загрузки" description={error} type="error" showIcon />
        <Button onClick={() => navigate('/resumes')} style={{ marginTop: 16 }}>Назад к списку</Button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerTitle}>
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate(`/resumes/${resumeId}`)}
            style={{ marginRight: 16 }}
          />
          <Breadcrumb
            items={[
              { title: <a onClick={() => navigate('/resumes')}>Мои резюме</a> },
              { title: <a onClick={() => navigate(`/resumes/${resumeId}`)}>{resume?.title || 'Резюме'}</a> },
              { title: 'Редактирование' },
            ]}
          />
        </div>

        <div className={styles.headerActions}>
           <Space>
             <Button 
               icon={<UndoOutlined />} 
               onClick={resetAll}
               disabled={applied_patches.length === 0}
             >
               Сброс
             </Button>
             <Button icon={<SaveOutlined />} onClick={saveDraft}>
               Сохранить
             </Button>
             <Button icon={<FilePdfOutlined />} onClick={handleExportPdf}>
               Экспорт PDF
             </Button>
           </Space>
        </div>
      </header>

      {/* Main Grid */}
      <main className={styles.grid}>
        <div style={{ height: '100%', overflow: 'hidden' }}> {/* Added overflow: hidden */}
           <ResumeEditChat />
        </div>
        <div style={{ height: '100%', overflow: 'hidden' }}>
           <ResumeEditPreview />
        </div>
      </main>
    </div>
  );
};
