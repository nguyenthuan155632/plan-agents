'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import TypewriterText from './TypewriterText'
import AIMessage from './AIMessage'
import TypewriterAIMessage from './TypewriterAIMessage'
import MessageItem from './MessageItem'

interface Message {
  id: number
  role: string
  content: string
  signal: string
  timestamp: string
}

interface ConversationViewProps {
  sessionId: string
  refreshKey: number
  onHandoverDetected?: (isWaiting: boolean) => void
}

export default function ConversationView({ sessionId, refreshKey, onHandoverDetected }: ConversationViewProps) {
  const [messages, setMessages] = useState<Message[]>([]) // All messages from backend
  const [visibleMessages, setVisibleMessages] = useState<Message[]>([]) // Messages shown to user (gradually)
  const [loading, setLoading] = useState(true)
  const [autoScroll, setAutoScroll] = useState(true)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const [isSessionActive, setIsSessionActive] = useState(false)
  const [currentlyAnimatingIndex, setCurrentlyAnimatingIndex] = useState<number>(-1)
  const [hasStartedAnimating, setHasStartedAnimating] = useState(false) // Track if animation has started for this session
  const [triggeredMessageIds, setTriggeredMessageIds] = useState<Set<number>>(new Set()) // Track which messages already triggered next turn
  const [pendingTriggerMessageId, setPendingTriggerMessageId] = useState<number | null>(null) // Message waiting to trigger next turn after animation
  const [isWaitingForNextAgent, setIsWaitingForNextAgent] = useState(false) // Show "Thinking..." indicator
  const [userRequestedInput, setUserRequestedInput] = useState(false) // User clicked "Jump In" button
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchMessages()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, refreshKey])

  // Reset when session changes
  useEffect(() => {
    setVisibleMessages([])
    setCurrentlyAnimatingIndex(-1)
    setHasStartedAnimating(false) // Reset flag for new session
    setTriggeredMessageIds(new Set()) // Reset triggered messages
    setPendingTriggerMessageId(null) // Reset pending trigger
    setIsWaitingForNextAgent(false) // Reset thinking indicator
    setUserRequestedInput(false) // Reset jump in flag
  }, [sessionId])

  // Gradually reveal messages one by one
  useEffect(() => {
    // If session is NOT active AND we haven't started animating yet, show all messages immediately (opening old conversation)
    if (!isSessionActive && !hasStartedAnimating && messages.length > 0) {
      console.log('📂 Opening completed session - showing all messages immediately')
      setVisibleMessages(messages)
      setCurrentlyAnimatingIndex(-1)
      return
    }

    // If we've shown all messages, nothing to do
    if (visibleMessages.length >= messages.length) {
      return
    }

    // If currently animating, wait for it to finish
    if (currentlyAnimatingIndex >= 0) {
      return
    }

    // Show next message (for active sessions or sessions that already started animating)
    const nextIndex = visibleMessages.length
    console.log('👀 Showing message', nextIndex + 1, 'of', messages.length)
    setVisibleMessages(messages.slice(0, nextIndex + 1))
    setCurrentlyAnimatingIndex(nextIndex) // This message will animate
    setHasStartedAnimating(true) // Mark that we've started animating this session
  }, [messages, visibleMessages, currentlyAnimatingIndex, isSessionActive, hasStartedAnimating])

  useEffect(() => {
    // Check realtime if user is near bottom before auto-scrolling
    const container = messagesContainerRef.current
    if (!container) return

    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 150

    // Only auto-scroll if user is near bottom
    if (isNearBottom) {
      scrollToBottom()
    }
  }, [visibleMessages]) // Removed autoScroll dependency

  // Auto-scroll when thinking indicator appears - but check position first
  useEffect(() => {
    if (!isWaitingForNextAgent) return

    const container = messagesContainerRef.current
    if (!container) return

    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 150

    // Only auto-scroll if user is near bottom
    if (isNearBottom) {
      scrollToBottom()
    }
  }, [isWaitingForNextAgent])

  const fetchMessages = async () => {
    try {
      const response = await fetch(`/api/messages/${sessionId}`)
      const data = await response.json()
      const newMessages = data.messages as Message[] || []
      const sessionIsActive = data.isActive || false

      setIsSessionActive(sessionIsActive)

      // Check if we just got a new message
      const gotNewMessage = newMessages.length > messages.length
      const lastNewMessage = gotNewMessage ? newMessages[newMessages.length - 1] : null

      setMessages(newMessages) // Store all messages, but don't show them all yet

      // Hide thinking indicator when new AGENT message arrives
      if (gotNewMessage && lastNewMessage && lastNewMessage.role !== 'Human') {
        console.log('🤖 New agent message arrived, hiding thinking indicator')
        setIsWaitingForNextAgent(false)
      }

      // Show thinking indicator when new HUMAN message arrives and session is active
      if (gotNewMessage && lastNewMessage && lastNewMessage.role === 'Human' && sessionIsActive) {
        console.log('👤 New human message arrived, showing thinking indicator')
        setIsWaitingForNextAgent(true)
      }

      // Reset userRequestedInput when new messages arrive (conversation continued)
      if (gotNewMessage && lastNewMessage && lastNewMessage.role === 'Human') {
        setUserRequestedInput(false)
      }

      // Check if last message has handover signal
      if (newMessages.length > 0) {
        const lastMessage = newMessages[newMessages.length - 1]
        const isWaitingForInput = (lastMessage.signal === 'handover' && sessionIsActive) || userRequestedInput
        if (onHandoverDetected) {
          onHandoverDetected(isWaitingForInput)
        }

        // If last message has CONTINUE signal and session is active, mark for trigger
        // Will actually trigger after animation completes
        // BUT: Don't trigger if user requested input
        if (lastMessage.signal === 'continue' &&
          sessionIsActive &&
          lastMessage.role !== 'Human' &&
          !triggeredMessageIds.has(lastMessage.id) &&
          !userRequestedInput) {  // Don't auto-trigger if user wants to jump in
          console.log('🔄 CONTINUE signal detected for message', lastMessage.id, ', will trigger after animation')
          setPendingTriggerMessageId(lastMessage.id)
        }
      }

    } catch (error) {
      console.error('Error fetching messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const triggerNextTurn = async (messageId: number) => {
    // Don't trigger if user requested input
    if (userRequestedInput) {
      console.log('⛔ Skipping auto-trigger - user requested input')
      return
    }

    try {
      // Mark as triggered
      setTriggeredMessageIds(prev => new Set(prev).add(messageId))
      setPendingTriggerMessageId(null)

      // Show thinking indicator
      setIsWaitingForNextAgent(true)

      // Wait a bit before triggering
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Check again if user requested input during the wait
      if (userRequestedInput) {
        console.log('⛔ User requested input during wait - canceling trigger')
        setIsWaitingForNextAgent(false)
        return
      }

      // Create a continue signal to trigger next agent turn
      console.log('🚀 Triggering next turn for session:', sessionId)
      const response = await fetch(`/api/sessions/${sessionId}/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ auto: true }),
      })

      if (!response.ok) {
        console.error('Failed to trigger next turn')
        setIsWaitingForNextAgent(false) // Hide on error
      } else {
        console.log('✅ Next turn triggered')
        // Keep showing thinking indicator until new message arrives
      }
    } catch (error) {
      console.error('Error triggering next turn:', error)
      setIsWaitingForNextAgent(false) // Hide on error
    }
  }

  const handleJumpIn = () => {
    console.log('👤 User requested to jump in!')
    setUserRequestedInput(true)
    setPendingTriggerMessageId(null) // Cancel any pending triggers
    setIsWaitingForNextAgent(false) // Hide thinking indicator
    if (onHandoverDetected) {
      onHandoverDetected(true) // Show input immediately
    }
  }

  const handleStopConversation = async () => {
    if (!confirm('Are you sure you want to stop this conversation? The agents will provide a final summary.')) {
      return
    }

    try {
      console.log('🛑 Sending stop request to agents...')
      const response = await fetch(`/api/sessions/${sessionId}/stop`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to send stop request')
      }

      const data = await response.json()
      console.log('✅', data.message)

      // Don't immediately mark as inactive - let agents respond first
      // The session will be marked as completed after agents provide summary

      // Refresh messages to show the stop request
      await fetchMessages()
    } catch (error) {
      console.error('❌ Error sending stop request:', error)
      alert('Failed to send stop request. Please try again.')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleScroll = () => {
    const container = messagesContainerRef.current
    if (!container) return

    // Check if user is near the bottom (within 100px)
    const isNearBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 100

    setAutoScroll(isNearBottom)
    setShowScrollButton(!isNearBottom)
  }

  const handleScrollToBottom = () => {
    setAutoScroll(true)
    scrollToBottom()
  }

  const formatRoleName = (role: string) => {
    switch (role) {
      case 'AgentA':
        return 'Agent A'
      case 'AgentB':
        return 'Agent B'
      case 'Human':
        return 'Human'
      default:
        return role
    }
  }

  // Wrap callbacks with useCallback to prevent re-creation
  const createAnimationCompleteHandler = useCallback((messageId: number, index: number) => {
    return () => {
      console.log('✅ Animation complete for message', index + 1, '(id:', messageId, ')')
      setCurrentlyAnimatingIndex(-1)

      if (pendingTriggerMessageId === messageId) {
        console.log('🎯 Animation completed for pending trigger message, triggering now')
        triggerNextTurn(messageId)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingTriggerMessageId])

  const handleTypingUpdate = useCallback(() => {
    const container = messagesContainerRef.current
    if (!container) return

    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 150

    if (isNearBottom) {
      scrollToBottom()
    }
  }, [])

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'AgentA':
        return {
          bg: 'bg-blue-300 dark:bg-blue-400',
          border: 'neo-border-thin',
          text: 'text-black',
          icon: '🔍'
        }
      case 'AgentB':
        return {
          bg: 'bg-purple-300 dark:bg-purple-400',
          border: 'neo-border-thin',
          text: 'text-black',
          icon: '💡'
        }
      case 'Human':
        return {
          bg: 'bg-pink-300 dark:bg-pink-400',
          border: 'neo-border-thin',
          text: 'text-black',
          icon: '👤'
        }
      default:
        return {
          bg: 'bg-gray-300 dark:bg-gray-400',
          border: 'neo-border-thin',
          text: 'text-black',
          icon: '❓'
        }
    }
  }

  const getSignalBadge = (signal: string) => {
    switch (signal) {
      case 'continue':
        return <span className="px-2 py-1 bg-blue-400 text-black border-2 border-black font-bold text-xs uppercase">→ Continue</span>
      case 'stop':
        return <span className="px-2 py-1 bg-red-400 text-black border-2 border-black font-bold text-xs uppercase">■ Stop</span>
      case 'handover':
        return <span className="px-2 py-1 bg-yellow-400 text-black border-2 border-black font-bold text-xs uppercase">✋ Handover</span>
      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-none neo-border neo-shadow p-6">
        <div className="text-gray-600 dark:text-gray-400 text-center py-8 font-bold">Loading conversation...</div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-none neo-border neo-shadow p-6 relative">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black text-black dark:text-white flex items-center uppercase tracking-tight">
          <span className="mr-3 text-3xl">💬</span>
          Conversation
        </h2>

        <div className="flex items-center space-x-3">
          {/* Jump In button - show when session is active and not already waiting for input */}
          {isSessionActive && !userRequestedInput && messages.length > 0 && messages[messages.length - 1]?.signal !== 'handover' && (
            <button
              onClick={handleJumpIn}
              className="px-4 py-2 bg-green-400 hover:bg-green-500 text-black font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide flex items-center space-x-2"
            >
              <span>✋</span>
              <span>Jump In</span>
            </button>
          )}

          {/* Stop Conversation button - show when session is active */}
          {isSessionActive && messages.length > 0 && (
            <button
              onClick={handleStopConversation}
              className="px-4 py-2 bg-red-400 hover:bg-red-500 text-black font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide flex items-center space-x-2"
            >
              <span>🛑</span>
              <span>Stop</span>
            </button>
          )}
        </div>
      </div>

      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="space-y-4 max-h-[600px] overflow-y-auto pr-2 scroll-smooth custom-scrollbar"
      >
        {visibleMessages.map((message, index) => {
          const colors = getRoleColor(message.role)
          const isLastVisibleMessage = index === visibleMessages.length - 1
          // Only animate agent messages, not human messages
          const shouldAnimate = isLastVisibleMessage &&
            currentlyAnimatingIndex === index &&
            message.role !== 'Human'

          // For human messages, complete immediately without animation
          if (message.role === 'Human' && isLastVisibleMessage && currentlyAnimatingIndex === index) {
            // Immediately mark as complete
            setTimeout(() => {
              setCurrentlyAnimatingIndex(-1)
              if (pendingTriggerMessageId === message.id) {
                triggerNextTurn(message.id)
              }
            }, 0)
          }

          return (
            <MessageItem
              key={message.id}
              message={message}
              shouldAnimate={shouldAnimate}
              colors={colors}
              onAnimationComplete={createAnimationCompleteHandler(message.id, index)}
              onTypingUpdate={handleTypingUpdate}
              formatRoleName={formatRoleName}
              getSignalBadge={getSignalBadge}
            />
          )
        })}

        {/* Show thinking indicator when waiting for next agent */}
        {isWaitingForNextAgent && (
          <div className="flex items-center space-x-3 p-4 rounded-none bg-yellow-300 dark:bg-yellow-400 neo-border-thin neo-shadow animate-pulse">
            <div className="flex space-x-1">
              <div className="w-3 h-3 bg-black rounded-none animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-3 h-3 bg-black rounded-none animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-3 h-3 bg-black rounded-none animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-black text-sm font-black uppercase">
              🤔 Thinking...
            </span>
          </div>
        )}

        {/* Show thinking indicator if there are more messages to display */}
        {isSessionActive && visibleMessages.length < messages.length && currentlyAnimatingIndex < 0 && !isWaitingForNextAgent && (
          <div className="flex items-center space-x-2 p-4 rounded-none bg-gray-200 dark:bg-gray-700 neo-border-thin">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-600 dark:bg-gray-400 rounded-none animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-600 dark:bg-gray-400 rounded-none animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-600 dark:bg-gray-400 rounded-none animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-gray-600 dark:text-gray-400 text-sm font-bold">
              Loading next message...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Scroll to Bottom Button - appears when user scrolls up */}
      {showScrollButton && (
        <button
          onClick={handleScrollToBottom}
          className="absolute bottom-8 right-8 bg-orange-400 hover:bg-orange-500 text-black rounded-none p-3 neo-border neo-shadow-hover z-10"
          aria-label="Scroll to bottom"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={3}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </button>
      )}

      {visibleMessages.length === 0 && (
        <div className="text-gray-600 dark:text-gray-400 text-center py-8 font-bold">
          No messages in this conversation yet
        </div>
      )}
    </div>
  )
}

