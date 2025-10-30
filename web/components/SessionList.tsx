'use client'

import { useEffect, useState } from 'react'

interface Session {
  id: string
  topic: string
  status: string
  started_at: string
  message_count: number
}

interface SessionListProps {
  onSelectSession: (sessionId: string) => void
  selectedSession: string | null
  refreshKey: number
}

export default function SessionList({ onSelectSession, selectedSession, refreshKey }: SessionListProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSessions()
  }, [refreshKey])

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/sessions')
      const data = await response.json()
      // Filter out sessions with null or undefined id
      const validSessions = (data.sessions || []).filter((s: Session) => s.id != null)
      setSessions(validSessions)
    } catch (error) {
      console.error('Error fetching sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500'
      case 'paused':
        return 'bg-yellow-500'
      case 'completed':
        return 'bg-gray-500'
      default:
        return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="bg-hacker-bg rounded-none neo-border neo-shadow p-6 border-2 border-hacker-terminal">
        <h2 className="text-xl font-bold text-hacker-terminal mb-4 font-mono">Sessions</h2>
        <div className="text-hacker-terminal text-center py-8 font-mono">Loading...</div>
      </div>
    )
  }

  return (
    <div className="bg-hacker-bg rounded-none neo-border neo-shadow p-6 border-2 border-hacker-terminal">
      <h2 className="text-2xl font-black text-hacker-terminal mb-6 flex items-center uppercase tracking-tight font-mono">
        <span className="mr-3 text-3xl">📚</span>
        Conversations
      </h2>

      {sessions.length === 0 ? (
        <div className="text-hacker-terminal text-center py-8">
          <p className="font-bold font-mono">No conversations yet</p>
          <p className="text-sm mt-2 font-mono">Start one using the CLI</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto overflow-x-hidden custom-scrollbar border-2 border-hacker-terminal p-2">
          {sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={`w-full text-left p-4 rounded-none neo-border-thin transition-all ${selectedSession === session.id
                ? 'bg-hacker-amber dark:bg-hacker-amber neo-shadow-lg text-hacker-bg'
                : 'bg-gray-900 dark:bg-gray-800 neo-shadow hover:neo-shadow-lg hover:-translate-x-0.5 hover:-translate-y-0.5 text-hacker-terminal border-2 border-hacker-terminal'
                }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-black text-hacker-terminal line-clamp-1 break-words text-base">
                    {session.topic || 'Untitled'}
                  </h3>
                  <p className="text-xs text-hacker-amber mt-1 truncate font-mono">
                    ID: {session.id}
                  </p>
                </div>
                <div className={`w-3 h-3 rounded-none border-2 border-hacker-terminal ${getStatusColor(session.status)} mt-1 ml-2 flex-shrink-0`}></div>
              </div>

              <div className="flex items-center justify-between text-xs text-hacker-terminal font-bold uppercase font-mono">
                <span>{session.status}</span>
                <span>{session.message_count} messages</span>
              </div>

              <div className="text-xs text-hacker-amber mt-2 font-mono">
                {new Date(session.started_at).toLocaleString()}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

