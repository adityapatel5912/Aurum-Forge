import { useState } from "react";
import { AlertCircle, CheckCircle2, Flame, RefreshCw, ShieldCheck, Sparkles, Wrench } from "lucide-react";
import { triggerBreakAndHeal } from "../api";
import type { SelfHealResult } from "../types";

export default function SelfHealDiffView() {
  const [result, setResult] = useState<SelfHealResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<"diff" | "side_by_side">("diff");

  const handleBreakAndHeal = async (bugType = "all") => {
    setLoading(true);
    try {
      const res = await triggerBreakAndHeal(bugType);
      setResult(res);
    } catch (err) {
      console.error("Self-heal trigger failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 text-cream">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gold/20 pb-3">
        <div className="flex items-center gap-2">
          <Wrench className="h-5 w-5 text-gold animate-pulse" />
          <h3 className="text-base font-bold tracking-wide text-cream">
            Self-Heal Studio <span className="text-xs font-normal text-gold">(&lt;200ms AST Live Diff)</span>
          </h3>
        </div>
        <button
          onClick={() => handleBreakAndHeal("all")}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-lg bg-red-600 px-3.5 py-1.5 text-xs font-bold text-white transition-all hover:bg-red-500 hover:shadow-[0_0_15px_rgba(239,68,68,0.5)]"
        >
          <Flame className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          {loading ? "Injecting & Healing in <200ms..." : "Break It & Live Heal"}
        </button>
      </div>

      <p className="text-xs text-cream/70">
        Clicking <strong>"Break It"</strong> injects an intentional duplicate return statement, a Windows backslash (<code className="font-mono text-gold">\</code>) path bug, and an insecure locator into the target FastMCP server. The AST Self-Healing engine automatically parses, diagnoses, repairs, and verifies the Python compilation in <strong>&lt;200ms</strong>.
      </p>

      {result && (
        <div className="flex flex-col gap-4">
          {/* Status & Latency Banner */}
          <div className="flex items-center justify-between rounded-xl border border-gold/30 bg-navy/90 p-4 shadow-xl">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-gold bg-gold/20 text-gold shadow-[0_0_12px_rgba(198,169,107,0.4)]">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-cream">Healed in {result.elapsed_ms}ms</span>
                  <span className="rounded border border-gold/40 bg-gold/15 px-2 py-0.5 text-[10px] font-bold text-gold">
                    AURUM GOLD (#C6A96B)
                  </span>
                </div>
                <div className="text-xs text-cream/70">{result.message}</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode(viewMode === "diff" ? "side_by_side" : "diff")}
                className="rounded-lg border border-gold/30 bg-gold/10 px-2.5 py-1 text-xs font-semibold text-gold hover:bg-gold/20"
              >
                {viewMode === "diff" ? "Show Side-by-Side" : "Show Unified Diff"}
              </button>
            </div>
          </div>

          {/* Patches Applied Card */}
          <div className="flex flex-col gap-2 rounded-xl border border-gold/20 bg-navy-light/40 p-3">
            <div className="text-xs font-bold uppercase tracking-wider text-gold">
              AST Auto-Patches Applied ({result.patches_applied?.length || 0})
            </div>
            <div className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
              {result.patches_applied?.map((p, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-cream/90">
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-400" />
                  <span>{p}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Diff View */}
          {viewMode === "diff" ? (
            <div className="flex flex-col gap-1 rounded-xl border border-gold/30 bg-[#050C1A] p-4 shadow-xl">
              <span className="text-xs font-semibold text-gold">Unified Patch Diff (AST Corrected):</span>
              <pre className="max-h-80 overflow-y-auto font-mono text-xs text-cream">
                {result.diff.split("\n").map((line, i) => {
                  if (line.startsWith("+")) {
                    return (
                      <div key={i} className="bg-emerald-900/30 text-emerald-300">
                        {line}
                      </div>
                    );
                  }
                  if (line.startsWith("-")) {
                    return (
                      <div key={i} className="bg-red-900/30 text-red-300">
                        {line}
                      </div>
                    );
                  }
                  return (
                    <div key={i} className="text-cream/60">
                      {line}
                    </div>
                  );
                })}
              </pre>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="flex flex-col gap-1 rounded-xl border border-red-500/30 bg-[#050C1A] p-3">
                <span className="text-xs font-bold text-red-400">Before (Injected Broken Code):</span>
                <pre className="max-h-80 overflow-y-auto font-mono text-[11px] text-cream/80">
                  {result.before_code}
                </pre>
              </div>
              <div className="flex flex-col gap-1 rounded-xl border border-emerald-500/30 bg-[#050C1A] p-3">
                <span className="text-xs font-bold text-emerald-400">After (Self-Healed AST Code):</span>
                <pre className="max-h-80 overflow-y-auto font-mono text-[11px] text-cream/80">
                  {result.after_code}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
