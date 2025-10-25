'use client'

import { useState } from 'react'

interface StartConversationProps {
  onSessionCreated: (sessionId: string) => void
}

export default function StartConversation({ onSessionCreated }: StartConversationProps) {
  const [topic, setTopic] = useState('')
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState('')

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
    <div className="bg-white dark:bg-gray-900 rounded-none neo-border neo-shadow p-6">
      <h2 className="text-2xl font-black text-black dark:text-white mb-6 flex items-center uppercase tracking-tight">
        <span className="mr-3 text-3xl">✨</span>
        Start New Conversation
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="topic" className="block text-sm font-black text-black dark:text-white mb-3 uppercase tracking-wide">
            What topic would you like the agents to discuss?
          </label>
          <textarea
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Best practices for API design, React vs Vue, Microservices vs Monolith, etc."
            rows={4}
            className="w-full px-4 py-3 bg-white dark:bg-gray-800 neo-border-thin text-black dark:text-white placeholder-gray-500 focus:outline-none focus:neo-shadow font-medium resize-none"
            disabled={isStarting}
          />
        </div>

        {error && (
          <div className="p-4 bg-red-300 dark:bg-red-400 neo-border-thin text-black text-sm font-bold">
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isStarting}
          className="w-full px-6 py-4 bg-green-400 hover:bg-green-500 disabled:bg-gray-400 disabled:cursor-not-allowed text-black font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide text-lg flex items-center justify-center"
        >
          {isStarting ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Starting...
            </>
          ) : (
            <>
              <span className="mr-2 text-2xl">🚀</span>
              Start Discussion
            </>
          )}
        </button>
      </form>
    </div>
  )
}

