import { useState } from "react";
import { ArrowRight, CheckCircle2, GitBranch, Layers, ShieldCheck, Sparkles, Zap } from "lucide-react";
import type { AurumChain } from "../types";

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
            Aurum Dependency Graph <span className="text-xs font-normal text-gold">(npm-like golden links)</span>
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
          <div className="flex items-start justify-between gap-4">
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

          {/* Interactive Golden Graph Visualizer */}
          <div className="relative overflow-hidden rounded-lg border border-gold/20 bg-[#050C1A] p-4">
            <div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-gold/80">
              Topological Dependency Map
            </div>

            {/* SVG Golden Flow Connections */}
            <div className="flex flex-col gap-3">
              {/* Root Chain Hub Node */}
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-gold bg-gold/20 text-gold shadow-[0_0_15px_rgba(198,169,107,0.4)]">
                  <Layers className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-xs font-bold text-gold">{activeChain.id}</div>
                  <div className="text-[10px] text-cream/60">Universal Root Orchestrator</div>
                </div>
              </div>

              {/* Golden Line Connectors to Member MCPs */}
              <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                {activeChain.dependencies.map((dep, idx) => (
                  <div
                    key={idx}
                    className="group relative flex items-center justify-between rounded-lg border border-gold/25 bg-navy-light/60 p-2.5 transition-all hover:border-gold hover:bg-gold/10 hover:shadow-[0_0_12px_rgba(198,169,107,0.25)]"
                  >
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-gold animate-pulse" />
                      <div>
                        <div className="text-xs font-bold text-cream">{dep.target.toUpperCase()} MCP</div>
                        <div className="text-[10px] text-gold/90">{dep.label}</div>
                      </div>
                    </div>
                    <span className="rounded border border-gold/30 bg-gold/10 px-1.5 py-0.5 text-[9px] font-semibold text-gold">
                      Linked
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Included Tools Manifest */}
          <div className="rounded-lg border border-gold/15 bg-navy-light/30 p-3">
            <div className="mb-2 flex items-center justify-between text-xs font-semibold text-cream/90">
              <span>Exposed FastMCP Tools ({activeChain.tools.length})</span>
              <span className="text-[11px] text-gold">Zero Sprawl · 1 Unified Endpoint</span>
            </div>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {activeChain.tools.map((tool, idx) => (
                <div key={idx} className="flex items-start gap-2 rounded bg-[#050C1A]/60 p-2 border border-gold/10">
                  <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-400" />
                  <div>
                    <div className="font-mono text-[11px] font-bold text-gold">{tool.name}</div>
                    <div className="text-[10px] text-cream/70">{tool.description}</div>
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
