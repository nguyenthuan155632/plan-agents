'use client'

import { memo } from 'react'
import TypewriterText from './TypewriterText'
import AIMessage from './AIMessage'
import TypewriterAIMessage from './TypewriterAIMessage'

interface MessageItemProps {
  message: {
    id: number
    role: string
    content: string
    signal: string
    timestamp: string
  }
  shouldAnimate: boolean
  colors: {
    bg: string
    border: string
    text: string
    icon: string
  }
  onAnimationComplete: () => void
  onTypingUpdate: () => void
  formatRoleName: (role: string) => string
  getSignalBadge: (signal: string) => JSX.Element | null
}

const MessageItem = memo(function MessageItem({
  message,
  shouldAnimate,
  colors,
  onAnimationComplete,
  onTypingUpdate,
  formatRoleName,
  getSignalBadge
}: MessageItemProps) {
  return (
    <div
      className={`p-4 rounded-none ${colors.border} ${colors.bg} neo-shadow`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{colors.icon}</span>
          <span className={`font-black ${colors.text} uppercase tracking-wide`}>
            {formatRoleName(message.role)}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {getSignalBadge(message.signal)}
          <span className="text-xs text-gray-600 dark:text-gray-500 font-mono">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className={`${colors.text}`}>
        {shouldAnimate ? (
          // Use TypewriterText for Human messages (simple text)
          message.role === 'Human' ? (
            <TypewriterText
              text={message.content}
              speed={50}
              onComplete={onAnimationComplete}
              onUpdate={onTypingUpdate}
            />
          ) : (
            // Use TypewriterAIMessage for Agent messages (markdown support)
            <TypewriterAIMessage
              text={message.content}
              speed={50}
              onComplete={onAnimationComplete}
              onUpdate={onTypingUpdate}
            />
          )
        ) : (
          // Static message display with markdown
          <AIMessage content={message.content} role={message.role as 'AgentA' | 'AgentB' | 'Human'} />
        )}
      </div>
    </div>
  )
})

export default MessageItem

