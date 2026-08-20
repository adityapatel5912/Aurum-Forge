import { useState } from "react";
import { ArrowRight, CheckCircle2, Download, GitBranch, Layers, ShieldCheck, Sparkles, Zap } from "lucide-react";
import type { AurumChain } from "../types";
import { downloadFile } from "../api";

interface Props {
  chains: AurumChain[];
  onSelectChain?: (chain: AurumChain) => void;
  onInstallChain?: (chainId: string) => void;
}

export default function AurumDependencyGraph({ chains, onSelectChain, onInstallChain }: Props) {
  const [selectedChainId, setSelectedChainId] = useState<string>(chains[0]?.id || "chain_research");
  const activeChain = chains.find((c) => c.id === selectedChainId) || chains[0];

  return (
    <div className="flex flex-col gap-4 text-cream">
      <div className="flex items-center justify-between border-b border-gold/20 pb-3">
        <div className="flex items-center gap-2">
          <GitBranch className="h-5 w-5 text-gold animate-pulse" />
          <h3 className="text-base font-bold tracking-wide text-cream">
            Aurum Dependency Graph <span className="text-xs font-normal text-gold">(SVG Golden Lines rgb(198,169,107))</span>
          </h3>
        </div>
        <span className="rounded-full border border-gold/30 bg-gold/10 px-2.5 py-0.5 text-xs font-semibold text-gold">
          {chains.length} Active Chains
        </span>
      </div>

      {/* Chain Selector Tabs */}
      <div className="flex flex-wrap gap-2">
        {chains.map((chain) => {
          const isSelected = chain.id === selectedChainId;
          return (
            <button
              key={chain.id}
              onClick={() => {
                setSelectedChainId(chain.id);
                if (onSelectChain) onSelectChain(chain);
              }}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                isSelected
                  ? "border border-gold bg-gold/20 text-cream shadow-[0_0_10px_rgba(198,169,107,0.3)]"
                  : "border border-gold/20 bg-navy-light/40 text-cream/70 hover:border-gold/50 hover:text-cream"
              }`}
            >
              <span className={`h-2 w-2 rounded-full ${isSelected ? "bg-gold" : "bg-gold/40"}`} />
              {chain.name}
            </button>
          );
        })}
      </div>

      {activeChain && (
        <div className="flex flex-col gap-4 rounded-xl border border-gold/30 bg-navy/90 p-4 shadow-xl backdrop-blur-sm">
          {/* Header Info */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-cream">{activeChain.name}</span>
                <span className="rounded border border-gold/40 bg-gold/15 px-2 py-0.5 text-[10px] font-bold text-gold">
                  {activeChain.badge}
                </span>
                <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
                  {activeChain.work_rewritten_hours} hrs Work Rewritten
                </span>
              </div>
              <p className="mt-1 text-xs text-cream/80">{activeChain.description}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => downloadFile(`/api/download/${activeChain.id}-mcp.zip`, `${activeChain.id}-mcp.zip`)}
                className="flex items-center gap-1.5 rounded-lg border border-gold/40 bg-gold/10 px-3 py-1.5 text-xs font-bold text-gold transition-all hover:bg-gold/20"
                title="Download Standalone Chain Zip (>1KB)"
              >
                <Download className="h-3.5 w-3.5" />
                Download Zip
              </button>
              {onInstallChain && (
                <button
                  onClick={() => onInstallChain(activeChain.id)}
                  className="flex shrink-0 items-center gap-1.5 rounded-lg bg-gold px-3 py-1.5 text-xs font-bold text-navy transition-all hover:bg-gold-light hover:shadow-[0_0_12px_rgba(198,169,107,0.5)]"
                >
                  <Zap className="h-3.5 w-3.5" />
                  1-Click Install
                </button>
              )}
            </div>
          </div>

          {/* Interactive Golden Graph Visualizer with Real SVG Lines */}
          <div className="relative overflow-hidden rounded-lg border border-gold/30 bg-[#050C1A] p-4">
            <div className="mb-3 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-gold">
              <span>Topological Dependency Map (Golden Flow)</span>
              <span className="font-mono text-[10px] text-emerald-400 font-bold">stroke: rgb(198, 169, 107)</span>
            </div>

            {/* SVG Visual Flow Connector Lines */}
            <div className="relative mb-4 h-36 w-full rounded-lg border border-gold/15 bg-gradient-to-b from-[#071329] to-[#040A17] p-2">
              <svg className="h-full w-full" viewBox="0 0 600 140" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <linearGradient id="gold-flow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="rgb(198, 169, 107)" stopOpacity="0.9" />
                    <stop offset="50%" stopColor="#E4D3AC" stopOpacity="1" />
                    <stop offset="100%" stopColor="rgb(198, 169, 107)" stopOpacity="0.9" />
                  </linearGradient>
                  <filter id="gold-glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="2" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                </defs>

                {/* Root Node at (80, 70) */}
                <g transform="translate(40, 45)">
                  <rect width="90" height="50" rx="10" fill="#0A1931" stroke="rgb(198, 169, 107)" strokeWidth="2" filter="url(#gold-glow)" />
                  <text x="45" y="24" textAnchor="middle" fill="#C6A96B" fontSize="10" fontWeight="bold">ROOT HUB</text>
                  <text x="45" y="38" textAnchor="middle" fill="#FFFBF0" fontSize="8">{activeChain.id}</text>
                </g>

                {/* Target Nodes at x=420 */}
                {activeChain.dependencies.map((dep, idx) => {
                  const total = activeChain.dependencies.length;
                  const targetY = 25 + idx * (90 / Math.max(1, total - 1));
                  const pathData = `M 130 70 C 260 70, 300 ${targetY}, 420 ${targetY}`;

                  return (
                    <g key={idx}>
                      {/* Golden Line Curve */}
                      <path
                        d={pathData}
                        fill="none"
                        stroke="rgb(198, 169, 107)"
                        strokeWidth="2.5"
                        strokeDasharray="4 2"
                        strokeLinecap="round"
                        className="animate-pulse"
                      />
                      {/* Animated Gold Pulse Particle */}
                      <circle r="3" fill="#C6A96B" filter="url(#gold-glow)">
                        <animateMotion path={pathData} dur={`${1.6 + idx * 0.3}s`} repeatCount="indefinite" />
                      </circle>
                      {/* Member Node */}
                      <g transform={`translate(420, ${targetY - 18})`}>
                        <rect width="140" height="36" rx="8" fill="#0D2344" stroke="rgb(198, 169, 107)" strokeWidth="1.5" />
                        <text x="10" y="16" fill="#C6A96B" fontSize="9" fontWeight="bold">
                          {dep.target.toUpperCase()} MCP
                        </text>
                        <text x="10" y="28" fill="#FFFBF0" fontSize="7" opacity="0.8">
                          {dep.label.length > 24 ? dep.label.slice(0, 22) + "…" : dep.label}
                        </text>
                      </g>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Golden Line Connectors to Member MCPs List */}
            <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
              {activeChain.dependencies.map((dep, idx) => (
                <div
                  key={idx}
                  className="group relative flex items-center justify-between rounded-lg border border-gold/25 bg-navy-light/60 p-2.5 transition-all hover:border-gold hover:bg-gold/10 hover:shadow-[0_0_12px_rgba(198,169,107,0.25)]"
                >
                  <div className="flex items-center gap-2">
                    <div className="h-2.5 w-2.5 rounded-full bg-gold animate-ping" />
                    <div>
                      <div className="text-xs font-bold text-cream">{dep.target.toUpperCase()} MCP</div>
                      <div className="text-[10px] text-gold font-medium">{dep.label}</div>
                    </div>
                  </div>
                  <span className="rounded border border-gold/30 bg-gold/10 px-2 py-0.5 text-[9px] font-semibold text-gold">
                    rgb(198,169,107) Linked
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Included Tools Manifest */}
          <div className="rounded-lg border border-gold/15 bg-navy-light/30 p-3">
            <div className="mb-2 flex items-center justify-between text-xs font-semibold text-cream/90">
              <span>Exposed FastMCP Tools ({activeChain.tools.length})</span>
              <span className="text-[11px] text-gold font-bold">Zero Sprawl · 1 Unified Endpoint</span>
            </div>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {activeChain.tools.map((tool, idx) => (
                <div key={idx} className="flex items-start gap-2 rounded bg-[#050C1A]/60 p-2 border border-gold/10 overflow-hidden">
                  <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-400" />
                  <div className="min-w-0 flex-1 overflow-hidden">
                    <div className="font-mono text-[11px] font-bold text-gold truncate" title={tool.name}>
                      {tool.name}
                    </div>
                    <div className="text-[10px] text-cream/70 line-clamp-2 break-words">
                      {tool.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
