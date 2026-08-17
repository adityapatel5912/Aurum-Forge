import { Lightbulb, Target } from "lucide-react";

const EXAMPLE_CHIPS = [
  "Find on 2 sites + log to DB",
  "Track drops on stores + notify",
  "Scrape events + order + update sheet",
];

interface Props {
  goal: string;
  onChange: (goal: string) => void;
}

export default function GoalInput({ goal, onChange }: Props) {
  return (
    <section>
      <div className="mb-2 flex items-center gap-2">
        <Target className="h-4 w-4 text-gold-deep" strokeWidth={2.2} />
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider text-navy">
          Why do you need MCPs?
        </h2>
      </div>
      <textarea
        value={goal}
        onChange={(e) => onChange(e.target.value)}
        rows={4}
        placeholder={'Describe workflow goal — e.g. "Find opportunities on Site A with prize > X, check prices on Site B, log to Site C database"'}
        className="w-full resize-none rounded-xl border border-navy/15 bg-white px-4 py-3 text-sm text-navy placeholder:text-navy/35 shadow-sm outline-none transition focus:border-gold focus:ring-2 focus:ring-gold/30"
      />
      <div className="mt-2.5 flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center gap-1 text-xs text-navy/50">
          <Lightbulb className="h-3.5 w-3.5" /> Examples:
        </span>
        {EXAMPLE_CHIPS.map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => onChange(chip)}
            className="rounded-full border border-gold/50 bg-gold/10 px-3 py-1 text-xs font-medium text-navy/75 transition hover:border-gold hover:bg-gold/20 hover:text-navy"
          >
            {chip}
          </button>
        ))}
      </div>
    </section>
  );
}
