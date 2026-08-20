import type {
  BenchmarkData,
  ForgeRegistryMcpMeta,
  ForgeResult,
  HistoryEntry,
  JobState,
  MarketplacePackage,
  Official,
  PlatformExport,
  PlatformKey,
  SelfHealResult,
  SystemValidation,
  UniversalConfig,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export function apiUrl(path: string): string {
  if (!API_BASE) return path;
  return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}

async function json<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(text || `${resp.status} ${resp.statusText}`);
  }
  return resp.json() as Promise<T>;
}

export function getOfficials() {
  return fetch(apiUrl("/api/officials")).then((r) => json<Official[]>(r));
}

export function startForge(payload: {
  goal: string;
  urls: string[];
  officials: string[];
}) {
  return fetch(apiUrl("/api/forge"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) =>
    json<{
      job_id: string;
      status?: "running" | "done" | "error";
      result?: ForgeResult;
      elapsed_seconds?: number;
    }>(r)
  );
}

export function getJob(jobId: string) {
  return fetch(apiUrl(`/api/jobs/${jobId}`)).then((r) => json<JobState>(r));
}

export function getHistory(query = "") {
  const url = query ? `/api/history?q=${encodeURIComponent(query)}` : "/api/history";
  return fetch(apiUrl(url)).then((r) => json<HistoryEntry[]>(r));
}

export function getHistoryItem(id: string) {
  return fetch(apiUrl(`/api/history/${id}`)).then((r) => json<HistoryEntry>(r));
}

export function getHistorySkill(id: string) {
  return fetch(apiUrl(`/api/history/${id}/skill`)).then((r) => json<{ id: string; skill: string }>(r));
}

export function getHistoryExport(id: string, platform: PlatformKey | string) {
  return fetch(apiUrl(`/api/history/${id}/export/${platform}`)).then((r) => json<PlatformExport>(r));
}

export function getForgeRegistryMcpConfig() {
  return fetch(apiUrl("/api/forge-registry-mcp/config")).then((r) => json<ForgeRegistryMcpMeta>(r));
}

// ------------------------------------------------------------- FORGE INFINITY OS
export function getUniversalConfig() {
  return fetch(apiUrl("/api/config/universal")).then((r) => json<UniversalConfig>(r));
}

export function injectIDEConfig(ide: string, mcp_name = "forge-factory", server_path = "") {
  return fetch(apiUrl("/api/config/inject"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ide, mcp_name, server_path }),
  }).then((r) => json<{ ok: boolean; message?: string; error?: string; config_path?: string }>(r));
}

export function validateSystemEnvironment(server_path = "") {
  const url = server_path ? `/api/config/validate?server_path=${encodeURIComponent(server_path)}` : "/api/config/validate";
  return fetch(apiUrl(url)).then((r) => json<SystemValidation>(r));
}

export function getMarketplace(q = "", category = "", tag = "") {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (category) params.set("category", category);
  if (tag) params.set("tag", tag);
  return fetch(apiUrl(`/api/marketplace/packages?${params.toString()}`)).then((r) =>
    json<{ categories: string[]; packages: MarketplacePackage[] }>(r)
  );
}

export function publishToMarketplace(payload: {
  mcp_id: string;
  author?: string;
  description?: string;
  tags?: string[];
  category?: string;
}) {
  return fetch(apiUrl("/api/marketplace/publish"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) => json<{ ok: boolean; message: string; package: MarketplacePackage }>(r));
}

export function installMarketplacePackage(package_id: string) {
  return fetch(apiUrl(`/api/marketplace/install/${encodeURIComponent(package_id)}`), {
    method: "POST",
  }).then((r) => json<{ ok: boolean; message: string; name: string; server_path: string }>(r));
}

export function triggerSelfHeal(server_path = "", error_log = "") {
  return fetch(apiUrl("/api/self-heal"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ server_path, error_log }),
  }).then((r) => json<SelfHealResult>(r));
}

export function getBenchmark(mcp_name = "unified-forge") {
  return fetch(apiUrl(`/api/benchmark?mcp_name=${encodeURIComponent(mcp_name)}`)).then((r) =>
    json<BenchmarkData>(r)
  );
}

export function triggerVoiceForge(voice_transcript: string) {
  return fetch(apiUrl("/api/factory/voice"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voice_transcript }),
  }).then((r) => json<any>(r));
}

export function triggerChaining(mcp_names: string[], composite_goal: string) {
  return fetch(apiUrl("/api/factory/chain"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mcp_names, composite_goal }),
  }).then((r) => json<any>(r));
}

export function getTelemetry() {
  return fetch(apiUrl("/api/telemetry")).then((r) => json<any>(r));
}

export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      return true;
    } catch {
      return false;
    }
  }
}

export async function downloadFile(url: string, filename: string): Promise<void> {
  const fullUrl = apiUrl(url);
  try {
    const res = await fetch(fullUrl);
    if (!res.ok) throw new Error(`Download failed: ${res.status}`);
    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(blobUrl), 2000);
  } catch (err) {
    console.error("Download file error:", err);
    const a = document.createElement("a");
    a.href = fullUrl;
    a.download = filename;
    a.target = "_blank";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

// ------------------------------------------------------------- FORGE-AURUM SUPER-HUB APIS
export function getAurumHubStatus() {
  return fetch(apiUrl("/api/aurum/hub/status")).then((r) => json<import("./types").AurumHubCatalog>(r));
}

export function getAurumHubTools() {
  return fetch(apiUrl("/api/aurum/hub/tools")).then((r) => json<import("./types").AurumTool[]>(r));
}

export function reloadAurumHub() {
  return fetch(apiUrl("/api/aurum/hub/reload"), { method: "POST" }).then((r) =>
    json<{ ok: boolean; total_tools: number; total_servers: number; discovered_servers: Record<string, any>; new_servers: string[] }>(r)
  );
}

export function autoSyncAurumHub() {
  return fetch(apiUrl("/api/aurum/hub/auto-sync"), { method: "POST" }).then((r) =>
    json<{ ok: boolean; total_servers: number; total_tools: number; ide_synced: string[] }>(r)
  );
}

export function wrapOfficialMCP(official_id: string) {
  return fetch(apiUrl("/api/aurum/wrap"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ official_id }),
  }).then((r) => json<{ ok: boolean; wrapped: any }>(r));
}

export function getAurumChains() {
  return fetch(apiUrl("/api/aurum/chains")).then((r) => json<{ ok: boolean; chains: import("./types").AurumChain[] }>(r));
}

export function installAurumChain(chain_id: string) {
  return fetch(apiUrl(`/api/aurum/chains/${encodeURIComponent(chain_id)}/install`), {
    method: "POST",
  }).then((r) => json<{ ok: boolean; message: string; name: string; server_path: string }>(r));
}

export function exportUniversalBridge(mcp_name: string, server_path = "", goal = "") {
  return fetch(apiUrl("/api/aurum/bridge/export"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mcp_name, server_path, goal }),
  }).then((r) => json<{ ok: boolean; mcp_name: string; zip_path: string; skill_content: string; download_url: string }>(r));
}

export function importUniversalBridge(skill_text: string, target_name = "imported_mcp") {
  return fetch(apiUrl("/api/aurum/bridge/import"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skill_text, target_name }),
  }).then((r) => json<any>(r));
}

export function getAurumTimeTravelHistory(target_id = "forge-aurum-hub") {
  return fetch(apiUrl(`/api/aurum/time-travel/history?target_id=${encodeURIComponent(target_id)}`)).then((r) =>
    json<{ ok: boolean; target_id: string; versions: import("./types").AurumTimeTravelCommit[] }>(r)
  );
}

export function getAurumTimeTravelDiff(target_id = "forge-aurum-hub", from_version = "1.0.0", to_version = "1.0.1") {
  return fetch(
    apiUrl(`/api/aurum/time-travel/diff?target_id=${encodeURIComponent(target_id)}&from_version=${encodeURIComponent(from_version)}&to_version=${encodeURIComponent(to_version)}`)
  ).then((r) => json<{ ok: boolean; diff: string; changed: boolean; from_version: string; to_version: string }>(r));
}

export function rollbackAurumTimeTravel(target_id: string, version_or_hash: string, server_path = "") {
  return fetch(apiUrl("/api/aurum/time-travel/rollback"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_id, version_or_hash, server_path }),
  }).then((r) => json<any>(r));
}

export function scanAurumSecurityVault(server_path = "", source_code = "") {
  return fetch(apiUrl("/api/aurum/vault/scan"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ server_path, source_code }),
  }).then((r) => json<import("./types").AurumSecurityReport>(r));
}

export function runLiveBenchmark(mcp_name = "forge-aurum-hub") {
  return fetch(apiUrl(`/api/aurum/benchmark/live?mcp_name=${encodeURIComponent(mcp_name)}`)).then((r) =>
    json<import("./types").LiveBenchmarkData>(r)
  );
}

export function triggerBreakAndHeal(bug_type = "all") {
  return fetch(apiUrl("/api/aurum/break-and-heal"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bug_type }),
  }).then((r) => json<import("./types").SelfHealResult>(r));
}

export function triggerVoiceToChain(voice_transcript: string) {
  return fetch(apiUrl("/api/aurum/voice-to-chain"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voice_transcript }),
  }).then((r) => json<any>(r));
}

export function triggerVoicePilot(voice = "Forge Research Chain with GitHub Browser Notion Email and publish as Aurum Gold") {
  return fetch(apiUrl("/api/aurum/voice-pilot"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voice }),
  }).then((r) => json<import("./types").VoicePilotResult>(r));
}

export function checkMcpHealth(server_name = "", server_path = "") {
  return fetch(apiUrl("/api/mcp/health-check"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ server_name, server_path }),
  }).then((r) => json<any>(r));
}

export function executeDag(dag: any, goal = "") {
  return fetch(apiUrl("/api/dag/execute"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dag, goal }),
  }).then((r) => json<any>(r));
}

// ------------------------------------------------------------- HEALTH SYSTEM APIS
export function getLiveness() {
  return fetch(apiUrl("/health/live")).then((r) => json<any>(r));
}

export function getReadiness() {
  return fetch(apiUrl("/health/ready")).then((r) => json<any>(r));
}

export function getHealthTelemetry() {
  return fetch(apiUrl("/health/telemetry")).then((r) => json<any>(r));
}
