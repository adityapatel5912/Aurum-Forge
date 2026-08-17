import { useState } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  ChevronDown,
  ClipboardCopy,
  Download,
  FileText,
  FlaskConical,
  FolderOpen,
  GitBranch,
  Loader2,
  Settings2,
  Share2,
  Sparkles,
  Table2,
  Terminal,
  XCircle,
} from "lucide-react";
import type { JobState, ForgeResult, PlatformKey } from "../types";
import { copyText } from "../api";
import AnvilIllustration from "./AnvilIllustration";
import ToolsTable from "./ToolsTable";
import DAGView from "./DAGView";
import CodePreview from "./CodePreview";
import ConfigSnippet from "./ConfigSnippet";

type Tab = "tools" | "dag" | "code" | "config" | "skill";

const TABS: { id: Tab; label: string; icon: typeof Table2 }[] = [
  { id: "tools", label: "Tools", icon: Table2 },
  { id: "dag", label: "DAG", icon: GitBranch },
  { id: "code", label: "server.py", icon: Terminal },
  { id: "skill", label: "SKILL.md", icon: FileText },
  { id: "config", label: "Config", icon: Settings2 },
];

const PLATFORM_OPTIONS: { id: PlatformKey; label: string }[] = [
  { id: "claude_code", label: "Claude Code" },
  { id: "cursor", label: "Cursor" },
  { id: "zcode", label: "Z Code (Zed)" },
  { id: "opencode", label: "OpenCode" },
  { id: "antigravity", label: "Antigravity" },
  { id: "codex", label: "Codex" },
];

/* --------------------------------------------------------------- empty -- */
function EmptyState() {
  return (
    <div className="flex h-full min-h-[420px] flex-col items-center justify-center gap-5 p-8 text-center">
      <AnvilIllustration />
      <div>
        <h3 className="font-display text-lg font-semibold text-navy">The anvil is hot</h3>
        <p className="mx-auto mt-1 max-w-sm text-sm leading-relaxed text-navy/55">
          Tell <span className="font-semibold text-navy">why</span> you need MCPs and add your sites —
          FORGE will scout them and forge one unified MCP server.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2 text-[11px] font-medium text-navy/45">
        {[
          "Single SKILL.md",
          "6-way agent export",
          "History storage",
          "Meta Forge MCP",
        ].map((s) => (
          <span key={s} className="rounded-full border border-navy/10 bg-white px-3 py-1">
            <Sparkles className="mr-1 inline h-3 w-3 text-gold-deep" /> {s}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------- loading -- */
function LoadingState({ job }: { job: JobState | null }) {
  const steps = job?.steps ?? [];
  const done = steps.filter((s) => s.state === "done").length;
  const pct = steps.length ? Math.round((done / steps.length) * 100) : 6;

  return (
    <div className="flex h-full min-h-[420px] flex-col justify-center gap-6 p-8">
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 animate-spin text-gold-deep" />
        <h3 className="font-display text-lg font-semibold text-navy">Forging Unified MCP Server…</h3>
      </div>

      <div>
        <div className="h-2.5 overflow-hidden rounded-full bg-navy/10">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-gold-deep via-gold to-gold-soft"
            animate={{ width: `${Math.max(pct, 6)}%` }}
            transition={{ type: "spring", stiffness: 90, damping: 20 }}
          />
        </div>
        <p className="mt-1.5 text-right text-xs font-semibold text-gold-deep">{pct}%</p>
      </div>

      <ul className="space-y-2.5">
        {(steps.length ? steps : [{ key: "wait", label: "Connecting to the forge…", state: "active" as const }]).map(
          (s) => (
            <li key={s.key} className="flex items-center gap-2.5 text-sm">
              {s.state === "done" ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-green-600" />
              ) : s.state === "active" ? (
                <Loader2 className="h-4 w-4 shrink-0 animate-spin text-gold-deep" />
              ) : (
                <span className="ml-[3px] mr-[3px] h-2 w-2 shrink-0 rounded-full border-2 border-navy/20" />
              )}
              <span className={s.state === "done" ? "text-navy/70" : s.state === "active" ? "font-semibold text-navy" : "text-navy/40"}>
                {s.label}
              </span>
            </li>
          )
        )}
      </ul>
    </div>
  );
}

/* -------------------------------------------------------------- result -- */
function ResultState({
  result,
  jobId,
  onViewSkill,
  onExport,
}: {
  result: ForgeResult;
  jobId?: string;
  onViewSkill?: (res: ForgeResult) => void;
  onExport?: (res: ForgeResult, platform: PlatformKey) => void;
}) {
  const [tab, setTab] = useState<Tab>("tools");
  const [flash, setFlash] = useState<string | null>(null);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);

  const flashMsg = (m: string) => {
    setFlash(m);
    setTimeout(() => setFlash(null), 2400);
  };

  const { stats } = result;

  const handleExportClick = async (platform: PlatformKey) => {
    setExportMenuOpen(false);
    if (onExport) {
      onExport(result, platform);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex h-full flex-col">
      {/* Success banner */}
      <div className="rounded-2xl bg-navy p-5 text-cream shadow-card">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-gold" />
              <h3 className="font-display text-base font-bold">
                MCP Server: {result.server_name}
              </h3>
              <span className="rounded-full bg-green-500/20 px-2 py-0.5 text-[10px] font-bold text-green-400">
                Active
              </span>
            </div>
            <p className="mt-1 text-sm text-cream/75">
              1 server operates{" "}
              <span className="font-bold text-gold-soft">{stats.custom} custom</span> +{" "}
              <span className="font-bold text-gold-soft">{stats.official} official</span> —{" "}
              {stats.core} core + {stats.forged} forged +{" "}
              {stats.tools_total - stats.core - stats.forged} official ={" "}
              <span className="font-bold text-gold-soft">{stats.tools_total} tools</span> in{" "}
              {stats.elapsed_s}s
            </p>
          </div>

          {/* Quick Action Group */}
          <div className="flex flex-wrap items-center gap-2">
            {/* View SKILL.md */}
            <button
              type="button"
              onClick={() => (onViewSkill ? onViewSkill(result) : setTab("skill"))}
              className="inline-flex items-center gap-1.5 rounded-xl border border-gold/40 bg-gold/10 px-3 py-1.5 font-display text-xs font-bold text-gold-soft transition hover:bg-gold hover:text-navy shadow-sm"
            >
              <FileText className="h-3.5 w-3.5" /> View SKILL.md
            </button>

            {/* Download ZIP */}
            <button
              type="button"
              onClick={() => window.open(jobId ? `/api/jobs/${jobId}/download` : `/api/history/${result.history_id || 'unified-mcp'}/download`, "_blank")}
              className="inline-flex items-center gap-1.5 rounded-xl bg-gold px-3 py-1.5 font-display text-xs font-bold text-navy transition hover:bg-gold-deep hover:text-cream shadow-forge"
            >
              <Download className="h-3.5 w-3.5" /> Download ZIP
            </button>

            {/* Export Dropdown Button */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setExportMenuOpen(!exportMenuOpen)}
                className="inline-flex items-center gap-1.5 rounded-xl bg-gold-deep px-3.5 py-1.5 font-display text-xs font-bold text-cream transition hover:bg-gold hover:text-navy shadow-sm"
              >
                <Share2 className="h-3.5 w-3.5 text-gold" /> Export <ChevronDown className="h-3 w-3" />
              </button>

              {exportMenuOpen && (
                <div className="absolute right-0 top-full mt-1.5 z-30 w-48 rounded-2xl border border-navy/15 bg-white p-1.5 shadow-2xl ring-1 ring-black/10">
                  <div className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-navy/40 border-b border-navy/5">
                    Export to Agent
                  </div>
                  {PLATFORM_OPTIONS.map((plat) => (
                    <button
                      key={plat.id}
                      type="button"
                      onClick={() => handleExportClick(plat.id)}
                      className="flex w-full items-center justify-between rounded-xl px-2.5 py-2 text-left text-xs font-semibold text-navy hover:bg-gold/15 hover:text-gold-deep transition"
                    >
                      <span>{plat.label}</span>
                      <span className="rounded bg-navy/10 px-1 py-0.5 text-[8.5px] font-mono text-navy/60">
                        {plat.id === "claude_code" || plat.id === "codex" || plat.id === "opencode" ? "CLI" : "JSON"}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-4 flex items-center gap-1 border-b border-navy/10">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`-mb-px inline-flex items-center gap-1.5 border-b-2 px-3.5 py-2 font-display text-xs font-semibold transition ${
              tab === id
                ? "border-gold text-navy font-bold"
                : "border-transparent text-navy/45 hover:text-navy/75"
            }`}
          >
            <Icon className="h-3.5 w-3.5" /> {label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <div className="min-h-0 flex-1 overflow-auto pt-4">
        {tab === "tools" && <ToolsTable tools={result.tools} />}
        {tab === "dag" && <DAGView dag={result.dag} />}
        {tab === "code" && <CodePreview code={result.server_py} />}
        {tab === "skill" && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-navy flex items-center gap-1.5">
                <FileText className="h-4 w-4 text-gold-deep" /> Single SKILL.md (Optimized for Agent Performance)
              </span>
              <button
                type="button"
                onClick={async () => {
                  if (await copyText(result.skill_content || "")) {
                    flashMsg("SKILL.md copied to clipboard");
                  }
                }}
                className="inline-flex items-center gap-1 rounded-lg border border-navy/20 bg-white px-2.5 py-1 text-xs font-semibold text-navy transition hover:border-navy hover:bg-navy hover:text-cream"
              >
                <ClipboardCopy className="h-3.5 w-3.5" /> Copy SKILL.md
              </button>
            </div>
            <pre className="max-h-[50vh] overflow-auto rounded-2xl bg-navy p-4 font-mono text-xs leading-relaxed text-cream/90 shadow-inner">
              <code>{result.skill_content || "# No SKILL.md generated"}</code>
            </pre>
          </div>
        )}
        {tab === "config" && <ConfigSnippet result={result} />}
      </div>

      {/* Actions footer */}
      <div className="mt-4 border-t border-navy/10 pt-4">
        {flash && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-2 rounded-lg bg-green-50 px-3 py-1.5 text-xs font-semibold text-green-700"
          >
            {flash}
          </motion.p>
        )}
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={async () => {
              await copyText(result.server_path);
              flashMsg("Absolute server path copied");
            }}
            className="inline-flex items-center gap-1.5 rounded-xl border border-navy/20 bg-white px-3.5 py-2 text-xs font-semibold text-navy transition hover:border-navy hover:bg-navy hover:text-cream"
          >
            <FolderOpen className="h-3.5 w-3.5" /> Copy Server Path
          </button>

          <button
            type="button"
            onClick={async () => {
              await copyText(`npx @modelcontextprotocol/inspector python "${result.server_path}"`);
              flashMsg("Inspector command copied — paste it in a terminal");
            }}
            className="inline-flex items-center gap-1.5 rounded-xl border border-navy/20 bg-white px-3.5 py-2 text-xs font-semibold text-navy transition hover:border-navy hover:bg-navy hover:text-cream"
          >
            <FlaskConical className="h-3.5 w-3.5" /> Test in Inspector
          </button>
        </div>
        <p className="mt-3 rounded-xl bg-gold/10 px-3.5 py-2.5 text-center font-display text-sm font-semibold text-navy">
          After config once, just say: <span className="break-all text-gold-deep">“{result.say_line}”</span>
        </p>
      </div>
    </motion.div>
  );
}

/* ---------------------------------------------------------------- root -- */
interface Props {
  phase: "idle" | "running" | "done" | "error";
  job: JobState | null;
  result: ForgeResult | null;
  error: string | null;
  jobId?: string;
  onViewSkill?: (res: ForgeResult) => void;
  onExport?: (res: ForgeResult, platform: PlatformKey) => void;
}

export default function UnifiedOutput({
  phase,
  job,
  result,
  error,
  jobId,
  onViewSkill,
  onExport,
}: Props) {
  return (
    <div className="flex h-full flex-col rounded-2xl border border-navy/10 bg-white/70 p-5 shadow-card backdrop-blur-sm">
      {phase === "idle" && <EmptyState />}
      {phase === "running" && <LoadingState job={job} />}
      {phase === "error" && (
        <div className="flex h-full min-h-[420px] flex-col items-center justify-center gap-4 p-8 text-center">
          <XCircle className="h-10 w-10 text-red-500" />
          <h3 className="font-display text-lg font-semibold text-navy">Forge failed</h3>
          <p className="max-w-md break-words rounded-xl bg-red-50 px-4 py-3 font-mono text-xs text-red-700">
            {error ?? "Unknown error"}
          </p>
        </div>
      )}
      {phase === "done" && result && (
        <ResultState
          result={result}
          jobId={jobId}
          onViewSkill={onViewSkill}
          onExport={onExport}
        />
      )}
    </div>
  );
}
