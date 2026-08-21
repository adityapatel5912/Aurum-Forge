# PLAYWRIGHT UI VERIFICATION — AGENT HANDOFF PROMPT

Copy everything below this line as the prompt for the Playwright verification agent.

---

You are the UI Verification Agent for the FORGE-AURUM hackathon project
(Devpost "Proof of Possible 2026"). Your job is to drive the real web UI with
Playwright browser automation and verify the judge-facing flows. DO NOT modify
any project code — you only test and report.

## Environment (already prepared — verify, don't rebuild)

- Project root: `D:\Aditya\Forge`
- Backend API: `http://127.0.0.1:8740` (started with
  `cd D:/Aditya/Forge && python backend/main.py --serve --port 8740`)
  - Health check: `GET /api/health` → `{"ok": true, ...}`
- Frontend (Vite dev): `http://localhost:5173`
  (started with `cd D:/Aditya/Forge/frontend && npm run dev`)
  - If 5173 is down, start it in the background and wait for HTTP 200.
  - If 8740 is down, start the backend and wait for `/api/health`.
- Known machine quirk: if Vite fails with an esbuild error, run
  `npm rebuild esbuild` inside `frontend/` once, then restart the dev server.

## Context — what was just fixed (verify these specifically)

1. `frontend/src/App.tsx` — `canForge` now allows goal-only input; the Forge
   button gets a disabled state + tooltip when the goal box is empty.
2. `backend/forge/intents.py` — deterministic intent router: RAM goal → 7 tools
   (`ram_search`, `ram_compare`, `ram_alert`, +4) in <1s; Notion goal → 5 tools;
   "useless/hello" goal → 1 tool `hello`; "test auto update" → `test1/2/3`.
3. `backend/main.py` — voice-to-chain now picks chains by explicit name first
   ("Ops Chain with GitHub…" → chain_ops, NOT research).
4. `VisualDAGCanvas.tsx` — DAG final nodes render Gold (#C6A96B) with pulse;
   T1 nodes show category "trigger" (from DAG meta), not "process".
5. Marketplace self-heal — `/api/marketplace/packages` must return 6 packages.
6. Hub real execution — tools now return REAL payloads
   (`execution_mode: "real"`), not stub strings.

## Test plan (in order)

### T1 — Goal-only forge (was broken, now fixed)
1. Navigate to `http://localhost:5173`.
2. Assert the Forge button is visible: "Forge Unified MCP (2.1s)".
3. With an EMPTY goal box, assert the button is disabled (has
   `disabled` attribute / reduced opacity).
4. Type into the "Plain English Goal" box exactly:
   `Track top 100 RAM products from Amazon, Newegg, BestBuy, Microcenter, B&H sorted by price`
5. Assert the button becomes enabled.
6. Click it. EXPECT: a POST to `/api/forge`, job polling on `/api/jobs/...`,
   completing in <2s with a success toast containing the server name
   (`ram_tracker`), and NO console errors.
7. In the network tab, verify the final job result's `tools` array contains
   `ram_search`, `ram_compare`, `ram_alert` (7 tools total).

### T2 — Voice presets & chain routing (was mis-routed)
1. Click the preset "Video to Notion + Slack 2.1s".
   EXPECT: status line "Auto-linked 4 stages…" or similar; center DAG shows
   nodes for `youtube_get_transcript`, `browser_fetch_enrich`,
   `chain_content_summarize`, `notion_create_page`, `slack_post_message`
   (these are the NEW spec tool names); the LAST node (slack) is Gold
   (#C6A96B) themed; the FIRST node (T1_youtube_transcript) is labeled
   "trigger", not "process".
2. In the "Plain English Goal" box, type:
   `Forge Ops Chain with GitHub Slack Gmail that monitors GitHub issues and alerts Slack and emails`
   then click the "Speak Workflow Command" button (or preset flow).
   EXPECT: the API call `/api/aurum/voice-to-chain` returns `chain_id:
   "chain_ops"` (verify via network response), NOT chain_research.
3. Repeat once with:
   `Forge Dev Chain with GitHub Notion Gmail that creates PR review doc in Notion`
   EXPECT `chain_id: "chain_dev_workflow"`.

### T3 — Marketplace & Graph view
1. Click the "Marketplace & Graph" switch (left rail; there are exactly 9
   switches — count and assert 9).
2. EXPECT: 5 chain cards render ("Research Chain", "Content Creator Chain",
   "Operations & Data Chain", "Dev Lead & Release Chain", "Sales & Growth
   Outreach Chain"), each with an AURUM GOLD badge, a "4 hrs Work Rewritten"
   tag, a "Download Zip" button, and the dependency graph shows golden lines
   (rgb(198,169,107)).
3. Verify `/api/marketplace/packages` (network) returns `packages` with
   length ≥ 6 and every chain package has `aurum_verified: true` + a 12-char
   `hash`.

### T4 — IDE Injector (real file write)
1. Click the "IDE Injector" switch.
2. EXPECT 4 verification lines: Normalized Path (contains
   `/forge_aurum_hub/server.py`), Python 3.x, FastMCP "Import Ready",
   "Gold Verified (#C6A96B)".
3. Click "1-Click Inject into ALL IDEs".
4. After it completes, read `C:/Users/Admin/.antigravity/mcp.json` (via your
   file tools or an evaluate fetch) and verify: `mcpServers` contains exactly
   the key `forge-aurum-hub` with `args` path using FORWARD slashes
   (`D:/Aditya/Forge/forge/mcp/forge_aurum_hub/server.py`) and no other
   registry-redundant entries.

### T5 — Skill Bridge download
1. Click the "Skill Bridge" switch.
2. Click "Generate Universal Skill & Zip" — expect POST
   `/api/aurum/bridge/export` → 200.
3. Click "Download Zip" — expect a download event for `unified-mcp.zip`.
4. Verify the downloaded zip: >1KB; contains exactly `server.py`, `SKILL.md`,
   `requirements.txt`, `README.md`, `forge.mcp.json`, `export.bat`,
   `export.sh`; `python -m py_compile <extracted>/server.py` passes; no `\`
   inside `forge.mcp.json`.

### T6 — Super-hub real execution spot-check (via UI network or hub CLI)
Run in a shell (not Playwright):
`cd D:/Aditya/Forge && python forge/mcp/forge_aurum_hub/server.py --list-tools`
EXPECT: TOTAL TOOLS ≥ 100 and the printed server list includes `ram_tracker`,
`chain_content`, `notion_workspace`, `hello_mcp`, `test_auto_update`.

### T7 — Console hygiene
Across the WHOLE session, assert zero console errors and zero HTTP 5xx
responses in the network log (ignore WebSocket/vite HMR noise).

## Reporting

Write your findings to `dist/PLAYWRIGHT_UI_REPORT.md` with:
- A PASS/FAIL table for T1–T7 with evidence (timings, tool names, file paths).
- Any console errors or failed requests (verbatim).
- Screenshots saved under `dist/` for: goal-only forge success (T1), Gold DAG
  node (T2), marketplace grid (T3), injector ticks (T4).
- A final line: `UI VERIFICATION: PASS` only if T1–T7 all pass; otherwise list
  blockers.

Do NOT fix code. Report only — a separate agent applies fixes.
