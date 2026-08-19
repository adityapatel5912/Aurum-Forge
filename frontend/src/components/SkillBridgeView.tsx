import { useState } from "react";
import { ArrowRightLeft, CheckCircle2, Copy, Download, FileCode, Layers, Sparkles, Upload } from "lucide-react";
import { copyText, downloadFile, exportUniversalBridge, importUniversalBridge } from "../api";

export default function SkillBridgeView() {
  const [mcpName, setMcpName] = useState("forge-aurum-hub");
  const [skillText, setSkillText] = useState("");
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importSkillInput, setImportSkillInput] = useState("");
  const [importResult, setImportResult] = useState<any>(null);
  const [mode, setMode] = useState<"export" | "import">("export");

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await exportUniversalBridge(mcpName);
      if (res.ok) {
        setSkillText(res.skill_content);
      }
    } catch (err) {
      console.error("Export bridge error:", err);
    } finally {
      setExporting(false);
    }
  };

  const handleImport = async () => {
    setImporting(true);
    try {
      const res = await importUniversalBridge(importSkillInput, "imported_workflow_mcp");
      setImportResult(res);
    } catch (err) {
      console.error("Import bridge error:", err);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 text-cream">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gold/20 pb-3">
        <div className="flex items-center gap-2">
          <ArrowRightLeft className="h-5 w-5 text-gold animate-pulse" />
          <h3 className="text-base font-bold tracking-wide text-cream">
            Universal Skill Bridge <span className="text-xs font-normal text-gold">(MCP ↔ Universal SKILL.md)</span>
          </h3>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setMode("export")}
            className={`rounded-lg px-2.5 py-1 text-xs font-semibold ${
              mode === "export"
                ? "border border-gold bg-gold/20 text-cream"
                : "border border-gold/20 bg-navy-light/40 text-cream/70"
            }`}
          >
            MCP → Universal Skill
          </button>
          <button
            onClick={() => setMode("import")}
            className={`rounded-lg px-2.5 py-1 text-xs font-semibold ${
              mode === "import"
                ? "border border-gold bg-gold/20 text-cream"
                : "border border-gold/20 bg-navy-light/40 text-cream/70"
            }`}
          >
            Skill → FastMCP Server
          </button>
        </div>
      </div>

      {mode === "export" ? (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between gap-3 rounded-lg border border-gold/20 bg-navy/80 p-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-gold">Target Server:</span>
              <input
                type="text"
                value={mcpName}
                onChange={(e) => setMcpName(e.target.value)}
                className="rounded border border-gold/20 bg-[#050C1A] px-2 py-1 font-mono text-xs text-cream outline-none focus:border-gold"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleExport}
                disabled={exporting}
                className="rounded-lg bg-gold px-3 py-1.5 text-xs font-bold text-navy hover:bg-gold-light hover:shadow-[0_0_12px_rgba(198,169,107,0.5)]"
              >
                {exporting ? "Synthesizing..." : "Generate Universal Skill & Zip"}
              </button>
              <button
                onClick={() => downloadFile("/api/download/unified-mcp.zip", "unified-mcp.zip")}
                className="flex items-center gap-1 rounded-lg border border-gold/40 bg-gold/10 px-3 py-1.5 text-xs font-bold text-gold hover:bg-gold/20"
                title="Download dist/unified-mcp.zip"
              >
                <Download className="h-3.5 w-3.5" />
                Download Zip
              </button>
            </div>
          </div>

          {/* IDE Compatibility Badges */}
          <div className="flex flex-wrap items-center gap-1.5 rounded-lg border border-gold/15 bg-navy-light/30 p-2 text-xs">
            <span className="text-cream/60">Universal Compatibility:</span>
            {["Google Antigravity", "Z Code (Zed)", "Claude Code", "Cursor", "Windsurf", "OpenCode", "Codex"].map((ide) => (
              <span key={ide} className="rounded border border-gold/30 bg-gold/10 px-2 py-0.5 text-[10px] font-semibold text-gold">
                {ide}
              </span>
            ))}
          </div>

          {/* Skill Content Preview */}
          {skillText && (
            <div className="flex flex-col gap-2 rounded-xl border border-gold/30 bg-navy/90 p-4 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gold">Universal SKILL.md (Saved at root /SKILL.md):</span>
                <button
                  onClick={() => {
                    copyText(skillText);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="flex items-center gap-1 rounded border border-gold/30 bg-gold/10 px-2 py-1 text-xs font-medium text-gold hover:bg-gold/20"
                >
                  <Copy className="h-3 w-3" />
                  {copied ? "Copied!" : "Copy SKILL.md"}
                </button>
              </div>
              <pre className="max-h-72 overflow-y-auto rounded-lg border border-gold/20 bg-[#050C1A] p-3 font-mono text-xs text-cream/90">
                {skillText}
              </pre>
            </div>
          )}
        </div>
      ) : (
        /* Reverse Mode: Skill -> MCP */
        <div className="flex flex-col gap-3 rounded-xl border border-gold/30 bg-navy/90 p-4 shadow-xl">
          <label className="text-xs font-semibold text-gold">Paste Universal SKILL.md to synthesize FastMCP Server:</label>
          <textarea
            rows={6}
            value={importSkillInput}
            onChange={(e) => setImportSkillInput(e.target.value)}
            placeholder="# Universal Skill: My Custom Workflow&#10;&#10;## FastMCP Tools&#10;- `query_database`: Query custom DB&#10;- `notify_slack`: Broadcast alerts"
            className="rounded border border-gold/20 bg-[#050C1A] p-2.5 font-mono text-xs text-cream outline-none focus:border-gold"
          />
          <button
            onClick={handleImport}
            disabled={importing || !importSkillInput.trim()}
            className="self-end rounded-lg bg-gold px-4 py-1.5 text-xs font-bold text-navy hover:bg-gold-light"
          >
            {importing ? "Synthesizing Server..." : "Reverse Synthesize FastMCP Server (AST Validated)"}
          </button>

          {importResult && (
            <div className="mt-2 flex flex-col gap-2 rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-3 text-xs">
              <div className="flex items-center gap-1.5 font-bold text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                Synthesized Server: {importResult.mcp_name} ({importResult.tools_count} Tools)
              </div>
              <div className="font-mono text-[11px] text-cream/80">Path: {importResult.server_path}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
