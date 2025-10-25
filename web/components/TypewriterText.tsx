'use client'

import { useEffect, useState } from 'react'

interface TypewriterTextProps {
  text: string
  speed?: number // chars per second
  onComplete?: () => void
  onUpdate?: () => void // Callback on each character
}

export default function TypewriterText({ text, speed = 50, onComplete, onUpdate }: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isSkipped, setIsSkipped] = useState(false)

  useEffect(() => {
    if (isSkipped) {
      setDisplayedText(text)
      setCurrentIndex(text.length)
      if (onComplete) onComplete()
      return
    }

    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)

        // Notify parent to scroll
        if (onUpdate) onUpdate()
      }, 1000 / speed) // Convert speed to milliseconds per char

      return () => clearTimeout(timeout)
    } else if (currentIndex === text.length && onComplete) {
      onComplete()
    }
  }, [currentIndex, text, speed, onComplete, onUpdate, isSkipped])

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('')
    setCurrentIndex(0)
    setIsSkipped(false)
  }, [text])

  const handleSkip = () => {
    setIsSkipped(true)
  }

  return (
    <div className="relative">
      <span className="whitespace-pre-wrap">
        {displayedText}
        {currentIndex < text.length && !isSkipped && (
          <span className="animate-pulse">▌</span>
        )}
      </span>

      {currentIndex < text.length && !isSkipped && (
        <button
          onClick={handleSkip}
          className="ml-3 text-xs text-gray-500 hover:text-gray-300 underline"
          title="Skip animation"
        >
          [skip]
        </button>
      )}
    </div>
  )
}

