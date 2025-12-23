import { Typography, Tag } from 'antd';
import { DollarOutlined, CodeOutlined, CalendarOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;

interface ParsedResume {
  name?: string;
  position?: string;
  salary?: string;
  skills?: string[];
  experience?: Array<{
    company: string;
    position: string;
    period: string;
    duration?: string;
    description?: string;
    achievements?: string[];
  }>;
  about?: string;
}

const parseResume = (content: string): ParsedResume => {
  const parsed: ParsedResume = {};
  const lines = content.split('\n').map(l => l.trim()).filter(l => l);

  // Парсинг имени (первая строка, обычно имя и фамилия)
  if (lines.length > 0) {
    const firstLine = lines[0];
    // Если первая строка не содержит двоеточие и не начинается с ключевых слов
    if (!firstLine.includes(':') && !firstLine.match(/^(Зарплата|Навыки|Опыт|О себе)/i)) {
      parsed.name = firstLine;
    }
  }

  // Парсинг должности (обычно вторая строка или после имени)
  let currentIndex = parsed.name ? 1 : 0;
  if (lines[currentIndex] && !lines[currentIndex].includes(':') && !lines[currentIndex].match(/^\d/)) {
    parsed.position = lines[currentIndex];
    currentIndex++;
  }

  // Парсинг зарплаты
  const salaryMatch = content.match(/Зарплата:\s*(\d+)\s*(\w+)/i);
  if (salaryMatch) {
    parsed.salary = `${salaryMatch[1]} ${salaryMatch[2]}`;
  }

  // Парсинг навыков
  const skillsMatch = content.match(/Навыки:\s*([^\n]+)/i);
  if (skillsMatch) {
    parsed.skills = skillsMatch[1]
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }

  // Парсинг опыта работы
  parsed.experience = [];
  const experienceSection = content.match(/Опыт работы:([\s\S]*?)(?=О себе:|$)/i);
  if (experienceSection) {
    const expText = experienceSection[1];
    
    // Разделяем на отдельные места работы по паттерну "Компания - Должность" или просто "Компания"
    // Используем более гибкий паттерн для разделения
    const jobPattern = /([^\n]+?)\s*-\s*([^\n]+?)\n(\d{4}-\d{2}-\d{2}(?:\s*-\s*\d{4}-\d{2}-\d{2})?)\s*(?:\(([^)]+)\))?/g;
    let match;
    const jobs: Array<{ company: string; position: string; period: string; duration?: string; text: string }> = [];
    
    // Сначала находим все заголовки работ
    const allMatches: Array<{ start: number; end: number; company: string; position: string; period: string; duration?: string }> = [];
    while ((match = jobPattern.exec(expText)) !== null) {
      allMatches.push({
        start: match.index,
        end: match.index + match[0].length,
        company: match[1].trim(),
        position: match[2].trim(),
        period: match[3].trim(),
        duration: match[4]?.trim(),
      });
    }
    
    // Если не нашли через паттерн, пробуем более простой способ
    if (allMatches.length === 0) {
      const lines = expText.split('\n').map(l => l.trim()).filter(l => l);
      let i = 0;
      while (i < lines.length) {
        // Ищем строку с форматом "Компания - Должность"
        const headerMatch = lines[i].match(/^(.+?)\s*-\s*(.+)$/);
        if (headerMatch) {
          const company = headerMatch[1].trim();
          const position = headerMatch[2].trim();
          i++;
          
          // Ищем дату на следующей строке
          let period = '';
          let duration = '';
          if (i < lines.length && lines[i].match(/^\d{4}-\d{2}-\d{2}/)) {
            const periodLine = lines[i];
            period = periodLine.replace(/\s*\([^)]+\)\s*$/, '').trim();
            const durationMatch = periodLine.match(/\(([^)]+)\)/);
            if (durationMatch) {
              duration = durationMatch[1].trim();
            }
            i++;
          }
          
          // Собираем текст до следующей работы или конца
          const jobTextLines: string[] = [];
          while (i < lines.length && !lines[i].match(/^[А-ЯЁ][а-яё\s]+?\s*-\s*[А-ЯЁ]/)) {
            jobTextLines.push(lines[i]);
            i++;
          }
          
          const jobText = jobTextLines.join('\n');
          jobs.push({ company, position, period, duration, text: jobText });
        } else {
          i++;
        }
      }
    } else {
      // Обрабатываем найденные работы
      for (let idx = 0; idx < allMatches.length; idx++) {
        const current = allMatches[idx];
        const next = allMatches[idx + 1];
        const start = current.end;
        const end = next ? next.start : expText.length;
        const jobText = expText.substring(start, end).trim();
        jobs.push({ ...current, text: jobText });
      }
    }
    
    // Парсим каждую работу
    jobs.forEach(job => {
      const lines = job.text.split('\n').map(l => l.trim()).filter(l => l);
      
      const descriptionLines: string[] = [];
      const achievements: string[] = [];
      let inAchievements = false;
      let currentAchievement = '';

      for (const line of lines) {
        // Пропускаем пустые строки
        if (!line) continue;
        
        // Проверяем, начинается ли секция достижений
        if (line.match(/^(Основные задачи и достижения|Основные задачи|Достижения|Задачи):/i)) {
          inAchievements = true;
          continue;
        }

        // Если строка начинается с маркера списка
        if (line.match(/^[•\-\*]\s*(.+)/)) {
          if (currentAchievement) {
            achievements.push(currentAchievement.trim());
          }
          const achievementMatch = line.match(/^[•\-\*]\s*(.+)/);
          if (achievementMatch) {
            currentAchievement = achievementMatch[1].trim();
          }
          inAchievements = true;
        } else if (inAchievements && line.length > 0) {
          // Продолжение достижения (многострочное)
          if (currentAchievement) {
            currentAchievement += ' ' + line;
          } else {
            achievements.push(line);
          }
        } else if (line.length > 0) {
          // Обычное описание
          descriptionLines.push(line);
        }
      }
      
      // Добавляем последнее достижение
      if (currentAchievement) {
        achievements.push(currentAchievement.trim());
      }

      parsed.experience.push({
        company: job.company,
        position: job.position,
        period: job.period,
        duration: job.duration,
        description: descriptionLines.join(' '),
        achievements: achievements.length > 0 ? achievements : undefined,
      });
    });
  }

  // Парсинг "О себе"
  // Ищем "О себе:" и берем весь текст до конца (не останавливаемся на "Для связи", так как это часть блока)
  let aboutMatch = content.match(/О себе:\s*([\s\S]*?)$/i);
  if (!aboutMatch) {
    aboutMatch = content.match(/О себе\s*:?\s*([\s\S]*?)$/i);
  }
  
  if (aboutMatch) {
    // Берем весь текст после "О себе:" до конца
    parsed.about = aboutMatch[1].trim();
  } else {
    // Если не нашли через паттерн, ищем после опыта работы
    const lines = content.split('\n').map(l => l.trim());
    let foundAboutStart = false;
    const aboutLines: string[] = [];
    let lastExpIndex = -1;
    
    // Находим индекс последнего места работы
    for (let i = lines.length - 1; i >= 0; i--) {
      if (lines[i].match(/^\w+\s*-\s*\w+/) && lines[i].includes('-')) {
        lastExpIndex = i;
        break;
      }
    }
    
    // Ищем "О себе" после опыта работы
    for (let i = lastExpIndex + 1; i < lines.length; i++) {
      const line = lines[i];
      
      // Пропускаем пустые строки в начале
      if (!foundAboutStart && !line) continue;
      
      // Пропускаем строки опыта работы
      if (line.match(/^\w+\s*-\s*\w+/) || line.match(/^\d{4}-\d{2}-\d{2}/) || 
          line.match(/^(Основные задачи|Достижения|Задачи):/i) ||
          line.match(/^[•\-\*]/)) {
        continue;
      }
      
      // Ищем начало "О себе"
      if (line.match(/^О себе/i)) {
        foundAboutStart = true;
        const match = line.match(/^О себе\s*:?\s*(.+)/i);
        if (match && match[1] && match[1].trim()) {
          aboutLines.push(match[1].trim());
        }
        continue;
      }
      
      // Если уже нашли начало, собираем весь текст до конца
      if (foundAboutStart) {
        if (line.length > 0) {
          aboutLines.push(line);
        }
      }
    }
    
    if (aboutLines.length > 0) {
      parsed.about = aboutLines.join('\n').trim();
    }
  }

  return parsed;
};

interface ResumeContentProps {
  content: string;
}

export const ResumeContent = ({ content }: ResumeContentProps) => {
  const parsed = parseResume(content);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Имя и должность */}
      {(parsed.name || parsed.position) && (
        <div>
          {parsed.name && (
            <Title level={2} style={{ margin: 0, marginBottom: 8, fontSize: 28, fontWeight: 700 }}>
              {parsed.name}
            </Title>
          )}
          {parsed.position && (
            <Text style={{ fontSize: 18, color: '#64748b', fontWeight: 500 }}>
              {parsed.position}
            </Text>
          )}
        </div>
      )}

      {/* Зарплата */}
      {parsed.salary && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <DollarOutlined style={{ color: '#2563eb', fontSize: 16 }} />
          <Text strong style={{ fontSize: 15 }}>
            Зарплата: {parsed.salary}
          </Text>
        </div>
      )}

      {/* Навыки */}
      {parsed.skills && parsed.skills.length > 0 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <CodeOutlined style={{ color: '#2563eb', fontSize: 16 }} />
            <Text strong style={{ fontSize: 15 }}>Навыки</Text>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {parsed.skills.map((skill, index) => (
              <Tag
                key={index}
                style={{
                  borderRadius: 8,
                  padding: '4px 12px',
                  fontSize: 13,
                  background: '#eff6ff',
                  borderColor: '#bfdbfe',
                  color: '#1e40af',
                }}
              >
                {skill}
              </Tag>
            ))}
          </div>
        </div>
      )}

      {/* Опыт работы */}
      {parsed.experience && parsed.experience.length > 0 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <CalendarOutlined style={{ color: '#2563eb', fontSize: 16 }} />
            <Title level={4} style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>
              Опыт работы
            </Title>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {parsed.experience.map((exp, index) => (
              <div
                key={index}
                style={{
                  padding: '20px',
                  background: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: 12,
                }}
              >
                <div style={{ marginBottom: 12 }}>
                  <Text strong style={{ fontSize: 16, display: 'block', marginBottom: 4 }}>
                    {exp.company}
                  </Text>
                  <Text style={{ fontSize: 14, color: '#64748b', display: 'block', marginBottom: 4 }}>
                    {exp.position}
                  </Text>
                  {exp.period && (
                    <Text style={{ fontSize: 13, color: '#94a3b8' }}>
                      {exp.period}
                      {exp.duration && ` (${exp.duration})`}
                    </Text>
                  )}
                </div>

                {exp.description && (
                  <Paragraph style={{ marginBottom: exp.achievements ? 12 : 0, fontSize: 14, lineHeight: 1.7 }}>
                    {exp.description}
                  </Paragraph>
                )}

                {exp.achievements && exp.achievements.length > 0 && (
                  <div>
                    <Text strong style={{ fontSize: 13, color: '#475569', display: 'block', marginBottom: 8 }}>
                      Основные задачи и достижения:
                    </Text>
                    <ul style={{ margin: 0, paddingLeft: 20, fontSize: 14, lineHeight: 1.8 }}>
                      {exp.achievements.map((achievement, idx) => (
                        <li key={idx} style={{ marginBottom: 8, color: '#334155' }}>
                          {achievement}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* О себе */}
      {parsed.about && parsed.about.trim().length > 0 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <InfoCircleOutlined style={{ color: '#2563eb', fontSize: 16 }} />
            <Title level={4} style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>
              О себе
            </Title>
          </div>
          <div
            style={{
              padding: '20px',
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: 12,
            }}
          >
            <Paragraph style={{ fontSize: 14, lineHeight: 1.8, color: '#334155', whiteSpace: 'pre-wrap', margin: 0 }}>
              {parsed.about}
            </Paragraph>
          </div>
        </div>
      )}

      {/* Если ничего не распарсилось, показываем оригинальный текст */}
      {!parsed.name && !parsed.position && !parsed.salary && !parsed.skills && !parsed.experience?.length && !parsed.about && (
        <div style={{ whiteSpace: 'pre-wrap', fontSize: 14, lineHeight: 1.8, color: '#334155' }}>
          {content}
        </div>
      )}
    </div>
  );
};

