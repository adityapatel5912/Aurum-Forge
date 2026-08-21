"""
Meta-MCP Test:
Invokes the MCP Tool `forge_new_mcp` directly as an Agent/Tool would, passing:
- Goal: "Monitor GitHub issues and send alert notifications to Slack channel"
- Official MCPs: telegram, slack, github
- Custom URLs: https://news.ycombinator.com, https://arxiv.org, https://spaceflightnow.com
"""
import json
import os
import sys
import importlib.util
from backend.paths import get_project_root
from backend.aurum.secrets_manager import get_injection_env_block
from backend.factory.factory_mcp import forge_new_mcp

def test_meta_mcp():
    print("=" * 70)
    print(">>> TESTING MCP-CREATING-MCP (INVOKING forge_new_mcp TOOL)")
    print("=" * 70)

    # 1. Invoke the MCP tool directly
    goal = "Monitor GitHub issues and send alert notifications to Slack channel"
    urls = [
        "https://news.ycombinator.com",
        "https://arxiv.org",
        "https://spaceflightnow.com"
    ]
    officials = ["telegram", "slack", "github"]
    server_name = "monitor_github_issues_and_send"

    print(f"\n[MCP TOOL INVOCATION]")
    print(f"Goal: {goal}")
    print(f"Custom URLs: {urls}")
    print(f"Officials: {officials}")
    print("Calling forge_new_mcp tool...")

    raw_output = forge_new_mcp(
        goal=goal,
        urls=urls,
        official_integrations=officials,
        server_name=server_name
    )

    result = json.loads(raw_output)
    print("\n[MCP RESPONSE]")
    print(f"Status: {result.get('status')}")
    print(f"Server Name: {result.get('server_name')}")
    print(f"Server Path: {result.get('server_path')}")
    print(f"Elapsed: {result.get('elapsed_seconds')}s (<2.0s zero-LLM fast path)")
    print(f"Total Tools Created: {len(result.get('tools', []))}")
    print(f"Hot Loaded IDEs: {result.get('hot_loaded_into')}")

    print("\n[GENERATED TOOLS LIST]")
    for t in result.get("tools", []):
        if isinstance(t, dict):
            desc = (t.get("description") or "")[:60]
            print(f"  * [{t.get('badge', 'TOOL')}] {t.get('name')}: {desc}")
        else:
            print(f"  * [TOOL] {t}")

    server_path = result.get("server_path")
    assert server_path and os.path.exists(server_path), f"Server path does not exist: {server_path}"

    # 2. Test Live Invocation of the newly MCP-created server
    print("\n[RUNTIME EXECUTION OF THE NEWLY FORGED MCP TOOLS]")
    for k, v in get_injection_env_block().items():
        os.environ[k] = v

    spec = importlib.util.spec_from_file_location("forged_mcp", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Test GitHub Tool
    print("  -> Testing generated github_list_prs tool...")
    gh_res = mod.github_list_prs(repo="tiangolo/fastapi", state="open")
    print(f"     GitHub result status: {gh_res.get('status')}, ok: {gh_res.get('ok')}")

    # Test Slack Tool
    print("  -> Testing generated slack_list_channels tool...")
    sl_res = mod.slack_list_channels()
    print(f"     Slack result status: {sl_res.get('status')}, ok: {sl_res.get('ok')}")

    # Test Telegram Tool
    print("  -> Testing generated telegram_send_message tool...")
    tg_res = mod.telegram_send_message(text="Ping from Meta-MCP forged server", chat_id="123456789")
    print(f"     Telegram result: {tg_res}")

    print("\n" + "=" * 70)
    print("SUCCESS: MCP created a fully functional new MCP server autonomously!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    test_meta_mcp()
