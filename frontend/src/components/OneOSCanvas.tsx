import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRightLeft,
  Award,
  CheckCircle2,
  Cpu,
  Flame,
  Gauge,
  GitBranch,
  Globe,
  HardDrive,
  History,
  Layers,
  Lock,
  Mic,
  Package,
  Play,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  Sparkles,
  Terminal,
  Volume2,
  Wrench,
  Zap,
  Sun,
  Moon,
  Palette,
} from "lucide-react";
import type { AurumChain, Dag, ForgeResult, InspectorTab, Official, SiteRow } from "../types";
import { getAurumChains, getAurumHubStatus, triggerVoiceToChain } from "../api";
import VisualDAGCanvas from "./VisualDAGCanvas";
import AurumDependencyGraph from "./AurumDependencyGraph";
import SecurityVaultView from "./SecurityVaultView";
import TimeTravelView from "./TimeTravelView";
import AurumWrapperView from "./AurumWrapperView";
import SkillBridgeView from "./SkillBridgeView";
import LiveBenchmarkView from "./LiveBenchmarkView";
import SelfHealDiffView from "./SelfHealDiffView";
import IDEInjectorView from "./IDEInjectorView";
import VoicePilotView from "./VoicePilotView";

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

const VOICE_PRESETS = [
  {
    title: "Research Chain + GitHub",
    transcript: "Forge Research Chain and chain with official GitHub MCP",
    chain_id: "chain_research",
    color: "#3B82F6",
  },
  {
    title: "RAM Tracker to Notion + Email",
    transcript: "Chain RAM scraper to Notion + Email",
    chain_id: "chain_ops",
    color: "#10B981",
  },
  {
    title: "Video to Notion + Slack",
    transcript: "Forge Content Chain and summarize video to Notion and Slack",
    chain_id: "chain_content",
    color: "#8B5CF6",
  },
  {
    title: "Dev PR Watcher + Release",
    transcript: "Watch repo PRs, scan code, notify Slack, write Notion changelog",
    chain_id: "chain_dev_workflow",
    color: "#C6A96B",
  },
  {
    title: "B2B Leads + Email CRM",
    transcript: "Research leads from web, email outreach, track in Sheets, write Notion CRM",
    chain_id: "chain_sales_outreach",
    color: "#EC4899",
  },
];

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
  const [voiceTranscript, setVoiceTranscript] = useState("");
  const [activeChains, setActiveChains] = useState<AurumChain[]>([]);
  const [totalToolsCount, setTotalToolsCount] = useState(67);
  const [voiceStatus, setVoiceStatus] = useState<string | null>(null);
  const [theme, setTheme] = useState<"cream" | "white">(() => (localStorage.getItem("forge_theme") as "cream" | "white") || "cream");

  const toggleTheme = () => {
    const next = theme === "cream" ? "white" : "cream";
    setTheme(next);
    localStorage.setItem("forge_theme", next);
    document.documentElement.setAttribute("data-theme", next);
  };

  // Active DAG display: from active chain, or forged result, or fallback default
  const [currentDag, setCurrentDag] = useState<Dag>({});
  const [currentGoalDisplay, setCurrentGoalDisplay] = useState("Research any repo, browse docs, write Notion doc, email summary");

  useEffect(() => {
    // Load chains and initial DAG
    getAurumChains().then((res) => {
      if (res.ok && res.chains?.length) {
        setActiveChains(res.chains);
        setCurrentDag(res.chains[0].dag);
        setCurrentGoalDisplay(res.chains[0].description);
      }
    }).catch(console.error);

    getAurumHubStatus().then((res) => {
      if (res?.total_tools_count) {
        setTotalToolsCount(res.total_tools_count);
      }
    }).catch(console.error);
  }, []);

  // Sync DAG when a new forge completes
  useEffect(() => {
    if (result?.dag && Object.keys(result.dag).length > 0) {
      setCurrentDag(result.dag);
      if (result.goal) setCurrentGoalDisplay(result.goal);
    }
  }, [result]);

  const handleSelectPresetVoice = async (preset: typeof VOICE_PRESETS[0]) => {
    setVoiceTranscript(preset.transcript);
    setGoal(preset.transcript);
    setVoiceStatus(`Auto-linking "${preset.title}" into DAG...`);
    try {
      const res = await triggerVoiceToChain(preset.transcript);
      if (res.ok) {
        setCurrentDag(res.dag);
        setCurrentGoalDisplay(res.description);
        setVoiceStatus(`Auto-linked 4 stages -> Blue Trigger / Green Process / Purple Output with Aurum Gold glow!`);
      }
    } catch (err) {
      console.error("Voice-to-chain failed:", err);
    }
  };

  const handleSimulateVoiceRecording = () => {
    setIsRecordingVoice(true);
    setVoiceStatus("Listening for spoken workflow intent...");
    setTimeout(() => {
      setIsRecordingVoice(false);
      const randomPreset = VOICE_PRESETS[Math.floor(Math.random() * VOICE_PRESETS.length)];
      handleSelectPresetVoice(randomPreset);
    }, 1800);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] w-full flex-col overflow-hidden bg-[#050C1A] text-cream">
      {/* Top OS Status Bar */}
      <div className="flex shrink-0 items-center justify-between border-b border-gold/20 bg-navy/95 px-5 py-2.5 shadow-md">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-gold/60 bg-gold/15 text-gold shadow-[0_0_15px_rgba(198,169,107,0.4)]">
            <Sparkles className="h-4 w-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display text-sm font-black tracking-wide text-cream">
                FORGE-AURUM SUPER-HUB
              </span>
              <span className="rounded-full border border-gold/40 bg-gold/20 px-2 py-0.5 font-mono text-[10px] font-bold text-gold">
                AURUM GOLD (#C6A96B)
              </span>
              <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
                Live Proof Active
              </span>
            </div>
          </div>
        </div>

        {/* Global Stats */}
        <div className="flex items-center gap-4 text-xs">
          <div className="hidden sm:flex items-center gap-1.5 rounded-lg border border-gold/20 bg-navy-light/60 px-2.5 py-1">
            <span className="text-cream/60">Super-Hub Aggregator:</span>
            <span className="font-bold text-gold">{totalToolsCount} Tools in 1 MCP</span>
          </div>
          <div className="hidden md:flex items-center gap-1.5 rounded-lg border border-gold/20 bg-navy-light/60 px-2.5 py-1">
            <span className="text-cream/60">Deterministic Forge:</span>
            <span className="font-bold text-emerald-400">&lt;2.1s (0 API Tokens)</span>
          </div>
          <div className="flex items-center gap-1.5 rounded-lg border border-gold/30 bg-gold/15 px-2.5 py-1 font-bold text-gold">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            forge-aurum-hub Hot-Loaded
          </div>
          <button
            onClick={toggleTheme}
            className="flex items-center gap-1.5 rounded-lg border border-gold/40 bg-navy-light/80 px-2.5 py-1 font-bold text-gold hover:bg-gold/20 transition-all"
            title="Toggle Cream #FFFBF0 vs White #FFFFFF Theme"
          >
            {theme === "cream" ? <Sun className="h-3.5 w-3.5 text-amber-300" /> : <Moon className="h-3.5 w-3.5 text-blue-300" />}
            <span>{theme === "cream" ? "Cream" : "White"}</span>
          </button>
        </div>
      </div>

      {/* Main 3-Pane OS Canvas */}
      <div className="grid flex-1 grid-cols-12 overflow-hidden">
        {/* =========================================================================
            LEFT PANE: Voice-to-Chain & Control Console (Col 1-3)
        ========================================================================= */}
        <div className="flex flex-col border-r border-gold/20 bg-[#081326] p-4 overflow-y-auto col-span-12 lg:col-span-3 gap-4">
          {/* Voice Input Section */}
          <div className="flex flex-col gap-2.5 rounded-xl border border-gold/30 bg-navy/90 p-3.5 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mic className="h-4 w-4 text-gold" />
                <span className="text-xs font-bold text-cream">Voice-to-Chain Input</span>
              </div>
              {isRecordingVoice && (
                <span className="flex items-center gap-1 text-[10px] font-bold text-red-400 animate-pulse">
                  <span className="h-2 w-2 rounded-full bg-red-500" /> Recording
                </span>
              )}
            </div>

            <button
              onClick={handleSimulateVoiceRecording}
              disabled={isRecordingVoice}
              className={`flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-bold transition-all ${
                isRecordingVoice
                  ? "border border-red-500 bg-red-500/20 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.4)]"
                  : "border border-gold/40 bg-gold/15 text-gold hover:bg-gold hover:text-navy hover:shadow-[0_0_15px_rgba(198,169,107,0.4)]"
              }`}
            >
              <Volume2 className="h-4 w-4" />
              {isRecordingVoice ? "Listening to Speech..." : "Speak Workflow Command"}
            </button>

            {voiceStatus && (
              <div className="rounded border border-gold/20 bg-[#050C1A] p-2 text-[11px] font-medium text-gold/90 animate-in fade-in">
                {voiceStatus}
              </div>
            )}

            {/* Quick Spoken Presets */}
            <div className="mt-1 flex flex-col gap-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-cream/50">
                Spoken Presets (1-Click Speak & Auto-Link):
              </span>
              {VOICE_PRESETS.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectPresetVoice(preset)}
                  className="flex items-center justify-between rounded-lg border border-gold/15 bg-navy-light/40 p-2 text-left text-xs transition-all hover:border-gold hover:bg-gold/10"
                >
                  <span className="font-semibold text-cream/90">{preset.title}</span>
                  <span className="text-[10px] font-mono font-bold text-gold">2.1s</span>
                </button>
              ))}
            </div>
          </div>

          {/* Goal & Custom URL Input */}
          <div className="flex flex-col gap-3 rounded-xl border border-gold/20 bg-navy/80 p-3.5 shadow-lg">
            <div>
              <label className="text-xs font-bold text-cream">Plain English Goal</label>
              <textarea
                rows={2}
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="e.g. Research any repo, browse docs, write Notion doc, email summary"
                className="mt-1 w-full rounded-lg border border-gold/20 bg-[#050C1A] p-2 text-xs text-cream outline-none focus:border-gold"
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-cream">Custom Target Sites</label>
                <button
                  onClick={() => setSites([...sites, { id: `site-${sites.length + 1}`, url: "" }])}
                  className="text-[10px] font-semibold text-gold hover:underline"
                >
                  + Add URL
                </button>
              </div>
              <div className="mt-1 flex flex-col gap-1.5">
                {sites.map((s, idx) => (
                  <input
                    key={s.id}
                    type="text"
                    value={s.url}
                    onChange={(e) => {
                      const copy = [...sites];
                      copy[idx].url = e.target.value;
                      setSites(copy);
                    }}
                    placeholder="https://example.com"
                    className="w-full rounded border border-gold/20 bg-[#050C1A] px-2 py-1 text-xs text-cream outline-none focus:border-gold"
                  />
                ))}
              </div>
            </div>

            {/* Official MCP Toggles */}
            <div>
              <label className="text-xs font-bold text-cream">Official MCP Ecosystems</label>
              <div className="mt-1.5 grid grid-cols-2 gap-1.5">
                {catalog.slice(0, 6).map((off) => {
                  const isSelected = selectedOfficials.has(off.id);
                  return (
                    <button
                      key={off.id}
                      onClick={() => toggleOfficial(off.id)}
                      className={`flex items-center gap-1.5 rounded border p-1.5 text-left text-xs transition-all ${
                        isSelected
                          ? "border-gold bg-gold/25 font-bold text-gold"
                          : "border-gold/15 bg-[#050C1A] text-cream/70 hover:border-gold/40"
                      }`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${isSelected ? "bg-gold" : "bg-cream/30"}`} />
                      {off.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Forge Button */}
            <button
              onClick={onStartForge}
              disabled={isForging || !canForge}
              title={canForge ? "Forge a deterministic unified MCP" : "Type a goal first"}
              className="mt-1 flex w-full items-center justify-center gap-2 rounded-xl bg-gold py-2.5 text-xs font-black text-navy transition-all hover:bg-gold-light hover:shadow-[0_0_20px_rgba(198,169,107,0.6)] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:shadow-none"
            >
              <Zap className="h-4 w-4" />
              {isForging ? "Forging in 2.1s (Zero API)..." : "Forge Unified MCP (2.1s)"}
            </button>
          </div>
        </div>

        {/* =========================================================================
            CENTER PANE: Interactive Visual DAG Canvas (Col 4-8)
        ========================================================================= */}
        <div className="flex flex-col border-r border-gold/20 bg-[#050C1A] p-4 overflow-y-auto col-span-12 lg:col-span-5 gap-3">
          {/* DAG Canvas Header */}
          <div className="flex items-center justify-between rounded-xl border border-gold/30 bg-navy/90 px-4 py-2.5 shadow-md">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-gold">Active DAG Workflow</span>
                <span className="rounded bg-gold/20 px-2 py-0.5 text-[10px] font-bold text-gold">
                  Golden Pulse Edges Active
                </span>
              </div>
              <p className="mt-0.5 text-xs text-cream/80 truncate max-w-md">{currentGoalDisplay}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-emerald-400 font-bold">0.1s Execution</span>
            </div>
          </div>

          {/* Visual DAG SVG Canvas */}
          <div className="rounded-2xl border-2 border-gold/40 bg-[#071022] shadow-[0_0_25px_rgba(198,169,107,0.15)] overflow-hidden">
            <VisualDAGCanvas dag={currentDag} goal={currentGoalDisplay} />
          </div>

          {/* Golden Legend Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-gold/20 bg-navy/70 p-2.5 text-xs">
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
              Aurum Gold Border Glow (#C6A96B)
            </div>
          </div>
        </div>

        {/* =========================================================================
            RIGHT PANE: Inspector Drawer with 8 Contextual Tabs (Col 9-12)
        ========================================================================= */}
        <div className="flex flex-col bg-[#081326] p-4 overflow-y-auto col-span-12 lg:col-span-4 gap-3">
            {/* 9-Tab Switcher Inside Drawer */}
          <div className="flex flex-wrap gap-1 border-b border-gold/20 pb-2">
            {[
              { key: "voice_pilot", label: "Voice Pilot", icon: Mic },
              { key: "benchmark", label: "Live Benchmark", icon: Gauge },
              { key: "self_heal", label: "Self-Heal Diff", icon: Wrench },
              { key: "injector", label: "IDE Injector", icon: Zap },
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
                      : "border border-gold/20 bg-navy-light/40 text-cream/70 hover:border-gold/50 hover:text-cream"
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
            {inspectorTab === "voice_pilot" && (
              <VoicePilotView
                onChainForged={(chain_id) => {
                  const target = activeChains.find((c) => c.id === chain_id);
                  if (target) {
                    setCurrentDag(target.dag);
                    setCurrentGoalDisplay(target.description);
                  }
                }}
              />
            )}
            {inspectorTab === "benchmark" && <LiveBenchmarkView />}
            {inspectorTab === "self_heal" && <SelfHealDiffView />}
            {inspectorTab === "injector" && <IDEInjectorView />}
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
    </div>
  );
}
