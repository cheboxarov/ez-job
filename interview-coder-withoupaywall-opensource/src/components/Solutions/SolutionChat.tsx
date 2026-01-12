import React, { useState, useRef, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useToast } from "../../contexts/toast"

interface Message {
  role: "user" | "assistant"
  content: string
}

interface SolutionChatProps {
  solutionData: string | null
}

export const SolutionChat: React.FC<SolutionChatProps> = ({ solutionData }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { t } = useTranslation()
  const { showToast } = useToast()

  // Автопрокрутка к новым сообщениям
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      role: "user",
      content: inputValue.trim()
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await window.electronAPI.sendChatMessage(
        userMessage.content,
        solutionData || undefined
      )
      
      if (response.success && response.response) {
        const assistantMessage: Message = {
          role: "assistant",
          content: response.response
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        showToast(
          t("common.errorTitle"),
          response.error || t("chat.error"),
          "error"
        )
      }
    } catch (error) {
      console.error("Error sending chat message:", error)
      showToast(
        t("common.errorTitle"),
        t("chat.error"),
        "error"
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="mt-4 space-y-2">
      <h2 className="text-[13px] font-medium text-white tracking-wide">
        {t("chat.title")}
      </h2>
      <div className="bg-white/5 rounded-md border border-white/10 overflow-hidden flex flex-col" style={{ maxHeight: "400px" }}>
        {/* Список сообщений */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-400 text-sm py-8">
              {t("chat.placeholder")}
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-[13px] leading-relaxed ${
                    message.role === "user"
                      ? "bg-blue-500/20 text-blue-100"
                      : "bg-white/10 text-gray-100"
                  }`}
                >
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {/* Индикатор загрузки */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white/10 text-gray-100 rounded-lg px-3 py-2 text-[13px]">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                  <span>{t("chat.thinking")}</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Поле ввода */}
        <div className="border-t border-white/10 p-3">
          <div className="flex gap-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t("chat.placeholder")}
              disabled={isLoading}
              className="flex-1 bg-white/5 border border-white/10 rounded-md px-3 py-2 text-[13px] text-white placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500/50 resize-none"
              rows={2}
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-200 rounded-md text-[13px] font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {t("chat.send")}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
