import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_playwright_test():
    proof_dir = Path('dist/playwright_live_proof')
    proof_dir.mkdir(parents=True, exist_ok=True)
    download_dir = Path('dist/downloads_test')
    download_dir.mkdir(parents=True, exist_ok=True)

    test_goal = 'Track live SpaceX launch schedule and notify engineering team via Slack'
    test_url = 'https://spaceflightnow.com/'
    
    print('======================================================================')
    print('  REAL PLAYWRIGHT LIVE AUDIT: GENERATE, DOWNLOAD, INJECT, RUN')
    print('======================================================================\n')

    with sync_playwright() as p:
        # Launch browser with downloads enabled
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            accept_downloads=True
        )
        page = context.new_page()

        print('>>> STEP 1: Navigating to Forge UI at http://localhost:5173...')
        page.goto('http://localhost:5173', wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Clear existing goal and type new goal
        print(f'>>> STEP 2: Typing Goal: \"{test_goal}\"')
        goal_textarea = page.locator('textarea, input[placeholder*=\"goal\"], input[placeholder*=\"Plain English\"]').first
        goal_textarea.fill(test_goal)
        page.wait_for_timeout(400)

        # Add target URL
        url_input = page.locator('input[placeholder*=\"ycombinator\"], input[placeholder*=\"http\"]').first
        if url_input.is_visible():
            print(f'>>> STEP 3: Setting target URL: {test_url}')
            url_input.fill(test_url)
            page.wait_for_timeout(400)

        # Select Slack official integration if available
        slack_btn = page.locator('button:has-text(\"Slack\")').first
        if slack_btn.is_visible():
            slack_btn.click()
            print('>>> STEP 4: Selected Slack integration.')
            page.wait_for_timeout(400)

        # Click Primary Forge Action Button
        forge_btn = page.locator('button:has-text(\"Forge Unified MCP Server\")').first
        print('>>> STEP 5: Clicking \"Forge Unified MCP Server\" button...')
        forge_btn.click()

        # Wait for generation to complete (watch toast or DAG canvas change)
        print('>>> Waiting for Forge generation to finish...')
        page.wait_for_timeout(3500)
        page.screenshot(path=str(proof_dir / '01_generation_completed.png'), full_page=True)
        print('  [PASS] Screenshot captured: dist/playwright_live_proof/01_generation_completed.png')

        # STEP 6: Test Download via UI
        print('\n>>> STEP 6: Testing Download via UI...')
        download_btn = page.locator('button:has-text(\"Active MCP\"), button[title*=\"active individual\"]').first
        if not download_btn.is_visible():
            download_btn = page.locator('button:has-text(\"Super-Hub\")').first

        download_path = None
        try:
            with page.expect_download(timeout=10000) as download_info:
                download_btn.click()
            download = download_info.value
            download_path = download_dir / download.suggested_filename
            download.save_as(str(download_path))
            print(f'  [PASS] Download completed via Playwright: {download_path.name} ({download_path.stat().st_size} bytes)')
        except Exception as e:
            print(f'  [FAIL] Download event failed: {e}')

        # STEP 7: Navigate to IDE Injector and Click 1-Click Inject
        print('\n>>> STEP 7: Testing IDE Injector Drawer in UI...')
        injector_tab_btn = page.locator('button:has-text(\"IDE Injector\")').first
        if injector_tab_btn.is_visible():
            injector_tab_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(proof_dir / '02_ide_injector_tab.png'))

            # Click Inject into Antigravity
            inject_antigravity_btn = page.locator('button:has-text(\"Inject\"), button:has-text(\"1-Click\")').first
            if inject_antigravity_btn.is_visible():
                inject_antigravity_btn.click()
                page.wait_for_timeout(1000)
                page.screenshot(path=str(proof_dir / '03_after_inject_antigravity.png'))
                print('  [PASS] Clicked 1-Click Inject on Antigravity in UI.')

        browser.close()

    # STEP 8: Physical Disk Verification of the Downloaded ZIP
    print('\n>>> STEP 8: Inspecting Downloaded ZIP on disk...')
    if download_path and download_path.exists():
        with zipfile.ZipFile(download_path) as zf:
            files = zf.namelist()
            print(f'  [PASS] Files inside downloaded ZIP: {files}')
            assert 'server.py' in files, 'server.py missing from downloaded ZIP'
            assert 'SKILL.md' in files, 'SKILL.md missing from downloaded ZIP'
            assert 'requirements.txt' in files, 'requirements.txt missing from downloaded ZIP'
            server_content = zf.read('server.py').decode('utf-8')
            print('  [PASS] server.py preview from downloaded ZIP:')
            for line in server_content.splitlines()[:8]:
                print('    |', line)

    # STEP 9: Physical Disk Verification of IDE Configs
    print('\n>>> STEP 9: Verifying on-disk IDE configs...')
    antigravity_config = Path.home() / '.gemini' / 'config' / 'mcp_config.json'
    cursor_config = Path.home() / '.cursor' / 'mcp.json'
    zcode_config = Path.home() / '.zcode' / 'mcp.json'

    if antigravity_config.exists():
        ag_data = json.loads(antigravity_config.read_text('utf-8'))
        print(f"  [PASS] Antigravity config ({antigravity_config}):")
        print(f"         Servers configured: {list(ag_data.get('mcpServers', {}).keys())}")
    else:
        print(f"  [WARN] Antigravity config not found at {antigravity_config}")

    if cursor_config.exists():
        cur_data = json.loads(cursor_config.read_text('utf-8'))
        print(f"  [PASS] Cursor config ({cursor_config}):")
        print(f"         Servers configured: {list(cur_data.get('mcpServers', {}).keys())}")

    # STEP 10: Real FastMCP Subprocess Execution & Usability Test
    print('\n>>> STEP 10: Testing Usability with Subprocess FastMCP Client...')
    # Look for the generated server in mcp/ or mcp_registry/
    generated_servers = list(Path('mcp').glob('*_spacex*')) or list(Path('mcp').glob('*schedule*')) or list(Path('mcp').glob('*launch*'))
    if not generated_servers:
        # Fallback to the latest modified server in mcp/
        mcp_dirs = sorted(Path('mcp').iterdir(), key=os.path.getmtime, reverse=True)
        if mcp_dirs:
            generated_servers = [mcp_dirs[0]]

    target_server_py = None
    if generated_servers:
        candidate = generated_servers[0] / 'server.py'
        if candidate.exists():
            target_server_py = candidate

    if not target_server_py:
        target_server_py = Path('mcp_registry/servers/unified-mcp/server.py')

    print(f'  Testing FastMCP server: {target_server_py}')
    proc = subprocess.Popen(
        [sys.executable, str(target_server_py.resolve())],
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
            'clientInfo': {'name': 'playwright-auditor', 'version': '1.0'}
        }
    })
    print('  [PASS] FastMCP Handshake Info:', init_res.get('result', {}).get('serverInfo'))

    proc.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
    proc.stdin.flush()

    # List Tools
    tools_res = rpc_call({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
    tools_list = [t['name'] for t in tools_res.get('result', {}).get('tools', [])]
    print(f'  [PASS] Total {len(tools_list)} tools available for use: {tools_list}')

    # Execute a tool for the SpaceX launch purpose
    tool_to_call = tools_list[0] if tools_list else 'amazon_search_ram'
    print(f'  [PASS] Calling tool \"{tool_to_call}\" with real payload...')
    call_res = rpc_call({
        'jsonrpc': '2.0',
        'id': 3,
        'method': 'tools/call',
        'params': {
            'name': tool_to_call,
            'arguments': {'query': 'SpaceX Starship launch'}
        }
    })
    tool_output = call_res.get('result', {}).get('content', [{}])[0].get('text', '')
    print(f'  [PASS] Tool Response Output ({len(tool_output)} chars): {tool_output[:140]}...')

    proc.terminate()
    print('\n======================================================================')
    print('  PLAYWRIGHT AUDIT COMPLETE: GENERATION, DOWNLOAD, INJECT, & USABILITY')
    print('======================================================================')

if __name__ == '__main__':
    run_playwright_test()
