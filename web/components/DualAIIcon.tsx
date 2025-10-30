'use client'

export default function DualAIIcon({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 512 512"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#1E1B4B', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#312E81', stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="blueGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#60A5FA', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#3B82F6', stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="purpleGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#C084FC', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#9333EA', stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#FCD34D', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#F59E0B', stopOpacity: 1 }} />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="4" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="shadow">
          <feDropShadow dx="0" dy="8" stdDeviation="12" floodOpacity="0.3" />
        </filter>
      </defs>

      {/* Transparent background */}
      <rect width="512" height="512" fill="none" rx="96" />

      {/* Subtle grid */}
      <g opacity="0.05">
        <line x1="0" y1="128" x2="512" y2="128" stroke="#FFF" strokeWidth="1" />
        <line x1="0" y1="256" x2="512" y2="256" stroke="#FFF" strokeWidth="1" />
        <line x1="0" y1="384" x2="512" y2="384" stroke="#FFF" strokeWidth="1" />
        <line x1="128" y1="0" x2="128" y2="512" stroke="#FFF" strokeWidth="1" />
        <line x1="256" y1="0" x2="256" y2="512" stroke="#FFF" strokeWidth="1" />
        <line x1="384" y1="0" x2="384" y2="512" stroke="#FFF" strokeWidth="1" />
      </g>

      {/* Central node */}
      <g filter="url(#glow)">
        <circle cx="256" cy="256" r="24" fill="url(#accentGradient)" opacity="0.3" />
        <circle cx="256" cy="256" r="16" fill="url(#accentGradient)" opacity="0.6" />
        <circle cx="256" cy="256" r="8" fill="#FCD34D" />
      </g>

      {/* Agent A - Blue neural network */}
      <g filter="url(#shadow)">
        <circle cx="140" cy="200" r="48" fill="url(#blueGlow)" opacity="0.9" />
        <circle cx="140" cy="200" r="36" fill="none" stroke="#60A5FA" strokeWidth="3" opacity="0.5" />
        <line x1="140" y1="200" x2="100" y2="160" stroke="url(#blueGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="100" cy="160" r="16" fill="url(#blueGlow)" opacity="0.8" />
        <line x1="140" y1="200" x2="100" y2="240" stroke="url(#blueGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="100" cy="240" r="16" fill="url(#blueGlow)" opacity="0.8" />
        <line x1="140" y1="200" x2="180" y2="160" stroke="url(#blueGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="180" cy="160" r="12" fill="url(#blueGlow)" opacity="0.8" />
        <line x1="140" y1="200" x2="180" y2="240" stroke="url(#blueGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="180" cy="240" r="12" fill="url(#blueGlow)" opacity="0.8" />
        <circle cx="140" cy="200" r="20" fill="#1E293B" />
        <circle cx="140" cy="200" r="12" fill="#60A5FA" />
        <g opacity="0.6">
          <circle cx="135" cy="195" r="3" fill="#FFF" />
          <circle cx="145" cy="195" r="3" fill="#FFF" />
          <circle cx="135" cy="205" r="3" fill="#FFF" />
          <circle cx="145" cy="205" r="3" fill="#FFF" />
        </g>
      </g>

      <line x1="188" y1="200" x2="232" y2="240" stroke="url(#blueGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.5" strokeDasharray="8 4" />

      {/* Agent B - Purple neural network */}
      <g filter="url(#shadow)">
        <circle cx="372" cy="312" r="48" fill="url(#purpleGlow)" opacity="0.9" />
        <circle cx="372" cy="312" r="36" fill="none" stroke="#C084FC" strokeWidth="3" opacity="0.5" />
        <line x1="372" y1="312" x2="412" y2="272" stroke="url(#purpleGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="412" cy="272" r="16" fill="url(#purpleGlow)" opacity="0.8" />
        <line x1="372" y1="312" x2="412" y2="352" stroke="url(#purpleGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="412" cy="352" r="16" fill="url(#purpleGlow)" opacity="0.8" />
        <line x1="372" y1="312" x2="332" y2="272" stroke="url(#purpleGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="332" cy="272" r="12" fill="url(#purpleGlow)" opacity="0.8" />
        <line x1="372" y1="312" x2="332" y2="352" stroke="url(#purpleGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
        <circle cx="332" cy="352" r="12" fill="url(#purpleGlow)" opacity="0.8" />
        <circle cx="372" cy="312" r="20" fill="#1E293B" />
        <circle cx="372" cy="312" r="12" fill="#C084FC" />
        <g opacity="0.6">
          <circle cx="367" cy="307" r="3" fill="#FFF" />
          <circle cx="377" cy="307" r="3" fill="#FFF" />
          <circle cx="367" cy="317" r="3" fill="#FFF" />
          <circle cx="377" cy="317" r="3" fill="#FFF" />
        </g>
      </g>

      <line x1="324" y1="312" x2="280" y2="272" stroke="url(#purpleGlow)" strokeWidth="4" strokeLinecap="round" opacity="0.5" strokeDasharray="8 4" />

      {/* Data particles */}
      <g opacity="0.4">
        <circle cx="200" cy="220" r="4" fill="#60A5FA" />
        <circle cx="215" cy="230" r="3" fill="#60A5FA" />
        <circle cx="228" cy="242" r="4" fill="#60A5FA" />
        <circle cx="312" cy="292" r="4" fill="#C084FC" />
        <circle cx="297" cy="282" r="3" fill="#C084FC" />
        <circle cx="284" cy="270" r="4" fill="#C084FC" />
      </g>

      {/* Bottom indicator */}
      <g filter="url(#shadow)">
        <rect x="156" y="420" width="200" height="48" rx="24" fill="#1E293B" opacity="0.8" />
        <rect x="158" y="422" width="196" height="44" rx="22" fill="none" stroke="url(#accentGradient)" strokeWidth="2" opacity="0.6" />
        <g opacity="0.7">
          <rect x="176" y="435" width="3" height="18" rx="1.5" fill="#60A5FA" />
          <rect x="186" y="435" width="3" height="18" rx="1.5" fill="#60A5FA" />
          <rect x="196" y="435" width="3" height="10" rx="1.5" fill="#C084FC" />
          <rect x="206" y="435" width="3" height="18" rx="1.5" fill="#C084FC" />
          <rect x="216" y="435" width="3" height="14" rx="1.5" fill="#FCD34D" />
          <rect x="226" y="435" width="3" height="18" rx="1.5" fill="#60A5FA" />
          <rect x="236" y="435" width="3" height="12" rx="1.5" fill="#C084FC" />
          <rect x="246" y="435" width="3" height="18" rx="1.5" fill="#60A5FA" />
          <rect x="256" y="435" width="3" height="16" rx="1.5" fill="#C084FC" />
          <rect x="266" y="435" width="3" height="18" rx="1.5" fill="#60A5FA" />
          <rect x="276" y="435" width="3" height="14" rx="1.5" fill="#FCD34D" />
          <rect x="286" y="435" width="3" height="18" rx="1.5" fill="#C084FC" />
          <rect x="296" y="435" width="3" height="10" rx="1.5" fill="#60A5FA" />
          <rect x="306" y="435" width="3" height="18" rx="1.5" fill="#C084FC" />
          <rect x="316" y="435" width="3" height="18" rx="1.5" fill="#60A5FA" />
          <rect x="326" y="435" width="3" height="14" rx="1.5" fill="#FCD34D" />
        </g>
      </g>

      {/* Corner accents */}
      <circle cx="80" cy="80" r="6" fill="url(#accentGradient)" opacity="0.4" />
      <circle cx="432" cy="80" r="6" fill="url(#accentGradient)" opacity="0.4" />
      <circle cx="80" cy="432" r="6" fill="url(#accentGradient)" opacity="0.4" />
      <circle cx="432" cy="432" r="6" fill="url(#accentGradient)" opacity="0.4" />
    </svg>
  )
}
