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
