'use client'

import { useState, useEffect } from 'react'
import SessionList from '@/components/SessionList'
import ConversationView from '@/components/ConversationView'
import StartConversation from '@/components/StartConversation'
import ContinueConversation from '@/components/ContinueConversation'
import Header from '@/components/Header'

export default function Home() {
  const [selectedSession, setSelectedSession] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [isWaitingForInput, setIsWaitingForInput] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true) // Default: hidden

  // Auto-refresh every 3 seconds (reduced from 2s to give users more time to read)
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const handleSessionCreated = (sessionId: string) => {
    setSelectedSession(sessionId)
    setRefreshKey(prev => prev + 1)
  }

  const handleMessageSent = () => {
    setIsWaitingForInput(false)
    setRefreshKey(prev => prev + 1)
  }

  return (
    <main className="min-h-screen bg-gray-100 dark:bg-gray-950">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Session List - Collapsible with animation */}
          <div className={`lg:col-span-1 transition-all duration-300 ${isSidebarCollapsed ? 'hidden' : 'block'}`}>
            <SessionList
              onSelectSession={setSelectedSession}
              selectedSession={selectedSession}
              refreshKey={refreshKey}
            />
          </div>

          {/* Toggle Sidebar Button - Top Right */}
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="fixed right-4 top-4 z-50 px-3 py-2 bg-purple-400 hover:bg-purple-500 text-black font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide flex items-center space-x-2 transition-all"
            title={isSidebarCollapsed ? 'Show History' : 'Hide History'}
          >
            <span className="text-lg">{isSidebarCollapsed ? '📜' : '✕'}</span>
            <span className="text-xs hidden sm:inline">{isSidebarCollapsed ? 'History' : 'Close'}</span>
          </button>

          {/* Main Content - Expands when sidebar collapsed */}
          <div className={`space-y-6 transition-all duration-300 ${isSidebarCollapsed ? 'lg:col-span-4' : 'lg:col-span-3'}`}>
            {/* Start New Conversation */}
            <StartConversation onSessionCreated={handleSessionCreated} />

            {/* Conversation View */}
            {selectedSession ? (
              <>
                <ConversationView
                  sessionId={selectedSession}
                  refreshKey={refreshKey}
                  onHandoverDetected={setIsWaitingForInput}
                />

                {/* Continue Conversation (shows only when waiting for input) */}
                <ContinueConversation
                  sessionId={selectedSession}
                  isWaitingForInput={isWaitingForInput}
                  onMessageSent={handleMessageSent}
                />
              </>
            ) : (
              <div className="bg-white dark:bg-gray-900 rounded-none neo-border neo-shadow p-12 text-center">
                <div className="text-8xl mb-6">🤖</div>
                <h2 className="text-3xl font-black text-black dark:text-white mb-4 uppercase tracking-tight">
                  Welcome to Dual AI Collaboration
                </h2>
                <p className="text-gray-600 dark:text-gray-400 font-bold text-lg">
                  Start a new conversation above {!isSidebarCollapsed && 'or select an existing one from the left'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

