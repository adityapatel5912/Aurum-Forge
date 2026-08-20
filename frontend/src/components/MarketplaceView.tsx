import { useEffect, useState } from "react";
import {
  Check,
  CheckCircle2,
  ChevronRight,
  Download,
  Filter,
  Layers,
  Package,
  Plus,
  Search,
  Sparkles,
  Tag,
  Upload,
  User,
  Zap,
} from "lucide-react";
import {
  downloadFile,
  getHistory,
  getMarketplace,
  installMarketplacePackage,
  publishToMarketplace,
} from "../api";
import type { HistoryEntry, MarketplacePackage } from "../types";

export default function MarketplaceView() {
  const [packages, setPackages] = useState<MarketplacePackage[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [installingId, setInstallingId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  // Publish Modal State
  const [publishModalOpen, setPublishModalOpen] = useState(false);
  const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState("");
  const [publishAuthor, setPublishAuthor] = useState("local_dev");
  const [publishDescription, setPublishDescription] = useState("");
  const [publishCategory, setPublishCategory] = useState("Browser Automation");
  const [publishTags, setPublishTags] = useState("");
  const [publishing, setPublishing] = useState(false);

  const fetchPackages = async () => {
    setLoading(true);
    try {
      const data = await getMarketplace(searchQuery, selectedCategory);
      setPackages(data.packages || []);
      setCategories(data.categories || []);
    } catch {
      setPackages([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPackages();
  }, [selectedCategory]);

  // Live search: debounce keystrokes so filtering happens as you type
  useEffect(() => {
    const t = window.setTimeout(() => {
      fetchPackages();
    }, 300);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPackages();
  };

  const handleInstall = async (pkg: MarketplacePackage) => {
    setInstallingId(pkg.package_id);
    try {
      const res = await installMarketplacePackage(pkg.package_id);
      if (res.ok) {
        setToast(`Installed '${pkg.name}' & hot-loaded into active IDEs!`);
        fetchPackages();
      }
    } catch (err) {
      setToast(`Install error: ${String(err)}`);
    } finally {
      setInstallingId(null);
      setTimeout(() => setToast(null), 3500);
    }
  };

  const openPublishModal = async () => {
    try {
      const hist = await getHistory();
      setHistoryEntries(hist);
      if (hist.length > 0) {
        setSelectedHistoryId(hist[0].id);
        setPublishDescription(hist[0].goal);
      }
    } catch {
      setHistoryEntries([]);
    }
    setPublishModalOpen(true);
  };

  const handlePublishSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHistoryId) return;
    setPublishing(true);
    try {
      const tagsArray = publishTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      const res = await publishToMarketplace({
        mcp_id: selectedHistoryId,
        author: publishAuthor,
        description: publishDescription,
        category: publishCategory,
        tags: tagsArray,
      });
      if (res.ok) {
        setToast(`Published '${res.package.name}' to Marketplace!`);
        setPublishModalOpen(false);
        fetchPackages();
      }
    } catch (err) {
      setToast(`Publish error: ${String(err)}`);
    } finally {
      setPublishing(false);
      setTimeout(() => setToast(null), 3500);
    }
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-2 rounded-2xl bg-navy px-4 py-3 text-xs font-bold text-cream shadow-2xl ring-1 ring-gold/40 animate-bounce">
          <Zap className="h-4 w-4 text-gold shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-navy/15 bg-gradient-to-br from-navy via-navy to-navy-light p-8 text-cream shadow-card">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-gold/20 px-3 py-1 text-[11px] font-bold tracking-wider text-gold uppercase mb-3">
              <Sparkles className="h-3 w-3" /> Day-0 Clean Package Ecosystem
            </div>
            <h2 className="font-display text-2xl font-bold tracking-tight text-cream sm:text-3xl">
              FORGE Marketplace
            </h2>
            <p className="mt-2 text-sm text-cream/70 leading-relaxed">
              The npm for FastMCP Servers. Publish custom browser & API workforce MCPs with 1-click, and install them into Antigravity, Z Code, Claude Code, and Cursor with zero restart.
            </p>
          </div>

          <button
            onClick={openPublishModal}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gold px-5 py-3.5 font-display text-xs font-bold uppercase tracking-wider text-navy shadow-forge transition hover:bg-gold-deep hover:text-cream shrink-0"
          >
            <Upload className="h-4 w-4" />
            Publish Forged MCP
          </button>
        </div>
      </div>

      {/* Search & Category Filter Toolbar */}
      <div className="flex flex-col gap-4 rounded-3xl border border-navy/10 bg-white/80 p-5 shadow-sm backdrop-blur-sm md:flex-row md:items-center md:justify-between">
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-navy/40" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search MCP servers by name, goal, or tools (e.g. RAM, Notion, devpost)..."
            className="w-full rounded-2xl border border-navy/10 bg-cream/30 py-2.5 pl-11 pr-4 text-xs font-medium text-navy placeholder:text-navy/40 focus:border-gold focus:outline-none focus:ring-2 focus:ring-gold/20"
          />
        </form>

        {/* Categories */}
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setSelectedCategory("")}
            className={`rounded-xl px-3.5 py-2 font-display text-xs font-bold transition ${
              selectedCategory === ""
                ? "bg-navy text-gold shadow-sm"
                : "bg-cream/60 text-navy/70 hover:bg-cream hover:text-navy"
            }`}
          >
            All Packages
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-xl px-3 py-2 font-display text-xs font-bold transition ${
                selectedCategory === cat
                  ? "bg-navy text-gold shadow-sm"
                  : "bg-cream/60 text-navy/70 hover:bg-cream hover:text-navy"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Packages Grid */}
      {loading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              className="h-56 animate-pulse rounded-3xl border border-navy/10 bg-white/40"
            />
          ))}
        </div>
      ) : packages.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-navy/20 bg-cream/40 p-12 text-center">
          <Package className="h-12 w-12 text-navy/30 mb-3" />
          <h3 className="font-display text-base font-bold text-navy">
            Marketplace Registry is Clean (Day 0)
          </h3>
          <p className="mt-1 max-w-md text-xs text-navy/55 leading-relaxed">
            No forged MCPs published yet. Build a new MCP in Forge Studio or click &quot;Publish Forged MCP&quot; to publish your first package to the ecosystem.
          </p>
          <button
            onClick={openPublishModal}
            className="mt-5 inline-flex items-center gap-1.5 rounded-2xl bg-navy px-4 py-2.5 font-display text-xs font-bold text-cream shadow-md hover:bg-navy-light"
          >
            <Upload className="h-3.5 w-3.5 text-gold" />
            Publish from History
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {packages.map((pkg) => (
            <div
              key={pkg.package_id}
              className="flex flex-col justify-between rounded-3xl border border-navy/10 bg-white/90 p-6 shadow-card transition-all duration-200 hover:-translate-y-1 hover:shadow-xl backdrop-blur-sm"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-navy text-gold shadow-sm font-bold font-mono">
                      {pkg.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 min-w-0">
                        <h4 className="font-display text-sm font-bold text-navy truncate" title={pkg.name}>
                          {pkg.name}
                        </h4>
                        {pkg.verified && (
                          <span title="Verified Integrity" className="shrink-0">
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                          </span>
                        )}
                      </div>
                      <span className="text-[11px] font-medium text-navy/50 truncate block" title={`v${pkg.version} • by ${pkg.author}`}>
                        v{pkg.version} &bull; by {pkg.author}
                      </span>
                    </div>
                  </div>

                  <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-gold-deep shrink-0">
                    {pkg.category}
                  </span>
                </div>

                {/* Description */}
                <p className="mt-3.5 text-xs text-navy/70 line-clamp-2 leading-relaxed break-words">
                  {pkg.description}
                </p>

                {/* Tools Pills */}
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {pkg.tools.slice(0, 3).map((t) => (
                    <span
                      key={t}
                      className="rounded-lg bg-navy/5 px-2 py-0.5 font-mono text-[10px] font-semibold text-navy/80 truncate max-w-[130px]"
                      title={t}
                    >
                      {t}
                    </span>
                  ))}
                  {pkg.tools.length > 3 && (
                    <span className="rounded-lg bg-navy/5 px-1.5 py-0.5 text-[10px] font-bold text-navy/50 shrink-0">
                      +{pkg.tools.length - 3} more
                    </span>
                  )}
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-6 flex items-center justify-between border-t border-navy/10 pt-4">
                <span className="text-[11px] font-semibold text-navy/50">
                  {pkg.installs_count} {pkg.installs_count === 1 ? "install" : "installs"}
                </span>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => downloadFile(`/api/download/${pkg.name}-mcp.zip`, `${pkg.name}-mcp.zip`)}
                    className="inline-flex items-center gap-1 rounded-xl border border-navy/20 bg-white/80 px-2.5 py-2 font-display text-xs font-semibold text-navy hover:bg-gold/15 transition"
                    title="Download Standalone Zip (>1KB)"
                  >
                    <Download className="h-3.5 w-3.5 text-gold-deep" />
                    Zip
                  </button>
                  <button
                    onClick={() => handleInstall(pkg)}
                    disabled={installingId === pkg.package_id}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-navy px-3.5 py-2 font-display text-xs font-bold text-cream shadow-sm transition hover:bg-navy-light hover:text-gold disabled:opacity-50"
                  >
                    <Zap className="h-3.5 w-3.5 text-gold" />
                    {installingId === pkg.package_id ? "Hot-Loading..." : "1-Click Install"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Publish Modal */}
      {publishModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/60 p-4 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg rounded-3xl border border-navy/20 bg-cream p-6 shadow-2xl font-sans">
            <h3 className="font-display text-lg font-bold text-navy">
              Publish Forged MCP to Marketplace
            </h3>
            <p className="text-xs text-navy/60 mt-1">
              Select an MCP server from your forge history to publish with single SKILL.md.
            </p>

            <form onSubmit={handlePublishSubmit} className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-navy/70 mb-1">
                  Select Forged Workflow
                </label>
                <select
                  value={selectedHistoryId}
                  onChange={(e) => {
                    setSelectedHistoryId(e.target.value);
                    const item = historyEntries.find((h) => h.id === e.target.value);
                    if (item) setPublishDescription(item.goal);
                  }}
                  className="w-full rounded-2xl border border-navy/15 bg-white p-3 text-xs font-medium text-navy focus:border-gold focus:outline-none"
                >
                  {historyEntries.map((h) => (
                    <option key={h.id} value={h.id}>
                      {h.mcp_name} — {h.goal.slice(0, 40)} ({h.tools.length} tools)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-navy/70 mb-1">
                  Author / Publisher Name
                </label>
                <input
                  type="text"
                  value={publishAuthor}
                  onChange={(e) => setPublishAuthor(e.target.value)}
                  placeholder="e.g. aditya_dev"
                  className="w-full rounded-2xl border border-navy/15 bg-white p-3 text-xs font-medium text-navy focus:border-gold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-navy/70 mb-1">
                  Category
                </label>
                <select
                  value={publishCategory}
                  onChange={(e) => setPublishCategory(e.target.value)}
                  className="w-full rounded-2xl border border-navy/15 bg-white p-3 text-xs font-medium text-navy focus:border-gold focus:outline-none"
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-navy/70 mb-1">
                  Description / Workflow Goal
                </label>
                <textarea
                  rows={2}
                  value={publishDescription}
                  onChange={(e) => setPublishDescription(e.target.value)}
                  className="w-full rounded-2xl border border-navy/15 bg-white p-3 text-xs font-medium text-navy focus:border-gold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-navy/70 mb-1">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  value={publishTags}
                  onChange={(e) => setPublishTags(e.target.value)}
                  placeholder="browser, ram, notion, alert"
                  className="w-full rounded-2xl border border-navy/15 bg-white p-3 text-xs font-medium text-navy focus:border-gold focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setPublishModalOpen(false)}
                  className="rounded-2xl border border-navy/15 px-4 py-2.5 text-xs font-bold text-navy/70 hover:bg-navy/5"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={publishing || !selectedHistoryId}
                  className="rounded-2xl bg-gold px-5 py-2.5 font-display text-xs font-bold text-navy shadow-md hover:bg-gold-deep hover:text-cream disabled:opacity-50"
                >
                  {publishing ? "Publishing..." : "Publish Package"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
