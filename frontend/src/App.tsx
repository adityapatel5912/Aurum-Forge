import { useCallback, useEffect, useRef, useState } from "react";
import {
  Clock,
  Database,
  Hammer,
  History,
  Layers,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  Zap,
} from "lucide-react";
import { copyText, getOfficials, getJob, startForge } from "./api";
import type {
  ForgeResult,
  HistoryEntry,
  JobState,
  Official,
  PlatformExport,
  PlatformKey,
  SiteRow,
} from "./types";
import GoalInput from "./components/GoalInput";
import CustomSitesList from "./components/CustomSitesList";
import OfficialMCPs from "./components/OfficialMCPs";
import UnifiedOutput from "./components/UnifiedOutput";
import HowItWorks from "./components/HowItWorks";
import ForgeHistory from "./components/ForgeHistory";
import HistoryGridView from "./components/HistoryGridView";
import ForgeRegistryMcpView from "./components/ForgeRegistryMcpView";
import ExportModal from "./components/ExportModal";
import SkillModal from "./components/SkillModal";

type Phase = "idle" | "running" | "done" | "error";
type MainTab = "current" | "history" | "meta_mcp";

const POLL_MS = 900;

function AnvilMark() {
  return (
    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-navy shadow-card">
      <svg width="26" height="26" viewBox="0 0 32 32" fill="none" aria-hidden>
        <path d="M7 13h18l-3 4h-7v2h5l-2 6h-4l-1-4H9z" fill="#C6A96B" />
        <rect x="5" y="10.5" width="22" height="3.5" rx="1.75" fill="#C6A96B" opacity="0.85" />
      </svg>
    </div>
  );
}

function historyEntryToResult(entry: HistoryEntry): ForgeResult {
  return {
    server_name: entry.mcp_name || "unified-forge",
    version: "1.0.0",
    goal: entry.goal,
    created_at: entry.timestamp,
    detected_officials: [],
    cores: [],
    sites: [],
    officials: [],
    tools: entry.tools.map((t) => ({
      name: t,
      source: "Forged Tool",
      badge: "FORGED",
      description: `Tool for ${entry.goal}`,
    })),
    dag: entry.dag || {},
    server_py: `# Server path: ${entry.abs_path}\n# Run: python "${entry.abs_path}"`,
    server_path: entry.abs_path,
    zip_path: entry.zip_path,
    zip_name: "unified-mcp.zip",
    skill_content: entry.skill_content,
    claude_snippet: {
      mcpServers: {
        [entry.mcp_name || "unified-forge"]: {
          command: "python",
          args: [entry.abs_path],
        },
      },
    },
    cursor_snippet: {
      mcpServers: {
        [entry.mcp_name || "unified-forge"]: {
          command: "python",
          args: [entry.abs_path],
        },
      },
    },
    readme: `# ${entry.mcp_name}\n\nWorkflow: ${entry.goal}\nServer: ${entry.abs_path}`,
    say_line: `Use ${entry.mcp_name || "unified-forge"} at ${entry.abs_path}`,
    stats: {
      custom: 1,
      official: 0,
      tools_total: entry.tools.length,
      forged: entry.tools.length,
      core: 0,
      elapsed_s: 0,
    },
    diagnostics: null,
    history_id: entry.id,
    history_entry: entry,
  };
}

export default function App() {
  const [activeTab, setActiveTab] = useState<MainTab>("current");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [refreshHistory, setRefreshHistory] = useState(0);

  const [goal, setGoal] = useState("");
  const [sites, setSites] = useState<SiteRow[]>([{ id: "site-1", url: "" }]);
  const [catalog, setCatalog] = useState<Official[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [detected, setDetected] = useState<Set<string>>(new Set());

  const [phase, setPhase] = useState<Phase>("idle");
  const [job, setJob] = useState<JobState | null>(null);
  const [jobId, setJobId] = useState<string | undefined>(undefined);
  const [result, setResult] = useState<ForgeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  // Modals
  const [exportModal, setExportModal] = useState<{
    isOpen: boolean;
    mcpName: string;
    serverPath: string;
    initialPlatform: PlatformKey;
    configs?: Record<string, PlatformExport>;
  }>({
    isOpen: false,
    mcpName: "unified-forge",
    serverPath: "",
    initialPlatform: "claude_code",
  });

  const [skillModal, setSkillModal] = useState<{
    isOpen: boolean;
    skillContent: string;
    goal?: string;
    mcpName?: string;
  }>({
    isOpen: false,
    skillContent: "",
  });

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3200);
  };

  useEffect(() => {
    getOfficials()
      .then(setCatalog)
      .catch(() => setCatalog([]));
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  const toggleOfficial = (id: string) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const moveOfficial = (name: string, rowId: string) => {
    setSites((prev) => prev.filter((s) => s.id !== rowId));
    if (name === "notion") {
      setSelected((prev) => new Set(prev).add("notion"));
    } else {
      setDetected((prev) => new Set(prev).add(name));
    }
  };

  const urls = sites.map((s) => s.url.trim()).filter(Boolean);
  const canForge = goal.trim().length > 0 && (urls.length > 0 || selected.size > 0);

  const poll = useCallback((id: string) => {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const snap = await getJob(id);
        setJob(snap);
        if (snap.status === "done" && snap.result) {
          if (pollRef.current) window.clearInterval(pollRef.current);
          setResult(snap.result);
          setPhase("done");
          setRefreshHistory((v) => v + 1);
        } else if (snap.status === "error") {
          if (pollRef.current) window.clearInterval(pollRef.current);
          setError(snap.error ?? "Unknown forge error");
          setPhase("error");
        }
      } catch (err) {
        if (pollRef.current) window.clearInterval(pollRef.current);
        setError(String(err));
        setPhase("error");
      }
    }, POLL_MS);
  }, []);

  const forge = async () => {
    if (!canForge || phase === "running") return;
    setActiveTab("current");
    setPhase("running");
    setJob(null);
    setResult(null);
    setError(null);
    try {
      const { job_id } = await startForge({ goal: goal.trim(), urls, officials: [...selected] });
      setJobId(job_id);
      poll(job_id);
    } catch (err) {
      setError(String(err));
      setPhase("error");
    }
  };

  // Export handlers
  const handleExportFromCard = async (
    target: { mcpName: string; serverPath: string; configs?: Record<string, PlatformExport> },
    platform: PlatformKey
  ) => {
    const platName = {
      claude_code: "Claude Code",
      cursor: "Cursor",
      zcode: "Z Code (Zed)",
      opencode: "OpenCode",
      antigravity: "Antigravity",
      codex: "Codex",
    }[platform];

    const isCli = platform === "claude_code" || platform === "codex" || platform === "opencode";
    const cleanPath = target.serverPath.replace(/\\/g, "/");

    if (isCli) {
      let cmd = `claude mcp add ${target.mcpName} -- python ${cleanPath}`;
      if (platform === "codex") cmd = `codex mcp add ${target.mcpName} -- python ${cleanPath}`;
      if (platform === "opencode") cmd = `opencode mcp add ${target.mcpName} -- python ${cleanPath}`;
      await copyText(cmd);
      showToast(`Exported to ${platName} — paste command in terminal!`);
    } else {
      const cfg = target.configs?.[platform]?.config || {
        mcpServers: {
          [target.mcpName]: {
            command: "python",
            args: [cleanPath],
          },
        },
      };
      await copyText(JSON.stringify(cfg, null, 2));
      showToast(`Exported to ${platName} — JSON config copied!`);
    }

    setExportModal({
      isOpen: true,
      mcpName: target.mcpName,
      serverPath: target.serverPath,
      initialPlatform: platform,
      configs: target.configs,
    });
  };

  const handleSelectHistoryEntry = (entry: HistoryEntry) => {
    const res = historyEntryToResult(entry);
    setResult(res);
    setPhase("done");
    setActiveTab("current");
  };

  const handleViewSkill = (skillText: string, g?: string, name?: string) => {
    setSkillModal({
      isOpen: true,
      skillContent: skillText,
      goal: g,
      mcpName: name || "unified-forge",
    });
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-cream font-sans text-navy">
      {/* Toast Notification */}
      {toastMsg && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-2 rounded-2xl bg-navy px-4 py-3 text-xs font-bold text-cream shadow-2xl ring-1 ring-gold/40 animate-bounce">
          <Zap className="h-4 w-4 text-gold shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Header */}
      <header className="sticky top-0 z-20 shrink-0 border-b border-navy/10 bg-cream/90 backdrop-blur-md">
        <div className="mx-auto flex w-full items-center justify-between gap-4 px-6 py-3.5">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-xl p-1.5 text-navy/60 hover:bg-navy/5 hover:text-navy transition lg:hidden"
              title="Toggle sidebar"
            >
              {sidebarOpen ? <PanelLeftClose className="h-5 w-5" /> : <PanelLeftOpen className="h-5 w-5" />}
            </button>
            <AnvilMark />
            <div>
              <h1 className="font-display text-xl font-bold leading-none tracking-tight text-navy">
                FORGE
              </h1>
              <p className="mt-1 text-xs font-medium text-navy/55">
                One Server Operates Everything
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="hidden sm:flex items-center gap-1.5 rounded-2xl border border-navy/10 bg-white/70 p-1 shadow-sm">
            <button
              type="button"
              onClick={() => setActiveTab("current")}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 font-display text-xs font-bold transition ${
                activeTab === "current"
                  ? "bg-navy text-gold shadow-sm"
                  : "text-navy/60 hover:text-navy hover:bg-white/60"
              }`}
            >
              <Hammer className="h-3.5 w-3.5" /> Forge Studio
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("history")}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 font-display text-xs font-bold transition ${
                activeTab === "history"
                  ? "bg-navy text-gold shadow-sm"
                  : "text-navy/60 hover:text-navy hover:bg-white/60"
              }`}
            >
              <Clock className="h-3.5 w-3.5" /> Forge History
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("meta_mcp")}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 font-display text-xs font-bold transition ${
                activeTab === "meta_mcp"
                  ? "bg-navy text-gold shadow-sm"
                  : "text-navy/60 hover:text-navy hover:bg-white/60"
              }`}
            >
              <Database className="h-3.5 w-3.5" /> Forge Registry MCP
            </button>
          </div>

          {/* Header Action Button */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setActiveTab("meta_mcp")}
              className="inline-flex items-center gap-1.5 rounded-2xl bg-gold px-3.5 py-2 font-display text-xs font-bold text-navy shadow-forge transition hover:bg-gold-deep hover:text-cream"
            >
              <Database className="h-3.5 w-3.5" />
              <span className="hidden md:inline">Install</span> Forge Registry MCP
            </button>
          </div>
        </div>
      </header>

      {/* Main Body with Left Sidebar */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Left Sidebar (300px) */}
        <div
          className={`${
            sidebarOpen ? "block" : "hidden"
          } w-80 shrink-0 border-r border-navy/10 bg-cream/40 transition-all duration-300 md:block`}
        >
          <ForgeHistory
            selectedId={result?.history_id}
            refreshTrigger={refreshHistory}
            onSelectEntry={handleSelectHistoryEntry}
            onViewSkill={(entry) =>
              handleViewSkill(entry.skill_content, entry.goal, entry.mcp_name)
            }
            onExport={(entry, platform) =>
              handleExportFromCard(
                {
                  mcpName: entry.mcp_name || "unified-forge",
                  serverPath: entry.abs_path,
                },
                platform
              )
            }
          />
        </div>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          {activeTab === "current" && (
            <div className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-6 lg:grid-cols-[420px_minmax(0,1fr)]">
              {/* Left Column: Form */}
              <div className="flex flex-col gap-6 rounded-3xl border border-navy/10 bg-white/80 p-6 shadow-card backdrop-blur-sm">
                <GoalInput goal={goal} onChange={setGoal} />
                <CustomSitesList
                  sites={sites}
                  onChange={setSites}
                  onMoveOfficial={moveOfficial}
                  disabled={phase === "running"}
                />
                <OfficialMCPs
                  catalog={catalog}
                  selected={selected}
                  onToggle={toggleOfficial}
                  detected={detected}
                  disabled={phase === "running"}
                />
                <button
                  type="button"
                  onClick={forge}
                  disabled={!canForge || phase === "running"}
                  className="group inline-flex w-full items-center justify-center gap-2.5 rounded-2xl bg-gold px-5 py-4 font-display text-sm font-bold uppercase tracking-wider text-navy shadow-forge transition enabled:hover:bg-gold-deep enabled:hover:text-cream disabled:cursor-not-allowed disabled:opacity-45 disabled:shadow-none"
                >
                  <Hammer className="h-[18px] w-[18px] transition group-enabled:group-hover:rotate-12" />
                  {phase === "running" ? "Forging Single SKILL.md & MCP Server…" : "Forge Unified MCP Server"}
                </button>
                {!canForge && phase === "idle" && (
                  <p className="-mt-3 text-center text-[11px] text-navy/40">
                    Write your goal, then add a site or pick an official MCP
                  </p>
                )}
              </div>

              {/* Right Column: Output */}
              <UnifiedOutput
                phase={phase}
                job={job}
                result={result}
                error={error}
                jobId={jobId}
                onViewSkill={(res) =>
                  handleViewSkill(res.skill_content || "", res.goal, res.server_name)
                }
                onExport={(res, platform) =>
                  handleExportFromCard(
                    {
                      mcpName: res.server_name,
                      serverPath: res.server_path,
                      configs: res.export_configs,
                    },
                    platform
                  )
                }
              />
            </div>
          )}

          {activeTab === "history" && (
            <HistoryGridView
              refreshTrigger={refreshHistory}
              onSelectEntry={handleSelectHistoryEntry}
              onViewSkill={(entry) =>
                handleViewSkill(entry.skill_content, entry.goal, entry.mcp_name)
              }
              onExport={(entry, platform) =>
                handleExportFromCard(
                  {
                    mcpName: entry.mcp_name || "unified-forge",
                    serverPath: entry.abs_path,
                  },
                  platform
                )
              }
            />
          )}

          {activeTab === "meta_mcp" && <ForgeRegistryMcpView />}

          <div className="mt-12">
            <HowItWorks />
          </div>
        </main>
      </div>

      {/* Export Modal */}
      <ExportModal
        isOpen={exportModal.isOpen}
        onClose={() => setExportModal((prev) => ({ ...prev, isOpen: false }))}
        mcpName={exportModal.mcpName}
        serverPath={exportModal.serverPath}
        initialPlatform={exportModal.initialPlatform}
        exportConfigs={exportModal.configs}
      />

      {/* SKILL Modal */}
      <SkillModal
        isOpen={skillModal.isOpen}
        onClose={() => setSkillModal((prev) => ({ ...prev, isOpen: false }))}
        skillContent={skillModal.skillContent}
        goal={skillModal.goal}
        mcpName={skillModal.mcpName}
      />
    </div>
  );
}
