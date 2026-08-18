import { useState } from "react";
import { CheckCircle2, Globe, Layers, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { wrapOfficialMCP } from "../api";

interface OfficialCard {
  id: string;
  name: string;
  category: string;
  description: string;
  toolsCount: number;
  env_vars: string[];
}

const OFFICIALS: OfficialCard[] = [
  {
    id: "github",
    name: "GitHub Official MCP",
    category: "DevTools",
    description: "Enterprise GitHub wrapper with self-healing PR, issue, and workflow automation.",
    toolsCount: 3,
    env_vars: ["GITHUB_TOKEN"],
  },
  {
    id: "notion",
    name: "Notion Official MCP",
    category: "Productivity",
    description: "Structured database manager with schema auto-inference and block formatting.",
    toolsCount: 2,
    env_vars: ["NOTION_TOKEN"],
  },
  {
    id: "filesystem",
    name: "Filesystem Official MCP",
    category: "System & Hardware",
    description: "Sandboxed filesystem with path normalization, atomic writes, and '/' guarantee.",
    toolsCount: 3,
    env_vars: [],
  },
  {
    id: "slack",
    name: "Slack Official MCP",
    category: "Productivity",
    description: "Real-time Slack messaging with channel auto-discovery and thread dispatch.",
    toolsCount: 2,
    env_vars: ["SLACK_BOT_TOKEN"],
  },
  {
    id: "gmail",
    name: "Gmail Official MCP",
    category: "Productivity",
    description: "High-deliverability Gmail SMTP wrapper with HTML templating.",
    toolsCount: 2,
    env_vars: ["GMAIL_USER", "GMAIL_APP_PASSWORD"],
  },
  {
    id: "browser",
    name: "Browser Official MCP",
    category: "Browser Automation",
    description: "Stealth DOM scraper with 2-locator fallback and anti-bot bypass.",
    toolsCount: 2,
    env_vars: [],
  },
  {
    id: "youtube",
    name: "YouTube Official MCP",
    category: "Data & APIs",
    description: "Video transcript extractor and metadata synthesizer for content pipelines.",
    toolsCount: 2,
    env_vars: [],
  },
];

export default function AurumWrapperView() {
  const [wrappingId, setWrappingId] = useState<string | null>(null);
  const [wrappedSuccess, setWrappedSuccess] = useState<Record<string, boolean>>({});

  const handleWrap = async (officialId: string) => {
    setWrappingId(officialId);
    try {
      const res = await wrapOfficialMCP(officialId);
      if (res.ok) {
        setWrappedSuccess((prev) => ({ ...prev, [officialId]: true }));
      }
    } catch (err) {
      console.error("Wrap error:", err);
    } finally {
      setWrappingId(null);
    }
  };

  return (
    <div className="flex flex-col gap-4 text-cream">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gold/20 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-gold animate-pulse" />
          <h3 className="text-base font-bold tracking-wide text-cream">
            Aurum Official MCP Wrapper <span className="text-xs font-normal text-gold">(Make Official Gold)</span>
          </h3>
        </div>
        <span className="rounded-full border border-gold/30 bg-gold/10 px-2.5 py-0.5 text-xs font-semibold text-gold">
          7 Official Ecosystems
        </span>
      </div>

      <p className="text-xs text-cream/70">
        Official servers (GitHub, Notion, Filesystem, Slack, Gmail, Browser, YouTube) are normally buggy, lack self-healing, and create MCP sprawl. The Aurum Wrapper enriches them with Gold resilience, 2-locator fallback, and hot-loads them into the Super-Hub.
      </p>

      {/* Grid of Official Servers */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {OFFICIALS.map((off) => {
          const isDone = wrappedSuccess[off.id];
          const isWrapping = wrappingId === off.id;

          return (
            <div
              key={off.id}
              className="flex flex-col justify-between rounded-xl border border-gold/25 bg-navy/90 p-4 shadow-lg transition-all hover:border-gold hover:shadow-[0_0_15px_rgba(198,169,107,0.25)]"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-cream">{off.name}</span>
                  <span className="rounded border border-gold/40 bg-gold/15 px-2 py-0.5 text-[9px] font-bold text-gold">
                    AURUM GOLD (#C6A96B)
                  </span>
                </div>
                <p className="mt-1.5 text-xs text-cream/75">{off.description}</p>
                <div className="mt-2 flex items-center gap-2 text-[10px] text-gold/90 font-medium">
                  <span>{off.toolsCount} FastMCP Tools</span>
                  <span>·</span>
                  <span>2-Locator Fallback Active</span>
                </div>
              </div>

              <div className="mt-3 border-t border-gold/15 pt-3">
                <button
                  onClick={() => handleWrap(off.id)}
                  disabled={isWrapping}
                  className={`flex w-full items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-bold transition-all ${
                    isDone
                      ? "border border-emerald-500/40 bg-emerald-500/20 text-emerald-300"
                      : "bg-gold text-navy hover:bg-gold-light hover:shadow-[0_0_12px_rgba(198,169,107,0.5)]"
                  }`}
                >
                  {isDone ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                      Wrapped into Gold & Hot-Loaded
                    </>
                  ) : isWrapping ? (
                    "Wrapping into Gold..."
                  ) : (
                    <>
                      <Zap className="h-3.5 w-3.5" />
                      Wrap into Gold (0.1s)
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
