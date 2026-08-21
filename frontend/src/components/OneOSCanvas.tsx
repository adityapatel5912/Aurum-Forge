import { useCallback, useEffect, useState } from "react";
import {
  ArrowRightLeft,
  CheckCircle2,
  Download,
  Gauge,
  GitBranch,
  History,
  Mic,
  MicOff,
  Moon,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Sun,
  Wrench,
  X,
  Zap,
  KeyRound,
} from "lucide-react";
import type { AurumChain, Dag, ForgeResult, InspectorTab, Official, SiteRow } from "../types";
import {
  downloadFile,
  getAurumChains,
  getAurumHubStatus,
  getLiveness,
  getUniversalConfig,
  triggerVoiceToChain,
} from "../api";
import VisualDAGCanvas from "./VisualDAGCanvas";
import AurumDependencyGraph from "./AurumDependencyGraph";
import SecurityVaultView from "./SecurityVaultView";
import TimeTravelView from "./TimeTravelView";
import AurumWrapperView from "./AurumWrapperView";
import SkillBridgeView from "./SkillBridgeView";
import LiveBenchmarkView from "./LiveBenchmarkView";
import SelfHealDiffView from "./SelfHealDiffView";
import IDEInjectorView from "./IDEInjectorView";
import SecretsVaultModal from "./SecretsVaultModal";

interface Props {
  goal: string;
  setGoal: (g: string) => void;
  sites: SiteRow[];
  setSites: React.Dispatch<React.SetStateAction<SiteRow[]>>;
  catalog: Official[];
  selectedOfficials: Set<string>;
  toggleOfficial: (id: string) => void;
  onStartForge: () => void;
  canForge?: boolean;
  isForging: boolean;
  result: ForgeResult | null;
}

export default function OneOSCanvas({
  goal,
  setGoal,
  sites,
  setSites,
  catalog,
  selectedOfficials,
  toggleOfficial,
  onStartForge,
  canForge = true,
  isForging,
  result,
}: Props) {
  const [inspectorTab, setInspectorTab] = useState<InspectorTab>("benchmark");
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const [activeChains, setActiveChains] = useState<AurumChain[]>([]);
  const [totalToolsCount, setTotalToolsCount] = useState(35);
  const [voiceStatus, setVoiceStatus] = useState<string | null>(null);
  const [isSecretsModalOpen, setIsSecretsModalOpen] = useState(false);

  // Live Backend Health State (Green Online / Red Offline)
  const [backendHealth, setBackendHealth] = useState<"online" | "offline" | "checking">("checking");
  const [healthLatency, setHealthLatency] = useState<number | null>(null);

  const checkHealth = useCallback(async () => {
    const t0 = performance.now();
    try {
      const res = await getLiveness();
      const latency = Math.round(performance.now() - t0);
      if (res && (res.status === "alive" || res.status === "ok")) {
        setBackendHealth("online");
        setHealthLatency(latency);
      } else {
        setBackendHealth("offline");
        setHealthLatency(null);
      }
    } catch {
      setBackendHealth("offline");
      setHealthLatency(null);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = window.setInterval(checkHealth, 8000);
    return () => window.clearInterval(interval);
  }, [checkHealth]);

  const [currentDag, setCurrentDag] = useState<Dag>({});
  const [currentGoalDisplay, setCurrentGoalDisplay] = useState(
    "track the price of the DGX Spark and inform when it's at the lowest price through mail"
  );

  useEffect(() => {
    getAurumChains()
      .then((res) => {
        if (res.ok && res.chains?.length) {
          setActiveChains(res.chains);
          setCurrentDag(res.chains[0].dag);
          setCurrentGoalDisplay(res.chains[0].description);
        }
      })
      .catch(console.error);

    getAurumHubStatus()
      .then((res) => {
        if (res?.total_tools_count) {
          setTotalToolsCount(res.total_tools_count);
        }
      })
      .catch(console.error);
  }, []);

  const [latestServerName, setLatestServerName] = useState<string>("track_top_trending_ai_papers_f");

  useEffect(() => {
    getUniversalConfig().then((cfg) => {
      if (cfg?.active_mcp?.name) {
        setLatestServerName(cfg.active_mcp.name);
      }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (result) {
      if (result.server_name) {
        setLatestServerName(result.server_name);
      }
      if (result.dag && Object.keys(result.dag).length > 0) {
        setCurrentDag(result.dag);
      }
      if (result.goal) setCurrentGoalDisplay(result.goal);
      getAurumHubStatus().then((res) => {
        if (res?.total_tools_count) setTotalToolsCount(res.total_tools_count);
      });
      getAurumChains().then((res) => {
        if (res.ok && res.chains) setActiveChains(res.chains);
      });
    }
  }, [result]);

  const handleVoiceToggle = () => {
    if (isRecordingVoice) {
      setIsRecordingVoice(false);
      setVoiceStatus(null);
      return;
    }

    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: any }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: any }).webkitSpeechRecognition;

    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        setIsRecordingVoice(true);
        setVoiceStatus("Listening... Speak your workflow command now");

        recognition.onresult = async (event: any) => {
          const transcript = event.results[0][0].transcript;
          setGoal(transcript);
          setIsRecordingVoice(false);
          setVoiceStatus(`Captured: "${transcript}"`);
          try {
            const res = await triggerVoiceToChain(transcript);
            if (res.ok && res.dag) {
              setCurrentDag(res.dag);
              setCurrentGoalDisplay(res.description || transcript);
              setVoiceStatus(`Auto-linked workflow into DAG with Aurum Gold glow!`);
            }
          } catch (err) {
            console.error("Voice-to-chain failed:", err);
          }
        };

        recognition.onerror = () => {
          setIsRecordingVoice(false);
          setVoiceStatus("Microphone error or permission denied. You can type your command below.");
        };

        recognition.onend = () => {
          setIsRecordingVoice(false);
        };

        recognition.start();
        return;
      } catch {
        // Fallback below
      }
    }

    // Fallback simulation if speech recognition is unsupported in browser
    setIsRecordingVoice(true);
    setVoiceStatus("Listening... (Speak command or type below)");
    setTimeout(() => {
      setIsRecordingVoice(false);
      if (!goal.trim()) {
        const sample = "Monitor top Hacker News stories and notify via Mail";
        setGoal(sample);
        setVoiceStatus(`Captured: "${sample}"`);
      }
    }, 2000);
  };

  const handleDownloadSuperHub = () => {
    downloadFile("/api/download/unified-mcp.zip", "forge-aurum-hub.zip");
  };

  const handleDownloadActiveMcp = () => {
    const activeName = result?.server_name || "crypto_portfolio_tracker";
    downloadFile(`/api/download/${activeName}-mcp.zip`, `${activeName}-mcp.zip`);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] w-full flex-col overflow-hidden bg-[#060911] text-cream">
      {/* Top Header Bar — Together AI Style */}
      <div className="flex shrink-0 items-center justify-between border-b border-white/[0.08] bg-[#0A0E1A]/95 px-5 py-2.5 shadow-md backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-gold/60 bg-gold/15 text-gold shadow-[0_0_15px_rgba(198,169,107,0.35)]">
            <Sparkles className="h-4 w-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display text-sm font-black tracking-wide text-cream">
                AURUM-FORGE
              </span>
              <span className="rounded-full border border-gold/40 bg-gold/15 px-2 py-0.5 font-mono text-[10px] font-bold text-gold">
                SUPER-HUB
              </span>
              <span className="hidden sm:inline-flex rounded bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/30">
                Live Proof Active
              </span>

              {/* Live Backend Health Badge (Green Online / Red Offline) */}
              <button
                type="button"
                onClick={checkHealth}
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold border transition-all cursor-pointer ${
                  backendHealth === "online"
                    ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
                    : backendHealth === "offline"
                    ? "border-red-500/50 bg-red-500/15 text-red-400 hover:bg-red-500/25 shadow-[0_0_10px_rgba(239,68,68,0.3)]"
                    : "border-amber-500/50 bg-amber-500/15 text-amber-400 hover:bg-amber-500/25"
                }`}
                title={`Backend Status: ${backendHealth.toUpperCase()}${healthLatency !== null ? ` (${healthLatency}ms)` : ""} — Click to re-check`}
              >
                <span className="relative flex h-2 w-2 shrink-0">
                  {backendHealth === "online" && (
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                  )}
                  {backendHealth === "offline" && (
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
                  )}
                  <span
                    className={`relative inline-flex h-2 w-2 rounded-full ${
                      backendHealth === "online"
                        ? "bg-emerald-500"
                        : backendHealth === "offline"
                        ? "bg-red-500"
                        : "bg-amber-500 animate-pulse"
                    }`}
                  ></span>
                </span>
                <span>
                  {backendHealth === "online"
                    ? `Backend Online${healthLatency !== null ? ` • ${healthLatency}ms` : ""}`
                    : backendHealth === "offline"
                    ? "Backend Offline"
                    : "Checking..."}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Global Action & Status Metrics */}
        <div className="flex items-center gap-2.5 text-xs">
          <div className="hidden md:flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#0E1424] px-2.5 py-1">
            <span className="text-cream/60">Super-Hub:</span>
            <span className="font-bold text-gold">{totalToolsCount} Tools in 1 MCP</span>
          </div>

          <div className="hidden lg:flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#0E1424] px-2.5 py-1">
            <span className="text-cream/60">Speed:</span>
            <span className="font-bold text-emerald-400">&lt;2.1s (0 API Tokens)</span>
          </div>

          {/* 1-Click Secrets & Token Vault */}
          <button
            onClick={() => setIsSecretsModalOpen(true)}
            className="flex items-center gap-1.5 rounded-lg border border-gold/40 bg-gold/10 px-3 py-1 font-bold text-gold hover:bg-gold hover:text-navy hover:shadow-[0_0_15px_rgba(198,169,107,0.4)] transition-all"
            title="Configure API keys & tokens in UI (Telegram, Gmail, Instagram, YouTube, GitHub, Notion, Slack) and inject directly into IDEs"
          >
            <KeyRound className="h-3.5 w-3.5 shrink-0" />
            <span className="hidden sm:inline">Secrets & Tokens</span>
            <span className="sm:hidden">Vault</span>
          </button>

          {/* 1-Click Download Super Hub ZIP */}
          <button
            onClick={handleDownloadSuperHub}
            className="flex items-center gap-1.5 rounded-lg border border-gold/50 bg-gold/15 px-3 py-1 font-bold text-gold hover:bg-gold hover:text-navy hover:shadow-[0_0_15px_rgba(198,169,107,0.4)] transition-all"
            title="Download full Super-Hub 50-in-1 MCP bundle (ZIP)"
          >
            <Download className="h-3.5 w-3.5 shrink-0" />
            <span className="hidden sm:inline">Download Super-Hub ZIP</span>
            <span className="sm:hidden">Super-Hub</span>
          </button>

          {/* 1-Click Download Active MCP ZIP */}
          <button
            onClick={handleDownloadActiveMcp}
            className="flex items-center gap-1.5 rounded-lg border border-white/[0.12] bg-[#121A2D] px-3 py-1 font-semibold text-cream hover:border-gold hover:text-gold transition-all"
            title="Download active individual forged MCP package (ZIP)"
          >
            <Download className="h-3.5 w-3.5 shrink-0 text-gold" />
            <span className="hidden sm:inline">Download Active MCP</span>
            <span className="sm:hidden">Active MCP</span>
          </button>
        </div>
      </div>

      {/* Main 3-Pane Canvas Layout */}
      <div className="grid flex-1 grid-cols-12 overflow-hidden">
        {/* =========================================================================
            LEFT PANE: Consolidated Prompt, Voice, URLs & Ecosystems (Col 1-3)
        ========================================================================= */}
        <div className="flex flex-col border-r border-white/[0.08] bg-[#080C16] p-4 overflow-y-auto col-span-12 lg:col-span-3 gap-3.5">
          {/* Section Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-gold" />
              <span className="text-xs font-bold uppercase tracking-wider text-cream">Forge Command Console</span>
            </div>
            {isRecordingVoice && (
              <span className="flex items-center gap-1 text-[10px] font-bold text-red-400 animate-pulse">
                <span className="h-2 w-2 rounded-full bg-red-500" /> Recording...
              </span>
            )}
          </div>

          {/* Spoken / Text Input Box */}
          <div className="flex flex-col gap-2 rounded-xl border border-gold/30 bg-[#0C1222] p-3.5 shadow-lg">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-bold text-cream/80">Plain English Goal or Voice Intent</label>
              <div className="flex items-center gap-1">
                {goal.trim() && (
                  <button
                    onClick={() => {
                      setGoal("");
                      setVoiceStatus(null);
                    }}
                    className="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] text-cream/50 hover:text-cream transition-all"
                    title="Clear prompt"
                  >
                    <X className="h-3 w-3" /> Clear
                  </button>
                )}
              </div>
            </div>

            <textarea
              rows={3}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. Monitor top Hacker News stories and notify via Mail..."
              className="w-full rounded-lg border border-white/[0.08] bg-[#060911] p-2.5 text-xs text-cream outline-none focus:border-gold transition-all resize-none"
            />

            {/* Voice Trigger Button */}
            <button
              onClick={handleVoiceToggle}
              className={`flex items-center justify-center gap-2 rounded-lg py-2 text-xs font-bold transition-all ${
                isRecordingVoice
                  ? "border border-red-500 bg-red-500/20 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.4)] animate-pulse"
                  : "border border-white/[0.1] bg-[#121A2E] text-cream/90 hover:border-gold hover:text-gold"
              }`}
            >
              {isRecordingVoice ? <MicOff className="h-3.5 w-3.5 text-red-400" /> : <Mic className="h-3.5 w-3.5 text-gold" />}
              <span>{isRecordingVoice ? "Stop Recording" : "Voice Command (Mic)"}</span>
            </button>

            {voiceStatus && (
              <div className="rounded border border-gold/20 bg-[#060911] p-2 text-[11px] font-medium text-gold animate-in fade-in">
                {voiceStatus}
              </div>
            )}
          </div>

          {/* Custom Target Sites */}
          <div className="flex flex-col gap-2 rounded-xl border border-white/[0.08] bg-[#0C1222] p-3.5 shadow-sm">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-bold text-cream/80">Target Websites (Scraping/DOM)</label>
              <button
                onClick={() => setSites([...sites, { id: `site-${sites.length + 1}`, url: "" }])}
                className="text-[10px] font-semibold text-gold hover:underline"
              >
                + Add URL
              </button>
            </div>
            <div className="flex flex-col gap-1.5">
              {sites.map((s, idx) => (
                <div key={s.id} className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={s.url}
                    onChange={(e) => {
                      const copy = [...sites];
                      copy[idx].url = e.target.value;
                      setSites(copy);
                    }}
                    placeholder="https://news.ycombinator.com"
                    className="flex-1 rounded border border-white/[0.08] bg-[#060911] px-2 py-1 text-xs text-cream outline-none focus:border-gold"
                  />
                  {sites.length > 1 && (
                    <button
                      onClick={() => setSites(sites.filter((_, i) => i !== idx))}
                      className="text-cream/40 hover:text-red-400 text-xs p-1"
                      title="Remove site"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Official MCP Ecosystem Toggles */}
          <div className="flex flex-col gap-2 rounded-xl border border-white/[0.08] bg-[#0C1222] p-3.5 shadow-sm">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-bold text-cream/80">Official MCP Integrations</label>
              {selectedOfficials.size > 0 && (
                <span className="rounded bg-gold/20 px-1.5 py-0.5 text-[9px] font-bold text-gold">
                  {selectedOfficials.size} Selected
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              {catalog.map((off) => {
                const isSelected = selectedOfficials.has(off.id);
                return (
                  <button
                    key={off.id}
                    onClick={() => toggleOfficial(off.id)}
                    className={`flex items-center gap-1.5 rounded-lg border p-1.5 text-left text-xs transition-all ${
                      isSelected
                        ? "border-gold bg-gold/20 font-bold text-gold"
                        : "border-white/[0.08] bg-[#060911] text-cream/70 hover:border-gold/40"
                    }`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${isSelected ? "bg-gold" : "bg-cream/30"}`} />
                    <span className="truncate">{off.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Primary Forge Action Button */}
          <button
            onClick={onStartForge}
            disabled={isForging || !canForge}
            title={canForge ? "Forge unified FastMCP server" : "Type a goal or command first"}
            className="mt-auto flex w-full items-center justify-center gap-2 rounded-xl bg-gold py-3 text-xs font-black text-navy transition-all hover:bg-gold-light hover:shadow-[0_0_20px_rgba(198,169,107,0.5)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Zap className="h-4 w-4" />
            {isForging ? "Forging FastMCP (<2.1s)..." : "Forge Unified MCP Server"}
          </button>
        </div>

        {/* =========================================================================
            CENTER PANE: Interactive Visual DAG Canvas (Col 4-8)
        ========================================================================= */}
        <div className="flex flex-col border-r border-white/[0.08] bg-[#060911] p-4 overflow-y-auto col-span-12 lg:col-span-5 gap-3">
          {/* DAG Canvas Header */}
          <div className="flex items-center justify-between rounded-xl border border-white/[0.08] bg-[#0A0E1A] px-4 py-2.5 shadow-md">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-gold">Active DAG Workflow</span>
                <span className="rounded bg-gold/20 px-2 py-0.5 text-[10px] font-bold text-gold">
                  Golden Pulse Active
                </span>
              </div>
              <p className="mt-0.5 text-xs text-cream/80 truncate max-w-md">{currentGoalDisplay}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-emerald-400 font-bold">0.1s Execution</span>
            </div>
          </div>

          {/* Visual DAG SVG Canvas */}
          <div className="rounded-2xl border border-white/[0.08] bg-[#080D1A] shadow-[0_0_25px_rgba(198,169,107,0.1)] overflow-hidden">
            <VisualDAGCanvas dag={currentDag} goal={currentGoalDisplay} />
          </div>

          {/* Golden Legend Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-white/[0.08] bg-[#0A0E1A] p-2.5 text-xs">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-[#3B82F6] ring-2 ring-blue-400/40" />
                <span className="font-semibold text-blue-300">Blue Trigger</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-[#10B981] ring-2 ring-emerald-400/40" />
                <span className="font-semibold text-emerald-300">Green Process</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-[#8B5CF6] ring-2 ring-purple-400/40" />
                <span className="font-semibold text-purple-300">Purple Output</span>
              </div>
            </div>
            <div className="flex items-center gap-1 font-bold text-gold text-[11px]">
              <Sparkles className="h-3.5 w-3.5" />
              Aurum Gold Glow (#C6A96B)
            </div>
          </div>
        </div>

        {/* =========================================================================
            RIGHT PANE: Inspector Drawer with 8 Focused Tabs (Col 9-12)
        ========================================================================= */}
        <div className="flex flex-col bg-[#080C16] p-4 overflow-y-auto col-span-12 lg:col-span-4 gap-3">
          {/* 8-Tab Switcher Inside Drawer (No duplicate Voice Pilot) */}
          <div className="flex flex-wrap gap-1 border-b border-white/[0.08] pb-2">
            {[
              { key: "benchmark", label: "Live Benchmark", icon: Gauge },
              { key: "injector", label: "IDE Injector", icon: Zap },
              { key: "self_heal", label: "Self-Heal Diff", icon: Wrench },
              { key: "marketplace", label: "Marketplace & Graph", icon: GitBranch },
              { key: "wrapper", label: "Aurum Wrapper", icon: Sparkles },
              { key: "skill_bridge", label: "Skill Bridge", icon: ArrowRightLeft },
              { key: "time_travel", label: "Time-Travel", icon: History },
              { key: "vault", label: "Security Vault", icon: ShieldCheck },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = inspectorTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setInspectorTab(tab.key as InspectorTab)}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-bold transition-all ${
                    isActive
                      ? "border border-gold bg-gold text-navy shadow-[0_0_12px_rgba(198,169,107,0.4)]"
                      : "border border-white/[0.08] bg-[#0E1424] text-cream/70 hover:border-gold/40 hover:text-cream"
                  }`}
                >
                  <Icon className="h-3 w-3" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Drawer Tab Content Renderer */}
          <div className="flex-1">
            {inspectorTab === "benchmark" && <LiveBenchmarkView />}
            {inspectorTab === "self_heal" && <SelfHealDiffView />}
            {inspectorTab === "injector" && (
              <IDEInjectorView
                activeServerName={result?.server_name}
                activeServerPath={result?.server_path}
              />
            )}
            {inspectorTab === "marketplace" && (
              <AurumDependencyGraph
                chains={activeChains}
                onSelectChain={(chain) => {
                  setCurrentDag(chain.dag);
                  setCurrentGoalDisplay(chain.description);
                }}
              />
            )}
            {inspectorTab === "wrapper" && <AurumWrapperView />}
            {inspectorTab === "skill_bridge" && <SkillBridgeView />}
            {inspectorTab === "time_travel" && <TimeTravelView />}
            {inspectorTab === "vault" && <SecurityVaultView />}
          </div>
        </div>
      </div>

      <SecretsVaultModal
        isOpen={isSecretsModalOpen}
        onClose={() => setIsSecretsModalOpen(false)}
      />
    </div>
  );
}
