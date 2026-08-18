import { useEffect, useState } from "react";
import {
  Activity,
  Check,
  CheckCircle2,
  Code2,
  Copy,
  Cpu,
  Gauge,
  Hammer,
  HardDrive,
  Layers,
  ShieldCheck,
  Sparkles,
  Terminal,
  Timer,
  Wrench,
  Zap,
} from "lucide-react";
import { copyText, getTelemetry } from "../api";

const FACTORY_TOOLS = [
  {
    name: "forge_new_mcp",
    signature: "forge_new_mcp(goal, urls, official_integrations, server_name)",
    description: "Deterministically compiles a unified MCP server in <2s with zero LLM, writes single root SKILL.md, and hot-loads into all IDEs.",
    badge: "ZERO-LLM",
  },
  {
    name: "forge_from_voice",
    signature: "forge_from_voice(voice_transcript)",
    description: "Parses spoken voice command, determines target URLs and official APIs, compiles MCP, and hot-loads without IDE restart.",
    badge: "VOICE",
  },
  {
    name: "hot_load_mcp",
    signature: "hot_load_mcp(mcp_name, server_path, target_ide='all')",
    description: "Atomically injects MCP config into Antigravity, Z Code, Claude Code, Cursor, and Windsurf without restarting.",
    badge: "HOT-LOAD",
  },
  {
    name: "publish_to_marketplace",
    signature: "publish_to_marketplace(mcp_id, author, description, tags)",
    description: "Packages and publishes a forged MCP to the Day-0 decentralized Marketplace (npm for MCPs).",
    badge: "MARKETPLACE",
  },
  {
    name: "chain_mcps",
    signature: "chain_mcps(mcp_names, composite_goal)",
    description: "Composes multiple forged MCPs into a single composite workflow DAG and unified agent pipeline.",
    badge: "CHAIN",
  },
  {
    name: "benchmark_mcp",
    signature: "benchmark_mcp(mcp_name='unified-forge')",
    description: "Runs real-time empirical benchmark proving 83x speedup, 100% token savings, and $0.00 cost vs Stainless/Spex.",
    badge: "BENCHMARK",
  },
  {
    name: "self_heal_mcp",
    signature: "self_heal_mcp(server_path, error_log='')",
    description: "Reads Inspector logs, eliminates duplicate returns, normalizes paths to '/', and applies AST-verified patches in <200ms.",
    badge: "SELF-HEAL",
  },
  {
    name: "improve_mcp",
    signature: "improve_mcp(mcp_name, feedback='')",
    description: "Auto-evolves parameter types, enhances locator fallback resilience, and regenerates single root SKILL.md instructions.",
    badge: "EVOLUTION",
  },
];

export default function FactoryMCPView() {
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);
  const [telemetry, setTelemetry] = useState<any>(null);

  // Live telemetry poll — invocation counts, latency, memory, self-heal events
  useEffect(() => {
    let alive = true;
    const poll = async () => {
      try {
        const t = await getTelemetry();
        if (alive) setTelemetry(t);
      } catch {
        /* backend offline — keep last snapshot */
      }
    };
    poll();
    const id = window.setInterval(poll, 3000);
    return () => {
      alive = false;
      window.clearInterval(id);
    };
  }, []);

  const handleCopy = async (cmd: string, key: string) => {
    await copyText(cmd);
    setCopiedCmd(key);
    setTimeout(() => setCopiedCmd(null), 2400);
  };

  const factoryPath = "d:/Aditya/Forge/forge/mcp/forge_factory_mcp/server.py";

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-navy/15 bg-gradient-to-br from-navy via-navy to-navy-light p-8 text-cream shadow-card">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-gold/20 px-3 py-1 text-[11px] font-bold tracking-wider text-gold uppercase mb-3">
            <Cpu className="h-3.5 w-3.5" /> Autonomous In-IDE Operating System
          </div>
          <h2 className="font-display text-2xl font-bold tracking-tight text-cream sm:text-3xl">
            FORGE Factory MCP
          </h2>
          <p className="mt-2 text-sm text-cream/70 leading-relaxed">
            The meta-layer where MCPs build, hot-load, self-heal, chain, and distribute MCPs autonomously. Run FORGE Factory directly inside Claude Code, Antigravity, or Z Code to create new workforce tools on voice command.
          </p>
        </div>
      </div>

      {/* Quick Connect Command */}
      <div className="rounded-3xl border border-navy/10 bg-white/90 p-6 shadow-card backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-display text-xs font-bold uppercase tracking-wider text-navy">
              Connect Factory MCP to Claude Code Terminal
            </h3>
            <p className="text-xs text-navy/55 mt-0.5">
              Run once to equip Claude Code with autonomous forge, hot-load, and self-heal capabilities
            </p>
          </div>
          <button
            onClick={() =>
              handleCopy(
                `claude mcp add forge-factory -- python "${factoryPath}"`,
                "claude_cmd"
              )
            }
            className="inline-flex items-center gap-1.5 rounded-xl bg-gold px-4 py-2 font-display text-xs font-bold text-navy shadow-sm hover:bg-gold-deep hover:text-cream transition"
          >
            {copiedCmd === "claude_cmd" ? (
              <Check className="h-3.5 w-3.5 text-navy" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
            {copiedCmd === "claude_cmd" ? "Copied!" : "Copy Command"}
          </button>
        </div>

        <div className="mt-3 flex items-center rounded-2xl bg-navy p-4 font-mono text-xs text-cream">
          <Terminal className="h-4 w-4 text-gold mr-3 shrink-0" />
          <span className="truncate">
            claude mcp add forge-factory -- python &quot;{factoryPath}&quot;
          </span>
        </div>
      </div>

      {/* Live Telemetry Dashboard */}
      <div className="rounded-3xl border border-navy/10 bg-white/90 p-6 shadow-card backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-navy" />
            <h3 className="font-display text-xs font-bold uppercase tracking-wider text-navy">
              Live Factory Telemetry
            </h3>
            <span className="flex h-2 w-2 animate-pulse rounded-full bg-emerald-500" title="live — refreshes every 3s" />
          </div>
          <span className="font-mono text-[10px] text-navy/40">
            since {telemetry?.started_at || "—"}
          </span>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-5">
          <div className="rounded-2xl bg-navy/5 p-3.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-navy/55">
              <Zap className="h-3 w-3" /> Invocations
            </div>
            <div className="mt-1 font-display text-2xl font-bold text-navy">
              {telemetry?.total_invocations ?? "—"}
            </div>
          </div>
          <div className="rounded-2xl bg-navy/5 p-3.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-navy/55">
              <Hammer className="h-3 w-3" /> Forges
            </div>
            <div className="mt-1 font-display text-2xl font-bold text-navy">
              {telemetry?.forges?.count ?? "—"}
              <span className="ml-1 text-[10px] font-medium text-navy/50">
                avg {telemetry?.forges?.avg_s ?? 0}s
              </span>
            </div>
          </div>
          <div className="rounded-2xl bg-navy/5 p-3.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-navy/55">
              <Timer className="h-3 w-3" /> Avg Latency
            </div>
            <div className="mt-1 font-display text-2xl font-bold text-navy">
              {telemetry?.avg_latency_ms?.forge_new_mcp != null
                ? `${Math.round(telemetry.avg_latency_ms.forge_new_mcp)}ms`
                : "—"}
            </div>
          </div>
          <div className="rounded-2xl bg-navy/5 p-3.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-navy/55">
              <ShieldCheck className="h-3 w-3" /> Self-Heals
            </div>
            <div className="mt-1 font-display text-2xl font-bold text-navy">
              {telemetry?.self_heal?.count ?? "—"}
              <span className="ml-1 text-[10px] font-medium text-emerald-600">
                avg {telemetry?.self_heal?.avg_ms ?? 0}ms
              </span>
            </div>
          </div>
          <div className="rounded-2xl bg-navy/5 p-3.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-navy/55">
              <HardDrive className="h-3 w-3" /> Memory
            </div>
            <div className="mt-1 font-display text-2xl font-bold text-navy">
              {telemetry?.memory_mb != null ? `${telemetry.memory_mb}MB` : "—"}
            </div>
          </div>
        </div>

        {/* Per-tool invocation chips */}
        {telemetry?.invocations && Object.keys(telemetry.invocations).length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {Object.entries(telemetry.invocations).map(([tool, count]: any) => (
              <span
                key={tool}
                className="rounded-lg bg-navy px-2.5 py-1 font-mono text-[10px] font-semibold text-gold"
                title={`avg ${telemetry.avg_latency_ms?.[tool] ?? 0}ms`}
              >
                {tool} × {count}
              </span>
            ))}
          </div>
        )}

        {/* Last self-heal event */}
        {telemetry?.self_heal?.last && (
          <div className="mt-3 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-[11px] font-medium text-emerald-900">
            <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">
              Last self-heal: {telemetry.self_heal.last.elapsed_ms}ms ·{" "}
              {telemetry.self_heal.last.patches_applied} patch(es) ·{" "}
              {telemetry.self_heal.last.server_path}
            </span>
          </div>
        )}
      </div>

      {/* 8 Factory Tools Manifest */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-sm font-bold uppercase tracking-wider text-navy">
            8 Autonomous Factory Tools Exposed to AI Agents
          </h3>
          <span className="text-xs font-medium text-navy/50">
            Deterministic Engine &bull; Zero LLM &bull; &lt;2s
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {FACTORY_TOOLS.map((tool) => (
            <div
              key={tool.name}
              className="flex flex-col justify-between rounded-3xl border border-navy/10 bg-white/90 p-5 shadow-card backdrop-blur-sm transition hover:border-gold/60"
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-bold text-navy">
                    {tool.name}
                  </span>
                  <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-[9px] font-bold text-gold-deep">
                    {tool.badge}
                  </span>
                </div>
                <code className="mt-1.5 block font-mono text-[11px] text-navy/60 break-all bg-navy/5 p-2 rounded-xl">
                  {tool.signature}
                </code>
                <p className="mt-2.5 text-xs text-navy/70 leading-relaxed">
                  {tool.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
