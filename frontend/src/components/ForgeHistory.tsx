import { useEffect, useState } from "react";
import {
  ChevronDown,
  Clock,
  Download,
  FileText,
  Layers,
  Search,
  Share2,
  Sparkles,
  Zap,
} from "lucide-react";
import type { HistoryEntry, PlatformKey } from "../types";
import { getHistory } from "../api";

function formatTimeAgo(isoString: string): string {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (diffSec < 45) return "Just now";
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    return `${Math.floor(diffSec / 86400)}d ago`;
  } catch {
    return "Recently";
  }
}

const PLATFORM_OPTIONS: { id: PlatformKey; label: string }[] = [
  { id: "cursor", label: "Cursor" },
  { id: "antigravity", label: "Antigravity" },
  { id: "codex", label: "Codex" },
  { id: "zcode", label: "Z Code (Zed)" },
];

interface Props {
  onSelectEntry: (entry: HistoryEntry) => void;
  onExport: (entry: HistoryEntry, platform: PlatformKey) => void;
  onViewSkill: (entry: HistoryEntry) => void;
  selectedId?: string;
  refreshTrigger?: number;
}

const LOCAL_STORAGE_KEY = "forge_history_backup";

export default function ForgeHistory({
  onSelectEntry,
  onExport,
  onViewSkill,
  selectedId,
  refreshTrigger = 0,
}: Props) {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  const fetchHistory = async (query = "") => {
    setLoading(true);
    try {
      const data = await getHistory(query);
      setHistory(data);
      if (data.length > 0) {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
      }
    } catch {
      // Fallback to localStorage
      try {
        const cached = localStorage.getItem(LOCAL_STORAGE_KEY);
        if (cached) {
          const parsed = JSON.parse(cached) as HistoryEntry[];
          if (query) {
            setHistory(
              parsed.filter(
                (p) =>
                  p.goal.toLowerCase().includes(query.toLowerCase()) ||
                  p.tools.some((t) => t.toLowerCase().includes(query.toLowerCase()))
              )
            );
          } else {
            setHistory(parsed);
          }
        }
      } catch {
        setHistory([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(search);
  }, [refreshTrigger, search]);

  const handleDownloadZip = (e: React.MouseEvent, entry: HistoryEntry) => {
    e.stopPropagation();
    window.open(`/api/history/${entry.id}/download`, "_blank");
  };

  return (
    <aside className="flex h-full w-full flex-col border-r border-navy/10 bg-cream/70 backdrop-blur-md">
      {/* Sidebar Header */}
      <div className="border-b border-navy/10 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-gold-deep" />
            <h2 className="font-display text-sm font-bold tracking-tight text-navy">
              Forge History
            </h2>
          </div>
          <span className="rounded-full bg-navy/10 px-2 py-0.5 text-[10px] font-bold text-navy/70">
            {history.length}
          </span>
        </div>

        {/* Search input */}
        <div className="relative mt-3">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-navy/40" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search forged MCPs..."
            className="w-full rounded-xl border border-navy/15 bg-white/90 py-1.5 pl-8 pr-3 text-xs text-navy placeholder:text-navy/40 focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {loading && history.length === 0 && (
          <div className="p-4 text-center text-xs text-navy/40">Loading history…</div>
        )}

        {!loading && history.length === 0 && (
          <div className="p-6 text-center text-xs text-navy/45">
            <Sparkles className="mx-auto mb-2 h-6 w-6 text-gold/60" />
            <p className="font-medium">No forged MCPs yet</p>
            <p className="mt-1 text-[11px] text-navy/40">
              Forge your first workflow to see it here
            </p>
          </div>
        )}

        {history.map((item) => {
          const isSelected = selectedId === item.id;
          const isDropdownOpen = activeDropdown === item.id;

          return (
            <div
              key={item.id}
              onClick={() => onSelectEntry(item)}
              className={`group relative cursor-pointer rounded-2xl border p-3 transition ${
                isSelected
                  ? "border-gold bg-white shadow-sm ring-1 ring-gold"
                  : "border-navy/10 bg-white/70 hover:border-navy/20 hover:bg-white hover:shadow-card"
              }`}
            >
              {/* Header row: goal + status dot */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="h-2 w-2 shrink-0 rounded-full bg-green-500 ring-2 ring-green-200" />
                  <h4 className="truncate font-display text-xs font-bold text-navy">
                    {item.goal || "Unified Workflow"}
                  </h4>
                </div>
                <span className="shrink-0 text-[10px] font-medium text-navy/45">
                  {formatTimeAgo(item.timestamp)}
                </span>
              </div>

              {/* Tools preview & meta */}
              <div className="mt-2 flex items-center justify-between text-[11px] text-navy/60">
                <span className="inline-flex items-center gap-1 rounded-md bg-navy/5 px-1.5 py-0.5 font-medium">
                  <Layers className="h-3 w-3 text-gold-deep" /> {item.tools?.length || 0} tools
                </span>
                <span className="font-mono text-[9.5px] text-navy/40 truncate max-w-[110px]">
                  {item.id}
                </span>
              </div>

              {/* Action buttons (hover / visible) */}
              <div className="mt-2.5 flex items-center gap-1.5 border-t border-navy/5 pt-2">
                {/* Download Zip */}
                <button
                  type="button"
                  title="Download ZIP"
                  onClick={(e) => handleDownloadZip(e, item)}
                  className="inline-flex items-center gap-1 rounded-lg border border-navy/15 bg-cream/50 px-2 py-1 text-[10.5px] font-semibold text-navy hover:bg-gold hover:text-navy transition"
                >
                  <Download className="h-3 w-3" /> ZIP
                </button>

                {/* View SKILL.md */}
                <button
                  type="button"
                  title="View SKILL.md"
                  onClick={(e) => {
                    e.stopPropagation();
                    onViewSkill(item);
                  }}
                  className="inline-flex items-center gap-1 rounded-lg border border-navy/15 bg-cream/50 px-2 py-1 text-[10.5px] font-semibold text-navy hover:bg-gold hover:text-navy transition"
                >
                  <FileText className="h-3 w-3" /> Skill
                </button>

                {/* Export Dropdown */}
                <div className="relative ml-auto">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveDropdown(isDropdownOpen ? null : item.id);
                    }}
                    className="inline-flex items-center gap-1 rounded-lg bg-navy px-2 py-1 text-[10.5px] font-bold text-cream hover:bg-navy/80 transition shadow-sm"
                  >
                    <Share2 className="h-3 w-3 text-gold" /> Export <ChevronDown className="h-2.5 w-2.5" />
                  </button>

                  {isDropdownOpen && (
                    <div
                      onClick={(e) => e.stopPropagation()}
                      className="absolute right-0 bottom-full mb-1 z-30 w-40 rounded-xl border border-navy/15 bg-white p-1 shadow-xl ring-1 ring-black/5"
                    >
                      <div className="px-2 py-1 text-[9px] font-bold uppercase tracking-wider text-navy/40 border-b border-navy/5">
                        Export to Agent
                      </div>
                      {PLATFORM_OPTIONS.map((plat) => (
                        <button
                          key={plat.id}
                          type="button"
                          onClick={() => {
                            setActiveDropdown(null);
                            onExport(item, plat.id);
                          }}
                          className="flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-xs font-semibold text-navy hover:bg-gold/15 hover:text-gold-deep transition"
                        >
                          {plat.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
