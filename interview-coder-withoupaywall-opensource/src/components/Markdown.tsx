import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { dracula } from "react-syntax-highlighter/dist/esm/styles/prism"

type MarkdownProps = {
  content: string
  className?: string
}

export function Markdown({ content, className }: MarkdownProps) {
  return (
    <ReactMarkdown
      className={className}
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="mb-2 text-sm font-semibold">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="mb-2 text-sm font-semibold">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide">
            {children}
          </h3>
        ),
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
        ul: ({ children }) => (
          <ul className="mb-2 list-disc pl-4 last:mb-0">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="mb-2 list-decimal pl-4 last:mb-0">{children}</ol>
        ),
        li: ({ children }) => <li className="mb-1 last:mb-0">{children}</li>,
        blockquote: ({ children }) => (
          <blockquote className="mb-2 border-l-2 border-white/20 pl-3 text-white/70 last:mb-0">
            {children}
          </blockquote>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            className="text-blue-300 underline underline-offset-2 transition hover:text-blue-200"
            onClick={(event) => {
              if (!href) return
              event.preventDefault()
              window.electronAPI?.openLink?.(href)
            }}
          >
            {children}
          </a>
        ),
        code: ({ inline, className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || "")
          if (!inline) {
            return (
              <div className="my-2">
                <SyntaxHighlighter
                  style={dracula}
                  language={match?.[1]}
                  PreTag="div"
                  wrapLongLines
                  customStyle={{
                    margin: 0,
                    padding: "0.6rem",
                    backgroundColor: "rgba(7, 10, 14, 0.6)",
                    borderRadius: "0.5rem",
                    fontSize: "0.75rem",
                    lineHeight: "1.35"
                  }}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              </div>
            )
          }
          return (
            <code
              className="rounded bg-white/10 px-1 py-0.5 text-[0.85em]"
              {...props}
            >
              {children}
            </code>
          )
        }
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
