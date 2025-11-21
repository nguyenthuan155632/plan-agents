'use client'

import { useState, useRef, useEffect } from 'react'

interface CodebaseInfo {
  indexed: boolean
  fileCount?: number
  lastModified?: string
  size?: number
  message?: string
}

export default function CodebaseUpload() {
  const [isOpen, setIsOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isReindexing, setIsReindexing] = useState(false)
  const [info, setInfo] = useState<CodebaseInfo | null>(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isOpen) {
      fetchInfo()
    }
  }, [isOpen])

  const fetchInfo = async () => {
    try {
      const res = await fetch('/api/codebase')
      const data = await res.json()
      setInfo(data)
    } catch (e) {
      console.error('Failed to fetch codebase info', e)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setError('')
    setSuccess('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch('/api/codebase', {
        method: 'POST',
        body: formData
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Upload failed')
      }

      setSuccess(`Uploaded ${data.fileCount} files successfully!`)
      fetchInfo()
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleReindex = async () => {
    setIsReindexing(true)
    setError('')
    setSuccess('')

    try {
      const res = await fetch('/api/codebase?action=reindex', {
        method: 'POST'
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Re-indexing failed')
      }

      setSuccess('Codebase re-indexed from project files!')
      fetchInfo()
    } catch (err: any) {
      setError(err.message || 'Re-indexing failed')
    } finally {
      setIsReindexing(false)
    }
  }

  const handleClear = async () => {
    if (!confirm('Are you sure you want to clear the codebase?')) return

    try {
      const res = await fetch('/api/codebase', { method: 'DELETE' })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Clear failed')
      }

      setSuccess('Codebase cleared')
      fetchInfo()
    } catch (err: any) {
      setError(err.message || 'Clear failed')
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center space-x-1.5 sm:space-x-2 bg-green-400 hover:bg-green-500 px-2 sm:px-4 py-1.5 sm:py-2 rounded-none neo-border-thin neo-shadow-hover transition-colors"
        title="Manage Codebase"
      >
        <span className="text-sm sm:text-base">📁</span>
        <span className="text-black text-[10px] sm:text-sm font-black uppercase font-mono">Codebase</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-none neo-border neo-shadow max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-black text-black uppercase tracking-tight font-mono flex items-center">
                  <span className="mr-2">📁</span> Codebase Manager
                </h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-2xl font-black text-black hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {/* Current Status */}
              <div className="mb-6 p-4 bg-gray-100 neo-border-thin">
                <h3 className="text-sm font-black text-black uppercase mb-2 font-mono">Current Status</h3>
                {info ? (
                  info.indexed ? (
                    <div className="space-y-1 text-sm font-mono">
                      <p><span className="font-bold">Files:</span> {info.fileCount}</p>
                      <p><span className="font-bold">Size:</span> {info.size ? formatSize(info.size) : 'N/A'}</p>
                      <p><span className="font-bold">Last Updated:</span> {info.lastModified ? new Date(info.lastModified).toLocaleString() : 'N/A'}</p>
                    </div>
                  ) : (
                    <p className="text-sm font-mono text-gray-600">No codebase indexed yet</p>
                  )
                ) : (
                  <p className="text-sm font-mono text-gray-600">Loading...</p>
                )}
              </div>

              {/* Upload Section */}
              <div className="mb-6">
                <h3 className="text-sm font-black text-black uppercase mb-3 font-mono">Upload Codebase</h3>
                <p className="text-xs text-gray-600 mb-3 font-mono">
                  Supported formats: .json (repomix), .md (markdown), .txt (plain text)
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".json,.md,.txt"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="codebase-upload"
                />
                <label
                  htmlFor="codebase-upload"
                  className={`block w-full px-4 py-3 text-center cursor-pointer font-black uppercase tracking-wide font-mono neo-border neo-shadow-hover transition-colors ${
                    isUploading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-400 hover:bg-blue-500'
                  }`}
                >
                  {isUploading ? 'Uploading...' : '📤 Choose File'}
                </label>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-3 mb-6">
                <button
                  onClick={handleReindex}
                  disabled={isReindexing}
                  className={`flex-1 px-4 py-2 font-black uppercase tracking-wide font-mono neo-border neo-shadow-hover transition-colors text-sm ${
                    isReindexing
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-yellow-400 hover:bg-yellow-500'
                  }`}
                >
                  {isReindexing ? '🔄 Indexing...' : '🔄 Re-index Project'}
                </button>
                <button
                  onClick={handleClear}
                  className="px-4 py-2 bg-red-400 hover:bg-red-500 font-black uppercase tracking-wide font-mono neo-border neo-shadow-hover transition-colors text-sm"
                >
                  🗑️ Clear
                </button>
              </div>

              {/* Messages */}
              {error && (
                <div className="p-3 bg-red-300 neo-border-thin text-black text-sm font-bold font-mono mb-4">
                  ⚠️ {error}
                </div>
              )}
              {success && (
                <div className="p-3 bg-green-300 neo-border-thin text-black text-sm font-bold font-mono mb-4">
                  ✅ {success}
                </div>
              )}

              {/* Help */}
              <div className="text-xs text-gray-500 font-mono space-y-2">
                <p className="font-bold">Supported file formats:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>.json</strong> - Repomix format: {`{ "files": [...] }`}</li>
                  <li><strong>.md</strong> - Markdown codebase documentation</li>
                  <li><strong>.txt</strong> - Plain text codebase dump</li>
                </ul>
                <p className="mt-2 font-bold">Generate with repomix:</p>
                <code className="block bg-gray-100 p-2 rounded">npx repomix --output codebase.json</code>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
