import { useEffect, useState } from "react";
import {
  Check,
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Lock,
  RefreshCw,
  Save,
  Shield,
  ShieldCheck,
  Sparkles,
  X,
  Zap,
} from "lucide-react";
import { getSecrets, injectSecrets, saveSecrets } from "../api";
import type { SecretsVaultData } from "../types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSaved?: () => void;
}

export default function SecretsVaultModal({ isOpen, onClose, onSaved }: Props) {
  const [vaultData, setVaultData] = useState<SecretsVaultData | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [injecting, setInjecting] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchVault = async () => {
    setLoading(true);
    try {
      const data = await getSecrets();
      setVaultData(data);
      const initialForm: Record<string, string> = {};
      for (const svc of data.services) {
        for (const k of svc.keys) {
          if (k.is_configured) {
            initialForm[k.key] = k.masked_value;
          }
        }
      }
      setFormData(initialForm);
    } catch (err) {
      console.error("Failed to load secrets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchVault();
      setStatusMsg(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleInputChange = (key: string, value: string) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const toggleShow = (key: string) => {
    setShowPassword((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async (andInject = false) => {
    setSaving(!andInject);
    setInjecting(andInject);
    setStatusMsg(null);
    try {
      const res = await saveSecrets(formData);
      setVaultData(res);
      if (andInject) {
        const injRes = await injectSecrets("all");
        if (injRes.ok) {
          setStatusMsg({
            type: "success",
            text: "Tokens saved and injected directly into Cursor, Antigravity, Codex, and Z Code!",
          });
        } else {
          setStatusMsg({ type: "success", text: "Tokens saved successfully!" });
        }
      } else {
        setStatusMsg({ type: "success", text: "Tokens saved to local secure vault!" });
      }
      if (onSaved) onSaved();
    } catch (err) {
      setStatusMsg({ type: "error", text: `Failed to save: ${String(err)}` });
    } finally {
      setSaving(false);
      setInjecting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/70 p-4 backdrop-blur-md animate-in fade-in duration-200">
      <div className="flex max-h-[92vh] w-full max-w-4xl flex-col overflow-hidden rounded-3xl border border-gold/30 bg-[#070B14] font-sans text-cream shadow-[0_0_50px_rgba(198,169,107,0.25)]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gold/20 bg-[#0B1120] px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-gold/40 bg-gold/15 text-gold shadow-md">
              <KeyRound className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold tracking-wide text-cream">
                  Official MCP Secrets & Token Vault
                </h2>
                <span className="rounded-full border border-gold/40 bg-gold/20 px-2.5 py-0.5 text-[10px] font-bold text-gold">
                  ZERO-LEAK DIRECT INJECTION
                </span>
              </div>
              <p className="text-xs text-cream/70">
                Enter API keys & tokens through the UI. Injected directly into IDE environment blocks — no need to give secrets to the agent!
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-2 text-cream/50 transition hover:bg-white/10 hover:text-cream"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Security Assurance Banner */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] bg-[#0A1224] px-6 py-3 text-xs">
          <div className="flex items-center gap-2 text-emerald-400">
            <ShieldCheck className="h-4 w-4 shrink-0" />
            <span className="font-semibold">
              Client-Side & IDE Direct Injection: Secrets are stored locally and never exposed in agent chat transcripts.
            </span>
          </div>
          {vaultData && (
            <div className="flex items-center gap-2 text-[11px] font-mono text-gold">
              <span>Configured:</span>
              <span className="rounded bg-gold/20 px-2 py-0.5 font-bold text-gold">
                {vaultData.configured_keys} / {vaultData.total_keys} Tokens
              </span>
            </div>
          )}
        </div>

        {/* Notification Status */}
        {statusMsg && (
          <div
            className={`mx-6 mt-4 flex items-center gap-2 rounded-xl p-3 text-xs font-semibold ${
              statusMsg.type === "success"
                ? "border border-emerald-500/40 bg-emerald-950/50 text-emerald-300"
                : "border border-red-500/40 bg-red-950/50 text-red-300"
            }`}
          >
            {statusMsg.type === "success" ? (
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
            ) : (
              <Shield className="h-4 w-4 shrink-0 text-red-400" />
            )}
            <span>{statusMsg.text}</span>
          </div>
        )}

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && !vaultData ? (
            <div className="flex items-center justify-center py-12 text-xs text-cream/50">
              <RefreshCw className="h-5 w-5 animate-spin mr-2 text-gold" />
              Loading secure vault...
            </div>
          ) : (
            vaultData?.services.map((svc) => (
              <div
                key={svc.service}
                className="rounded-2xl border border-white/[0.08] bg-[#0A0F1D] p-4 shadow-sm transition-all hover:border-gold/30"
              >
                <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-cream">{svc.name}</span>
                    <span className="text-[11px] text-cream/50 font-mono">
                      (Official FastMCP)
                    </span>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                      svc.configured
                        ? "border border-emerald-500/40 bg-emerald-500/20 text-emerald-300"
                        : "border border-amber-500/40 bg-amber-500/20 text-amber-300"
                    }`}
                  >
                    {svc.configured ? (
                      <>
                        <Check className="h-3 w-3" /> Ready & Configured
                      </>
                    ) : (
                      "Missing Credentials"
                    )}
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {svc.keys.map((k) => {
                    const isVisible = showPassword[k.key] || false;
                    const val = formData[k.key] || "";
                    return (
                      <div key={k.key} className="flex flex-col gap-1">
                        <div className="flex items-center justify-between text-[11px]">
                          <label className="font-semibold text-cream/80 flex items-center gap-1">
                            {k.label}
                            {k.required && <span className="text-amber-400">*</span>}
                          </label>
                          <span className="font-mono text-[10px] text-gold/80">{k.key}</span>
                        </div>
                        <div className="relative flex items-center">
                          <input
                            type={isVisible ? "text" : "password"}
                            value={val}
                            onChange={(e) => handleInputChange(k.key, e.target.value)}
                            placeholder={k.placeholder}
                            className="w-full rounded-xl border border-white/[0.1] bg-[#050811] px-3 py-2 pr-9 font-mono text-xs text-cream placeholder-cream/20 outline-none transition focus:border-gold focus:ring-1 focus:ring-gold"
                          />
                          <button
                            type="button"
                            onClick={() => toggleShow(k.key)}
                            className="absolute right-2.5 text-cream/40 hover:text-cream transition"
                            title={isVisible ? "Hide" : "Show"}
                          >
                            {isVisible ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                          </button>
                        </div>
                        <span className="text-[10px] text-cream/45">{k.description}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-gold/20 bg-[#0B1120] px-6 py-4">
          <span className="text-[11px] text-cream/60">
            Injected into: <strong className="text-gold">Cursor</strong>,{" "}
            <strong className="text-gold">Antigravity</strong>,{" "}
            <strong className="text-gold">Codex</strong>, and{" "}
            <strong className="text-gold">Z Code</strong>
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleSave(false)}
              disabled={saving || injecting}
              className="flex items-center gap-1.5 rounded-xl border border-gold/40 bg-gold/10 px-4 py-2 text-xs font-bold text-gold transition hover:bg-gold/20 disabled:opacity-50"
            >
              <Save className="h-3.5 w-3.5" />
              {saving ? "Saving..." : "Save Locally"}
            </button>
            <button
              onClick={() => handleSave(true)}
              disabled={saving || injecting}
              className="flex items-center gap-1.5 rounded-xl bg-gold px-5 py-2 text-xs font-bold text-navy shadow-lg transition hover:bg-gold-light hover:shadow-[0_0_20px_rgba(198,169,107,0.5)] disabled:opacity-50"
            >
              <Zap className="h-3.5 w-3.5" />
              {injecting ? "Injecting into All IDEs..." : "Save & 1-Click Inject All"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
