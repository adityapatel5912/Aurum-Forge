import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Code2,
  FileCode,
  Flame,
  Play,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Wrench,
  Zap,
} from "lucide-react";
import { triggerSelfHeal } from "../api";
import type { SelfHealResult } from "../types";

export default function SelfHealStudio() {
  const [errorLog, setErrorLog] = useState(
    `Runtime Warning: Duplicate return detected in search_ram tool function.\nSyntaxNotice: Windows backslash unescaped in path: D:\\Aditya\\Forge\\mcp_registry\\servers\\unified-mcp\\server.py`
  );
  const [serverPath, setServerPath] = useState("");
  const [healing, setHealing] = useState(false);
  const [result, setResult] = useState<SelfHealResult | null>(null);

  const handleRunSelfHeal = async () => {
    setHealing(true);
    try {
      const res = await triggerSelfHeal(serverPath, errorLog);
      setResult(res);
    } catch (err) {
      setResult({
        ok: false,
        server_path: serverPath,
        errors_detected: [String(err)],
        patches_applied: [],
        code_modified: false,
        compilation_verified: false,
        diff: "",
        elapsed_ms: 0,
        message: `Self-heal failure: ${String(err)}`,
      });
    } finally {
      setHealing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-navy/15 bg-gradient-to-br from-navy via-navy to-navy-light p-8 text-cream shadow-card">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-gold/20 px-3 py-1 text-[11px] font-bold tracking-wider text-gold uppercase mb-3">
              <ShieldCheck className="h-3.5 w-3.5" /> Autonomous Code Repair Engine
            </div>
            <h2 className="font-display text-2xl font-bold tracking-tight text-cream sm:text-3xl">
              Self-Healing & AST Diagnostic Studio
            </h2>
            <p className="mt-2 text-sm text-cream/70 leading-relaxed">
              Diagnose runtime stderr and Inspector logs in &lt;200ms. Automatically eliminates duplicate return bugs, fixes Windows backslash paths, sanitizes FastMCP imports, and verifies with strict py_compile before saving.
            </p>
          </div>

          <button
            onClick={handleRunSelfHeal}
            disabled={healing}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gold px-5 py-3.5 font-display text-xs font-bold uppercase tracking-wider text-navy shadow-forge transition hover:bg-gold-deep hover:text-cream disabled:opacity-50 shrink-0"
          >
            <Wrench className="h-4 w-4" />
            {healing ? "Diagnosing & Healing..." : "Run Auto Self-Heal (<200ms)"}
          </button>
        </div>
      </div>

      {/* Main Grid: Input & Diagnostic Output */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left Column: Log Ingestion */}
        <div className="flex flex-col gap-4 rounded-3xl border border-navy/10 bg-white/90 p-6 shadow-card backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileCode className="h-4 w-4 text-navy" />
              <h3 className="font-display text-xs font-bold uppercase tracking-wider text-navy">
                Inspector / Runtime Stderr Log
              </h3>
            </div>
            <button
              onClick={() =>
                setErrorLog(
                  `Runtime Warning: Duplicate return detected in search_ram tool function.\nSyntaxNotice: Windows backslash unescaped in path: D:\\Aditya\\Forge\\mcp_registry\\servers\\unified-mcp\\server.py`
                )
              }
              className="text-[11px] font-bold text-gold-deep hover:underline"
            >
              Reset Sample Log
            </button>
          </div>

          <textarea
            rows={6}
            value={errorLog}
            onChange={(e) => setErrorLog(e.target.value)}
            placeholder="Paste MCP Inspector errors, Python tracebacks, or timeout notices here..."
            className="w-full rounded-2xl border border-navy/15 bg-navy/5 p-4 font-mono text-xs text-navy focus:border-gold focus:outline-none leading-relaxed"
          />

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-navy/70 mb-1">
              Target Server File Path (Optional — defaults to active unified server)
            </label>
            <input
              type="text"
              value={serverPath}
              onChange={(e) => setServerPath(e.target.value)}
              placeholder="e.g. D:/Aditya/Forge/mcp_registry/servers/unified-mcp/server.py"
              className="w-full rounded-2xl border border-navy/15 bg-white p-3 text-xs font-medium text-navy focus:border-gold focus:outline-none"
            />
          </div>

          <button
            onClick={handleRunSelfHeal}
            disabled={healing}
            className="mt-2 inline-flex items-center justify-center gap-2 rounded-2xl bg-navy px-5 py-3 font-display text-xs font-bold uppercase tracking-wider text-cream shadow-md hover:bg-navy-light hover:text-gold disabled:opacity-50"
          >
            <Zap className="h-3.5 w-3.5 text-gold" />
            {healing ? "Analyzing AST..." : "Inspect & Apply Auto-Patches"}
          </button>
        </div>

        {/* Right Column: Diagnostic Results */}
        <div className="flex flex-col gap-4 rounded-3xl border border-navy/10 bg-white/90 p-6 shadow-card backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-xs font-bold uppercase tracking-wider text-navy">
              Diagnostic & Patch Verification
            </h3>
            {result && (
              <span className="rounded-full bg-emerald-100 px-3 py-1 font-mono text-[10px] font-bold text-emerald-800">
                Completed in {result.elapsed_ms}ms
              </span>
            )}
          </div>

          {result ? (
            <div className="space-y-4">
              {/* Status Banner */}
              <div
                className={`rounded-2xl border p-4 text-xs font-medium ${
                  result.ok
                    ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                    : "border-red-200 bg-red-50 text-red-900"
                }`}
              >
                <div className="flex items-center gap-2 font-bold">
                  {result.ok ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  )}
                  <span>{result.message}</span>
                </div>
                {result.compilation_verified && (
                  <p className="mt-1 text-[11px] text-emerald-700 font-mono">
                    &bull; py_compile strict verification passed with 0 syntax errors.
                  </p>
                )}
              </div>

              {/* Errors Detected */}
              {result.errors_detected.length > 0 && (
                <div>
                  <span className="font-display text-[11px] font-bold uppercase tracking-wider text-navy/70">
                    Anomalies Detected ({result.errors_detected.length})
                  </span>
                  <ul className="mt-1.5 space-y-1">
                    {result.errors_detected.map((err, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 rounded-xl bg-amber-50 px-3 py-1.5 text-xs text-amber-900 border border-amber-200/60"
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-amber-500 shrink-0" />
                        <span>{err}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Patches Applied */}
              {result.patches_applied.length > 0 && (
                <div>
                  <span className="font-display text-[11px] font-bold uppercase tracking-wider text-navy/70">
                    Auto-Patches Applied ({result.patches_applied.length})
                  </span>
                  <ul className="mt-1.5 space-y-1">
                    {result.patches_applied.map((patch, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-1.5 text-xs text-emerald-900 border border-emerald-200/60"
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                        <span>{patch}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-56 flex-col items-center justify-center rounded-2xl border border-dashed border-navy/15 bg-cream/30 p-6 text-center">
              <Sparkles className="h-8 w-8 text-gold mb-2" />
              <p className="font-display text-xs font-bold text-navy/70">Ready to Heal</p>
              <p className="text-[11px] text-navy/50 mt-1 max-w-xs">
                Click &quot;Inspect &amp; Apply Auto-Patches&quot; to test autonomous AST error diagnosis and atomic compilation.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Code Diff Viewer */}
      {result?.diff && (
        <div className="overflow-hidden rounded-3xl border border-navy/15 bg-navy shadow-card text-cream">
          <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-6 py-3.5">
            <div className="flex items-center gap-2">
              <Code2 className="h-4 w-4 text-gold" />
              <h3 className="font-display text-xs font-bold uppercase tracking-wider text-gold">
                AST Patch Diff Viewer
              </h3>
            </div>
            <span className="font-mono text-[11px] text-cream/50">
              {result.server_path}
            </span>
          </div>

          <pre className="max-h-72 overflow-x-auto p-5 font-mono text-xs leading-relaxed">
            {result.diff.split("\n").map((line, i) => {
              const isAdd = line.startsWith("+") && !line.startsWith("+++");
              const isSub = line.startsWith("-") && !line.startsWith("---");
              return (
                <div
                  key={i}
                  className={`px-2 py-0.5 rounded ${
                    isAdd
                      ? "bg-emerald-950/80 text-emerald-300 font-bold"
                      : isSub
                      ? "bg-red-950/80 text-red-300 line-through opacity-80"
                      : "text-cream/80"
                  }`}
                >
                  {line}
                </div>
              );
            })}
          </pre>
        </div>
      )}
    </div>
  );
}
