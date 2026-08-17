import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Copy, Terminal, FileCode2, X, Sparkles, AlertCircle } from "lucide-react";
import { copyText } from "../api";
import type { PlatformExport, PlatformKey } from "../types";

const PLATFORMS: { id: PlatformKey; label: string; iconLabel: string; isCli: boolean }[] = [
  { id: "claude_code", label: "Claude Code", iconLabel: "CC", isCli: true },
  { id: "cursor", label: "Cursor", iconLabel: "CU", isCli: false },
  { id: "zcode", label: "Z Code (Zed)", iconLabel: "ZD", isCli: false },
  { id: "opencode", label: "OpenCode", iconLabel: "OC", isCli: true },
  { id: "antigravity", label: "Antigravity", iconLabel: "AG", isCli: false },
  { id: "codex", label: "Codex", iconLabel: "CX", isCli: true },
];

interface Props {
  isOpen: boolean;
  onClose: () => void;
  mcpName: string;
  serverPath: string;
  initialPlatform?: PlatformKey;
  exportConfigs?: Record<string, PlatformExport>;
}

export default function ExportModal({
  isOpen,
  onClose,
  mcpName,
  serverPath,
  initialPlatform = "claude_code",
  exportConfigs,
}: Props) {
  const [activePlatform, setActivePlatform] = useState<PlatformKey>(initialPlatform);
  const [copiedCmd, setCopiedCmd] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);

  if (!isOpen) return null;

  const cleanPath = serverPath.replace(/\\/g, "/");
  const platformMeta = PLATFORMS.find((p) => p.id === activePlatform) || PLATFORMS[0];
  const isCli = exportConfigs?.[activePlatform]?.is_cli ?? platformMeta.isCli;

  const configObj = exportConfigs?.[activePlatform]?.config ?? {
    mcpServers: {
      [mcpName]: {
        command: "python",
        args: [cleanPath],
        env: {
          NOTION_TOKEN: "<your_notion_token>",
          GMAIL_USER: "<your_gmail_address>",
          GMAIL_APP_PASSWORD: "<your_gmail_app_password>",
        },
      },
    },
  };

  const getCommand = (): string | null => {
    if (exportConfigs?.[activePlatform]?.command) return exportConfigs[activePlatform].command;
    if (isCli) {
      if (activePlatform === "claude_code") return `claude mcp add ${mcpName} -- python ${cleanPath}`;
      if (activePlatform === "codex") return `codex mcp add ${mcpName} -- python ${cleanPath}`;
      if (activePlatform === "opencode") return `opencode mcp add ${mcpName} -- python ${cleanPath}`;
    }
    return null;
  };

  const getConfigPath = (): string => {
    if (exportConfigs?.[activePlatform]?.config_path) return exportConfigs[activePlatform].config_path!;
    switch (activePlatform) {
      case "claude_code":
        return "%APPDATA%/Claude/claude_desktop_config.json";
      case "cursor":
        return ".cursor/mcp.json (in project root or global settings)";
      case "zcode":
        return "~/.config/zed/settings.json (under context_servers)";
      case "opencode":
        return "opencode_mcp.json";
      case "antigravity":
        return "~/.config/antigravity/mcp.json";
      case "codex":
        return "codex_mcp.json";
      default:
        return "mcp.json";
    }
  };

  const activeCmd = getCommand();
  const jsonText = JSON.stringify(configObj, null, 2);

  const handleCopyCmd = async () => {
    if (activeCmd && (await copyText(activeCmd))) {
      setCopiedCmd(true);
      setTimeout(() => setCopiedCmd(false), 2000);
    }
  };

  const handleCopyJson = async () => {
    if (await copyText(jsonText)) {
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/60 p-4 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          className="relative flex max-h-[90vh] w-full max-w-2xl flex-col rounded-3xl border border-navy/15 bg-cream shadow-2xl overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-navy/10 bg-white/80 px-6 py-4 backdrop-blur">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold/20 text-gold-deep">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-display text-lg font-bold text-navy">
                  Export MCP Server
                </h3>
                <p className="text-xs text-navy/55">
                  1-Click configuration for 6 AI coding platforms
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="rounded-xl p-2 text-navy/40 hover:bg-navy/5 hover:text-navy transition"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Platform selection pills */}
          <div className="flex flex-wrap gap-1.5 border-b border-navy/10 bg-white/40 px-6 py-3">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => setActivePlatform(p.id)}
                className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 font-display text-xs font-semibold transition ${
                  activePlatform === p.id
                    ? "bg-navy text-gold shadow-sm"
                    : "bg-white/80 text-navy/70 hover:bg-white hover:text-navy border border-navy/10"
                }`}
              >
                <span className="flex h-4 w-4 items-center justify-center rounded bg-gold/20 text-[9px] font-bold text-gold-deep">
                  {p.iconLabel}
                </span>
                {p.label}
                {p.isCli ? (
                  <span className="rounded bg-navy/10 px-1 py-0.2 text-[8.5px] font-mono text-navy/60">CLI</span>
                ) : (
                  <span className="rounded bg-gold/20 px-1 py-0.2 text-[8.5px] font-mono text-gold-deep">JSON</span>
                )}
              </button>
            ))}
          </div>

          {/* Content Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Terminal Command Box (Only if platform has CLI) */}
            {isCli && activeCmd && (
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-xs font-bold text-navy uppercase tracking-wider">
                    <Terminal className="h-3.5 w-3.5 text-gold-deep" /> CLI Terminal Command
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyCmd}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-gold px-3 py-1 text-xs font-bold text-navy shadow-sm transition hover:bg-gold-deep hover:text-cream"
                  >
                    {copiedCmd ? <Check className="h-3.5 w-3.5 text-green-700" /> : <Copy className="h-3.5 w-3.5" />}
                    {copiedCmd ? "Command Copied!" : "Copy Command"}
                  </button>
                </div>
                <div className="rounded-2xl bg-navy p-3.5 shadow-inner">
                  <code className="font-mono text-xs text-gold-soft break-all select-all leading-relaxed">
                    {activeCmd}
                  </code>
                </div>
                <p className="mt-1.5 text-[11px] text-navy/55">
                  Paste and execute in your terminal to register `{mcpName}` with {platformMeta.label}.
                </p>
              </div>
            )}

            {/* Non-CLI notice */}
            {!isCli && (
              <div className="flex items-start gap-2.5 rounded-2xl border border-gold/40 bg-gold/10 p-3.5 text-xs text-navy/80">
                <AlertCircle className="h-4 w-4 text-gold-deep shrink-0 mt-0.5" />
                <div>
                  <strong className="text-navy">{platformMeta.label} uses file-based MCP configuration.</strong>
                  <p className="mt-0.5 text-[11.5px] text-navy/70">
                    Copy the JSON block below into <code className="bg-white/70 px-1 py-0.5 rounded font-mono text-navy font-bold">{getConfigPath()}</code> and reload.
                  </p>
                </div>
              </div>
            )}

            {/* JSON Config Box */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <span className="flex items-center gap-1.5 text-xs font-bold text-navy uppercase tracking-wider">
                    <FileCode2 className="h-3.5 w-3.5 text-gold-deep" /> JSON Configuration Snippet
                  </span>
                  <p className="text-[10.5px] text-navy/50 font-mono mt-0.5">
                    {getConfigPath()}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleCopyJson}
                  className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition ${
                    !isCli
                      ? "bg-gold text-navy font-bold hover:bg-gold-deep hover:text-cream shadow-sm"
                      : "border border-navy/20 bg-white text-navy hover:border-navy hover:bg-navy hover:text-cream"
                  }`}
                >
                  {copiedJson ? <Check className="h-3.5 w-3.5 text-green-600" /> : <Copy className="h-3.5 w-3.5" />}
                  {copiedJson ? "JSON Copied!" : "Copy JSON"}
                </button>
              </div>
              <pre className="max-h-52 overflow-auto rounded-2xl bg-navy p-3.5 font-mono text-[11.5px] leading-relaxed text-cream/90 shadow-inner">
                <code>{jsonText}</code>
              </pre>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-navy/10 bg-white/80 px-6 py-3.5">
            <span className="text-xs font-medium text-navy/60">
              Server: <strong className="text-navy">{mcpName}</strong>
            </span>
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl bg-navy px-5 py-2 text-xs font-bold text-cream transition hover:bg-navy/80"
            >
              Done
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
