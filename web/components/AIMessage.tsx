'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'

interface AIMessageProps {
  content: string
  role: 'AgentA' | 'AgentB' | 'Human'
}

export default function AIMessage({ content, role }: AIMessageProps) {
  return (
    <div className="prose prose-sm max-w-none dark:prose-invert">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          // Headings
          h1: ({ children }) => (
            <h1 className="text-2xl font-black text-black dark:text-white uppercase tracking-tight mt-6 mb-4 border-b-4 border-black dark:border-white pb-2">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-black text-black dark:text-white uppercase tracking-tight mt-5 mb-3 border-b-2 border-black dark:border-white pb-1">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-bold text-black dark:text-white uppercase tracking-wide mt-4 mb-2">
              {children}
            </h3>
          ),

          // Code blocks
          code: ({ inline, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''

            if (inline) {
              return (
                <code
                  className="bg-gray-200 dark:bg-gray-800 text-pink-600 dark:text-pink-400 px-2 py-1 rounded-none border-2 border-black dark:border-white font-mono text-sm font-bold"
                  {...props}
                >
                  {children}
                </code>
              )
            }

            return (
              <div className="my-4">
                {language && (
                  <div className="bg-gray-900 text-white px-4 py-2 font-mono text-xs font-bold uppercase tracking-wide border-2 border-black">
                    {language}
                  </div>
                )}
                <pre className="!mt-0 !p-4 bg-gray-100 dark:bg-gray-900 overflow-x-auto border-2 border-black dark:border-white !rounded-none">
                  <code className="font-mono text-sm text-black dark:text-white" {...props}>
                    {children}
                  </code>
                </pre>
              </div>
            )
          },

          // Lists
          ul: ({ children }) => (
            <ul className="my-4 space-y-2 list-none pl-0">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-4 space-y-2 list-none pl-0 counter-reset-list">
              {children}
            </ol>
          ),
          li: ({ children, ordered }: any) => (
            <li className="flex items-start">
              <span className="inline-block w-8 h-8 bg-yellow-400 dark:bg-yellow-500 border-2 border-black dark:border-white flex items-center justify-center font-black text-black mr-3 flex-shrink-0">
                {ordered ? '•' : '→'}
              </span>
              <span className="flex-1 pt-1 font-medium text-black dark:text-white">{children}</span>
            </li>
          ),

          // Paragraphs
          p: ({ children }) => (
            <p className="my-3 text-black dark:text-white font-medium leading-relaxed">
              {children}
            </p>
          ),

          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="my-4 pl-4 border-l-4 border-purple-500 dark:border-purple-400 bg-purple-100 dark:bg-purple-900/30 p-4 rounded-none neo-border italic">
              {children}
            </blockquote>
          ),

          // Tables
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto">
              <table className="w-full border-4 border-black dark:border-white rounded-none">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-yellow-400 dark:bg-yellow-500">
              {children}
            </thead>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left font-black text-black uppercase tracking-wide border-2 border-black dark:border-white">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 border-2 border-black dark:border-white font-medium text-black dark:text-white">
              {children}
            </td>
          ),

          // Links
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 font-bold underline decoration-2 decoration-blue-600 dark:decoration-blue-400 hover:bg-blue-400 hover:text-black transition-colors px-1"
            >
              {children} ↗
            </a>
          ),

          // Horizontal rule
          hr: () => (
            <hr className="my-6 border-0 border-t-4 border-black dark:border-white" />
          ),

          // Strong/Bold
          strong: ({ children }) => (
            <strong className="font-black text-black dark:text-white bg-yellow-300 dark:bg-yellow-500 px-1">
              {children}
            </strong>
          ),

          // Emphasis/Italic
          em: ({ children }) => (
            <em className="italic text-purple-700 dark:text-purple-400 font-semibold">
              {children}
            </em>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

