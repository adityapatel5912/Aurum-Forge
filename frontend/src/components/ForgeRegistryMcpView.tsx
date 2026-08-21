import { useEffect, useState } from "react";
import {
  Check,
  ChevronDown,
  Code2,
  Copy,
  Database,
  ExternalLink,
  Layers,
  Search,
  Share2,
  Sparkles,
  Terminal,
  Zap,
} from "lucide-react";
import { copyText, getForgeRegistryMcpConfig } from "../api";
import type { ForgeRegistryMcpMeta, PlatformKey } from "../types";

const PLATFORMS: { id: PlatformKey; label: string; isCli: boolean }[] = [
  { id: "cursor", label: "Cursor", isCli: false },
  { id: "antigravity", label: "Antigravity", isCli: false },
  { id: "codex", label: "Codex", isCli: true },
  { id: "zcode", label: "Z Code (Zed)", isCli: false },
];

export default function ForgeRegistryMcpView() {
  const [meta, setMeta] = useState<ForgeRegistryMcpMeta | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<PlatformKey>("cursor");
  const [copiedCmd, setCopiedCmd] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);
  const [exportDropdownOpen, setExportDropdownOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2500);
  };

  useEffect(() => {
    getForgeRegistryMcpConfig()
      .then(setMeta)
      .catch(() => {
        // Fallback meta
        setMeta({
          name: "forge-registry",
          server_path: "forge/mcp/forge_registry_mcp/server.py",
          description: "Meta MCP server exposing all forged MCPs and SKILL.md files to any AI Agent",
          tools: [
            { name: "list_forged_mcps", description: "List all MCP servers generated in Forge" },
            { name: "get_mcp_details", description: "Get details of a specific forged MCP by id" },
            { name: "get_skill", description: "Get the single SKILL.md for that workflow" },
            { name: "search_mcps", description: "Search forged MCPs by goal text or tool name" },
            { name: "export_mcp_to_platform", description: "Export MCP Server to AI IDEs" },
          ],
          platforms: {} as any,
          install_command:
            "codex mcp add forge-registry -- python forge/mcp/forge_registry_mcp/server.py",
        });
      });
  }, []);

  const activeExport = meta?.platforms?.[selectedPlatform];
  const isCurrentCli = PLATFORMS.find((p) => p.id === selectedPlatform)?.isCli ?? false;
  const activeCmd =
    activeExport?.command ||
    `codex mcp add forge-registry -- python ${meta?.server_path || "forge/mcp/forge_registry_mcp/server.py"}`;

  const jsonSnippet = activeExport?.config || {
    mcpServers: {
      "forge-registry": {
        command: "python",
        args: [meta?.server_path || "forge/mcp/forge_registry_mcp/server.py"],
      },
    },
  };

  const handleDropdownSelect = async (platform: PlatformKey) => {
    setSelectedPlatform(platform);
    setExportDropdownOpen(false);
    const platInfo = PLATFORMS.find((p) => p.id === platform);
    const platName = platInfo?.label || platform;

    const platExport = meta?.platforms?.[platform];
    const cmd = platExport?.command || `codex mcp add forge-registry -- python ${meta?.server_path || "forge/mcp/forge_registry_mcp/server.py"}`;
    const cfg = platExport?.config || {
      mcpServers: {
        "forge-registry": {
          command: "python",
          args: [meta?.server_path || "forge/mcp/forge_registry_mcp/server.py"],
        },
      },
    };

    if (platInfo?.isCli) {
      await copyText(cmd);
      showToast(`Exported to ${platName} — CLI command copied!`);
    } else {
      await copyText(JSON.stringify(cfg, null, 2));
      showToast(`Exported to ${platName} — JSON config copied!`);
    }
  };

  const handleCopyCmd = async () => {
    if (await copyText(activeCmd)) {
      setCopiedCmd(true);
      setTimeout(() => setCopiedCmd(false), 2000);
      showToast("Install command copied to clipboard!");
    }
  };

  const handleCopyJson = async () => {
    if (await copyText(JSON.stringify(jsonSnippet, null, 2))) {
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
      showToast("JSON configuration copied to clipboard!");
    }
  };

  return (
    <div className="mx-auto w-full max-w-5xl space-y-6">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-2 rounded-2xl bg-navy px-4 py-3 text-xs font-bold text-cream shadow-2xl ring-1 ring-gold/40 animate-bounce">
          <Zap className="h-4 w-4 text-gold shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-navy p-8 text-cream shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-gold/40 bg-gold/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-gold-soft">
              <Database className="h-3.5 w-3.5" /> Meta MCP Server
            </div>
            <h2 className="mt-3 font-display text-2xl font-bold tracking-tight text-cream sm:text-3xl">
              Custom Forge Registry MCP
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-cream/80">
              Install this meta MCP server once into your AI agent (Claude Code, Cursor, Zed, OpenCode, Antigravity, or Codex).
              Your agent can then query all MCP servers and SKILL.md workflows forged in Forge at any time.
            </p>
          </div>

          {/* 6-Way Export Dropdown */}
          <div className="relative shrink-0">
            <button
              type="button"
              onClick={() => setExportDropdownOpen(!exportDropdownOpen)}
              className="inline-flex items-center gap-2 rounded-2xl bg-gold px-5 py-3 font-display text-xs font-bold text-navy shadow-forge transition hover:bg-gold-deep hover:text-cream"
            >
              <Share2 className="h-4 w-4" /> Export Registry MCP <ChevronDown className="h-3.5 w-3.5" />
            </button>

            {exportDropdownOpen && (
              <div className="absolute right-0 top-full mt-2 z-40 w-52 rounded-2xl border border-navy/15 bg-white p-1.5 shadow-2xl ring-1 ring-black/10">
                <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-navy/40 border-b border-navy/5">
                  Export to 6 AI Platforms
                </div>
                {PLATFORMS.map((plat) => (
                  <button
                    key={plat.id}
                    type="button"
                    onClick={() => handleDropdownSelect(plat.id)}
                    className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-xs font-semibold text-navy hover:bg-gold/15 hover:text-gold-deep transition"
                  >
                    <span>{plat.label}</span>
                    <span className="rounded bg-navy/10 px-1 py-0.5 text-[9px] font-mono text-navy/60">
                      {plat.isCli ? "CLI" : "JSON"}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="absolute right-0 top-0 -mr-16 -mt-16 h-64 w-64 rounded-full bg-gold/10 blur-3xl pointer-events-none" />
      </div>

      {/* 6-Way Installation Cards */}
      <div className="rounded-3xl border border-navy/10 bg-white/80 p-6 shadow-card backdrop-blur-sm space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-navy/10 pb-4">
          <div>
            <h3 className="font-display text-base font-bold text-navy flex items-center gap-2">
              <Terminal className="h-4 w-4 text-gold-deep" />
              Platform Configuration ({PLATFORMS.find((p) => p.id === selectedPlatform)?.label})
            </h3>
            <p className="text-xs text-navy/55">
              Select your AI client to view and copy the exact setup
            </p>
          </div>

          {/* Platform Tabs */}
          <div className="flex flex-wrap gap-1 bg-cream/70 p-1 rounded-2xl border border-navy/10">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPlatform(p.id)}
                className={`rounded-xl px-3 py-1.5 font-display text-xs font-semibold transition ${
                  selectedPlatform === p.id
                    ? "bg-navy text-gold shadow-sm"
                    : "text-navy/70 hover:text-navy hover:bg-white/60"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Command Box (if CLI) */}
        {isCurrentCli && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-navy uppercase tracking-wider">
                Terminal Command
              </span>
              <button
                type="button"
                onClick={handleCopyCmd}
                className="inline-flex items-center gap-1.5 rounded-xl bg-gold px-3.5 py-1.5 font-display text-xs font-bold text-navy shadow-sm transition hover:bg-gold-deep hover:text-cream"
              >
                {copiedCmd ? <Check className="h-3.5 w-3.5 text-green-700" /> : <Copy className="h-3.5 w-3.5" />}
                {copiedCmd ? "Copied to Clipboard!" : "Copy Install Command"}
              </button>
            </div>
            <div className="rounded-2xl bg-navy p-4 shadow-inner">
              <code className="font-mono text-xs text-gold-soft break-all select-all leading-relaxed">
                {activeCmd}
              </code>
            </div>
          </div>
        )}

        {/* JSON Snippet */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-navy uppercase tracking-wider">
              Config Snippet ({activeExport?.config_file || "mcp.json"})
            </span>
            <button
              type="button"
              onClick={handleCopyJson}
              className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
                !isCurrentCli
                  ? "bg-gold text-navy font-bold hover:bg-gold-deep hover:text-cream shadow-sm"
                  : "border border-navy/20 bg-white text-navy hover:border-navy hover:bg-navy hover:text-cream"
              }`}
            >
              {copiedJson ? <Check className="h-3.5 w-3.5 text-green-600" /> : <Copy className="h-3.5 w-3.5" />}
              {copiedJson ? "Copied JSON!" : "Copy JSON"}
            </button>
          </div>
          <pre className="max-h-48 overflow-auto rounded-2xl bg-navy p-4 font-mono text-[11.5px] leading-relaxed text-cream/90 shadow-inner">
            <code>{JSON.stringify(jsonSnippet, null, 2)}</code>
          </pre>
        </div>
      </div>

      {/* Meta Tools Catalog */}
      <div className="rounded-3xl border border-navy/10 bg-white/80 p-6 shadow-card backdrop-blur-sm space-y-4">
        <h3 className="font-display text-base font-bold text-navy flex items-center gap-2">
          <Layers className="h-4 w-4 text-gold-deep" />
          Tools Provided by Forge Registry MCP
        </h3>
        <p className="text-xs text-navy/55">
          Once installed, your agent can autonomously invoke these tools:
        </p>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {meta?.tools.map((t) => (
            <div
              key={t.name}
              className="rounded-2xl border border-navy/10 bg-cream/30 p-4 transition hover:bg-white hover:shadow-card"
            >
              <div className="flex items-center gap-2">
                <Code2 className="h-4 w-4 text-gold-deep shrink-0" />
                <code className="font-mono text-xs font-bold text-navy">{t.name}</code>
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-navy/65">
                {t.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
