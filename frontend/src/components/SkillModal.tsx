import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Copy, FileText, Sparkles, X, Zap } from "lucide-react";
import { copyText } from "../api";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  skillContent: string;
  goal?: string;
  mcpName?: string;
}

export default function SkillModal({
  isOpen,
  onClose,
  skillContent,
  goal,
  mcpName = "unified-forge",
}: Props) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = async () => {
    if (await copyText(skillContent)) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/60 p-4 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          className="relative flex max-h-[90vh] w-full max-w-3xl flex-col rounded-3xl border border-navy/15 bg-cream shadow-2xl overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-navy/10 bg-white/80 px-6 py-4 backdrop-blur">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold/20 text-gold-deep">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-display text-lg font-bold text-navy">
                    SKILL.md
                  </h3>
                  <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-[10px] font-bold text-gold-deep uppercase">
                    Single Workflow Skill
                  </span>
                </div>
                <p className="text-xs text-navy/55">
                  Single source of truth for agent execution — directly references `{mcpName}` tools
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="rounded-xl p-2 text-navy/40 hover:bg-navy/5 hover:text-navy transition"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Performance Callout */}
          <div className="flex items-center gap-3 border-b border-navy/10 bg-gold/10 px-6 py-2.5 text-xs text-navy/80 font-medium">
            <Zap className="h-4 w-4 text-gold-deep shrink-0" />
            <span>
              <strong>Optimized for Agent Performance:</strong> No tool rediscovery overhead. Agent executes DAG in sequence.
            </span>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            <pre className="max-h-[55vh] overflow-auto rounded-2xl bg-navy p-5 font-mono text-xs leading-relaxed text-cream/90 shadow-inner">
              <code>{skillContent}</code>
            </pre>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-navy/10 bg-white/80 px-6 py-4">
            <span className="text-xs text-navy/60">
              Saved to <code className="bg-navy/5 px-1.5 py-0.5 rounded font-mono text-navy">mcp_registry/servers/{mcpName}/SKILL.md</code>
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 rounded-xl bg-gold px-4 py-2 font-display text-xs font-bold text-navy shadow-sm transition hover:bg-gold-deep hover:text-cream"
              >
                {copied ? <Check className="h-4 w-4 text-green-700" /> : <Copy className="h-4 w-4" />}
                {copied ? "Copied SKILL.md!" : "Copy SKILL.md"}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="rounded-xl bg-navy px-4 py-2 text-xs font-bold text-cream transition hover:bg-navy/80"
              >
                Close
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
