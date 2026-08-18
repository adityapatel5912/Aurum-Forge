export interface OfficialTool {
  tool_name: string;
  description: string;
}

export interface Official {
  id: string;
  name: string;
  kind: string;
  token_env: string;
  description: string;
  tools: OfficialTool[];
}

export interface SiteRow {
  id: string;
  url: string;
}

export interface SiteResult {
  url: string;
  slug: string;
  label: string;
  mode: string;
  elements: number;
  tools: string[];
  core_covered?: boolean;
}

export interface OfficialResult {
  id: string;
  name: string;
  tool_names: string[];
  token_env: string;
}

export interface ToolRow {
  name: string;
  source: string;
  badge: "FORGED" | "OFFICIAL" | "CORE";
  description: string;
}

export interface DagTask {
  tool: string;
  source: string;
  parallel?: boolean;
  deps?: string[];
  params?: Record<string, unknown>;
  category?: "trigger" | "process" | "output";
}

export type Dag = Record<string, DagTask>;

export interface ForgeStats {
  custom: number;
  official: number;
  tools_total: number;
  forged: number;
  core: number;
  elapsed_s: number;
}

export type PlatformKey =
  | "claude_code"
  | "cursor"
  | "zcode"
  | "opencode"
  | "antigravity"
  | "codex";

export interface PlatformExport {
  platform_id: PlatformKey;
  platform: string;
  is_cli: boolean;
  command?: string | null;
  config_file: string;
  config_path?: string;
  config: Record<string, unknown>;
  instructions?: string;
}

export interface HistoryEntry {
  id: string;
  timestamp: string;
  goal: string;
  mcp_name: string;
  abs_path: string;
  tools: string[];
  dag: Dag;
  skill_content: string;
  zip_path: string;
}

export interface ForgeRegistryMcpMeta {
  name: string;
  server_path: string;
  description: string;
  tools: { name: string; description: string }[];
  platforms: Record<PlatformKey, PlatformExport>;
  install_command: string;
}

export interface ForgeResult {
  server_name: string;
  version: string;
  goal: string;
  created_at: string;
  detected_officials: string[];
  cores: string[];
  sites: SiteResult[];
  officials: OfficialResult[];
  tools: ToolRow[];
  dag: Dag;
  server_py: string;
  server_path: string;
  zip_path: string;
  zip_name: string;
  claude_snippet: Record<string, unknown>;
  cursor_snippet: Record<string, unknown>;
  skill_content?: string;
  export_configs?: Record<PlatformKey, PlatformExport>;
  history_id?: string;
  history_entry?: HistoryEntry;
  readme: string;
  say_line: string;
  stats: ForgeStats;
  diagnostics: unknown;
}

export interface JobStep {
  key: string;
  label: string;
  state: "pending" | "active" | "done" | "error";
}

export interface JobState {
  id: string;
  status: "running" | "done" | "error";
  steps: JobStep[];
  result: ForgeResult | null;
  error: string | null;
  download_url?: string;
}

// ------------------------------------------------------------- OS Additions
export interface IDEConfigItem {
  ide_name: string;
  config_path: string;
  format: string;
  snippet?: Record<string, unknown>;
  cli_command?: string;
  how_to_connect: string;
  is_cli: boolean;
}

export interface UniversalConfig {
  version: string;
  name: string;
  description: string;
  active_mcp: {
    name: string;
    server_path: string;
    command: string;
    args: string[];
    env?: Record<string, string>;
  };
  servers: Record<string, {
    name: string;
    description: string;
    command: string;
    args: string[];
  }>;
  ides: Record<string, IDEConfigItem>;
  export_scripts: {
    windows: string;
    unix: string;
  };
}

export interface SystemValidation {
  ok: boolean;
  path_exists: boolean;
  server_path: string;
  python_available: boolean;
  python_version: string;
  fastmcp_ready: boolean;
  root_normalized: string;
}

export interface MarketplacePackage {
  package_id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  category: string;
  tags: string[];
  tools_count: number;
  tools: string[];
  dag?: Dag;
  server_path: string;
  skill_content?: string;
  installs_count: number;
  verified: boolean;
  published_at: string;
}

export interface BenchmarkBaseline {
  name: string;
  time_to_first_tool_s: number;
  tool_count: number;
  tokens_consumed: number;
  token_savings_pct: number;
  api_cost_usd: number;
  api_key_required: boolean;
  self_heal_latency_ms: number;
  hot_load_latency_s: number;
  zero_llm_mode: boolean;
  supports_ide_hotload: boolean;
  single_root_skill: boolean;
  resilience_score: number;
  live_measured_time_s?: number;
}

export interface BenchmarkData {
  ok: boolean;
  tested_at: string;
  mcp_name: string;
  summary: {
    headline: string;
    speedup_vs_stainless_x: number;
    token_savings_tokens: number;
    cost_savings_usd: number;
    self_heal_speed: string;
  };
  baselines: {
    forge_infinity: BenchmarkBaseline;
    stainless: BenchmarkBaseline;
    spex: BenchmarkBaseline;
    manual_llm: BenchmarkBaseline;
  };
  radar_comparison: Array<{
    metric: string;
    FORGE_INFINITY: number;
    Stainless: number;
    Spex: number;
    Manual: number;
  }>;
  live_execution: {
    live_measured_seconds: number;
    tools_generated: number;
    zero_llm: boolean;
    tokens_used: number;
    api_cost: number;
    speedup_vs_stainless: number;
    speedup_vs_spex: number;
    speedup_vs_manual: number;
  };
}

export interface SelfHealResult {
  ok: boolean;
  server_path: string;
  errors_detected: string[];
  patches_applied: string[];
  code_modified: boolean;
  compilation_verified: boolean;
  compilation_error?: string | null;
  diff: string;
  elapsed_ms: number;
  message: string;
  before_code?: string;
  after_code?: string;
  badge?: string;
}

// ------------------------------------------------------------- FORGE-AURUM SUPER-HUB TYPES
export interface AurumTool {
  name: string;
  description: string;
  badge: string;
  badge_color: string;
  source: string;
  official_id?: string;
  chain_id?: string;
  verified?: boolean;
}

export interface AurumHubCatalog {
  server_name: string;
  total_tools_count: number;
  aurum_gold_badge: string;
  categories: {
    core_tools: number;
    official_wrapped_tools: number;
    production_chain_tools: number;
  };
  tools: AurumTool[];
}

export interface AurumChainDependency {
  source: string;
  target: string;
  label: string;
}

export interface AurumChain {
  id: string;
  name: string;
  tagline: string;
  description: string;
  category: string;
  author: string;
  version: string;
  work_rewritten_hours: number;
  badge: string;
  badge_color: string;
  members: string[];
  dependencies: AurumChainDependency[];
  dag: Dag;
  tools: Array<{ name: string; badge: string; description: string }>;
}

export interface AurumSecurityFinding {
  rule: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  message: string;
  line: number;
}

export interface AurumSecurityReport {
  target: string;
  security_score: number;
  aurum_security_badge: boolean;
  badge_color: string;
  badge_label: string;
  can_publish: boolean;
  findings_count: number;
  findings: AurumSecurityFinding[];
  clean: boolean;
  summary: string;
}

export interface AurumTimeTravelCommit {
  version_id: string;
  version: string;
  target_id: string;
  hash: string;
  timestamp: string;
  author: string;
  summary: string;
  tools_count: number;
  tools: any[];
  dag: Dag;
  server_py: string;
  skill_content: string;
  aurum_proof: {
    verified: boolean;
    badge: string;
    security_score: number;
    latency_ms: number;
    work_rewritten_hours?: number;
  };
}

export interface LiveBenchmarkData {
  ok: boolean;
  tested_at: string;
  mcp_name: string;
  badge: string;
  live_speed_test: {
    live_measured_seconds: number;
    stainless_baseline_seconds: number;
    speedup_factor: number;
    tokens_consumed: number;
    tokens_saved: number;
    api_cost_usd: number;
    cost_saved_usd: number;
    zero_llm_mode: boolean;
  };
  baselines: Record<string, BenchmarkBaseline>;
  radar_comparison: Array<{
    metric: string;
    FORGE_AURUM: number;
    Stainless: number;
    Spex: number;
    Manual: number;
  }>;
}

export interface ProofLedgerStep {
  tool: string;
  stage?: string;
  color?: string;
  action: string;
  latency_ms: number;
  status: "success" | "error";
  screenshot?: string;
  notion_link?: string;
  email_preview?: {
    to?: string;
    subject?: string;
    body_snippet?: string;
  };
  params?: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface ProofLedgerData {
  chain_id: string;
  hash: string;
  aurum_verified: boolean;
  badge: string;
  badge_color: string;
  executed_at: string;
  steps: ProofLedgerStep[];
  steps_count: number;
  time_human: string;
  time_aurum: string;
  tokens_saved: string;
  cost_saved: string;
  total_latency_ms: number;
  verifiable: boolean;
  verification_details?: {
    hash_algorithm: string;
    sandbox_isolation: string;
    zero_api_tokens: boolean;
    diff_self_healed: boolean;
    credential_status: string;
  };
}

export interface VoicePilotStepResult {
  step_index: number;
  step_key: string;
  step_name: string;
  status: string;
  elapsed_ms: number;
  elapsed_s?: number;
  message: string;
  [key: string]: unknown;
}

export interface VoicePilotResult {
  ok: boolean;
  status: string;
  voice_transcript: string;
  chain_id: string;
  chain_name: string;
  hash: string;
  aurum_verified: boolean;
  badge: string;
  total_time_seconds: number;
  time_saved_human: string;
  tokens_saved: string;
  cost_saved: string;
  steps: VoicePilotStepResult[];
  proof_ledger: ProofLedgerData;
  files_created: {
    server_py: string;
    zip_path: string;
    skill_path: string;
    marketplace_json: string;
    antigravity_config: string;
  };
  summary: string;
}

export type InspectorTab =
  | "voice_pilot"
  | "benchmark"
  | "self_heal"
  | "injector"
  | "marketplace"
  | "wrapper"
  | "skill_bridge"
  | "time_travel"
  | "vault";

