import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  Download,
  ExternalLink,
  Eye,
  Globe2,
  Leaf,
  Loader2,
  Recycle,
  ShieldCheck,
  Sun,
} from "lucide-react";
import {
  downloadFile,
  getEarthChains,
  getEarthHealth,
  getEarthStats,
  runEarthChain,
  type EarthChain,
  type EarthChainResult,
  type EarthHealth,
  type EarthStats,
} from "../api";
import EarthDependencyGraph from "./EarthDependencyGraph";
import VisualDAGCanvas from "./VisualDAGCanvas";

/**
 * EarthForwardView — Earth Addition for NextStep Hacks 2026 (Earth Forward).
 * Additive-only new page served at /earth. The One OS Canvas at "/" is untouched.
 * Tagline: Forge Once. Use Everywhere. Verify Forever. For Earth.
 */

type EarthMode = "cream" | "white" | "earth";

const MODE_TOKENS: Record<EarthMode, { bg: string; panel: string; text: string; sub: string; edge: string }> = {
  cream: { bg: "#FFFBF0", panel: "#FFFFFF", text: "#0A1931", sub: "#3d4f6d", edge: "rgba(198,169,107,0.4)" },
  white: { bg: "#FFFFFF", panel: "#F6F7FB", text: "#0A1931", sub: "#3d4f6d", edge: "rgba(59,130,246,0.25)" },
  earth: { bg: "#ECFDF5", panel: "#FFFFFF", text: "#064E3B", sub: "#047857", edge: "rgba(16,185,129,0.4)" },
};

const GREEN = "#10B981";
const GOLD = "#C6A96B";
const SKY = "#3B82F6";
const THEME_KEY_EARTH = "forge-aurum-theme-earth";
const PROOF_HASH = "f6cdbd0a07f2";

const CHAIN_CARDS = [
  {
    key: "eco_monitor",
    id: "chain_eco_monitor",
    name: "Eco Monitor",
    icon: Eye,
    desc: "Climate search → NASA/EPA enrich → live AQI + water score → Notion report → #earth-forward Slack alert.",
    lines: ["ROOT->CLIMATE", "ROOT->WATER", "ROOT->NOTION", "ROOT->SLACK"],
  },
  {
    key: "waste_reduce",
    id: "chain_waste_reduce",
    name: "Waste Reduce",
    icon: Recycle,
    desc: "Waste audit kg + CO2 → Sheets log → Notion reduction plan → #sustainability Slack alert.",
    lines: ["ROOT->WASTE", "ROOT->SHEETS", "ROOT->NOTION", "ROOT->SLACK"],
  },
  {
    key: "renewable_optimize",
    id: "chain_renewable_optimize",
    name: "Renewable Optimize",
    icon: Sun,
    desc: "Live solar irradiance → kW + savings + ROI → Sheets log → Notion adoption plan → Slack alert.",
    lines: ["ROOT->RENEWABLE", "ROOT->SHEETS", "ROOT->NOTION", "ROOT->SLACK"],
  },
] as const;

export default function EarthForwardView({ onBackToForge }: { onBackToForge: () => void }) {
  const [mode, setMode] = useState<EarthMode>(() => {
    const saved = window.localStorage.getItem(THEME_KEY_EARTH);
    return saved === "white" || saved === "earth" || saved === "cream" ? saved : "earth";
  });
  const [health, setHealth] = useState<EarthHealth | null>(null);
  const [stats, setStats] = useState<EarthStats | null>(null);
  const [chains, setChains] = useState<EarthChain[]>([]);
  const [city, setCity] = useState("Balasar, Gujarat");
  const [usageKwh, setUsageKwh] = useState(300);
  const [items, setItems] = useState("plastic_bottle, food_scraps, cardboard");
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, EarthChainResult | { error: string }>>({});
  const [lastResult, setLastResult] = useState<EarthChainResult | null>(null);
  const [activeDag, setActiveDag] = useState<Record<string, any>>({});
  const [activeGoal, setActiveGoal] = useState("Earth Forward — Eco Monitor Chain");

  useEffect(() => {
    window.localStorage.setItem(THEME_KEY_EARTH, mode);
  }, [mode]);

  useEffect(() => {
    document.title = "AURUM-FORGE Earth — Earth Forward | NextStep Hacks 2026";
  }, []);

  const refresh = useCallback(() => {
    getEarthHealth().then(setHealth).catch(() => setHealth(null));
    getEarthStats().then(setStats).catch(() => setStats(null));
    getEarthChains()
      .then((res) => {
        if (res.ok && res.earth_chains?.length) {
          setChains(res.earth_chains);
          const first = res.earth_chains.find((c) => c.id === "chain_eco_monitor") || res.earth_chains[0];
          if (first?.dag) {
            setActiveDag(first.dag);
            if (first.description) setActiveGoal(first.description);
          }
        }
      })
      .catch(() => setChains([]));
  }, []);

  useEffect(() => {
    refresh();
    const t = window.setInterval(() => {
      getEarthStats().then(setStats).catch(() => {});
    }, 12000);
    return () => window.clearInterval(t);
  }, [refresh]);

  const runChain = useCallback(
    async (key: string) => {
      setRunning(key);
      try {
        const parsedItems = items
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
        const res = await runEarthChain({
          chain: key,
          city,
          items: parsedItems.length ? parsedItems : ["plastic_bottle", "food_scraps", "cardboard"],
          usage_kwh: usageKwh,
          slack_channel: key === "eco_monitor" ? "#earth-forward" : "#sustainability",
        });
        setResults((prev) => ({ ...prev, [key]: res }));
        setLastResult(res);
        const meta = chains.find((c) => c.id === CHAIN_CARDS.find((k) => k.key === key)?.id);
        if (meta?.dag) {
          setActiveDag(meta.dag);
          setActiveGoal(meta.description);
        }
        getEarthStats().then(setStats).catch(() => {});
      } catch (err) {
        setResults((prev) => ({ ...prev, [key]: { error: String(err) } }));
      } finally {
        setRunning(null);
      }
    },
    [chains, city, items, usageKwh]
  );

  const tokens = MODE_TOKENS[mode];
  const themeVars = useMemo(
    () =>
      ({
        "--earth-bg": tokens.bg,
        "--earth-panel": tokens.panel,
        "--earth-text": tokens.text,
        "--earth-sub": tokens.sub,
        "--earth-edge": tokens.edge,
      }) as React.CSSProperties,
    [tokens]
  );

  return (
    <div
      className="min-h-screen w-full overflow-y-auto"
      style={{ ...themeVars, background: "var(--earth-bg)", color: "var(--earth-text)" }}
      data-earth-theme={mode}
    >
      {/* ================= Header ================= */}
      <header
        className="sticky top-0 z-20 border-b backdrop-blur-md"
        style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}
      >
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-5 py-3">
          <div className="flex items-center gap-3">
            {/* [ATTACHED_LOGO] slot — drop the logo asset here (3:2) */}
            <div
              className="flex h-10 w-[60px] items-center justify-center rounded-lg border-2 font-display text-sm font-black"
              style={{ borderColor: GOLD, color: GOLD, background: "#FFFFFF" }}
              title="ATTACHED_LOGO slot (3:2)"
            >
              AF
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-display text-base font-black tracking-wide" style={{ color: "var(--earth-text)" }}>
                  AURUM-FORGE <span style={{ color: GREEN }}>EARTH</span>
                </span>
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-black"
                  style={{ background: "rgba(16,185,129,0.15)", color: GREEN, border: `1px solid ${GREEN}` }}
                >
                  🌍 EARTH FORWARD — NEXTSTEP HACKS 2026
                </span>
                {health && (
                  <span
                    className="rounded-full px-2 py-0.5 text-[10px] font-bold"
                    style={{ background: "rgba(198,169,107,0.15)", color: GOLD, border: `1px solid ${GOLD}` }}
                    title={`uptime ${health.uptime_s}s • ${health.total_tools} tools • ${health.total_servers} servers`}
                  >
                    <span className="mr-1 inline-block h-1.5 w-1.5 animate-pulse rounded-full align-middle" style={{ background: GREEN }} />
                    {health.total_tools} tools · hash {health.hash}
                  </span>
                )}
              </div>
              <p className="text-[11px] font-semibold" style={{ color: "var(--earth-sub)" }}>
                Forge Once. Use Everywhere. Verify Forever. <span style={{ color: GREEN }}>For Earth.</span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Earth Mode Toggle [Cream | White | Earth] */}
            <div className="flex overflow-hidden rounded-lg border text-[11px] font-bold" style={{ borderColor: "var(--earth-edge)" }}>
              {(["cream", "white", "earth"] as EarthMode[]).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className="px-3 py-1.5 transition-all"
                  style={{
                    background: mode === m ? (m === "earth" ? GREEN : GOLD) : "transparent",
                    color: mode === m ? "#FFFFFF" : "var(--earth-sub)",
                  }}
                  title={`Earth Mode: ${m} (localStorage ${THEME_KEY_EARTH})`}
                >
                  {m === "cream" ? "Cream" : m === "white" ? "White" : "🌍 Earth"}
                </button>
              ))}
            </div>
            <button
              onClick={onBackToForge}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[11px] font-black transition-all hover:opacity-90"
              style={{ background: GOLD, color: "#0A1931" }}
            >
              <ArrowLeft className="h-3.5 w-3.5" /> Back to Forge
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-6">
        {/* ================= Hero: theme + QR + stats ================= */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div
            className="rounded-2xl border p-5 lg:col-span-2"
            style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}
          >
            <h1 className="font-display text-2xl font-black" style={{ color: "var(--earth-text)" }}>
              Earth Addition — <span style={{ color: GREEN }}>Earth Forward Edition</span>
            </h1>
            <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--earth-sub)" }}>
              New additive page for FORGE: 3 Earth Forward chains (Eco Monitor · Waste Reduce · Renewable Optimize)
              plus the <code className="font-mono" style={{ color: GREEN }}>forge_eco</code> MCP — live air quality via free
              Open-Meteo APIs, water scores, waste CO₂ audits, solar ROI, wildlife monitoring. Zero-LLM runtime, 0 tokens,
              every result sealed with a 12-char hash. Built with local communities in mind (default city:{" "}
              <b>Balasar, Gujarat</b>).
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <StatTile label="Eco Reports" value={stats?.total_reports ?? 0} icon={Activity} color={SKY} />
              <StatTile label="Waste kg audited" value={stats?.total_waste_kg_reduced ?? 0} icon={Recycle} color={GREEN} />
              <StatTile label="Solar kW potential" value={stats?.total_solar_potential_kw ?? 0} icon={Sun} color={GOLD} />
              <StatTile label="CO₂ kg saved" value={stats?.total_co2_saved_kg ?? 0} icon={Leaf} color={GREEN} />
            </div>
            <div className="mt-3 flex flex-wrap gap-3 text-[11px] font-bold" style={{ color: "var(--earth-sub)" }}>
              <span>Tokens saved: <b style={{ color: GREEN }}>{(stats?.total_tokens_saved ?? 0).toLocaleString()}</b></span>
              <span>Uptime: <b>{Math.round(health?.uptime_s ?? 0)}s</b></span>
              <span>Chains: <b>{chains.length} Earth + 5 Forge = 8</b></span>
              <span>Proof hash: <b className="font-mono" style={{ color: GOLD }}>{PROOF_HASH}</b></span>
            </div>
          </div>

          {/* QR placeholder — 400x400 space, Gold on White */}
          <div className="flex flex-col items-center justify-center rounded-2xl border p-4" style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}>
            <div
              className="flex aspect-square w-full max-w-[220px] items-center justify-center rounded-xl border-2 border-dashed text-center"
              style={{ borderColor: GOLD, background: "#FFFFFF" }}
            >
              <div>
                <div className="font-mono text-[10px] font-black" style={{ color: GOLD }}>
                  [PLACEHOLDER:
                  <br />
                  QR_CODE_DEMO]
                </div>
                <div className="mt-1 text-[9px] font-bold" style={{ color: "#0A1931" }}>
                  400x400 · Gold #C6A96B on White
                  <br />
                  Scan for Demo Video
                </div>
              </div>
            </div>
            <p className="mt-2 text-[10px] font-semibold" style={{ color: "var(--earth-sub)" }}>
              QR code added at submission time
            </p>
          </div>
        </section>

        {/* ================= Inputs ================= */}
        <section className="mt-5 grid grid-cols-1 gap-3 rounded-2xl border p-4 sm:grid-cols-3" style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}>
          <label className="text-xs font-bold" style={{ color: "var(--earth-sub)" }}>
            City
            <input
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="mt-1 w-full rounded-lg border px-3 py-2 text-sm font-semibold outline-none"
              style={{ borderColor: "var(--earth-edge)", color: "var(--earth-text)", background: "var(--earth-bg)" }}
              placeholder="Balasar, Gujarat"
            />
          </label>
          <label className="text-xs font-bold" style={{ color: "var(--earth-sub)" }}>
            Monthly usage (kWh)
            <input
              type="number"
              value={usageKwh}
              min={1}
              onChange={(e) => setUsageKwh(Number(e.target.value) || 300)}
              className="mt-1 w-full rounded-lg border px-3 py-2 text-sm font-semibold outline-none"
              style={{ borderColor: "var(--earth-edge)", color: "var(--earth-text)", background: "var(--earth-bg)" }}
            />
          </label>
          <label className="text-xs font-bold" style={{ color: "var(--earth-sub)" }}>
            Waste items (comma separated)
            <input
              value={items}
              onChange={(e) => setItems(e.target.value)}
              className="mt-1 w-full rounded-lg border px-3 py-2 text-sm font-semibold outline-none"
              style={{ borderColor: "var(--earth-edge)", color: "var(--earth-text)", background: "var(--earth-bg)" }}
            />
          </label>
        </section>

        {/* ================= 3 Chain Cards ================= */}
        <section className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">
          {CHAIN_CARDS.map((card) => {
            const Icon = card.icon;
            const meta = chains.find((c) => c.id === card.id);
            const result = results[card.key];
            const isRunning = running === card.key;
            const isError = result && "error" in result;
            return (
              <div
                key={card.key}
                className="flex flex-col rounded-2xl border p-4 transition-all"
                style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className="flex h-9 w-9 items-center justify-center rounded-xl"
                      style={{ background: "rgba(16,185,129,0.15)", border: `1px solid ${GREEN}` }}
                    >
                      <Icon className="h-4 w-4" style={{ color: GREEN }} />
                    </div>
                    <div>
                      <h3 className="font-display text-sm font-black" style={{ color: "var(--earth-text)" }}>
                        {card.name}
                      </h3>
                      <span className="font-mono text-[9px] font-bold" style={{ color: GOLD }}>
                        {meta ? `hash ${meta.hash} · aurum_verified` : "hash — · aurum_verified"}
                      </span>
                    </div>
                  </div>
                </div>
                <p className="mt-2 text-[11px] leading-relaxed" style={{ color: "var(--earth-sub)" }}>
                  {card.desc}
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {card.lines.map((l) => (
                    <span
                      key={l}
                      className="rounded px-1.5 py-0.5 font-mono text-[9px] font-bold"
                      style={{ background: "rgba(16,185,129,0.12)", color: GREEN }}
                    >
                      {l}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => runChain(card.key)}
                  disabled={isRunning}
                  className="mt-3 flex items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-black text-white transition-all hover:opacity-90 disabled:opacity-60"
                  style={{ background: GREEN, boxShadow: "0 6px 20px -6px rgba(16,185,129,0.55)" }}
                >
                  {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap />}
                  {isRunning ? "Running chain (<2.1s)..." : "Run Chain"}
                </button>

                {result && !isError && !("error" in result) && (
                  <div className="mt-3 rounded-xl border p-3 text-[11px]" style={{ borderColor: GREEN, background: "rgba(16,185,129,0.06)" }}>
                    <ProofRow label="Notion" value={(result as EarthChainResult).notion_url} link />
                    <ProofRow label="Slack" value={`posted: ${String((result as EarthChainResult).slack_posted)} → ${((result as EarthChainResult).slack_channel || "#earth-forward")}`} ok={!!(result as EarthChainResult).slack_posted} />
                    <ProofRow label="Hash" value={(result as EarthChainResult).workflow_hash || (result as EarthChainResult).hash} mono />
                    <ProofRow label="Time" value={(result as EarthChainResult).time_human} />
                    <ProofRow label="Tokens saved" value={((result as EarthChainResult).tokens_saved || 0).toLocaleString()} />
                    {(result as EarthChainResult).proof_ledger?.screenshots && (
                      <div className="mt-2">
                        <span className="font-bold" style={{ color: "var(--earth-sub)" }}>Screenshots (base64):</span>{" "}
                        <img
                          src={(result as EarthChainResult).proof_ledger!.screenshots}
                          alt="proof screenshot"
                          className="mt-1 inline-block rounded border"
                          style={{ borderColor: GOLD }}
                          width={28}
                          height={28}
                        />
                      </div>
                    )}
                  </div>
                )}
                {isError && (
                  <div className="mt-3 rounded-xl border border-red-300 bg-red-50 p-3 text-[11px] font-bold text-red-600">
                    {(result as { error: string }).error}
                  </div>
                )}
              </div>
            );
          })}
        </section>

        {/* ================= DAG Canvas + Dependency Graph ================= */}
        <section className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border p-4" style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}>
            <div className="mb-2 flex items-center justify-between">
              <h3 className="font-display text-sm font-black" style={{ color: "var(--earth-text)" }}>
                Active Earth DAG <span className="text-[10px] font-bold" style={{ color: GREEN }}>Green Trigger · Blue Process · Purple Output · Gold Pulse</span>
              </h3>
            </div>
            <div className="overflow-hidden rounded-xl">
              <VisualDAGCanvas dag={activeDag} goal={activeGoal} />
            </div>
          </div>
          <div className="rounded-2xl border p-4" style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}>
            <h3 className="mb-2 font-display text-sm font-black" style={{ color: "var(--earth-text)" }}>
              EarthDependencyGraph — golden green lines
            </h3>
            <EarthDependencyGraph />
          </div>
        </section>

        {/* ================= Proof Ledger ================= */}
        <section className="mt-5 rounded-2xl border p-5" style={{ background: "var(--earth-panel)", borderColor: "var(--earth-edge)" }}>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="flex items-center gap-2 font-display text-sm font-black" style={{ color: "var(--earth-text)" }}>
              <ShieldCheck className="h-4 w-4" style={{ color: GOLD }} /> Proof Ledger — Earth Forward · Evidence not pitch
            </h3>
            <span className="rounded-full px-2 py-0.5 text-[10px] font-black" style={{ background: "rgba(198,169,107,0.15)", color: GOLD, border: `1px solid ${GOLD}` }}>
              verifiable: true · aurum_verified
            </span>
          </div>
          {lastResult ? (
            <div className="mt-3 grid grid-cols-1 gap-3 text-[11px] sm:grid-cols-2 lg:grid-cols-4">
              <ProofTile label="Canonical hash" value={PROOF_HASH} />
              <ProofTile label="Workflow hash" value={lastResult.workflow_hash || lastResult.hash} />
              <ProofTile label="Notion URL" value={lastResult.notion_url} link={lastResult.notion_url} />
              <ProofTile label="Slack posted" value={String(lastResult.slack_posted)} ok={lastResult.slack_posted} />
              <ProofTile label="Time" value={lastResult.time_human} />
              <ProofTile label="Tokens saved" value={(lastResult.tokens_saved || 0).toLocaleString()} />
              <ProofTile label="Latency (measured)" value={`${lastResult.latency_s ?? "—"}s`} />
              <ProofTile label="Zero-LLM" value="true · 0 runtime tokens" ok />
            </div>
          ) : (
            <p className="mt-3 text-[12px] font-semibold" style={{ color: "var(--earth-sub)" }}>
              Run any chain above — the Proof Ledger fills with notion_url, slack posted, hash, screenshots (base64),
              time_human and tokens_saved. Evidence not pitch.
            </p>
          )}
          <details className="mt-3">
            <summary className="cursor-pointer text-[11px] font-bold" style={{ color: GREEN }}>
              Slack message preview (last run)
            </summary>
            <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded-lg border p-3 text-[10px]" style={{ borderColor: "var(--earth-edge)", color: "var(--earth-sub)" }}>
              {lastResult?.message_preview || "— run a chain to see the #earth-forward / #sustainability message —"}
            </pre>
          </details>
        </section>

        {/* ================= Downloads ================= */}
        <section className="mt-5 flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-black" style={{ color: "var(--earth-sub)" }}>Download evidence zips (&gt;1KB):</span>
          {[
            { label: "eco-report.zip", url: "/api/download/eco-report.zip" },
            { label: "forge_eco-mcp.zip", url: "/api/download/forge_eco-mcp.zip" },
            { label: "chain_eco_monitor-mcp.zip", url: "/api/download/chain_eco_monitor-mcp.zip" },
            { label: "chain_waste_reduce-mcp.zip", url: "/api/download/chain_waste_reduce-mcp.zip" },
            { label: "chain_renewable_optimize-mcp.zip", url: "/api/download/chain_renewable_optimize-mcp.zip" },
          ].map((z) => (
            <button
              key={z.label}
              onClick={() => downloadFile(z.url, z.label)}
              className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[11px] font-bold transition-all hover:opacity-80"
              style={{ borderColor: GOLD, color: GOLD, background: "rgba(198,169,107,0.1)" }}
            >
              <Download className="h-3 w-3" /> {z.label}
            </button>
          ))}
        </section>
      </main>

      {/* ================= Footer ================= */}
      <footer className="mt-6 border-t px-5 py-4" style={{ borderColor: "var(--earth-edge)", background: "var(--earth-panel)" }}>
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 text-[11px] font-semibold" style={{ color: "var(--earth-sub)" }}>
          <span className="flex items-center gap-1.5">
            <Globe2 className="h-3.5 w-3.5" style={{ color: GREEN }} />
            Forge Once. Use Everywhere. Verify Forever. <span style={{ color: GREEN }}>For Earth.</span>
          </span>
          <span className="flex flex-wrap items-center gap-3">
            <a href="https://aurum-forge.vercel.app" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:underline" style={{ color: SKY }}>
              <ExternalLink className="h-3 w-3" /> aurum-forge.vercel.app
            </a>
            <a href="https://aurum-forge.onrender.com/api/health" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:underline" style={{ color: SKY }}>
              <ExternalLink className="h-3 w-3" /> /api/health
            </a>
            <a href="https://aurum-forge.onrender.com/api/earth/health" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:underline" style={{ color: GREEN }}>
              <ExternalLink className="h-3 w-3" /> /api/earth/health
            </a>
            <button onClick={onBackToForge} className="flex items-center gap-1 hover:underline" style={{ color: GOLD }}>
              <ArrowLeft className="h-3 w-3" /> One OS Canvas (9 switches)
            </button>
          </span>
        </div>
      </footer>
    </div>
  );
}

function Zap() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M13 2L4.09 12.97a1 1 0 0 0 .77 1.64H11l-1.8 7.04a1 1 0 0 0 1.72.93l8.99-10.96a1 1 0 0 0-.77-1.64H13l1.8-7.04A1 1 0 0 0 13 2z" />
    </svg>
  );
}

function StatTile({ label, value, icon: Icon, color }: { label: string; value: number; icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>; color: string }) {
  return (
    <div className="rounded-xl border p-3" style={{ borderColor: "var(--earth-edge)", background: "var(--earth-bg)" }}>
      <div className="flex items-center gap-1.5 text-[10px] font-bold" style={{ color: "var(--earth-sub)" }}>
        <Icon className="h-3 w-3" style={{ color }} /> {label}
      </div>
      <div className="mt-1 font-display text-lg font-black" style={{ color }}>
        {typeof value === "number" ? Math.round(value * 100) / 100 : value}
      </div>
    </div>
  );
}

function ProofTile({ label, value, link, ok }: { label: string; value: string; link?: string; ok?: boolean }) {
  return (
    <div className="rounded-xl border p-3" style={{ borderColor: "var(--earth-edge)", background: "var(--earth-bg)" }}>
      <div className="text-[10px] font-bold" style={{ color: "var(--earth-sub)" }}>{label}</div>
      {link ? (
        <a href={link} target="_blank" rel="noreferrer" className="mt-0.5 block break-all font-mono text-[11px] font-bold hover:underline" style={{ color: SKY }}>
          {value}
        </a>
      ) : (
        <div className="mt-0.5 flex items-center gap-1 break-all font-mono text-[11px] font-bold" style={{ color: ok ? GREEN : "var(--earth-text)" }}>
          {ok && <CheckCircle2 className="h-3 w-3 shrink-0" />} {value}
        </div>
      )}
    </div>
  );
}

function ProofRow({ label, value, link, mono, ok }: { label: string; value: string; link?: boolean; mono?: boolean; ok?: boolean }) {
  return (
    <div className="mt-1 flex items-baseline gap-2">
      <span className="w-24 shrink-0 font-bold" style={{ color: "var(--earth-sub)" }}>{label}:</span>
      {link ? (
        <a href={value} target="_blank" rel="noreferrer" className="break-all font-semibold hover:underline" style={{ color: SKY }}>{value}</a>
      ) : (
        <span className={`break-all font-semibold ${mono ? "font-mono" : ""}`} style={{ color: ok ? GREEN : "var(--earth-text)" }}>{value}</span>
      )}
    </div>
  );
}
