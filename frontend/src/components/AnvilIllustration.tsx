export default function AnvilIllustration() {
  return (
    <div className="pointer-events-none select-none" aria-hidden>
      <svg width="220" height="170" viewBox="0 0 220 170" fill="none" className="mx-auto drop-shadow-sm">
        {/* sparkles */}
        <g stroke="#C6A96B" strokeWidth="2" strokeLinecap="round">
          <path d="M42 28v10M37 33h10" />
          <path d="M180 46v8M176 50h8" />
          <path d="M160 12v7M156.5 15.5h7" />
        </g>
        {/* hammer */}
        <g transform="rotate(24 150 38)">
          <rect x="143" y="14" width="22" height="16" rx="3" fill="#0A1931" />
          <rect x="150" y="28" width="7" height="34" rx="3" fill="#C6A96B" />
        </g>
        {/* anvil */}
        <g>
          <path d="M28 62h150l-16 20h-44v10h26l-9 34H84l-6-34h30V82H52z" fill="#0A1931" />
          <path d="M28 62h150l-16 20h-44v10h26l-9 34H84l-6-34h30V82H52z" fill="url(#anvilSheen)" />
          <rect x="24" y="58" width="158" height="9" rx="4.5" fill="#C6A96B" />
        </g>
        {/* impact sparks */}
        <g stroke="#C6A96B" strokeWidth="2.5" strokeLinecap="round" opacity="0.9">
          <path d="M96 50l-6-8M110 48l0-9M124 50l6-8" />
        </g>
        <defs>
          <linearGradient id="anvilSheen" x1="28" y1="58" x2="178" y2="130" gradientUnits="userSpaceOnUse">
            <stop stopColor="#3d4f6d" stopOpacity="0.55" />
            <stop offset="0.5" stopColor="#16294a" stopOpacity="0.2" />
            <stop offset="1" stopColor="#0A1931" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
