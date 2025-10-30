import DualAIIcon from './DualAIIcon'

export default function Header() {
  return (
    <header className="bg-white border-b-4 border-black neo-shadow">
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-8">
        <div className="flex items-center justify-between flex-wrap gap-3 sm:gap-6">
          <div className="flex items-center space-x-2 sm:space-x-4">
            <DualAIIcon className="w-14 h-14" />
            <div>
              <h1 className="text-xl sm:text-4xl font-black text-black uppercase tracking-tighter leading-tight font-mono">
                Dual AI Collaboration
              </h1>
              <p className="text-gray-600 text-[10px] sm:text-sm font-bold uppercase tracking-wide mt-0.5 sm:mt-1 font-mono">
                Watch AI agents brainstorm in real-time
              </p>
            </div>
          </div>

          <div className="flex space-x-2 sm:space-x-3 w-full sm:w-auto justify-end">
            <div className="flex items-center space-x-1.5 sm:space-x-2 bg-blue-400 px-2 sm:px-4 py-1.5 sm:py-2 rounded-none neo-border-thin neo-shadow">
              <div className="w-2 h-2 sm:w-3 sm:h-3 bg-black rounded-none animate-pulse"></div>
              <span className="text-black text-[10px] sm:text-sm font-black uppercase font-mono">Agent A</span>
            </div>
            <div className="flex items-center space-x-1.5 sm:space-x-2 bg-red-400 px-2 sm:px-4 py-1.5 sm:py-2 rounded-none neo-border-thin neo-shadow">
              <div className="w-2 h-2 sm:w-3 sm:h-3 bg-black rounded-none animate-pulse"></div>
              <span className="text-black text-[10px] sm:text-sm font-black uppercase font-mono">Agent B</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

