import type { ToolRow } from "../types";

interface Props {
  tools: ToolRow[];
}

export default function ToolsTable({ tools }: Props) {
  return (
    <div className="overflow-hidden rounded-xl border border-navy/10">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="bg-navy text-cream">
            <th className="px-4 py-2.5 font-display text-xs font-semibold uppercase tracking-wider">Tool</th>
            <th className="px-4 py-2.5 font-display text-xs font-semibold uppercase tracking-wider">Source</th>
            <th className="px-4 py-2.5 font-display text-xs font-semibold uppercase tracking-wider">Badge</th>
          </tr>
        </thead>
        <tbody>
          {tools.map((t, i) => (
            <tr key={t.name} className={i % 2 ? "bg-white" : "bg-cream/60"}>
              <td className="px-4 py-2.5">
                <code className="font-mono text-xs font-semibold text-navy">{t.name}</code>
                <p className="mt-0.5 max-w-md text-[11px] leading-snug text-navy/50">{t.description}</p>
              </td>
              <td className="px-4 py-2.5 text-xs text-navy/70">{t.source}</td>
              <td className="px-4 py-2.5">
                <span
                  className={`inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                    t.badge === "FORGED"
                      ? "border border-gold/70 bg-gold/15 text-gold-deep"
                      : t.badge === "CORE"
                        ? "bg-gold text-navy"
                        : "bg-navy text-cream"
                  }`}
                >
                  {t.badge}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
