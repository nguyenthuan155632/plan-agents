'use client'

import { useState, useEffect, useRef } from 'react'
import AIMessage from './AIMessage'

interface TypewriterAIMessageProps {
  text: string
  speed?: number // characters per second
  onComplete?: () => void
  onUpdate?: () => void
}

export default function TypewriterAIMessage({
  text,
  speed = 50,
  onComplete,
  onUpdate
}: TypewriterAIMessageProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [isSkipped, setIsSkipped] = useState(false)

  // Use refs to avoid re-creating the effect
  const onCompleteRef = useRef(onComplete)
  const onUpdateRef = useRef(onUpdate)

  useEffect(() => {
    onCompleteRef.current = onComplete
    onUpdateRef.current = onUpdate
  }, [onComplete, onUpdate])

  useEffect(() => {
    if (isSkipped) {
      setDisplayedText(text)
      setIsComplete(true)
      if (onCompleteRef.current) onCompleteRef.current()
      return
    }

    let currentIndex = 0
    const intervalTime = 1000 / speed

    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        currentIndex++
        setDisplayedText(text.slice(0, currentIndex))
        if (onUpdateRef.current) onUpdateRef.current()
      } else {
        setIsComplete(true)
        clearInterval(interval)
        if (onCompleteRef.current) onCompleteRef.current()
      }
    }, intervalTime)

    return () => clearInterval(interval)
  }, [text, speed, isSkipped]) // Removed onComplete and onUpdate from dependencies

  const handleSkip = () => {
    setIsSkipped(true)
    setDisplayedText(text)
    setIsComplete(true)
    if (onCompleteRef.current) onCompleteRef.current()
  }

  return (
    <div className="relative">
      {/* While typing: show plain text with blinking cursor */}
      {!isComplete ? (
        <div className="whitespace-pre-wrap font-medium text-black dark:text-white pb-6">
          {displayedText}
          <span className="inline-block w-2 h-5 bg-black dark:bg-white ml-1 animate-pulse"></span>
        </div>
      ) : (
        /* When complete: render full markdown */
        <AIMessage content={displayedText} role="AgentA" />
      )}

      {!isComplete && !isSkipped && (
        <button
          onClick={handleSkip}
          className="absolute bottom-0 right-0 px-1.5 py-0.5 bg-orange-400 hover:bg-orange-500 text-black text-[9px] font-bold rounded-none border border-black hover:neo-shadow uppercase tracking-wider opacity-50 hover:opacity-100 transition-all"
        >
          skip
        </button>
      )}
    </div>
  )
}

