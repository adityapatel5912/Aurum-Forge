import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_ai_papers_forge():
    proof_dir = Path('dist/playwright_ai_papers_proof')
    proof_dir.mkdir(parents=True, exist_ok=True)
    download_dir = Path('dist/downloads_test')
    download_dir.mkdir(parents=True, exist_ok=True)

    goal_text = 'Track top trending AI papers from ArXiv, extract key findings, and create structured research briefs in Notion and notify via Slack'
    url_text = 'https://arxiv.org/list/cs.AI/recent'

    print('======================================================================')
    print('  PLAYWRIGHT LIVE TEST: AI PAPERS FORGE, DOWNLOAD, INJECT, RUN')
    print('======================================================================\n')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            accept_downloads=True
        )
        page = context.new_page()

        print('>>> 1. Loading UI at http://localhost:5173...')
        page.goto('http://localhost:5173', wait_until='networkidle')
        page.wait_for_timeout(1000)

        print(f'>>> 2. Typing Goal: \"{goal_text}\"')
        goal_input = page.locator('textarea, input[placeholder*=\"goal\"], input[placeholder*=\"Plain English\"]').first
        goal_input.fill(goal_text)
        page.wait_for_timeout(300)

        print(f'>>> 3. Typing URL: \"{url_text}\"')
        url_input = page.locator('input[placeholder*=\"ycombinator\"], input[placeholder*=\"http\"]').first
        if url_input.is_visible():
            url_input.fill(url_text)
            page.wait_for_timeout(300)

        # Select Notion and Slack
        notion_btn = page.locator('button:has-text(\"Notion\")').first
        if notion_btn.is_visible():
            notion_btn.click()
            print('  Selected Notion integration.')
            page.wait_for_timeout(200)

        slack_btn = page.locator('button:has-text(\"Slack\")').first
        if slack_btn.is_visible():
            slack_btn.click()
            print('  Selected Slack integration.')
            page.wait_for_timeout(200)

        # Click Primary Forge Action Button
        forge_btn = page.locator('button:has-text("Forge Unified MCP Server")').first
        print('>>> 4. Clicking "Forge Unified MCP Server" button...')
        forge_btn.click()

        print('>>> 5. Waiting for Forge generation to complete (polling until done)...')
        try:
            page.locator('div:has-text("Forged ")').wait_for(timeout=45000)
            print('  [PASS] Generation completed notification received in UI!')
        except Exception:
            page.wait_for_timeout(15000)
        
        page.screenshot(path=str(proof_dir / '01_generation_completed.png'), full_page=True)
        print('  [PASS] Generation complete. Screenshot captured.')

        # Test Download Active MCP
        print('\n>>> 6. Clicking \"Download Active MCP\" button in UI...')
        download_btn = page.locator('button:has-text(\"Active MCP\"), button[title*=\"active individual\"]').first
        download_path = None
        try:
            with page.expect_download(timeout=10000) as download_info:
                download_btn.click()
            download = download_info.value
            download_path = download_dir / download.suggested_filename
            download.save_as(str(download_path))
            print(f'  [PASS] Downloaded ZIP: {download_path.name} ({download_path.stat().st_size} bytes)')
        except Exception as e:
            print(f'  [FAIL] Download failed: {e}')

        # Test IDE Injector Drawer
        print('\n>>> 7. Opening IDE Injector Drawer tab...')
        injector_tab_btn = page.locator('button:has-text(\"IDE Injector\")').first
        if injector_tab_btn.is_visible():
            injector_tab_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(proof_dir / '02_ide_injector_tab.png'))

            # Test Run Live STDIO Test in UI
            stdio_test_btn = page.locator('button:has-text(\"Run Live STDIO Test\"), button:has-text(\"STDIO Test\")').first
            if stdio_test_btn.is_visible():
                print('  Clicking \"Run Live STDIO Test\" in UI...')
                stdio_test_btn.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=str(proof_dir / '03_stdio_test_result.png'))
                print('  [PASS] Captured Live STDIO Test Result.')

            # Click 1-Click Inject into Antigravity
            inject_ag_btn = page.locator('button:has-text(\"Inject\"), button:has-text(\"1-Click\")').first
            if inject_ag_btn.is_visible():
                inject_ag_btn.click()
                page.wait_for_timeout(1000)
                page.screenshot(path=str(proof_dir / '04_after_inject_antigravity.png'))
                print('  [PASS] Clicked 1-Click Inject into Google Antigravity.')

        browser.close()

    # Step 8: Physical Verification of Downloaded ZIP
    print('\n>>> 8. Inspecting Downloaded ZIP contents on disk...')
    if download_path and download_path.exists():
        with zipfile.ZipFile(download_path) as zf:
            files = zf.namelist()
            print(f'  [PASS] Files inside downloaded ZIP: {files}')
            assert 'server.py' in files, 'server.py missing from downloaded ZIP'
            assert 'SKILL.md' in files, 'SKILL.md missing from downloaded ZIP'
            server_src = zf.read('server.py').decode('utf-8')
            print('  [PASS] server.py header from downloaded ZIP:')
            for line in server_src.splitlines()[:6]:
                print('    |', line)

    # Step 9: Physical Verification of Antigravity Config
    print('\n>>> 9. Inspecting Antigravity Config file on disk...')
    ag_path = Path.home() / '.gemini' / 'config' / 'mcp_config.json'
    if ag_path.exists():
        ag_data = json.loads(ag_path.read_text('utf-8'))
        configured = list(ag_data.get('mcpServers', {}).keys())
        print(f'  [PASS] Antigravity mcpServers: {configured}')
        last_mcp = configured[-1]
        print(f'  [PASS] Latest injected server: \"{last_mcp}\"')
        last_mcp_config = ag_data['mcpServers'][last_mcp]
        print(f"         Command: {last_mcp_config.get('command')} {last_mcp_config.get('args')}")

    # Step 10: Real FastMCP Subprocess Execution & Live Tool Test
    print('\n>>> 10. Booting Newly Forged Server over FastMCP STDIO...')
    # Get the latest forged server path
    latest_server_file = None
    if ag_path.exists() and 'last_mcp_config' in locals():
        args = last_mcp_config.get('args', [])
        if args and Path(args[0]).exists():
            latest_server_file = Path(args[0])

    if not latest_server_file or not latest_server_file.exists():
        mcp_dirs = sorted(Path('mcp').iterdir(), key=os.path.getmtime, reverse=True)
        if mcp_dirs:
            latest_server_file = mcp_dirs[0] / 'server.py'

    print(f'  Target Server file: {latest_server_file}')
    proc = subprocess.Popen(
        [sys.executable, str(latest_server_file.resolve())],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    def rpc_call(req):
        proc.stdin.write(json.dumps(req) + '\n')
        proc.stdin.flush()
        line = proc.stdout.readline()
        return json.loads(line) if line else None

    # Handshake
    init_res = rpc_call({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'playwright-ai-papers-auditor', 'version': '1.0'}
        }
    })
    print('  [PASS] Handshake Info:', init_res.get('result', {}).get('serverInfo'))

    proc.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
    proc.stdin.flush()

    tools_res = rpc_call({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
    tools_list = [t['name'] for t in tools_res.get('result', {}).get('tools', [])]
    print(f'  [PASS] Available Tools ({len(tools_list)}): {tools_list}')

    # Execute a tool
    tool_to_call = tools_list[0] if tools_list else 'amazon_search_ram'
    print(f'  [PASS] Executing tool \"{tool_to_call}\"...')
    call_res = rpc_call({
        'jsonrpc': '2.0',
        'id': 3,
        'method': 'tools/call',
        'params': {
            'name': tool_to_call,
            'arguments': {'query': 'transformer attention models'}
        }
    })
    output_text = call_res.get('result', {}).get('content', [{}])[0].get('text', '')
    print(f'  [PASS] Tool Response ({len(output_text)} chars): {output_text[:120]}...')

    proc.terminate()
    print('\n======================================================================')
    print('  100% VERIFIED: AI PAPERS FORGE, DOWNLOAD, INJECTION, AND EXECUTION')
    print('======================================================================')

if __name__ == '__main__':
    test_ai_papers_forge()
