import { useRef } from 'react';
import { Button, Space, Typography } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { useResumeEditStore } from '../stores/resumeEditStore';
import styles from '../pages/ResumeEditPage.module.css';

const { Text } = Typography;

export const ResumeEditPreview = () => {
  const { original_resume_text, current_resume_text, draft_patches, applyPatch, rejectPatch } = useResumeEditStore();
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Найти позицию патча в тексте
  const findPatchPosition = (patch: typeof draft_patches[0], textToSearch: string) => {
    // Используем только номера строк для определения позиции
    const lines = textToSearch.split('\n');
    
    // Конвертируем из 1-based (от бэкенда) в 0-based (для массивов)
    const startLine0 = patch.start_line - 1;
    const endLine0 = patch.end_line - 1;

    // Проверка валидности номеров строк
    if (startLine0 < 0 || endLine0 >= lines.length || startLine0 > endLine0) {
      return null;
    }

    // Вычисляем позицию начала патча в тексте
    let startPos = 0;
    for (let i = 0; i < startLine0 && i < lines.length; i++) {
      startPos += lines[i].length + 1; // +1 для символа переноса строки
    }

    // Для insert позиция - это конец строки start_line
    if (patch.type === 'insert') {
      const insertAfterLine = lines[startLine0];
      const endPos = startPos + insertAfterLine.length;
      return { start: endPos, end: endPos };
    }

    // Для replace и delete вычисляем позицию конца
    let endPos = startPos;
    for (let i = startLine0; i <= endLine0 && i < lines.length; i++) {
      endPos += lines[i].length;
      if (i < endLine0) {
        endPos += 1; // +1 для символа переноса строки между строками
      }
    }

    return { start: startPos, end: endPos };
  };

  const renderContent = () => {
    const baseText = current_resume_text || original_resume_text;
    
    // Подготовка данных патчей
    const patchesWithPositions = draft_patches
      .map((patch) => {
        let position = findPatchPosition(patch, baseText);
        if (!position && baseText !== original_resume_text) {
             position = findPatchPosition(patch, original_resume_text);
        }
        return { patch, position };
      })
      .sort((a, b) => (a.position?.start || 0) - (b.position?.start || 0));

    const foundPatches = patchesWithPositions.filter((item) => item.position !== null);
    const notFoundPatches = patchesWithPositions.filter((item) => item.position === null);

    const renderNotFoundPatches = () => {
        if (notFoundPatches.length === 0) return null;
        return (
             <div style={{ marginTop: 24, padding: 16, backgroundColor: '#fef2f2', borderRadius: 8, border: '1px solid #fee2e2' }}>
              <Text strong style={{ display: 'block', marginBottom: 12, color: '#b91c1c' }}>
                Не удалось автоматически найти место для изменений:
              </Text>
              {notFoundPatches.map(({ patch }) => (
                <div key={patch.id} style={{ marginBottom: 16, padding: 12, backgroundColor: 'white', borderRadius: 6, border: '1px solid #e5e7eb' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                    {patch.reason}
                  </Text>
                  <div style={{ marginBottom: 8 }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>Искали текст:</Text>
                    <div style={{ 
                        background: '#f3f4f6', padding: 8, borderRadius: 4, marginTop: 4, 
                        fontSize: 12, fontFamily: 'monospace', color: '#374151' 
                    }}>
                    {(patch.old_text || '').substring(0, 100)}
                    {(patch.old_text || '').length > 100 ? '...' : ''}
                    </div>
                  </div>
                  <Space style={{ marginTop: 8 }}>
                    <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => applyPatch(patch.id)}>Принять</Button>
                    <Button danger size="small" icon={<CloseOutlined />} onClick={() => rejectPatch(patch.id)}>Отклонить</Button>
                  </Space>
                </div>
              ))}
            </div>
        );
    };

    // INLINE MODE (единственный режим)
    const parts: Array<{ type: 'text' | 'old' | 'new'; content: string; patchId?: string }> = [];
    let lastPos = 0;

    foundPatches.forEach(({ patch, position }) => {
      if (!position) return;
      
      if (position.start > lastPos) {
        parts.push({ type: 'text', content: baseText.slice(lastPos, position.start) });
      }

      if (patch.type === 'replace' || patch.type === 'delete') {
        parts.push({ type: 'old', content: patch.old_text, patchId: patch.id });
      }
      if (patch.type === 'replace' || patch.type === 'insert') {
        parts.push({ type: 'new', content: patch.new_text || '', patchId: patch.id });
      }
      lastPos = position.end; 
    });

    if (lastPos < baseText.length) {
      parts.push({ type: 'text', content: baseText.slice(lastPos) });
    }

    return (
      <div style={{ fontSize: 14, lineHeight: 1.8 }}>
        {parts.map((part, index) => {
          if (part.type === 'text') return <span key={index} style={{color: 'var(--text-main)', whiteSpace: 'pre-wrap'}}>{part.content}</span>;
          if (part.type === 'old') return (
             <span key={index} style={{
                 background: '#fee2e2', color: '#b91c1c', textDecoration: 'line-through', 
                 padding: '0 4px', borderRadius: 4, margin: '0 2px'
             }}>{part.content}</span>
          );
          if (part.type === 'new') return (
             <span key={index} style={{
                 background: '#dcfce7', color: '#15803d', padding: '0 4px', borderRadius: 4, margin: '0 2px',
                 borderBottom: '2px solid #22c55e', position: 'relative', display: 'inline-block'
             }}>
                 {part.content}
                 <div style={{position: 'absolute', top: -32, right: 0, display: 'flex', gap: 4, background: 'white', padding: 4, borderRadius: 6, boxShadow: '0 4px 6px rgba(0,0,0,0.1)', zIndex: 10, border: '1px solid #e5e7eb'}}>
                      <Button 
                         type="text" 
                         size="small" 
                         icon={<CheckOutlined />} 
                         onClick={() => applyPatch(part.patchId!)} 
                         style={{ color: '#16a34a', minWidth: 24, height: 24, padding: 0 }}
                      />
                      <Button 
                         type="text" 
                         size="small" 
                         icon={<CloseOutlined />} 
                         onClick={() => rejectPatch(part.patchId!)} 
                         style={{ color: '#dc2626', minWidth: 24, height: 24, padding: 0 }} 
                      />
                 </div>
             </span>
          );
          return null;
        })}
        {renderNotFoundPatches()}
      </div>
    );
  };

  return (
    <div className={styles.previewSection}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
          <div className={styles.previewContent} ref={scrollContainerRef}>
             {renderContent()}
          </div>
      </div>
    </div>
  );
};
