'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface AIMessageProps {
  content: string
  role: 'AgentA' | 'AgentB' | 'Human'
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="text-xs text-gray-400 hover:text-white transition-colors"
    >
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

export default function AIMessage({ content }: AIMessageProps) {
  return (
    <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:text-gray-900 dark:prose-headings:text-gray-100">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''
            const codeString = String(children).replace(/\n$/, '')

            if (!inline && (match || codeString.includes('\n'))) {
              return (
                <div className="not-prose my-4 rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between bg-gray-800 px-4 py-2 text-xs">
                    <span className="text-gray-400 font-mono">{language || 'code'}</span>
                    <CopyButton text={codeString} />
                  </div>
                  <SyntaxHighlighter
                    style={oneDark}
                    language={language || 'text'}
                    PreTag="div"
                    customStyle={{
                      margin: 0,
                      borderRadius: 0,
                      borderTopLeftRadius: 0,
                      borderTopRightRadius: 0,
                    }}
                    {...props}
                  >
                    {codeString}
                  </SyntaxHighlighter>
                </div>
              )
            }

            return (
              <code className="bg-gray-200 dark:bg-gray-700 text-pink-600 dark:text-pink-400 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            )
          },
          p({ children }) {
            return <p className="my-3 leading-relaxed text-gray-700 dark:text-gray-300">{children}</p>
          },
          ul({ children }) {
            return <ul className="my-3 space-y-1 list-disc pl-6">{children}</ul>
          },
          ol({ children }) {
            return <ol className="my-3 space-y-1 list-decimal pl-6">{children}</ol>
          },
          li({ children }) {
            return <li className="text-gray-700 dark:text-gray-300">{children}</li>
          },
          h1({ children }) {
            return <h1 className="text-2xl font-bold mt-6 mb-4 text-gray-900 dark:text-gray-100">{children}</h1>
          },
          h2({ children }) {
            return <h2 className="text-xl font-semibold mt-5 mb-3 text-gray-900 dark:text-gray-100">{children}</h2>
          },
          h3({ children }) {
            return <h3 className="text-lg font-semibold mt-4 mb-2 text-gray-800 dark:text-gray-200">{children}</h3>
          },
          blockquote({ children }) {
            return (
              <blockquote className="my-4 pl-4 border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20 py-2 pr-4 italic text-gray-600 dark:text-gray-400">
                {children}
              </blockquote>
            )
          },
          a({ href, children }) {
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                {children}
              </a>
            )
          },
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto">
                <table className="min-w-full border border-gray-300 dark:border-gray-600">{children}</table>
              </div>
            )
          },
          th({ children }) {
            return <th className="px-4 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 font-semibold text-left">{children}</th>
          },
          td({ children }) {
            return <td className="px-4 py-2 border border-gray-300 dark:border-gray-600">{children}</td>
          },
          strong({ children }) {
            return <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
