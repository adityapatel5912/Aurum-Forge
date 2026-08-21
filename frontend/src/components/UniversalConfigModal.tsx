import { useEffect, useState } from "react";
import {
  Check,
  CheckCircle2,
  Code2,
  Copy,
  Cpu,
  Download,
  ExternalLink,
  Layers,
  Sparkles,
  Terminal,
  X,
  XCircle,
  Zap,
} from "lucide-react";
import {
  copyText,
  getUniversalConfig,
  injectIDEConfig,
  validateSystemEnvironment,
} from "../api";
import type { SystemValidation, UniversalConfig } from "../types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  serverPath?: string;
  mcpName?: string;
}

type IDEKey =
  | "cursor"
  | "antigravity"
  | "codex"
  | "z_code";

export default function UniversalConfigModal({
  isOpen,
  onClose,
  serverPath,
  mcpName = "forge-factory",
}: Props) {
  const [activeIDE, setActiveIDE] = useState<IDEKey>("cursor");
  const [config, setConfig] = useState<UniversalConfig | null>(null);
  const [validation, setValidation] = useState<SystemValidation | null>(null);
  const [copied, setCopied] = useState(false);
  const [injecting, setInjecting] = useState<string | null>(null);
  const [injectStatus, setInjectStatus] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (isOpen) {
      getUniversalConfig()
        .then(setConfig)
        .catch(() => setConfig(null));
      validateSystemEnvironment(serverPath)
        .then(setValidation)
        .catch(() => setValidation(null));
    }
  }, [isOpen, serverPath]);

  if (!isOpen) return null;

  const currentItem = config?.ides?.[activeIDE];
  const cleanServerPath = (serverPath || config?.active_mcp.server_path || "").replace(/\\/g, "/");

  const handleCopy = async (text: string) => {
    await copyText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2400);
  };

  const handleAutoInject = async (ideKey: string) => {
    setInjecting(ideKey);
    try {
      const res = await injectIDEConfig(ideKey, mcpName, cleanServerPath);
      if (res.ok) {
        setInjectStatus((prev) => ({ ...prev, [ideKey]: true }));
      }
    } catch {
      setInjectStatus((prev) => ({ ...prev, [ideKey]: false }));
    } finally {
      setInjecting(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/60 p-4 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-navy/20 bg-cream font-sans shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-navy/10 bg-white/70 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-navy text-gold shadow-md">
              <Code2 className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-display text-lg font-bold text-navy">
                Universal IDE Config Hub
              </h2>
              <p className="text-xs text-navy/55">
                Connect FastMCP into Cursor, Antigravity, Codex, or Z Code in seconds &bull; Normalized '/' Paths
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-2 text-navy/50 hover:bg-navy/5 hover:text-navy"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Live System Validator Bar */}
        <div className="border-b border-navy/10 bg-navy/5 px-6 py-3">
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-4">
              <span className="font-bold text-navy">System Status:</span>

              <div className="flex items-center gap-1.5">
                {validation?.path_exists ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                ) : (
                  <XCircle className="h-4 w-4 text-amber-600" />
                )}
                <span className="text-navy/70">Server Path Verified</span>
              </div>

              <div className="flex items-center gap-1.5">
                {validation?.python_available ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-600" />
                )}
                <span className="text-navy/70">Python {validation?.python_version || "3.x"}</span>
              </div>

              <div className="flex items-center gap-1.5">
                {validation?.fastmcp_ready ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                ) : (
                  <XCircle className="h-4 w-4 text-amber-600" />
                )}
                <span className="text-navy/70">FastMCP Ready</span>
              </div>
            </div>

            <button
              onClick={() => handleAutoInject("all")}
              disabled={injecting !== null}
              className="inline-flex items-center gap-1.5 rounded-xl bg-gold px-3.5 py-1.5 font-display text-xs font-bold text-navy shadow-sm transition hover:bg-gold-deep hover:text-cream disabled:opacity-50"
            >
              <Zap className="h-3.5 w-3.5" />
              {injecting === "all" ? "Injecting All..." : "1-Click Auto-Inject All IDEs"}
            </button>
          </div>
        </div>

        {/* IDE Selector Tabs */}
        <div className="flex flex-wrap gap-2 border-b border-navy/10 bg-cream/50 px-6 py-3">
          {[
            { id: "cursor", label: "Cursor", badge: "IDE" },
            { id: "antigravity", label: "Antigravity", badge: "Google" },
            { id: "codex", label: "Codex", badge: "CLI" },
            { id: "z_code", label: "Z Code (Zed)", badge: "Fast" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveIDE(item.id as IDEKey)}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 font-display text-xs font-bold transition ${
                activeIDE === item.id
                  ? "bg-navy text-gold shadow-sm"
                  : "bg-white/70 text-navy/65 hover:bg-white hover:text-navy"
              }`}
            >
              <span>{item.label}</span>
              <span
                className={`rounded-md px-1.5 py-0.5 text-[9px] ${
                  activeIDE === item.id ? "bg-white/20 text-cream" : "bg-navy/10 text-navy/60"
                }`}
              >
                {item.badge}
              </span>
            </button>
          ))}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {currentItem ? (
            <>
              {/* How to Connect Box */}
              <div className="rounded-2xl border border-navy/10 bg-white/80 p-4 shadow-sm">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-gold-deep" />
                    <h4 className="font-display text-xs font-bold uppercase tracking-wider text-navy">
                      How to Connect in {currentItem.ide_name}
                    </h4>
                  </div>
                  <button
                    onClick={() => handleAutoInject(activeIDE)}
                    disabled={injecting === activeIDE}
                    className="inline-flex items-center gap-1 rounded-lg bg-navy px-3 py-1 font-display text-[11px] font-bold text-cream hover:bg-navy-light disabled:opacity-50"
                  >
                    <Zap className="h-3 w-3 text-gold" />
                    {injecting === activeIDE
                      ? "Injecting..."
                      : injectStatus[activeIDE]
                      ? "Injected! Re-inject"
                      : `1-Click Inject into ${currentItem.ide_name}`}
                  </button>
                </div>
                <p className="mt-2 whitespace-pre-line text-xs font-medium text-navy/70 leading-relaxed">
                  {currentItem.how_to_connect}
                </p>
                <div className="mt-2 flex items-center gap-2 text-[11px] font-mono text-navy/50">
                  <span>Target Config:</span>
                  <span className="bg-navy/5 px-2 py-0.5 rounded text-navy/80 truncate">
                    {currentItem.config_path}
                  </span>
                </div>
              </div>

              {/* Code Snippet / CLI Command */}
              {currentItem.is_cli && currentItem.cli_command ? (
                <div className="space-y-2">
                  <label className="font-display text-xs font-bold uppercase tracking-wider text-navy/70">
                    Terminal Command (Run once)
                  </label>
                  <div className="relative flex items-center rounded-2xl border border-navy/15 bg-navy p-4 text-cream shadow-inner font-mono text-xs">
                    <Terminal className="h-4 w-4 text-gold mr-3 shrink-0" />
                    <span className="truncate">{currentItem.cli_command}</span>
                    <button
                      onClick={() => handleCopy(currentItem.cli_command || "")}
                      className="ml-auto rounded-lg bg-white/10 px-3 py-1.5 text-xs font-bold text-cream hover:bg-white/20 transition flex items-center gap-1"
                    >
                      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                      {copied ? "Copied" : "Copy"}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="font-display text-xs font-bold uppercase tracking-wider text-navy/70">
                      Configuration JSON Snippet
                    </label>
                    <button
                      onClick={() =>
                        handleCopy(JSON.stringify(currentItem.snippet || {}, null, 2))
                      }
                      className="inline-flex items-center gap-1 text-xs font-bold text-navy hover:text-gold-deep"
                    >
                      {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                      {copied ? "Copied to Clipboard!" : "Copy JSON"}
                    </button>
                  </div>
                  <pre className="max-h-60 overflow-x-auto rounded-2xl border border-navy/15 bg-navy p-4 font-mono text-xs text-cream shadow-inner leading-relaxed">
                    {JSON.stringify(currentItem.snippet || {}, null, 2)}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <p className="text-xs text-navy/50">Loading universal configuration...</p>
          )}

          {/* Root File Notice */}
          <div className="rounded-2xl border border-gold/30 bg-gold/10 p-4 text-xs text-navy/80 leading-relaxed">
            <span className="font-bold text-navy">Single Universal Config File: </span>
            This configuration is saved at <code className="font-mono text-navy font-bold">forge.mcp.json</code> at your workspace root.
            You can also run <code className="font-mono text-navy font-bold">export.bat</code> (Windows) or <code className="font-mono text-navy font-bold">bash export.sh</code> (macOS/Linux) to configure your environment automatically!
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-navy/10 bg-white/70 px-6 py-4">
          <span className="text-xs font-mono text-navy/50">
            forge.mcp.json v2.0 &bull; Normalized Posix Paths
          </span>
          <button
            onClick={onClose}
            className="rounded-2xl bg-navy px-5 py-2.5 font-display text-xs font-bold text-cream shadow-md hover:bg-navy-light transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
