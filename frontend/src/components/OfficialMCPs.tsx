import { BadgeCheck, Check, Mail } from "lucide-react";
import type { Official } from "../types";

interface Props {
  catalog: Official[];
  selected: Set<string>;
  onToggle: (id: string) => void;
  detected?: Set<string>;
  disabled?: boolean;
}

export default function OfficialMCPs({ catalog, selected, onToggle, detected, disabled }: Props) {
  const detectedList = [...(detected ?? [])];
  return (
    <section>
      <div className="mb-2 flex items-center gap-2">
        <BadgeCheck className="h-4 w-4 text-navy" strokeWidth={2.2} />
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider text-navy">
          Official MCPs
        </h2>
        {selected.size > 0 && (
          <span className="rounded-full bg-navy px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-cream">
            {selected.size} selected
          </span>
        )}
      </div>

      {detectedList.length > 0 && (
        <div className="mb-2 flex flex-wrap items-center gap-2 rounded-xl border border-navy/70 bg-navy px-3 py-2">
          <Mail className="h-3.5 w-3.5 text-gold" />
          <span className="text-xs font-medium text-cream/85">
            Detected from your URLs (official API — core tools included automatically):
          </span>
          {detectedList.map((name) => (
            <span
              key={name}
              className="rounded-full bg-gold px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-navy"
            >
              {name}
            </span>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {catalog.map((official) => {
          const on = selected.has(official.id);
          return (
            <button
              key={official.id}
              type="button"
              disabled={disabled}
              onClick={() => onToggle(official.id)}
              className={`group relative rounded-xl border p-3 text-left transition disabled:cursor-not-allowed disabled:opacity-60 ${
                on
                  ? "border-navy bg-navy text-cream shadow-card"
                  : "border-navy/15 bg-white text-navy hover:border-navy/40"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-display text-sm font-semibold">{official.name}</span>
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                    on ? "bg-gold text-navy" : "border border-navy/25 bg-cream text-navy/70"
                  }`}
                >
                  {on && <Check className="h-3 w-3" strokeWidth={3} />}
                  Official
                </span>
              </div>
              <p className={`mt-1 text-xs leading-snug ${on ? "text-cream/70" : "text-navy/50"}`}>
                {official.description}
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                {official.tools.map((t) => (
                  <code
                    key={t.tool_name}
                    className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                      on ? "bg-cream/15 text-gold-soft" : "bg-navy/5 text-navy/60"
                    }`}
                  >
                    {t.tool_name}
                  </code>
                ))}
              </div>
            </button>
          );
        })}
      </div>
      <p className="mt-2 text-xs text-navy/45">
        Wrapped as typed tools in the same server — bring your own token (shown after forging).
      </p>
    </section>
  );
}
