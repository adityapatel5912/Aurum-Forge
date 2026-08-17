import { Globe, Plus, ShieldCheck, Trash2, Wrench } from "lucide-react";
import type { SiteRow } from "../types";
import { classifyUrl } from "../utils/detectOfficial";

interface Props {
  sites: SiteRow[];
  onChange: (sites: SiteRow[]) => void;
  onMoveOfficial?: (name: string, rowId: string) => void;
  disabled?: boolean;
}

export default function CustomSitesList({ sites, onChange, onMoveOfficial, disabled }: Props) {
  const update = (id: string, url: string) =>
    onChange(sites.map((s) => (s.id === id ? { ...s, url } : s)));

  const remove = (id: string) => onChange(sites.filter((s) => s.id !== id));

  const add = () => onChange([...sites, { id: crypto.randomUUID(), url: "" }]);

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4 text-gold-deep" strokeWidth={2.2} />
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider text-navy">
            Custom Sites
          </h2>
        </div>
        <button
          type="button"
          onClick={add}
          disabled={disabled}
          className="inline-flex items-center gap-1 rounded-lg border border-navy/20 bg-white px-2.5 py-1 text-xs font-semibold text-navy transition hover:border-navy hover:bg-navy hover:text-cream disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Plus className="h-3.5 w-3.5" /> Add Site
        </button>
      </div>

      <div className="space-y-2">
        {sites.map((site) => {
          const verdict = classifyUrl(site.url);
          const isOfficial = verdict.type === "OFFICIAL" && site.url.trim().length > 2;
          const isCoreCovered = verdict.name === "amazon" && site.url.trim().length > 2;
          return (
            <div key={site.id} className="space-y-1.5">
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Globe className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-navy/30" />
                  <input
                    value={site.url}
                    onChange={(e) => update(site.id, e.target.value)}
                    disabled={disabled}
                    placeholder="https://example.com"
                    spellCheck={false}
                    className="w-full rounded-lg border border-navy/15 bg-white py-2 pl-9 pr-28 text-sm text-navy placeholder:text-navy/35 shadow-sm outline-none transition focus:border-gold focus:ring-2 focus:ring-gold/30 disabled:bg-navy/5"
                  />
                  <span
                    className={`pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                      isOfficial
                        ? "bg-navy text-cream"
                        : isCoreCovered
                          ? "border border-gold/70 bg-white text-gold-deep"
                          : "border border-gold/60 bg-gold/15 text-gold-deep"
                    }`}
                  >
                    {isOfficial ? (
                      <span className="inline-flex items-center gap-1">
                        <ShieldCheck className="h-3 w-3" /> Official API
                      </span>
                    ) : isCoreCovered ? (
                      <span className="inline-flex items-center gap-1">
                        <Wrench className="h-3 w-3" /> Core ready
                      </span>
                    ) : (
                      "Will forge"
                    )}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => remove(site.id)}
                  disabled={disabled || sites.length === 0}
                  aria-label="Remove site"
                  className="rounded-lg border border-navy/10 bg-white p-2 text-navy/40 transition hover:border-red-300 hover:text-red-500 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {isOfficial && (
                <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-navy/70 bg-navy px-3 py-2 text-cream">
                  <p className="text-xs leading-snug">
                    <span className="font-bold capitalize">{verdict.name}</span> has an official
                    API — no browser forging needed (its core tools ship in every server).
                  </p>
                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => onMoveOfficial?.(verdict.name, site.id)}
                    className="shrink-0 rounded-lg bg-gold px-3 py-1 text-xs font-bold text-navy transition hover:bg-gold-deep hover:text-cream disabled:opacity-50"
                  >
                    Move to Official
                  </button>
                </div>
              )}
            </div>
          );
        })}
        {sites.length === 0 && (
          <button
            type="button"
            onClick={add}
            className="w-full rounded-lg border border-dashed border-navy/25 bg-white/50 py-3 text-xs font-medium text-navy/50 transition hover:border-gold hover:text-navy"
          >
            + Add any site — e.g. a hackathon platform, an e-commerce store
          </button>
        )}
      </div>
      <p className="mt-2 text-xs text-navy/45">
        Any site works — e.g. a hackathon platform, an e-commerce store. Gmail / Notion are
        auto-detected as official; Amazon ships with 3 core tools.
      </p>
    </section>
  );
}
