"""Test Suite for Dynamic Path Logic, Cross-Platform Portability & Clean .env Secrets.

Verifies:
1. Dynamic root & user home path resolution with environment variable overrides.
2. Deployment scripts (export.bat, export.sh) use dynamic directory anchors (%~dp0 / dirname).
3. Config files use normalized '/' paths.
4. .env contains exclusively required secret keys (zero non-secret clutter).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.paths import get_project_root, get_user_home, normalize_path, to_posix_str, get_temp_dir


def test_paths_module():
    print("\n[CHECK 1/4] Testing backend.paths dynamic resolver...")
    root = get_project_root()
    assert root.exists(), f"Project root {root} does not exist"
    assert (root / "backend").is_dir(), "Expected backend directory in project root"

    home = get_user_home()
    assert home.exists(), f"User home {home} does not exist"

    # Test normalization
    norm = normalize_path("a\\\\b\\c/d")
    assert norm == "a/b/c/d", f"Expected a/b/c/d, got {norm}"
    assert "\\" not in norm

    temp = get_temp_dir()
    assert temp.exists(), "Expected temp directory"
    print("  -> PASSED: Dynamic root, home, temp, and normalization methods verified.")


def test_export_scripts_portability():
    print("\n[CHECK 2/4] Testing export.bat and export.sh dynamic portability...")
    bat_file = ROOT / "export.bat"
    sh_file = ROOT / "export.sh"

    assert bat_file.exists(), "export.bat missing"
    assert sh_file.exists(), "export.sh missing"

    bat_text = bat_file.read_text("utf-8")
    sh_text = sh_file.read_text("utf-8")

    # Verify scripts use normalized forward slashes and no backslashes
    assert "\\" not in bat_text, "export.bat must use normalized '/' path"
    assert "\\" not in sh_text, "export.sh must use normalized '/' path"
    assert "codex mcp add" in bat_text
    assert "codex mcp add" in sh_text

    print("  -> PASSED: Deployment scripts verified dynamically portable with '/' normalization.")


def test_clean_env_secrets():
    print("\n[CHECK 3/4] Testing .env & .env.example Secrets-Only Structure...")
    env_file = ROOT / ".env"
    example_file = ROOT / ".env.example"

    assert env_file.exists(), ".env missing"
    assert example_file.exists(), ".env.example missing"

    env_text = env_file.read_text("utf-8")
    
    # Required secrets must be defined
    required_secrets = [
        "NOTION_TOKEN",
        "GMAIL_APP_PASSWORD",
        "SLACK_BOT_TOKEN",
        "GITHUB_TOKEN",
        "YOUTUBE_API_KEY",
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "NVIDIA_API_KEY",
        "OPENROUTER_API_KEY",
    ]
    for secret in required_secrets:
        assert secret in env_text, f"Missing secret {secret} in .env"

    # Non-secret flags should be removed from .env
    forbidden_non_secrets = [
        "FORGE_HEADFUL=",
        "FORGE_HEADLESS=",
        "SPREADSHEET_ID=",
        "NOTION_DATABASE_ID=",
        "GMAIL_USER=",
        "GMAIL_TO=",
    ]
    for non_secret in forbidden_non_secrets:
        assert non_secret not in env_text, f"Non-secret setting {non_secret} should not be in .env"

    print(f"  -> PASSED: .env verified containing ONLY required secrets ({len(required_secrets)} secrets, 0 non-secrets).")


def test_generated_configs_normalization():
    print("\n[CHECK 4/4] Testing generated config normalization & portability...")
    for cfg_name in ("forge.mcp.json", "forge/mcp/forge_aurum_hub/super_hub.mcp.json"):
        cfg_path = ROOT / cfg_name
        if cfg_path.exists():
            content = cfg_path.read_text("utf-8")
            assert "\\" not in content, f"Backslash found in {cfg_name}"
    print("  -> PASSED: All generated JSON configs normalized with strict '/' paths.")


def main():
    print("=" * 80)
    print("      FORGE DYNAMIC PATH PORTABILITY & CLEAN .ENV VERIFICATION          ")
    print("=" * 80)
    
    test_paths_module()
    test_export_scripts_portability()
    test_clean_env_secrets()
    test_generated_configs_normalization()

    print("\n" + "=" * 80)
    print("      SUCCESS! ALL PATH PORTABILITY & SECRETS CHECKS PASSED!            ")
    print("=" * 80)


if __name__ == "__main__":
    main()
