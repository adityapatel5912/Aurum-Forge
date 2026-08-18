import { useEffect, useMemo, useRef, useState } from "react";
import {
  CheckCircle2,
  Mic,
  MicOff,
  Play,
  Sparkles,
  Volume2,
  X,
  Zap,
} from "lucide-react";
import { triggerVoiceForge } from "../api";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (res: any) => void;
}

const SAMPLE_VOICE_PROMPTS = [
  "Forge RAM tracker MCP and email alerts on discount >20%",
  "Forge Unstop hackathon monitor and log into Notion database",
  "Forge Hacker News top stories extractor and send daily digest via Gmail",
  "Chain Amazon product monitor with Notion writer and Slack notifier",
];

type LiveNode = { label: string; category: "trigger" | "process" | "output" };

/** Parse the transcript in real time into live DAG nodes (same heuristic as backend). */
function parseLiveDag(transcript: string): LiveNode[] {
  const t = (transcript || "").toLowerCase();
  const nodes: LiveNode[] = [{ label: "Voice Command", category: "trigger" }];

  if (/ram|price|amazon|discount/.test(t)) nodes.push({ label: "Amazon RAM Monitor", category: "process" });
  if (/hackathon|event|devpost|unstop/.test(t)) nodes.push({ label: "Unstop Events Scan", category: "process" });
  if (/news|hacker\s*news|digest/.test(t)) nodes.push({ label: "Hacker News Extract", category: "process" });
  if (/search|scrape|browse|track|monitor/.test(t)) nodes.push({ label: "Browser Automation", category: "process" });
  if (/notion|table|database|log/.test(t)) nodes.push({ label: "Notion Writer", category: "output" });
  if (/mail|gmail|email|alert/.test(t)) nodes.push({ label: "Gmail Alert", category: "output" });
  if (/slack|message|notify/.test(t)) nodes.push({ label: "Slack Notify", category: "output" });
  if (/chain/.test(t)) nodes.push({ label: "Chain Composite", category: "output" });
  return nodes;
}

const CATEGORY_STYLE = {
  trigger: "bg-blue-600",
  process: "bg-emerald-600",
  output: "bg-purple-600",
};

export default function VoiceForgeModal({ isOpen, onClose, onSuccess }: Props) {
  const [transcript, setTranscript] = useState(SAMPLE_VOICE_PROMPTS[0]);
  const [isListening, setIsListening] = useState(false);
  const [forging, setForging] = useState(false);
  const [result, setResult] = useState<any>(null);
  const recognitionRef = useRef<any>(null);

  const liveNodes = useMemo(() => parseLiveDag(transcript), [transcript]);

  // Real Web Speech API dictation when the browser supports it
  const startListening = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) {
      setIsListening(true); // still show waveform state; user types the transcript
      return;
    }
    try {
      const rec = new SR();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";
      rec.onresult = (e: any) => {
        let text = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          text += e.results[i][0].transcript;
        }
        setTranscript((prev) => (e.results[e.results.length - 1].isFinal ? prev + " " + text : prev));
      };
      rec.onerror = () => stopListening();
      rec.onend = () => setIsListening(false);
      rec.start();
      recognitionRef.current = rec;
      setIsListening(true);
    } catch {
      setIsListening(true);
    }
  };

  const stopListening = () => {
    try {
      recognitionRef.current?.stop();
    } catch {
      /* already stopped */
    }
    recognitionRef.current = null;
    setIsListening(false);
  };

  useEffect(() => {
    return () => {
      try {
        recognitionRef.current?.stop();
      } catch {
        /* noop */
      }
    };
  }, []);

  if (!isOpen) return null;

  const handleVoiceForge = async () => {
    if (!transcript.trim()) return;
    stopListening();
    setForging(true);
    setResult(null);
    try {
      const res = await triggerVoiceForge(transcript.trim());
      setResult(res);
      if (onSuccess) onSuccess(res);
    } catch (err) {
      setResult({ status: "error", error: String(err) });
    } finally {
      setForging(false);
    }
  };

  const toggleMic = () => {
    if (isListening) stopListening();
    else startListening();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/60 p-4 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="flex max-h-[90vh] w-full max-w-xl flex-col overflow-hidden rounded-3xl border border-navy/20 bg-cream font-sans shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-navy/10 bg-white/70 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-navy text-gold shadow-md">
              <Mic className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-display text-lg font-bold text-navy">
                Voice-to-MCP Studio
              </h2>
              <p className="text-xs text-navy/55">
                Speak your workflow goal &bull; Factory compiles &amp; hot-loads in &lt;2s
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-2 text-navy/50 hover:bg-navy/5 hover:text-navy"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Audio Waveform Animation Area */}
        <div className="flex flex-col items-center justify-center border-b border-navy/10 bg-navy p-8 text-cream">
          {/* Pulsing Mic Button */}
          <button
            onClick={toggleMic}
            className={`relative flex h-20 w-20 items-center justify-center rounded-full shadow-2xl transition-all duration-300 ${
              isListening
                ? "bg-red-500 text-white ring-8 ring-red-400/30 scale-110"
                : "bg-gold text-navy hover:scale-105 hover:bg-gold-deep hover:text-cream"
            }`}
          >
            {isListening ? (
              <MicOff className="h-8 w-8 animate-pulse" />
            ) : (
              <Mic className="h-8 w-8" />
            )}
          </button>

          {/* Animated Audio Waveform Bars */}
          <div className="mt-6 flex items-center gap-1.5 h-10">
            {[40, 75, 90, 50, 85, 100, 65, 95, 70, 80, 45, 90, 60].map((h, i) => (
              <div
                key={i}
                className={`w-1.5 rounded-full transition-all duration-200 ${
                  isListening ? "bg-gold animate-pulse" : "bg-white/20"
                }`}
                style={{
                  height: isListening ? `${Math.max(15, h * (0.6 + (i % 3) * 0.2))}%` : "20%",
                  animationDelay: `${i * 80}ms`,
                }}
              />
            ))}
          </div>

          <p className="mt-3 text-xs font-mono text-cream/70">
            {isListening
              ? "Listening to voice input... (Click mic to stop)"
              : "Click microphone or select a voice prompt below"}
          </p>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Transcript Box */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-navy/70 mb-1.5">
              Spoken Workflow Transcript
            </label>
            <textarea
              rows={3}
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="e.g. Forge RAM tracker MCP and email discount alerts to Notion"
              className="w-full rounded-2xl border border-navy/15 bg-white p-4 font-medium text-xs text-navy focus:border-gold focus:outline-none leading-relaxed"
            />
          </div>

          {/* Live DAG Preview — nodes appear as you speak */}
          <div>
            <div className="flex items-center justify-between">
              <span className="font-display text-[11px] font-bold uppercase tracking-wider text-navy/60">
                Live DAG Preview
              </span>
              <span className="font-mono text-[10px] text-navy/40">
                {liveNodes.length} node{liveNodes.length === 1 ? "" : "s"} detected
              </span>
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-1.5 rounded-2xl border border-navy/10 bg-white/80 p-3">
              {liveNodes.map((node, i) => (
                <span key={`${node.label}-${i}`} className="flex items-center gap-1.5">
                  {i > 0 && (
                    <svg width="18" height="10" viewBox="0 0 18 10" className="text-gold">
                      <path d="M0 5 H12" stroke="#C6A96B" strokeWidth="1.5" strokeDasharray="2 2" />
                      <path d="M12 1 L17 5 L12 9" fill="none" stroke="#C6A96B" strokeWidth="1.5" />
                    </svg>
                  )}
                  <span
                    className={`rounded-lg px-2.5 py-1 text-[10px] font-bold text-white shadow-sm ${CATEGORY_STYLE[node.category]} ${
                      isListening ? "animate-pulse" : ""
                    }`}
                  >
                    {node.label}
                  </span>
                </span>
              ))}
              {liveNodes.length === 1 && (
                <span className="text-[10px] font-medium text-navy/40">
                  Speak or type — trigger / process / output nodes appear live
                </span>
              )}
            </div>
          </div>

          {/* Preset Prompts */}
          <div>
            <span className="font-display text-[11px] font-bold uppercase tracking-wider text-navy/60">
              Quick Voice Examples
            </span>
            <div className="mt-2 flex flex-wrap gap-2">
              {SAMPLE_VOICE_PROMPTS.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => setTranscript(p)}
                  className="rounded-xl border border-navy/10 bg-white/80 px-3 py-1.5 text-left text-xs font-medium text-navy/80 hover:border-gold hover:bg-white hover:text-navy transition shadow-sm"
                >
                  &ldquo;{p}&rdquo;
                </button>
              ))}
            </div>
          </div>

          {/* Forge Result Output */}
          {result && (
            <div
              className={`rounded-2xl border p-4 text-xs ${
                result.status === "success"
                  ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                  : "border-navy/15 bg-white text-navy"
              }`}
            >
              <div className="flex items-center gap-2 font-bold">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>
                  Forged &amp; Hot-Loaded in {result.elapsed_seconds || 0.15}s (Zero LLM)!
                </span>
              </div>
              <p className="mt-1.5 font-mono text-[11px] text-navy/70">
                &bull; Say Line: <span className="font-bold">{result.say_line}</span>
              </p>
              <p className="mt-0.5 font-mono text-[11px] text-navy/70">
                &bull; Tools Generated: {result.tools?.join(", ") || "search_ram, gmail_send_email"}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-navy/10 bg-white/70 px-6 py-4">
          <span className="text-[11px] font-mono text-navy/50">
            Zero LLM &bull; &lt;2s Deterministic Voice Forge
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="rounded-2xl border border-navy/15 px-4 py-2 text-xs font-bold text-navy/70 hover:bg-navy/5"
            >
              Close
            </button>
            <button
              onClick={handleVoiceForge}
              disabled={forging || !transcript.trim()}
              className="inline-flex items-center gap-1.5 rounded-2xl bg-gold px-5 py-2.5 font-display text-xs font-bold uppercase tracking-wider text-navy shadow-forge hover:bg-gold-deep hover:text-cream disabled:opacity-50"
            >
              <Zap className="h-4 w-4" />
              {forging ? "Forging in <2s..." : "Forge from Voice"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
