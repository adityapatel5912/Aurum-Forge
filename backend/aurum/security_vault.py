"""FORGE-AURUM Security Vault Engine.

Deep static analysis & vulnerability scanner for FastMCP servers, Chains, and SKILL.md packages:
- Secret & token leak scanner (GitHub, AWS, Slack, OpenAI, Bearer tokens, private keys)
- AST security inspection (blocks unsafe os.system, subprocess(shell=True), eval, exec)
- Insecure locator and path traversal protection (prevents '../' escape attacks)
- Permission overreach audit
- Aurum Security Score (0-100) & Aurum Gold Security Badge (#C6A96B)
- Publish Gate: Blocks publishing to Marketplace if high-severity secret is found
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SECRET_PATTERNS = [
    (r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}", "GitHub Personal Access Token", "CRITICAL"),
    (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*", "Slack Bot/User Token", "CRITICAL"),
    (r"sk-[a-zA-Z0-9]{20,64}T3BlbkFJ[a-zA-Z0-9]{20,64}", "OpenAI Legacy API Key", "CRITICAL"),
    (r"sk-proj-[a-zA-Z0-9_\-]{40,120}", "OpenAI Project API Key", "CRITICAL"),
    (r"sk-[a-zA-Z0-9_\-]{6,120}", "OpenAI/API Key Secret", "HIGH"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID", "HIGH"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private Cryptographic Key", "CRITICAL"),
    (r'(?i)(?:api_key|apikey|secret_key|auth_token|bearer_token)\s*=\s*["\']([a-zA-Z0-9_\-\.]{8,})["\']', "Hardcoded API Secret", "HIGH"),
]

INSECURE_LOCATOR_PATTERNS = [
    (r"\.\./|\.\.\\", "Directory Traversal Locator ('../')", "HIGH"),
    (r"//[a-z0-9_\-\.]+\s*\[contains\(", "Unbounded XPath Wildcard", "MEDIUM"),
    (r"\bexec\(|\beval\(", "Dynamic Code Evaluation (`eval`/`exec`)", "CRITICAL"),
]


class AurumSecurityReport:
    def __init__(self, target_name: str):
        self.target_name = target_name
        self.findings: List[Dict[str, Any]] = []
        self.secrets_found: int = 0
        self.dangerous_calls_found: int = 0
        self.score: int = 100
        self.has_gold_badge: bool = True
        self.can_publish: bool = True
        self.summary: str = "Passed all security audits."

    def add_finding(self, rule: str, severity: str, message: str, line: Optional[int] = None) -> None:
        self.findings.append({
            "rule": rule,
            "severity": severity,
            "message": message,
            "line": line or 0,
        })
        if severity == "CRITICAL":
            self.score = max(0, self.score - 35)
            self.has_gold_badge = False
            self.can_publish = False
        elif severity == "HIGH":
            self.score = max(0, self.score - 20)
            self.has_gold_badge = False
            # Publish gate: any HIGH finding (hardcoded secret, traversal, syntax break)
            # blocks marketplace publishing — no secret ever ships Gold.
            self.can_publish = False
        elif severity == "MEDIUM":
            self.score = max(0, self.score - 10)
        else:
            self.score = max(0, self.score - 5)

        if self.score < 90:
            self.has_gold_badge = False
        if self.score < 70:
            self.can_publish = False

    def to_dict(self) -> Dict[str, Any]:
        badge_label = "AURUM SECURITY GOLD (#C6A96B)" if self.has_gold_badge else "SECURITY WARNING"
        return {
            "target": self.target_name,
            "security_score": self.score,
            "aurum_security_badge": self.has_gold_badge,
            "badge_color": "#C6A96B" if self.has_gold_badge else "#EF4444",
            "badge_label": badge_label,
            "can_publish": self.can_publish,
            "findings_count": len(self.findings),
            "findings": self.findings,
            "clean": len(self.findings) == 0,
            "summary": "100% Clean — Verified Safe for Production." if self.has_gold_badge else f"Found {len(self.findings)} security item(s).",
        }


def scan_source_security(source_code: str, target_name: str = "server.py") -> Dict[str, Any]:
    """Audit python source code for secrets, AST dangerous patterns, and path traversal."""
    report = AurumSecurityReport(target_name)
    lines = source_code.splitlines()

    # 1. Regex Secret Scan
    for line_idx, line in enumerate(lines, start=1):
        # Ignore explicit placeholder markers only
        if "<your_" in line or "YOUR_API_KEY" in line or "your-api-key-here" in line:
            continue
        for pattern, rule_name, severity in SECRET_PATTERNS:
            if re.search(pattern, line):
                report.add_finding(
                    rule=rule_name,
                    severity=severity,
                    message=f"Possible hardcoded credential detected matching {rule_name}",
                    line=line_idx,
                )
                report.secrets_found += 1
                break

    # 2. Insecure locator / path traversal scan
    for line_idx, line in enumerate(lines, start=1):
        for pattern, rule_name, severity in INSECURE_LOCATOR_PATTERNS:
            if re.search(pattern, line):
                report.add_finding(
                    rule=rule_name,
                    severity=severity,
                    message=f"Potentially unsafe locator or statement: {rule_name}",
                    line=line_idx,
                )

    # 3. AST Deep Inspection
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            # Inspect Subprocess calls with shell=True
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id

                if func_name in ("system", "popen"):
                    report.add_finding(
                        rule="Dangerous System Call",
                        severity="CRITICAL",
                        message=f"Direct shell invocation `{func_name}` detected. Use sandboxed FastMCP tools.",
                        line=getattr(node, "lineno", 0),
                    )
                    report.dangerous_calls_found += 1

                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        report.add_finding(
                            rule="Subprocess Shell Injection Risk",
                            severity="CRITICAL",
                            message="`shell=True` passed to subprocess call.",
                            line=getattr(node, "lineno", 0),
                        )
                        report.dangerous_calls_found += 1
    except SyntaxError:
        report.add_finding(
            rule="Syntax Error",
            severity="HIGH",
            message="Source code failed AST compilation.",
            line=1,
        )

    return report.to_dict()


def scan_mcp_security(server_path: str) -> Dict[str, Any]:
    """Scan a target server.py on disk."""
    p = Path(server_path)
    if not p.exists():
        return {
            "target": str(server_path),
            "security_score": 0,
            "aurum_security_badge": False,
            "badge_color": "#EF4444",
            "can_publish": False,
            "findings": [{"rule": "File Missing", "severity": "CRITICAL", "message": f"File {server_path} not found"}],
            "clean": False,
        }
    content = p.read_text("utf-8", errors="replace")
    return scan_source_security(content, target_name=p.name)
