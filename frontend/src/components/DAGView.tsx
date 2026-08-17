import { ChevronDown } from "lucide-react";
import type { Dag } from "../types";

interface Props {
  dag: Dag;
}

/** Group task ids into topological levels (parallel tasks share a level). */
function levels(dag: Dag): string[][] {
  const ids = Object.keys(dag);
  const done = new Set<string>();
  const out: string[][] = [];
  let remaining = new Set(ids);
  while (remaining.size) {
    const ready = [...remaining].filter((id) => (dag[id].deps ?? []).every((d) => done.has(d) || !(d in dag)));
    const level = ready.length ? ready : [...remaining];
    out.push(level);
    level.forEach((id) => done.add(id));
    remaining = new Set([...remaining].filter((id) => !done.has(id)));
  }
  return out;
}

export default function DAGView({ dag }: Props) {
  const rows = levels(dag);
  if (!rows.length) {
    return <p className="text-sm text-navy/50">No DAG planned (add sites or officials).</p>;
  }

  return (
    <div className="space-y-1">
      {rows.map((level, i) => (
        <div key={i}>
          {i > 0 && (
            <div className="flex justify-center py-1">
              <div className="flex flex-col items-center">
                {level.map((id) => (
                  <div key={id} className="flex items-center gap-1.5 py-0.5">
                    <span className="font-mono text-[10px] text-navy/40">{id}</span>
                    <ChevronDown className="h-3.5 w-3.5 text-navy/35" />
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="flex flex-wrap items-stretch justify-center gap-2">
            {level.map((id) => {
              const task = dag[id];
              const isCore = task.source.startsWith("Core");
              const isOfficial = task.source.startsWith("Official");
              const goldNode = !isOfficial;
              return (
                <div
                  key={id}
                  className={`min-w-[150px] max-w-[240px] flex-1 rounded-xl border px-3 py-2.5 shadow-sm ${
                    goldNode
                      ? "border-gold/60 bg-gradient-to-br from-gold/15 to-gold/5"
                      : "border-navy/70 bg-navy text-cream"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[10px] font-bold uppercase tracking-wide opacity-60">
                      {id}
                    </span>
                    <span
                      className={`rounded-full px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide ${
                        isCore
                          ? "bg-gold text-navy"
                          : goldNode
                            ? "bg-gold/25 text-gold-deep"
                            : "bg-cream/15 text-gold-soft"
                      }`}
                    >
                      {isCore ? "Core" : goldNode ? "Forged" : "Official"}
                    </span>
                  </div>
                  <code className={`mt-1 block break-words text-xs font-semibold ${goldNode ? "text-navy" : "text-cream"}`}>
                    {task.tool}
                  </code>
                  <p className={`mt-0.5 truncate text-[10px] ${goldNode ? "text-navy/50" : "text-cream/60"}`}>
                    {task.source}
                  </p>
                  {task.parallel && (
                    <span className="mt-1 inline-block text-[9px] font-bold uppercase tracking-wider text-gold-deep">
                      ∥ parallel
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
