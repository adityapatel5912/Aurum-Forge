import { useState } from "react";
import { Check, Copy, FileCode2, KeyRound, MessageSquareQuote } from "lucide-react";
import { copyText } from "../api";

function SnippetBlock({ title, subtitle, text }: { title: string; subtitle: string; text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between gap-2">
        <div>
          <h4 className="flex items-center gap-1.5 font-display text-xs font-semibold text-navy">
            <FileCode2 className="h-3.5 w-3.5 text-gold-deep" /> {title}
          </h4>
          <p className="text-[11px] text-navy/45">{subtitle}</p>
        </div>
        <button
          type="button"
          onClick={async () => {
            if (await copyText(text)) {
              setCopied(true);
              setTimeout(() => setCopied(false), 1800);
            }
          }}
          className="inline-flex items-center gap-1 rounded-lg border border-navy/20 bg-white px-2.5 py-1 text-xs font-semibold text-navy transition hover:border-navy hover:bg-navy hover:text-cream"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-green-600" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="max-h-64 overflow-auto rounded-xl bg-navy p-3.5 text-[11.5px] leading-relaxed text-cream/90">
        <code>{text}</code>
      </pre>
    </div>
  );
}

interface Props {
  result: import("../types").ForgeResult;
}

export default function ConfigSnippet({ result }: Props) {
  const claudeText = JSON.stringify(result.claude_snippet, null, 2);
  const cursorText = JSON.stringify(result.cursor_snippet, null, 2);

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-gold/50 bg-gold/10 p-3.5">
        <div className="flex items-start gap-2.5">
          <KeyRound className="mt-0.5 h-4 w-4 shrink-0 text-gold-deep" />
          <div className="min-w-0">
            <p className="text-xs font-semibold text-navy">Absolute path (auto-filled)</p>
            <code className="mt-1 block break-all rounded-lg bg-white/80 px-2.5 py-1.5 font-mono text-xs text-navy">
              {result.server_path}
            </code>
          </div>
        </div>
      </div>

      <SnippetBlock
        title="claude_config_snippet.json"
        subtitle="Windows %APPDATA%/Claude/ · macOS ~/Library/Application Support/Claude/"
        text={claudeText}
      />
      <SnippetBlock
        title="cursor_config_snippet.json"
        subtitle="Copy into .cursor/mcp.json and reload the window"
        text={cursorText}
      />

      <div className="rounded-xl bg-navy p-4 text-cream shadow-card">
        <div className="flex items-start gap-2.5">
          <MessageSquareQuote className="mt-1 h-4 w-4 shrink-0 text-gold" />
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-gold-soft">
              After config once, just say
            </p>
            <p className="mt-1 break-all font-display text-sm font-semibold leading-snug">
              “{result.say_line}”
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
