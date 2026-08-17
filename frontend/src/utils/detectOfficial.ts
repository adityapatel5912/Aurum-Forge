/**
 * URL classifier — mirrors backend/forge/utils/detect_official.py exactly.
 * Official-API domains (Gmail, Notion) must NOT be browser-forged;
 * amazon is custom but covered by the hardcoded amazon core.
 */
export interface UrlVerdict {
  type: "OFFICIAL" | "CUSTOM";
  name: string;
}

export function classifyUrl(url: string): UrlVerdict {
  const urlLow = (url || "").toLowerCase();
  if (urlLow.includes("amazon")) {
    return { type: "CUSTOM", name: "amazon" };
  }
  if (["mail.google", "gmail"].some((k) => urlLow.includes(k))) {
    return { type: "OFFICIAL", name: "gmail" };
  }
  if (urlLow.includes("notion")) {
    return { type: "OFFICIAL", name: "notion" };
  }
  return { type: "CUSTOM", name: url };
}

/** Sites fully covered by a hardcoded core — no scout / no LLM needed. */
export const CORE_SITE_NAMES = new Set(["amazon"]);
