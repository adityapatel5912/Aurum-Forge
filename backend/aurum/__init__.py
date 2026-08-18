"""FORGE-AURUM SUPER-HUB Core Package.

Ecosystem OS providing:
- Aurum Wrapper (Official MCPs -> Aurum Gold)
- Super-Hub (50-in-1 unified FastMCP aggregator)
- 5 Real Work Production Chains
- Universal Skill Bridge (MCP <-> universal SKILL.md + unified-mcp.zip for all IDEs)
- Time-Travel (Git-like commit versioning & 1-click rollback)
- Security Vault (AST & secret scanner with Aurum Security Gold Badge)
"""
from __future__ import annotations

from backend.aurum.chains import (
    PRODUCTION_CHAINS,
    get_all_chains,
    get_chain_by_id,
    seed_production_chains,
)
from backend.aurum.security_vault import (
    AurumSecurityReport,
    scan_mcp_security,
    scan_source_security,
)
from backend.aurum.skill_bridge import (
    convert_mcp_to_universal_skill,
    export_universal_bundle,
    import_skill_to_mcp,
)
from backend.aurum.super_hub import (
    AurumSuperHub,
    get_super_hub,
)
from backend.aurum.time_travel import (
    commit_version,
    get_version_history,
    rollback_to_version,
)
from backend.aurum.wrapper import (
    OFFICIAL_AURUM_CATALOG,
    get_wrapped_official_server,
    wrap_official_mcp,
)

__all__ = [
    "OFFICIAL_AURUM_CATALOG",
    "wrap_official_mcp",
    "get_wrapped_official_server",
    "AurumSuperHub",
    "get_super_hub",
    "PRODUCTION_CHAINS",
    "get_all_chains",
    "get_chain_by_id",
    "seed_production_chains",
    "convert_mcp_to_universal_skill",
    "export_universal_bundle",
    "import_skill_to_mcp",
    "commit_version",
    "get_version_history",
    "rollback_to_version",
    "scan_source_security",
    "scan_mcp_security",
    "AurumSecurityReport",
]
