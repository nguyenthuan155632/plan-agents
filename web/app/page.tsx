'use client'

import { useState, useEffect } from 'react'
import DualAIIcon from '@/components/DualAIIcon'
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
    <main className="min-h-screen bg-gray-100">
      <Header />

      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6">
          {/* Session List - Collapsible with animation - TEMPORARILY HIDDEN */}
          {false && (
            <div className={`lg:col-span-1 transition-all duration-300 ${isSidebarCollapsed ? 'hidden' : 'block'}`}>
              <SessionList
                onSelectSession={setSelectedSession}
                selectedSession={selectedSession}
                refreshKey={refreshKey}
              />
            </div>
          )}

          {/* Toggle Sidebar Button - Top Right - TEMPORARILY HIDDEN */}
          {false && (
            <button
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              className="fixed right-3 sm:right-4 top-3 sm:top-4 z-50 px-2 sm:px-3 py-1.5 sm:py-2 bg-purple-400 hover:bg-purple-500 active:bg-purple-600 text-black font-black rounded-none neo-border neo-shadow-hover uppercase tracking-wide flex items-center space-x-1 sm:space-x-2 transition-all text-xs sm:text-sm touch-manipulation"
              title={isSidebarCollapsed ? 'Show History' : 'Hide History'}
            >
              <span className="text-base sm:text-lg">{isSidebarCollapsed ? '📜' : '✕'}</span>
              <span className="hidden sm:inline">{isSidebarCollapsed ? 'History' : 'Close'}</span>
            </button>
          )}

          {/* Main Content - Expands when sidebar collapsed */}
          <div className={`space-y-4 sm:space-y-6 transition-all duration-300 ${isSidebarCollapsed ? 'lg:col-span-4' : 'lg:col-span-3'}`}>
            {/* Start New Conversation */}
            <StartConversation onSessionCreated={handleSessionCreated} hasActiveSession={!!selectedSession} />

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
              <div className="bg-white rounded-none neo-border neo-shadow p-6 sm:p-12 text-center">
                <div className="flex justify-center mb-4 sm:mb-6">
                  <DualAIIcon className="w-24 h-24" />
                </div>
                <h2 className="text-xl sm:text-3xl font-black text-black mb-3 sm:mb-4 uppercase tracking-tight font-mono">
                  Welcome to Dual AI Collaboration
                </h2>
                <p className="text-gray-600 font-bold text-sm sm:text-lg font-mono">
                  Start a new conversation above
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

