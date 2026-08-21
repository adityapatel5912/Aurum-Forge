import { useEffect, useState } from "react";

/**
 * EarthDependencyGraph — Earth Forward dependency DAG.
 * ROOT -> CLIMATE / RENEWABLE / WASTE / WATER (Earth Green rgb(16,185,129))
 * ROOT -> NOTION / SLACK (Aurum Gold rgb(198,169,107), pulsing).
 * Same shape as AurumDependencyGraph but with green + gold Earth lines.
 */

const GREEN = "rgb(16,185,129)";
const GOLD = "rgb(198,169,107)";
const SKY = "rgb(59,130,246)";

interface NodeSpec {
  id: string;
  label: string;
  x: number;
  y: number;
  color: string;
  line: string;
  gold?: boolean;
}

const NODES: NodeSpec[] = [
  { id: "ROOT", label: "🌍 EARTH", x: 90, y: 170, color: "#10B981", line: GREEN },
  { id: "CLIMATE", label: "CLIMATE", x: 300, y: 40, color: "#10B981", line: GREEN },
  { id: "RENEWABLE", label: "RENEWABLE", x: 300, y: 105, color: SKY, line: GREEN },
  { id: "WASTE", label: "WASTE", x: 300, y: 170, color: "#10B981", line: GREEN },
  { id: "WATER", label: "WATER", x: 300, y: 235, color: SKY, line: GREEN },
  { id: "NOTION", label: "NOTION", x: 500, y: 105, color: "#8B5CF6", line: GOLD, gold: true },
  { id: "SLACK", label: "SLACK", x: 500, y: 235, color: "#C6A96B", line: GOLD, gold: true },
];

export default function EarthDependencyGraph() {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const t = window.setInterval(() => setTick((v) => v + 1), 1400);
    return () => window.clearInterval(t);
  }, []);

  return (
    <div className="w-full overflow-hidden rounded-2xl border border-emerald-500/20 bg-[#06120D] p-2 shadow-[0_0_25px_rgba(16,185,129,0.12)]">
      <svg viewBox="0 0 600 290" className="h-auto w-full" role="img" aria-label="Earth Forward dependency graph">
        <defs>
          <filter id="earthGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Golden-green dependency lines */}
        {NODES.filter((n) => n.id !== "ROOT").map((n, i) => {
          const phase = (tick + i) % 3;
          const midX = (90 + 300) / 2;
          return (
            <g key={`line-${n.id}`}>
              <path
                d={`M 118 170 C ${midX} 170, ${midX} ${n.y}, 272 ${n.y}`}
                fill="none"
                stroke={n.line}
                strokeWidth={n.gold ? 2.4 : 2}
                strokeOpacity={0.85}
                filter="url(#earthGlow)"
              />
              <circle r={3.2} fill={n.line} opacity={phase === 0 ? 1 : 0.35}>
                <animateMotion
                  dur="2.2s"
                  repeatCount="indefinite"
                  path={`M 118 170 C ${midX} 170, ${midX} ${n.y}, 272 ${n.y}`}
                  begin={`${i * 0.18}s`}
                />
              </circle>
            </g>
          );
        })}

        {/* NOTION <- green sources, SLACK <- green sources (gold pulse) */}
        <path d="M 328 105 L 472 105" fill="none" stroke={GOLD} strokeWidth={2.4} strokeOpacity={0.9} filter="url(#earthGlow)" />
        <path d="M 328 235 L 472 235" fill="none" stroke={GOLD} strokeWidth={2.4} strokeOpacity={0.9} filter="url(#earthGlow)" />
        <path d="M 328 40 C 420 40, 440 80, 472 100" fill="none" stroke={GOLD} strokeWidth={1.6} strokeOpacity={0.5} strokeDasharray="4 3" />
        <path d="M 328 105 C 420 105, 440 200, 472 228" fill="none" stroke={GOLD} strokeWidth={1.6} strokeOpacity={0.5} strokeDasharray="4 3" />

        {/* Nodes */}
        {NODES.map((n) => {
          const isRoot = n.id === "ROOT";
          const pulse = n.gold && (tick % 3 === 0);
          return (
            <g key={n.id} filter={isRoot || pulse ? "url(#earthGlow)" : undefined}>
              <rect
                x={n.x - 28}
                y={n.y - 17}
                width={isRoot ? 56 : 56}
                height={34}
                rx={10}
                fill={isRoot ? "rgba(16,185,129,0.22)" : "rgba(6,18,13,0.95)"}
                stroke={n.color}
                strokeWidth={isRoot ? 2.2 : 1.4}
              />
              <text
                x={n.x}
                y={n.y + 4}
                textAnchor="middle"
                fontSize={isRoot ? 10 : 9}
                fontWeight={800}
                fill={isRoot ? "#10B981" : n.color}
              >
                {n.label}
              </text>
            </g>
          );
        })}

        <text x={90} y={215} textAnchor="middle" fontSize={8} fill="rgba(16,185,129,0.8)" fontWeight={700}>
          ROOT
        </text>
        <text x={500} y={60} textAnchor="middle" fontSize={8} fill="rgba(198,169,107,0.9)" fontWeight={700}>
          GOLD PULSE
        </text>
      </svg>

      <div className="flex flex-wrap items-center justify-between gap-2 px-3 pb-1 pt-2 text-[10px]">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1 font-bold text-emerald-400">
            <span className="h-2 w-2 rounded-full" style={{ background: GREEN }} /> Earth Green rgb(16,185,129)
          </span>
          <span className="flex items-center gap-1 font-bold" style={{ color: GOLD }}>
            <span className="h-2 w-2 rounded-full" style={{ background: GOLD }} /> Aurum Gold rgb(198,169,107)
          </span>
        </div>
        <span className="font-mono font-bold text-emerald-300">ROOT-&gt;CLIMATE/RENEWABLE/WASTE/WATER/NOTION/SLACK</span>
      </div>
    </div>
  );
}
