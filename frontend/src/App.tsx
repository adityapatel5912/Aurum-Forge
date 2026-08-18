import { useCallback, useEffect, useRef, useState } from "react";
import { Zap } from "lucide-react";
import { getOfficials, getJob, startForge } from "./api";
import type { ForgeResult, JobState, Official, SiteRow } from "./types";
import OneOSCanvas from "./components/OneOSCanvas";

const POLL_MS = 800;

export default function App() {
  const [goal, setGoal] = useState("");
  const [sites, setSites] = useState<SiteRow[]>([{ id: "site-1", url: "" }]);
  const [catalog, setCatalog] = useState<Official[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const [phase, setPhase] = useState<"idle" | "running" | "done" | "error">("idle");
  const [job, setJob] = useState<JobState | null>(null);
  const [jobId, setJobId] = useState<string | undefined>(undefined);
  const [result, setResult] = useState<ForgeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3200);
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem("forge_theme") || "cream";
    document.documentElement.setAttribute("data-theme", savedTheme);
    getOfficials()
      .then(setCatalog)
      .catch(() => setCatalog([]));
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  const toggleOfficial = (id: string) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const urls = sites.map((s) => s.url.trim()).filter(Boolean);
  const canForge = goal.trim().length > 0 && (urls.length > 0 || selected.size > 0);

  const poll = useCallback((id: string) => {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const snap = await getJob(id);
        setJob(snap);
        if (snap.status === "done" && snap.result) {
          if (pollRef.current) window.clearInterval(pollRef.current);
          setResult(snap.result);
          setPhase("done");
          showToast(`Forged ${snap.result.server_name} in ${snap.result.stats.elapsed_s}s!`);
        } else if (snap.status === "error") {
          if (pollRef.current) window.clearInterval(pollRef.current);
          setError(snap.error ?? "Forge error");
          setPhase("error");
        }
      } catch (err) {
        if (pollRef.current) window.clearInterval(pollRef.current);
        setError(String(err));
        setPhase("error");
      }
    }, POLL_MS);
  }, []);

  const handleStartForge = async () => {
    if (!canForge || phase === "running") return;
    setPhase("running");
    setJob(null);
    setResult(null);
    setError(null);
    try {
      const { job_id } = await startForge({ goal: goal.trim(), urls, officials: [...selected] });
      setJobId(job_id);
      poll(job_id);
    } catch (err) {
      setError(String(err));
      setPhase("error");
    }
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#050C1A] text-cream">
      {/* Toast Notification */}
      {toastMsg && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-2 rounded-2xl bg-navy px-4 py-3 text-xs font-bold text-cream shadow-2xl ring-1 ring-gold/40 animate-bounce">
          <Zap className="h-4 w-4 text-gold shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Main Single OS Canvas View */}
      <OneOSCanvas
        goal={goal}
        setGoal={setGoal}
        sites={sites}
        setSites={setSites}
        catalog={catalog}
        selectedOfficials={selected}
        toggleOfficial={toggleOfficial}
        onStartForge={handleStartForge}
        isForging={phase === "running"}
        result={result}
      />
    </div>
  );
}
