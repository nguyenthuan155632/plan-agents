export default function Header() {
  return (
    <header className="bg-white dark:bg-gray-900 border-b-4 border-black neo-shadow">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between flex-wrap gap-6">
          <div className="flex items-center space-x-4">
            <div className="text-6xl">🤖</div>
            <div>
              <h1 className="text-4xl font-black text-black dark:text-white uppercase tracking-tighter leading-tight">
                Dual AI Collaboration
              </h1>
              <p className="text-gray-600 dark:text-gray-400 text-sm font-bold uppercase tracking-wide mt-1">
                Watch two AI agents brainstorm in real-time
              </p>
            </div>
          </div>

          <div className="flex space-x-3">
            <div className="flex items-center space-x-2 bg-blue-400 px-4 py-2 rounded-none neo-border-thin neo-shadow">
              <div className="w-3 h-3 bg-black rounded-none animate-pulse"></div>
              <span className="text-black text-sm font-black uppercase">Agent A</span>
            </div>
            <div className="flex items-center space-x-2 bg-purple-400 px-4 py-2 rounded-none neo-border-thin neo-shadow">
              <div className="w-3 h-3 bg-black rounded-none animate-pulse"></div>
              <span className="text-black text-sm font-black uppercase">Agent B</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

