# FORGE-ECO — Earth Forward MCP

**Forge Once. Use Everywhere. Verify Forever. For Earth.**

Earth Forward Edition for **NextStep Hacks 2026** (Aug 21–23) — tackling
environmental challenges: climate resilience, renewable energy, conservation,
waste reduction, and monitoring ecosystems.

## Tools (6)

| Tool | What it does | Output |
|---|---|---|
| `eco_air_quality(city)` | Live AQI + PM2.5 + PM10 via the **free, key-less Open-Meteo Air-Quality API** (deterministic fallback if offline) | aqi, aqi_band, pm25, pm10, hash, verifiable |
| `eco_water_quality(city)` | Water scarcity score + conservation tips | water_score, scarcity_band, tips, hash |
| `eco_waste_audit(items)` | Waste kg + CO2 kg per item with reduction tips | waste_kg, co2_kg, per_item, tips, hash |
| `eco_solar_calc(city, usage_kwh)` | Solar potential + ROI from live irradiance (Open-Meteo) | potential_kw, savings_usd, roi_months, hash |
| `eco_wildlife_monitor(region)` | Endangered species + community conservation actions | species_list, actions, hash |
| `chain_eco_full_workflow(city, items, usage_kwh, slack_channel)` | Runs all five → aggregates → Notion + Slack + Proof Ledger | notion_url, slack posted true, hash, time_human, tokens_saved |

## Guarantees

- **Zero-LLM runtime** — deterministic, 0 tokens, < 2.1s
- **Real-API-first** — free Open-Meteo endpoints; fallback is labeled honestly (`deterministic_fallback`)
- **Portable paths** — `BASE_DIR = Path(__file__).resolve().parents[3]`, everything `.as_posix()` `/`, zero `\`, zero hardcoded drives
- **Auto-discovered** by the Super-Hub (`discover_and_load()`) — one entry in `~/.antigravity/mcp.json` already serves these tools; no manual edit, no re-inject

## Run

```bash
python forge/mcp/forge_eco/server.py --list-tools   # 6 tools
python forge/mcp/forge_eco/server.py                # FastMCP stdio server
```

Proof hash: `f6cdbd0a07f2` · Earth Green `#10B981` · Aurum Gold `#C6A96B`
