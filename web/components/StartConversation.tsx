'use client'

import { useState, useEffect } from 'react'

interface StartConversationProps {
  onSessionCreated: (sessionId: string) => void
  hasActiveSession?: boolean
}

export default function StartConversation({ onSessionCreated, hasActiveSession = false }: StartConversationProps) {
  const [topic, setTopic] = useState('')
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState('')
  const [isCollapsed, setIsCollapsed] = useState(hasActiveSession)

  // Auto-collapse when session becomes active
  useEffect(() => {
    if (hasActiveSession) {
      setIsCollapsed(true)
    }
  }, [hasActiveSession])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    setIsStarting(true)
    setError('')

    try {
      const response = await fetch('/api/sessions/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: topic.trim() }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start conversation')
      }

      setTopic('')
      onSessionCreated(data.sessionId)

    } catch (err: any) {
      setError(err.message || 'Failed to start conversation')
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <div className="bg-hacker-bg rounded-none neo-border neo-shadow border-2 border-hacker-terminal">
      {/* Header - Always visible, clickable to toggle */}
      <button
        type="button"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full p-4 sm:p-6 flex items-center justify-between text-hacker-terminal hover:bg-hacker-amber transition-colors"
      >
        <h2 className="text-xl sm:text-2xl font-black text-hacker-terminal flex items-center uppercase tracking-tight font-mono">
          <span className="mr-2 sm:mr-3 text-2xl sm:text-3xl hacker-green">✨</span>
          <span className="text-base sm:text-2xl font-mono">Start New Conversation</span>
        </h2>
        <span className="text-xl sm:text-2xl text-hacker-terminal font-black">
          {isCollapsed ? '▼' : '▲'}
        </span>
      </button>

      {/* Form - Collapsible with smooth animation */}
      <div className={`overflow-hidden transition-all duration-300 ${isCollapsed ? 'max-h-0' : 'max-h-[600px]'}`}>
        <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4 p-4 sm:p-6 pt-0">
          <div>
            <label htmlFor="topic" className="block text-xs sm:text-sm font-black text-hacker-terminal mb-2 sm:mb-3 uppercase tracking-wide font-mono">
              What topic would you like the agents to discuss?
            </label>
            <textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Best practices for API design, React vs Vue, Microservices vs Monolith, etc."
              rows={4}
              className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-white neo-border-thin text-black placeholder-gray-500 focus:outline-none focus:neo-shadow font-medium resize-none text-sm sm:text-base font-mono border-2 border-hacker-terminal"
              disabled={isStarting}
            />
          </div>

          {error && (
            <div className="p-3 sm:p-4 bg-hacker-red neo-border-thin text-hacker-bg text-xs sm:text-sm font-bold font-mono border-2 border-hacker-terminal">
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isStarting}
            className="w-full px-4 sm:px-6 py-3 sm:py-4 bg-hacker-green hover:bg-green-500 active:bg-green-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-hacker-bg font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide text-base sm:text-lg flex items-center justify-center touch-manipulation font-mono"
          >
            {isStarting ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-hacker-bg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="font-mono">Starting...</span>
              </>
            ) : (
              <>
                <span className="mr-2 text-xl sm:text-2xl">🚀</span>
                <span className="font-mono">Start Discussion</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

