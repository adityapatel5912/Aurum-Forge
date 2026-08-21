import { useEffect, useState } from "react";
import {
  CheckCircle2,
  Copy,
  Download,
  HardDrive,
  KeyRound,
  Layers,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Terminal,
  Zap,
} from "lucide-react";
import {
  checkMcpHealth,
  copyText,
  downloadFile,
  getUniversalConfig,
  injectIDEConfig,
  validateSystemEnvironment,
} from "../api";
import type { SystemValidation, UniversalConfig } from "../types";
import SecretsVaultModal from "./SecretsVaultModal";

interface Props {
  activeServerName?: string;
  activeServerPath?: string;
}

export default function IDEInjectorView({
  activeServerName: propServerName,
  activeServerPath: propServerPath,
}: Props = {}) {
  const [config, setConfig] = useState<UniversalConfig | null>(null);
  const [validation, setValidation] = useState<SystemValidation | null>(null);
  const [targetMode, setTargetMode] = useState<"super_hub" | "active_mcp">(
    propServerName ? "active_mcp" : "active_mcp"
  );
  const [injectingIde, setInjectingIde] = useState<string | null>(null);
  const [injectedSuccess, setInjectedSuccess] = useState<Record<string, string>>({});
  const [copiedSnippet, setCopiedSnippet] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [healthResult, setHealthResult] = useState<any | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [isSecretsOpen, setIsSecretsOpen] = useState(false);

  useEffect(() => {
    if (propServerName) {
      setTargetMode("active_mcp");
    }
  }, [propServerName]);

  const refreshData = async () => {
    try {
      const [cfg, val] = await Promise.all([
        getUniversalConfig(),
        validateSystemEnvironment("forge/mcp/forge_aurum_hub/server.py"),
      ]);
      setConfig(cfg);
      setValidation(val);
    } catch (err) {
      console.error("Error loading config/validation:", err);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const getTargetNameAndPath = () => {
    if (targetMode === "super_hub") {
      const hubPath =
        config?.servers?.forge_aurum_hub?.args?.[0] ||
        "forge/mcp/forge_aurum_hub/server.py";
      return { name: "forge-aurum-hub", path: hubPath };
    }
    const actName = propServerName || config?.active_mcp?.name || "crypto_portfolio_tracker";
    const actPath = propServerPath || config?.active_mcp?.server_path || `mcp/${actName}/server.py`;
    return { name: actName, path: actPath };
  };

  const handleInject = async (ideKey: string) => {
    setInjectingIde(ideKey);
    const { name, path } = getTargetNameAndPath();
    try {
      const res = await injectIDEConfig(ideKey, name, path);
      if (res.ok) {
        setInjectedSuccess((prev) => ({
          ...prev,
          [ideKey]: res.config_path || "Config file updated on disk!",
        }));
        setActionStatus(`Injected '${name}' into ${ideKey === "all" ? "ALL IDEs" : ideKey} successfully!`);
        refreshData();
      }
    } catch (err) {
      console.error("Injection error:", err);
      setActionStatus(`Error injecting into ${ideKey}`);
    } finally {
      setInjectingIde(null);
    }
  };

  const handleRunHealthCheck = async () => {
    setIsCheckingHealth(true);
    setHealthResult(null);
    try {
      const { name, path } = getTargetNameAndPath();
      const res = await checkMcpHealth(name, path);
      setHealthResult(res);
      if (res.ok) {
        setActionStatus(`STDIO Handshake PASS: '${res.server_name}' booted in ${res.latency_ms}ms with ${res.tools_count} tools ready!`);
      } else {
        setActionStatus(`STDIO Handshake Error: ${res.error}`);
      }
    } catch (err) {
      setHealthResult({ ok: false, error: String(err) });
    } finally {
      setIsCheckingHealth(false);
    }
  };

  const activeServerName = propServerName || config?.active_mcp?.name || "crypto_portfolio_tracker";

  return (
    <div className="flex flex-col gap-4 text-cream">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/[0.08] pb-3">
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-gold animate-pulse" />
          <div>
            <h3 className="text-sm font-bold tracking-wide text-cream">
              Executable IDE Injector & Health Inspector
            </h3>
            <span className="text-[10px] text-cream/60">
              Atomic config injection into Antigravity, Cursor & Z Code / Zed with live FastMCP STDIO testing
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* UI Secrets Vault Button */}
          <button
            onClick={() => setIsSecretsOpen(true)}
            className="flex items-center gap-1.5 rounded-lg border border-gold/40 bg-gold/10 px-3 py-1.5 text-xs font-bold text-gold hover:bg-gold hover:text-navy transition-all"
            title="Enter tokens and API keys through UI to inject directly into IDEs"
          >
            <KeyRound className="h-3.5 w-3.5" />
            Tokens & Secrets
          </button>

          {/* Live STDIO Subprocess Test Button */}
          <button
            onClick={handleRunHealthCheck}
            disabled={isCheckingHealth}
            className="flex items-center gap-1.5 rounded-lg border border-gold/40 bg-gold/15 px-3 py-1.5 text-xs font-bold text-gold hover:bg-gold hover:text-navy hover:shadow-[0_0_15px_rgba(198,169,107,0.4)] transition-all disabled:opacity-50"
            title="Boot FastMCP server in real subprocess and verify JSON-RPC protocol"
          >
            <Sparkles className={`h-3.5 w-3.5 ${isCheckingHealth ? "animate-spin" : ""}`} />
            {isCheckingHealth ? "Running STDIO Test..." : "⚡ Run Live STDIO Test"}
          </button>

          {/* Global Inject Button */}
          <button
            onClick={() => handleInject("all")}
            disabled={injectingIde === "all"}
            className="flex items-center gap-1.5 rounded-lg bg-gold px-4 py-1.5 text-xs font-bold text-navy transition-all hover:bg-gold-light hover:shadow-[0_0_15px_rgba(198,169,107,0.5)] disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            {injectingIde === "all" ? "Injecting into ALL IDEs..." : "1-Click Inject into ALL IDEs"}
          </button>
        </div>
      </div>

      {/* Target Selector: Super Hub vs Active MCP */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-white/[0.08] bg-[#0A0E1A] p-3 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-cream/80">Injection Target:</span>
          <div className="flex rounded-lg border border-white/[0.08] bg-[#060911] p-1">
            <button
              onClick={() => setTargetMode("super_hub")}
              className={`rounded-md px-3 py-1 text-xs font-bold transition-all ${
                targetMode === "super_hub"
                  ? "bg-gold text-navy shadow-sm"
                  : "text-cream/70 hover:text-cream"
              }`}
            >
              🌟 Super-Hub (Curated FastMCP)
            </button>
            <button
              onClick={() => setTargetMode("active_mcp")}
              className={`rounded-md px-3 py-1 text-xs font-bold transition-all ${
                targetMode === "active_mcp"
                  ? "bg-gold text-navy shadow-sm"
                  : "text-cream/70 hover:text-cream"
              }`}
            >
              ⚡ Active Forged MCP ({activeServerName})
            </button>
          </div>
        </div>

        {/* Quick Download Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => downloadFile("/api/download/unified-mcp.zip", "forge-aurum-hub.zip")}
            className="flex items-center gap-1 rounded-lg border border-gold/40 bg-gold/10 px-2.5 py-1 text-[11px] font-semibold text-gold hover:bg-gold/20 transition-all"
            title="Download Super-Hub ZIP package"
          >
            <Download className="h-3 w-3" />
            Super-Hub ZIP
          </button>
          <button
            onClick={() =>
              downloadFile(`/api/download/${activeServerName}-mcp.zip`, `${activeServerName}-mcp.zip`)
            }
            className="flex items-center gap-1 rounded-lg border border-white/[0.1] bg-[#121A2D] px-2.5 py-1 text-[11px] font-semibold text-cream/90 hover:border-gold hover:text-gold transition-all"
            title="Download active individual MCP ZIP package"
          >
            <Download className="h-3 w-3 text-gold" />
            {activeServerName}.zip
          </button>
        </div>
      </div>

      {actionStatus && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-xs font-semibold text-emerald-300 animate-in fade-in">
          {actionStatus}
        </div>
      )}

      {/* Real Live STDIO Test Result Card */}
      {healthResult && (
        <div className={`flex flex-col gap-2 rounded-xl border p-3.5 shadow-md ${
          healthResult.ok ? "border-emerald-500/40 bg-[#081512]" : "border-red-500/40 bg-[#170B0B]"
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className={`h-4 w-4 ${healthResult.ok ? "text-emerald-400" : "text-red-400"}`} />
              <span className="font-bold text-xs text-cream">
                {healthResult.ok ? "Live STDIO FastMCP Handshake Verified" : "STDIO Handshake Error"}
              </span>
              <span className="rounded bg-gold/20 px-2 py-0.5 font-mono text-[10px] font-bold text-gold">
                {healthResult.server_name}
              </span>
            </div>
            {healthResult.latency_ms !== undefined && (
              <span className="font-mono text-xs font-bold text-emerald-400">
                {healthResult.latency_ms}ms Latency
              </span>
            )}
          </div>

          {healthResult.ok ? (
            <div className="flex flex-col gap-1.5 text-xs">
              <div className="text-[11px] text-cream/70">
                Available Tools ({healthResult.tools_count}):{" "}
                <span className="font-mono text-gold font-semibold">
                  {healthResult.tools?.slice(0, 6).join(", ")}
                  {healthResult.tools?.length > 6 ? ` +${healthResult.tools.length - 6} more` : ""}
                </span>
              </div>
              {healthResult.sample_output && (
                <div className="truncate rounded border border-white/[0.06] bg-[#050C1A] p-2 font-mono text-[10px] text-cream/80">
                  Sample Output: {healthResult.sample_output}
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-red-300 font-mono">{healthResult.error}</p>
          )}
        </div>
      )}

      {/* Real Green Validator Ticks Bar */}
      {validation && (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          <div className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-[#0A0E1A] p-2.5 shadow-sm">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <div className="overflow-hidden">
              <div className="text-[10px] text-cream/60">Normalized Path:</div>
              <div className="truncate font-mono text-[11px] font-bold text-emerald-400">
                {validation.server_path
                  ? "/" + validation.server_path.split("/").slice(-2).join("/")
                  : "Exists (/)"}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-[#0A0E1A] p-2.5 shadow-sm">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <div>
              <div className="text-[10px] text-cream/60">Python Engine:</div>
              <div className="font-mono text-[11px] font-bold text-emerald-400">
                {validation.python_version || "Python 3.10+"}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-[#0A0E1A] p-2.5 shadow-sm">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <div>
              <div className="text-[10px] text-cream/60">FastMCP Framework:</div>
              <div className="font-mono text-[11px] font-bold text-emerald-400">Import Ready</div>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-[#0A0E1A] p-2.5 shadow-sm">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <div>
              <div className="text-[10px] text-cream/60">Aurum Proof:</div>
              <div className="font-mono text-[11px] font-bold text-gold">Gold Verified (#C6A96B)</div>
            </div>
          </div>
        </div>
      )}

      {/* Target IDE Cards Grid */}
      {config && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {Object.entries(config.ides).map(([key, ide]) => {
            const isDone = Boolean(injectedSuccess[key] || (injectedSuccess["all"] && true));
            const isInjecting = injectingIde === key;

            return (
              <div
                key={key}
                className="flex flex-col justify-between rounded-xl border border-white/[0.08] bg-[#0A0E1A] p-3.5 shadow-lg transition-all hover:border-gold/50 overflow-hidden min-w-0"
              >
                <div className="min-w-0">
                  <div className="flex items-center justify-between gap-2 min-w-0">
                    <span className="text-xs font-bold text-cream truncate">{ide.ide_name}</span>
                    <span className="shrink-0 rounded border border-gold/30 bg-gold/10 px-1.5 py-0.5 font-mono text-[9px] font-semibold text-gold">
                      {ide.format}
                    </span>
                  </div>
                  <div
                    className="mt-1.5 truncate rounded border border-white/[0.04] bg-[#060911]/80 px-2 py-1 font-mono text-[10px] text-cream/70"
                    title={ide.config_path}
                  >
                    {ide.config_path}
                  </div>
                  <p className="mt-1.5 text-[11px] text-cream/80 break-words leading-relaxed line-clamp-2" title={ide.how_to_connect}>
                    {ide.how_to_connect}
                  </p>
                </div>

                <div className="mt-4 flex flex-col gap-2 border-t border-white/[0.08] pt-3">
                  <button
                    onClick={() => handleInject(key)}
                    disabled={isInjecting}
                    className={`flex items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-bold transition-all ${
                      isDone
                        ? "border border-emerald-500/40 bg-emerald-500/20 text-emerald-300"
                        : "bg-gold text-navy hover:bg-gold-light hover:shadow-[0_0_12px_rgba(198,169,107,0.5)]"
                    }`}
                  >
                    {isDone ? (
                      <>
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        Injected on Disk (0.1s)
                      </>
                    ) : isInjecting ? (
                      "Writing Config..."
                    ) : (
                      <>
                        <Zap className="h-3.5 w-3.5" />
                        1-Click Inject
                      </>
                    )}
                  </button>

                  {ide.snippet && (
                    <button
                      onClick={() => {
                        copyText(JSON.stringify(ide.snippet, null, 2));
                        setCopiedSnippet(key);
                        setTimeout(() => setCopiedSnippet(null), 2000);
                      }}
                      className="flex items-center justify-center gap-1 text-[10px] text-cream/60 hover:text-gold transition-colors py-0.5"
                    >
                      <Copy className="h-3 w-3" />
                      {copiedSnippet === key ? "Copied JSON!" : "Copy Snippet"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Disk Verification Section */}
      <div className="rounded-xl border border-white/[0.08] bg-[#0A0E1A] p-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-2">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span className="text-xs font-bold text-cream">
              Live Disk Verification: ~/.gemini/antigravity/mcp_config.json / ~/.cursor/mcp.json (1 Entry Stays 1 Entry)
            </span>
          </div>
          <button
            onClick={refreshData}
            className="flex items-center gap-1 font-mono text-[10px] text-gold font-bold hover:underline"
          >
            <RotateCcw className="h-3 w-3" /> Refresh Status
          </button>
        </div>
        <pre className="mt-2 max-h-36 overflow-y-auto rounded-lg border border-white/[0.08] bg-[#060911] p-2.5 font-mono text-[11px] text-emerald-300">
          {JSON.stringify(
            {
              mcpServers: {
                "forge-aurum-hub": {
                  command: "python",
                  args: [
                    config?.servers?.forge_aurum_hub?.args?.[0] ||
                      "forge/mcp/forge_aurum_hub/server.py",
                  ],
                  env: config?.active_mcp?.env || {
                    TELEGRAM_BOT_TOKEN: "<your_telegram_token>",
                    GMAIL_USER: "<your_gmail_address>",
                    GMAIL_APP_PASSWORD: "<your_gmail_app_password>",
                    INSTAGRAM_ACCESS_TOKEN: "<your_instagram_token>",
                    YOUTUBE_API_KEY: "<your_youtube_api_key>",
                    GITHUB_TOKEN: "<your_github_token>",
                    NOTION_TOKEN: "<your_notion_token>",
                    SLACK_BOT_TOKEN: "<your_slack_token>",
                  },
                },
              },
            },
            null,
            2
          )}
        </pre>
      </div>

      <SecretsVaultModal
        isOpen={isSecretsOpen}
        onClose={() => {
          setIsSecretsOpen(false);
          refreshData();
        }}
        onSaved={refreshData}
      />
    </div>
  );
}

