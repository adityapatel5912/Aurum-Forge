import { MessageSquareText, Globe2, BadgeCheck, Server } from "lucide-react";

const STEPS = [
  {
    icon: MessageSquareText,
    title: "Tell Why",
    text: "Describe the workflow you want in plain English — the goal drives the plan.",
  },
  {
    icon: Globe2,
    title: "Add Sites",
    text: "Any websites you use — official APIs are auto-detected, others are scouted and forged (2 tools each + 7 core tools always).",
  },
  {
    icon: BadgeCheck,
    title: "Select Official",
    text: "Toggle the official MCPs you already use — they get wrapped in too.",
  },
  {
    icon: Server,
    title: "One Unified Server",
    text: "Get one server.py + ZIP. Configure once in Claude/Cursor — then just say the path.",
  },
];

export default function HowItWorks() {
  return (
    <section className="mx-auto w-full max-w-6xl px-6 pb-14">
      <h2 className="mb-5 text-center font-display text-sm font-semibold uppercase tracking-[0.2em] text-navy/50">
        How it works
      </h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {STEPS.map(({ icon: Icon, title, text }, i) => (
          <div
            key={title}
            className="relative rounded-2xl border border-navy/10 bg-white/70 p-4 shadow-sm backdrop-blur-sm"
          >
            <span className="absolute right-3 top-3 font-display text-2xl font-bold text-navy/10">
              {i + 1}
            </span>
            <div className="mb-2 inline-flex rounded-xl bg-navy p-2">
              <Icon className="h-4 w-4 text-gold" />
            </div>
            <h3 className="font-display text-sm font-semibold text-navy">{title}</h3>
            <p className="mt-1 text-xs leading-relaxed text-navy/55">{text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
