import type {
  ForgeRegistryMcpMeta,
  HistoryEntry,
  JobState,
  Official,
  PlatformExport,
  PlatformKey,
} from "./types";

async function json<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(text || `${resp.status} ${resp.statusText}`);
  }
  return resp.json() as Promise<T>;
}

export function getOfficials() {
  return fetch("/api/officials").then((r) => json<Official[]>(r));
}

export function startForge(payload: {
  goal: string;
  urls: string[];
  officials: string[];
}) {
  return fetch("/api/forge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) => json<{ job_id: string }>(r));
}

export function getJob(jobId: string) {
  return fetch(`/api/jobs/${jobId}`).then((r) => json<JobState>(r));
}

export function getHistory(query = "") {
  const url = query ? `/api/history?q=${encodeURIComponent(query)}` : "/api/history";
  return fetch(url).then((r) => json<HistoryEntry[]>(r));
}

export function getHistoryItem(id: string) {
  return fetch(`/api/history/${id}`).then((r) => json<HistoryEntry>(r));
}

export function getHistorySkill(id: string) {
  return fetch(`/api/history/${id}/skill`).then((r) => json<{ id: string; skill: string }>(r));
}

export function getHistoryExport(id: string, platform: PlatformKey | string) {
  return fetch(`/api/history/${id}/export/${platform}`).then((r) => json<PlatformExport>(r));
}

export function getForgeRegistryMcpConfig() {
  return fetch("/api/forge-registry-mcp/config").then((r) => json<ForgeRegistryMcpMeta>(r));
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
