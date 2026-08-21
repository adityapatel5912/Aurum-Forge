# FORGE-AURUM GLITCH HUNTER & AUDIT REPORT
**QA Judge & Senior Developer Perception Audit**
**Evaluation Deadline / Period:** Hackathon 2026 | Proof of Possible ($9,000 Prize Pool)
**System Audit Target:** `http://localhost:5173` (Frontend) & `http://localhost:8740` (REST API / MCP Super-Hub)

---

## 1. Executive Summary & Current Pre-Fix Score

```
========================================================================================
CURRENT SCORE: 60 / 100 — FAIL (JUDGE PERCEPTION: UNPOLISHED / BROKEN DOWNLOADS)
----------------------------------------------------------------------------------------
- Working Implementation:    20 / 30  (Downloads 404, namespace warning spam, missing route)
- Technical Intelligence:    20 / 30  (DAG golden pulse missing, inflated 1.4s AST timer)
- Usability & Developer UX:  10 / 25  (MCPs not downloadable from UI, White theme flicker)
- Responsible Development:   10 / 15  (Vault dirty scan alert subtle, unhandled errors)
========================================================================================
BLOCKING ROADBLOCKS:
1. MCPs NOT DOWNLOADABLE: Clicking 'Download' yields 404 / missing backend route.
2. FastMCP Tool Registration Warnings: Dirty duplicate component stderr spam.
3. AurumDependencyGraph Golden Lines Missing: Rendered as flex cards, not SVG strokes rgb(198,169,107).
4. White Theme Background Inconsistencies: Hardcoded #050C1A causing high-contrast collisions.
5. Self-Heal Latency Display: Reports 1444ms due to Windows disk I/O instead of 9-78ms in-memory AST.
========================================================================================
```

---

## 2. Comprehensive Glitch Inventory (20 Documented Findings)

### [CRITICAL] 1. MCPs Not Downloadable from Skill Bridge (Direct 404)
- **Where:** Skill Bridge View (`SkillBridgeView.tsx`), "Download Zip" button linking to `/dist/unified-mcp.zip`.
- **What judge sees:** Judge clicks "Download Zip" -> Gets a `404 Not Found` error.
- **Why judge thinks not proper:** Judge concludes: *"The MCP generator does not actually produce downloadable files. It's a non-functional mock UI."* Instant disqualification / 0 for exportability.
- **Console/Network:** `GET http://localhost:5173/dist/unified-mcp.zip 404 (Not Found)` (Vite dev server on port 5173 does not proxy static `/dist/` files).
- **Impact on /100:** Usability: 25 &rarr; 5 | Work: 30 &rarr; 15.

---

### [CRITICAL] 2. Missing Generic File Download REST Endpoint in Backend
- **Where:** `backend/main.py` & `frontend/src/api.ts`.
- **What judge sees:** Skill bridge export returns `"download_url": "/api/jobs/export/download?path=..."`, but `backend/main.py` has no endpoint handler registered for `/api/jobs/export/download` or `/api/download/{filename}`.
- **Why judge thinks not proper:** Judge inspecting network calls sees 404 on API download requests.
- **Console/Network:** `GET /api/jobs/export/download -> 404 Not Found`.
- **Impact on /100:** Usability: 25 &rarr; 8 | Work: 30 &rarr; 18.

---

### [CRITICAL] 3. FastMCP Tool Registration Duplicate Name Warning Spam
- **Where:** `forge/mcp/forge_aurum_hub/server.py` (`_register_fastmcp_tool` & `discover_and_load`).
- **What judge sees:** Running `python forge/mcp/forge_aurum_hub/server.py --list-tools` or `@modelcontextprotocol/inspector` dumps 14+ warning lines:
  `WARNING Component already exists: tool:run_chain@...`, `WARNING Component already exists: tool:list_chain_members@...`.
- **Why judge thinks not proper:** Judge thinks tool registry is buggy and name collisions will cause tool hijacking during agent execution.
- **Console/Network:** FastMCP `Component already exists` warnings in terminal and stderr logs.
- **Impact on /100:** Responsible: 15 &rarr; 8 | Intelligence: 30 &rarr; 18.

---

### [CRITICAL] 4. Marketplace Chain MCPs Lack Direct Browser Download Buttons
- **Where:** Marketplace View & AurumDependencyGraph (`MarketplaceView.tsx` / `AurumDependencyGraph.tsx`).
- **What judge sees:** Chains (`chain_content`, `chain_research`, `chain_ops`, `chain_dev_workflow`, `chain_sales_outreach`) only have "1-Click Install", but no direct "Download Zip" button for standalone offline bundles (`dist/chain-*-mcp.zip` >1KB).
- **Why judge thinks not proper:** Judge who wants to test the MCP in an external IDE or command line without running the full super-hub UI cannot download the bundle.
- **Impact on /100:** Usability: 25 &rarr; 10 | Work: 30 &rarr; 20.

---

### [HIGH] 5. AurumDependencyGraph Missing SVG Golden Flow Lines
- **Where:** Center / Right Pane (`AurumDependencyGraph.tsx`).
- **What judge sees:** Dependency graph is rendered using basic HTML card elements rather than interactive SVG curves with `stroke: rgb(198, 169, 107)` connecting root orchestrator &rarr; YOUTUBE / BROWSER / NOTION / SLACK.
- **Why judge thinks not proper:** Judge expects a visual npm-style DAG dependency graph with animated golden pulses.
- **Impact on /100:** Technical Intelligence: 30 &rarr; 20.

---

### [HIGH] 6. White Theme Background Inconsistency & Contrast Flaws
- **Where:** Top OS Bar theme switcher `[Cream | White]` and canvas panels (`OneOSCanvas.tsx`, `index.css`).
- **What judge sees:** Switching between Cream (`#FFFBF0`) and White (`#FFFFFF`) leaves hardcoded dark classes (`bg-[#050C1A]`, `bg-[#081326]`, `bg-[#071022]`) causing visual flicker and unstyled card borders.
- **Why judge thinks not proper:** Judge thinks the theme toggle is broken and unpolished.
- **Impact on /100:** Usability: 25 &rarr; 12.

---

### [HIGH] 7. Self-Heal Studio Latency Display Inflated by Disk I/O (1444ms vs 9-78ms)
- **Where:** `SelfHealDiffView.tsx` & `backend/main.py:591` (`/api/aurum/break-and-heal`).
- **What judge sees:** UI displays `Healed in 1444.55ms` instead of true AST in-memory diagnosis and repair time of 9-78ms (<200ms threshold).
- **Why judge thinks not proper:** Judge sees the `<200ms` claim contradicted by the 1.4s number on screen.
- **Impact on /100:** Intelligence: 30 &rarr; 22.

---

### [HIGH] 8. Visual DAG Canvas Missing Synchronized `@keyframes goldPulse`
- **Where:** `VisualDAGCanvas.tsx` center pane.
- **What judge sees:** SVG canvas animates flow particles, but node borders and dataflow lines do not synchronize with the Aurum Gold `#C6A96B` pulse keyframe animation.
- **Why judge thinks not proper:** The workflow graph looks static and doesn't communicate real-time stage orchestration.
- **Impact on /100:** Intelligence: 30 &rarr; 22.

---

### [MEDIUM] 9. IDE Injector Real File Verification Status
- **Where:** `IDEInjectorView.tsx`.
- **What judge sees:** Shows text "Injected on Disk (0.1s)" upon click, but lacks a live inspect modal or visual preview of the written `~/.antigravity/mcp.json` file on disk with forward slashes (`/`).
- **Why judge thinks not proper:** Judge wants to verify that the file actually exists on their filesystem with clean path normalization.
- **Impact on /100:** Usability: 25 &rarr; 18.

---

### [MEDIUM] 10. Time-Travel Timeline Initial State Missing Canonical Commit
- **Where:** `TimeTravelView.tsx` & `backend/aurum/time_travel.py`.
- **What judge sees:** When opened for the first time, history can appear empty or generate an unindexed hash rather than showcasing the canonical release hash `f6cdbd0a07f2`.
- **Why judge thinks not proper:** Judge sees an empty timeline and assumes version control is unseeded.
- **Impact on /100:** Intelligence: 30 &rarr; 24.

---

### [MEDIUM] 11. Security Vault Dirty Scan Visual Callout
- **Where:** `SecurityVaultView.tsx`.
- **What judge sees:** Scanning dirty code (`sk-proj-...` or `sk-abc123`) correctly flags the secret and sets `can_publish: false`, but the warning banner is subtle instead of a prominent red blocked gate (`#EF4444`).
- **Why judge thinks not proper:** Judge expects a clear and prominent security block preventing unauthorized publishing.
- **Impact on /100:** Responsible: 15 &rarr; 11.

---

### [MEDIUM] 12. Universal Zip Archive File Structure Redundancy
- **Where:** `forge/zip_builder.py`.
- **What judge sees:** Zip archives contain both root files and a subfolder `unified-mcp/`, increasing archive size unnecessarily.
- **Why judge thinks not proper:** Unzipping creates redundant nested directories.
- **Impact on /100:** Work: 30 &rarr; 24.

---

### [MEDIUM] 13. Content Chain Full Workflow Execution Proof Artifacts
- **Where:** `mcp_registry/servers/chain_content/server.py`.
- **What judge sees:** Content chain workflow output must explicitly include verified Notion page URL (`https://notion.so/...`), Slack post confirmation, cryptographic hash, and base64 screenshot proofs.
- **Why judge thinks not proper:** Judge cannot verify the real end-to-end execution without tangible proof artifacts.
- **Impact on /100:** Work: 30 &rarr; 25.

---

### [MEDIUM] 14. Top OS Bar Tool Counter Initial State Jump
- **Where:** `OneOSCanvas.tsx` header.
- **What judge sees:** Hardcoded fallback `67 Tools in 1 MCP` flashes before jumping to `81 Tools in 1 MCP`.
- **Why judge thinks not proper:** Minor visual jump during page load.
- **Impact on /100:** Usability: 25 &rarr; 22.

---

### [LOW] 15. Voice Pilot 60-Second Demo Script Copy Formatting
- **Where:** `VoicePilotView.tsx` "60-Second Demo Script" modal.
- **What judge sees:** Script is clean plain text, but syntax highlights for timestamps (`[00:00 - 00:05]`) enhance readability.
- **Impact on /100:** Usability: 25 &rarr; 23.

---

### [LOW] 16. Benchmark Table Contrast in Light Theme
- **Where:** `LiveBenchmarkView.tsx`.
- **What judge sees:** Comparison table header colors need higher contrast against pure `#FFFFFF` background in light theme.
- **Impact on /100:** Usability: 25 &rarr; 23.

---

### [LOW] 17. Self-Heal Diff Viewer Contrast in Light Theme
- **Where:** `SelfHealDiffView.tsx`.
- **What judge sees:** Diff container retains dark background even in light theme mode.
- **Impact on /100:** Usability: 25 &rarr; 23.

---

### [LOW] 18. Proof Deck & Demo Script Export Verification
- **Where:** `dist/AURUM_DECK.pdf` & `dist/DEMO_SCRIPT.md`.
- **What judge sees:** Needs guaranteed verified generation and accessibility in `dist/`.
- **Impact on /100:** Work: 30 &rarr; 27.

---

### [LOW] 19. Super-Hub Background Watcher Debouncing
- **Where:** `forge/mcp/forge_aurum_hub/watcher.py`.
- **What judge sees:** File watcher should suppress excessive re-scan notifications on rapid file touch events.
- **Impact on /100:** Responsible: 15 &rarr; 14.

---

### [LOW] 20. Voice Preset Auto-Link Toast Notification
- **Where:** `OneOSCanvas.tsx` Voice Input section.
- **What judge sees:** Spoken presets auto-link immediately into the DAG, but a toast notification with the Gold Badge `#C6A96B` improves clarity.
- **Impact on /100:** Usability: 25 &rarr; 24.

---

## 3. Judge Perception Comparison: Before vs Target

| Dimension | Before Audit (Current Glitched State) | Target After Phase 3 Fixes |
| :--- | :--- | :--- |
| **Download Experience** | 404 Not Found on ZIP download links &rarr; *"Fake / unusable"* | Direct blob download of `unified-mcp.zip` & `chain-*-mcp.zip` (200 OK, >1KB) |
| **Super-Hub CLI** | Stderr polluted with FastMCP component duplicate warnings | Clean 0-warning output: `TOTAL TOOLS: 81`, `1 entry in ~/.antigravity/mcp.json` |
| **Theme System** | Background flickers between `#050C1A` and `#FFFFFF`, contrast issues | Seamless Cream `#FFFBF0` &harr; White `#FFFFFF` with 70 Gold `#C6A96B` elements preserved |
| **DAG & Graph Visuals** | Static cards in dependency map, missing pulse | Animated golden curves `rgb(198,169,107)` with `@keyframes goldPulse` |
| **Self-Heal Latency** | 1444ms displayed on screen | True AST in-memory repair of 9-78ms (<200ms threshold) |
| **IDE Injection** | Static feedback | 4 Live Green Ticks with verified forward slash (`/`) disk write to `~/.antigravity/mcp.json` |
| **Final Score** | **60 / 100 (FAIL)** | **100 / 100 (WINNING READY)** |
