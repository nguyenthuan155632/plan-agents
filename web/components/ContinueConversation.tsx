'use client'

import { useState } from 'react'

interface ContinueConversationProps {
  sessionId: string
  isWaitingForInput: boolean
  onMessageSent: () => void
}

export default function ContinueConversation({
  sessionId,
  isWaitingForInput,
  onMessageSent
}: ContinueConversationProps) {
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState('')

  if (!isWaitingForInput) {
    return null // Don't show input if not waiting for human input
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!message.trim()) {
      setError('Please enter a message')
      return
    }

    setIsSending(true)
    setError('')

    try {
      const response = await fetch(`/api/sessions/${sessionId}/continue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message.trim() }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send message')
      }

      setMessage('')
      onMessageSent()

    } catch (err: any) {
      setError(err.message || 'Failed to send message')
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="bg-hacker-amber rounded-none neo-border neo-shadow-lg p-4 sm:p-6 border-2 border-hacker-terminal">
      <h3 className="text-lg sm:text-xl font-black text-hacker-bg mb-3 sm:mb-4 flex items-center uppercase tracking-wide font-mono">
        <span className="mr-2 sm:mr-3 text-xl sm:text-2xl">✋</span>
        <span className="text-sm sm:text-xl font-mono">Agents are waiting for your input</span>
      </h3>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your message to continue the conversation..."
            rows={3}
            className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-white neo-border-thin text-black placeholder-gray-500 focus:outline-none focus:neo-shadow font-medium resize-none text-sm sm:text-base font-mono border-2 border-hacker-terminal"
            disabled={isSending}
          />
        </div>

        {error && (
          <div className="p-3 bg-hacker-red neo-border-thin text-hacker-bg text-xs sm:text-sm font-bold font-mono border-2 border-hacker-terminal">
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isSending}
          className="w-full px-4 sm:px-6 py-3 bg-hacker-green hover:bg-green-500 active:bg-green-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-hacker-bg font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide text-sm sm:text-base flex items-center justify-center touch-manipulation font-mono"
        >
          {isSending ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-hacker-bg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="font-mono">Sending...</span>
            </>
          ) : (
            <>
              <span className="mr-2 text-base sm:text-xl">💬</span>
              <span className="font-mono">Send Message</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}

