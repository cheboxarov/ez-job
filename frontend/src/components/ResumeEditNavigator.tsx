import { useEffect, useState } from 'react';
import styles from '../pages/ResumeEditPage.module.css';

interface ResumeEditNavigatorProps {
  text: string;
  patches: any[];
  onSectionClick: (section: string, position: number) => void;
}

interface Section {
  id: string;
  title: string;
  position: number;
  patchCount: number;
}

const SECTION_KEYWORDS = [
  { id: 'header', title: 'Заголовок', keywords: ['резюме', 'resume'] },
  { id: 'contacts', title: 'Контакты', keywords: ['контакты', 'contacts', 'email', 'телефон'] },
  { id: 'position', title: 'Должность', keywords: ['желаемая должность', 'position'] },
  { id: 'experience', title: 'Опыт работы', keywords: ['опыт работы', 'experience', 'work history'] },
  { id: 'education', title: 'Образование', keywords: ['образование', 'education'] },
  { id: 'skills', title: 'Навыки', keywords: ['навыки', 'skills', 'ключевые навыки'] },
  { id: 'about', title: 'О себе', keywords: ['о себе', 'about', 'обо мне'] },
];

export const ResumeEditNavigator = ({ text, patches, onSectionClick }: ResumeEditNavigatorProps) => {
  const [sections, setSections] = useState<Section[]>([]);
  const [activeSection, setActiveSection] = useState<string>('');

  useEffect(() => {
    if (!text) return;

    const foundSections: Section[] = [];
    const lines = text.split('\n');
    let currentPos = 0;

    // Очень простой парсер: ищем ключевые слова в начале строк или в строках CAPS
    // Более надежный способ - если бы у нас была структура JSON, но у нас текст.
    // Попробуем просто найти первые вхождения ключевых слов
    
    // Всегда добавляем "Начало"
    foundSections.push({ id: 'top', title: 'Начало', position: 0, patchCount: 0 });

    SECTION_KEYWORDS.forEach(sec => {
      // Ищем первое вхождение любого из ключевых слов секции
      // Игнорируем регистр
      let minPos = -1;
      
      sec.keywords.forEach(keyword => {
        const pos = text.toLowerCase().indexOf(keyword.toLowerCase());
        if (pos !== -1) {
          if (minPos === -1 || pos < minPos) {
            minPos = pos;
          }
        }
      });

      if (minPos !== -1 && minPos > 100) { // Игнорируем если слишком близко к началу (кроме спец случаев)
         // Проверяем, не дублируется ли уже (бывает такое)
         foundSections.push({
           id: sec.id,
           title: sec.title,
           position: minPos,
           patchCount: 0
         });
      }
    });

    // Сортируем по позиции
    foundSections.sort((a, b) => a.position - b.position);

    // Подсчет патчей для каждой секции
    // Патч относится к секции, если его позиция находится между началом этой секции и началом следующей
    const patchesWithPos = patches.map(p => {
       // Грубая оценка позиции патча (можно взять логику из Preview)
       // Пока просто используем indexOf old_text
       const pos = text.indexOf(p.old_text);
       return { ...p, pos: pos !== -1 ? pos : 0 };
    });

    foundSections.forEach((section, idx) => {
      const nextSectionPos = idx < foundSections.length - 1 ? foundSections[idx + 1].position : text.length;
      
      const count = patchesWithPos.filter(p => p.pos >= section.position && p.pos < nextSectionPos).length;
      section.patchCount = count;
    });

    setSections(foundSections);
  }, [text, patches]);

  return (
    <div className={styles.navigator}>
      <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Навигация
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {sections.map((section) => (
          <div
            key={section.id}
            className={`${styles.navItem} ${activeSection === section.id ? styles.navItemActive : ''}`}
            onClick={() => {
              setActiveSection(section.id);
              onSectionClick(section.id, section.position);
            }}
          >
            <span>{section.title}</span>
            {section.patchCount > 0 && (
              <span className={styles.patchBadge}>{section.patchCount}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
