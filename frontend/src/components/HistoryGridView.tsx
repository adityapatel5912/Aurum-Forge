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

function formatDateTime(isoString: string): string {
  try {
    const d = new Date(isoString);
    return d.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
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
  refreshTrigger?: number;
}

export default function HistoryGridView({
  onSelectEntry,
  onExport,
  onViewSkill,
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
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(search);
  }, [refreshTrigger, search]);

  const handleDownload = (e: React.MouseEvent, entry: HistoryEntry) => {
    e.stopPropagation();
    window.open(`/api/history/${entry.id}/download`, "_blank");
  };

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      {/* Header with Search */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-navy/10 bg-white/80 p-6 shadow-card backdrop-blur-sm">
        <div>
          <h2 className="font-display text-xl font-bold text-navy flex items-center gap-2">
            <Clock className="h-5 w-5 text-gold-deep" />
            Forged MCP Servers History
          </h2>
          <p className="mt-1 text-xs text-navy/55">
            Browse, re-download, and export any previously forged workflow server
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy/40" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search goal or tools…"
            className="w-full rounded-2xl border border-navy/15 bg-white py-2 pl-9 pr-4 text-xs text-navy placeholder:text-navy/40 focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>
      </div>

      {/* Grid */}
      {loading && history.length === 0 && (
        <div className="rounded-3xl border border-navy/10 bg-white/50 p-12 text-center text-sm text-navy/50">
          Loading forged servers…
        </div>
      )}

      {!loading && history.length === 0 && (
        <div className="rounded-3xl border border-navy/10 bg-white/70 p-12 text-center shadow-card">
          <Sparkles className="mx-auto h-8 w-8 text-gold-deep/50 mb-3" />
          <h3 className="font-display text-base font-bold text-navy">No history records found</h3>
          <p className="mt-1 text-xs text-navy/50">
            Forge a workflow in the Current tab to create your first MCP server entry.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
        {history.map((item) => {
          const isDropdownOpen = activeDropdown === item.id;
          return (
            <div
              key={item.id}
              className="flex flex-col justify-between rounded-3xl border border-navy/10 bg-white/85 p-5 shadow-card transition hover:border-gold/50 hover:shadow-lg backdrop-blur-sm"
            >
              <div>
                {/* Top badges */}
                <div className="flex items-center justify-between gap-2 border-b border-navy/5 pb-3">
                  <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-gold-deep">
                    {item.mcp_name || "unified-forge"}
                  </span>
                  <span className="text-[10px] font-medium text-navy/45">
                    {formatDateTime(item.timestamp)}
                  </span>
                </div>

                {/* Goal title */}
                <h3 className="mt-3 font-display text-sm font-bold leading-snug text-navy line-clamp-2">
                  {item.goal}
                </h3>

                {/* Tools Count & Tags */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  <span className="inline-flex items-center gap-1 rounded-lg bg-navy/5 px-2 py-1 text-[10.5px] font-bold text-navy">
                    <Layers className="h-3 w-3 text-gold-deep" /> {item.tools?.length || 0} Tools
                  </span>
                  {item.tools?.slice(0, 3).map((t) => (
                    <span
                      key={t}
                      className="rounded-lg bg-cream px-2 py-1 font-mono text-[10px] text-navy/70 truncate max-w-[120px]"
                    >
                      {t}
                    </span>
                  ))}
                  {(item.tools?.length || 0) > 3 && (
                    <span className="rounded-lg bg-cream px-1.5 py-1 text-[10px] font-medium text-navy/40">
                      +{(item.tools?.length || 0) - 3}
                    </span>
                  )}
                </div>

                {/* SKILL snippet preview */}
                {item.skill_content && (
                  <div className="mt-3 rounded-xl bg-navy/5 p-2.5">
                    <div className="flex items-center justify-between text-[10px] font-bold text-navy/50 uppercase tracking-wider mb-1">
                      <span className="flex items-center gap-1">
                        <FileText className="h-3 w-3" /> SKILL.md
                      </span>
                    </div>
                    <p className="line-clamp-2 font-mono text-[10px] text-navy/70 leading-relaxed">
                      {item.skill_content.slice(0, 150)}...
                    </p>
                  </div>
                )}
              </div>

              {/* Action buttons */}
              <div className="mt-5 flex items-center gap-2 border-t border-navy/5 pt-3">
                <button
                  type="button"
                  onClick={() => onSelectEntry(item)}
                  className="rounded-xl border border-navy/15 bg-white px-3 py-1.5 text-xs font-semibold text-navy hover:bg-navy hover:text-cream transition"
                >
                  View
                </button>

                <button
                  type="button"
                  onClick={() => onViewSkill(item)}
                  className="rounded-xl border border-navy/15 bg-white px-3 py-1.5 text-xs font-semibold text-navy hover:bg-gold hover:text-navy transition"
                >
                  Skill
                </button>

                <button
                  type="button"
                  onClick={(e) => handleDownload(e, item)}
                  className="rounded-xl bg-gold px-3 py-1.5 text-xs font-bold text-navy hover:bg-gold-deep hover:text-cream transition shadow-sm"
                >
                  <Download className="inline h-3 w-3 mr-1" /> ZIP
                </button>

                {/* Export dropdown */}
                <div className="relative ml-auto">
                  <button
                    type="button"
                    onClick={() => setActiveDropdown(isDropdownOpen ? null : item.id)}
                    className="inline-flex items-center gap-1 rounded-xl bg-navy px-3 py-1.5 text-xs font-bold text-cream hover:bg-navy/80 transition"
                  >
                    <Share2 className="h-3 w-3 text-gold" /> Export <ChevronDown className="h-3 w-3" />
                  </button>

                  {isDropdownOpen && (
                    <div
                      onClick={(e) => e.stopPropagation()}
                      className="absolute right-0 bottom-full mb-1 z-30 w-44 rounded-2xl border border-navy/15 bg-white p-1.5 shadow-2xl ring-1 ring-black/10"
                    >
                      <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-navy/40 border-b border-navy/5">
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
                          className="flex w-full items-center justify-between rounded-xl px-2.5 py-2 text-left text-xs font-semibold text-navy hover:bg-gold/15 hover:text-gold-deep transition"
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
    </div>
  );
}
