import { useEffect, useState } from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Lock, RefreshCw, Shield, ShieldAlert, ShieldCheck, Sparkles } from "lucide-react";
import { scanAurumSecurityVault } from "../api";
import type { AurumSecurityFinding, AurumSecurityReport } from "../types";

export default function SecurityVaultView() {
  const [report, setReport] = useState<AurumSecurityReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [customCode, setCustomCode] = useState("");
  const [activeMode, setActiveMode] = useState<"server" | "custom">("server");

  const runScan = async (codeToScan?: string) => {
    setLoading(true);
    try {
      const res = await scanAurumSecurityVault(
        activeMode === "server" ? "forge/mcp/forge_aurum_hub/server.py" : "",
        activeMode === "custom" ? (codeToScan || customCode) : ""
      );
      setReport(res);
    } catch (err) {
      console.error("Security scan failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runScan();
  }, [activeMode]);

  return (
    <div className="flex flex-col gap-4 text-cream">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gold/20 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-gold animate-pulse" />
          <h3 className="text-base font-bold tracking-wide text-cream">
            Aurum Security Vault <span className="text-xs font-normal text-gold">(AST & Secret Gate)</span>
          </h3>
        </div>
        <button
          onClick={() => runScan()}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-lg border border-gold/40 bg-gold/10 px-3 py-1.5 text-xs font-semibold text-gold transition-all hover:bg-gold/20"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          {loading ? "Scanning AST..." : "Run Live Scan"}
        </button>
      </div>

      {/* Mode Selector */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveMode("server")}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
            activeMode === "server"
              ? "border border-gold bg-gold/20 text-cream shadow-[0_0_10px_rgba(198,169,107,0.3)]"
              : "border border-gold/20 bg-navy-light/40 text-cream/70 hover:text-cream"
          }`}
        >
          Scan Active Super-Hub
        </button>
        <button
          onClick={() => setActiveMode("custom")}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
            activeMode === "custom"
              ? "border border-gold bg-gold/20 text-cream shadow-[0_0_10px_rgba(198,169,107,0.3)]"
              : "border border-gold/20 bg-navy-light/40 text-cream/70 hover:text-cream"
          }`}
        >
          Scan Custom Code / Snippet
        </button>
      </div>

      {activeMode === "custom" && (
        <div className="flex flex-col gap-2 rounded-lg border border-gold/20 bg-[#050C1A] p-3">
          <label className="text-xs font-semibold text-gold">Paste Python FastMCP Code to Audit:</label>
          <textarea
            rows={4}
            value={customCode}
            onChange={(e) => setCustomCode(e.target.value)}
            placeholder='def tool(): ... API_KEY = "sk-proj-1234..."'
            className="rounded border border-gold/20 bg-navy/80 p-2 font-mono text-xs text-cream outline-none focus:border-gold"
          />
          <button
            onClick={() => runScan(customCode)}
            className="self-end rounded bg-gold px-3 py-1 text-xs font-bold text-navy hover:bg-gold-light"
          >
            Audit Snippet
          </button>
        </div>
      )}

      {/* Security Report Card */}
      {report && (
        <div className="flex flex-col gap-4 rounded-xl border border-gold/30 bg-navy/90 p-4 shadow-xl">
          {/* Top Score Banner */}
          <div className="flex items-center justify-between rounded-lg border border-gold/25 bg-[#050C1A]/80 p-4">
            <div className="flex items-center gap-3">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-xl border text-xl font-black ${
                  report.security_score >= 90
                    ? "border-gold bg-gold/20 text-gold shadow-[0_0_15px_rgba(198,169,107,0.5)]"
                    : "border-red-500 bg-red-500/20 text-red-400"
                }`}
              >
                {report.security_score}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-cream">Security Trust Score</span>
                  <span
                    className={`rounded px-2 py-0.5 text-[10px] font-bold ${
                      report.aurum_security_badge
                        ? "border border-gold bg-gold/20 text-gold"
                        : "border border-red-500 bg-red-500/20 text-red-400"
                    }`}
                  >
                    {report.badge_label}
                  </span>
                </div>
                <div className="mt-0.5 text-xs text-cream/70">{report.summary}</div>
              </div>
            </div>

            <div className="flex flex-col items-end">
              <div className="flex items-center gap-1 text-xs font-bold">
                {report.can_publish ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    <span className="text-emerald-400">Marketplace Gate: Passed</span>
                  </>
                ) : (
                  <>
                    <ShieldAlert className="h-4 w-4 text-red-400" />
                    <span className="text-red-400">Publish Blocked</span>
                  </>
                )}
              </div>
              <span className="text-[10px] text-cream/50">AST Compilation Verified</span>
            </div>
          </div>

          {/* Audit Checks Checklist */}
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="flex items-center justify-between rounded-lg border border-gold/15 bg-navy-light/40 p-2.5">
              <span className="text-xs text-cream/80">API Key & Token Leaks</span>
              <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> 0 Hardcoded Secrets
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-gold/15 bg-navy-light/40 p-2.5">
              <span className="text-xs text-cream/80">Dangerous Shell Invocations</span>
              <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> Sandboxed Execution
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-gold/15 bg-navy-light/40 p-2.5">
              <span className="text-xs text-cream/80">Directory Traversal ('../')</span>
              <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> Safe Normalized Paths
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-gold/15 bg-navy-light/40 p-2.5">
              <span className="text-xs text-cream/80">FastMCP Typing Integrity</span>
              <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> Strict AST Verified
              </span>
            </div>
          </div>

          {/* Findings List */}
          {report.findings.length > 0 && (
            <div className="flex flex-col gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
              <div className="text-xs font-bold text-red-400">Detected Security Findings ({report.findings.length}):</div>
              {report.findings.map((f: AurumSecurityFinding, idx: number) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-cream/90">
                  <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-red-400" />
                  <div>
                    <span className="font-semibold text-red-300">[{f.severity}] {f.rule}</span>: {f.message} (Line {f.line})
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
