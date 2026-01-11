import type { CSSProperties } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';
import styles from './MarkdownMessage.module.css';

type MarkdownMessageVariant = 'assistant' | 'user';

interface MarkdownMessageProps {
  content: string;
  variant?: MarkdownMessageVariant;
  className?: string;
}

export const MarkdownMessage = ({
  content,
  variant = 'assistant',
  className,
}: MarkdownMessageProps) => {
  const isUser = variant === 'user';
  const styleVars: CSSProperties = {
    '--md-link-color': isUser ? '#dbeafe' : '#2563eb',
    '--md-link-decoration': isUser ? 'rgba(255, 255, 255, 0.7)' : 'rgba(37, 99, 235, 0.45)',
    '--md-inline-code-bg': isUser ? 'rgba(255, 255, 255, 0.18)' : 'rgba(15, 23, 42, 0.08)',
    '--md-code-bg': isUser ? 'rgba(255, 255, 255, 0.16)' : 'rgba(15, 23, 42, 0.06)',
    '--md-quote-border': isUser ? 'rgba(255, 255, 255, 0.4)' : 'rgba(37, 99, 235, 0.35)',
    '--md-hr-color': isUser ? 'rgba(255, 255, 255, 0.3)' : 'rgba(148, 163, 184, 0.6)',
    '--md-table-border': isUser ? 'rgba(255, 255, 255, 0.25)' : 'rgba(148, 163, 184, 0.4)',
    '--md-table-header': isUser ? 'rgba(255, 255, 255, 0.12)' : 'rgba(15, 23, 42, 0.04)',
  };

  return (
    <div className={[styles.markdown, className].filter(Boolean).join(' ')} style={styleVars}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          a: ({ children, ...props }) => (
            <a
              {...props}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(event) => event.stopPropagation()}
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
