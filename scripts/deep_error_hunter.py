import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def hunt_all_errors():
    proof_dir = Path('dist/playwright_errors_audit')
    proof_dir.mkdir(parents=True, exist_ok=True)

    console_errors = []
    failed_requests = []
    layout_issues = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Test standard desktop resolution
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        page.on('console', lambda msg: console_errors.append(f'[{msg.type}] {msg.text}') if msg.type in ['error', 'warning'] else None)
        page.on('requestfailed', lambda req: failed_requests.append(f'{req.method} {req.url} -> {req.failure}'))
        page.on('response', lambda res: failed_requests.append(f'{res.request.method} {res.url} -> HTTP {res.status}') if res.status >= 400 else None)

        print('=== 1. AUDITING HOMEPAGE & DARK THEME ===')
        page.goto('http://localhost:5173', wait_until='networkidle')
        page.wait_for_timeout(1000)
        page.screenshot(path=str(proof_dir / '01_home_dark.png'), full_page=True)

        # Check for any overlapping text or overflowing elements
        overflowing = page.evaluate('''() => {
            const elements = document.querySelectorAll('*');
            const issues = [];
            for (const el of elements) {
                if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0 && !['HTML', 'BODY', 'svg', 'path', 'PRE', 'CODE'].includes(el.tagName)) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 30 && rect.height > 10 && rect.top < 1080) {
                        issues.push({
                            tag: el.tagName,
                            className: el.className ? el.className.toString().slice(0, 50) : '',
                            text: el.innerText ? el.innerText.slice(0, 40) : '',
                            scrollWidth: el.scrollWidth,
                            clientWidth: el.clientWidth
                        });
                    }
                }
            }
            return issues.slice(0, 15);
        }''')
        print(f'Dark Mode Overflow Elements Found: {len(overflowing)}')
        for iss in overflowing:
            print('  Overflow:', iss)

        print('\n=== 2. AUDITING WHITE / LIGHT THEME ===')
        theme_btn = page.locator('button[title*=\"Theme\"], button:has(svg.lucide-sun), button:has(svg.lucide-moon)').first
        if theme_btn.is_visible():
            theme_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(proof_dir / '02_home_light.png'), full_page=True)

            # Check low contrast or invisible text in light mode
            contrast_issues = page.evaluate('''() => {
                const elements = document.querySelectorAll('p, span, h1, h2, h3, h4, div, button, label');
                const bad = [];
                for (const el of elements) {
                    if (el.children.length === 0 && el.innerText && el.innerText.trim().length > 0) {
                        const style = window.getComputedStyle(el);
                        const color = style.color;
                        const bg = style.backgroundColor;
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.bottom <= window.innerHeight) {
                            // Check for pure white text on light bg or illegible colors
                            if (color.includes('255, 255, 255') || color.includes('248, 250, 252')) {
                                bad.push({
                                    text: el.innerText.slice(0, 30),
                                    color: color,
                                    bg: bg,
                                    class: el.className ? el.className.toString().slice(0, 40) : ''
                                });
                            }
                        }
                    }
                }
                return bad.slice(0, 15);
            }''')
            print(f'White Theme Contrast / Color Issues Found: {len(contrast_issues)}')
            for ci in contrast_issues:
                print('  Contrast issue:', ci)

        print('\n=== 3. AUDITING ALL 8 DRAWER TABS IN WHITE THEME ===')
        tabs = [
            'Live Benchmark',
            'IDE Injector',
            'Self-Heal Diff',
            'Marketplace & Graph',
            'Aurum Wrapper',
            'Skill Bridge',
            'Time-Travel',
            'Security Vault'
        ]
        for idx, tab_name in enumerate(tabs):
            tab_btn = page.locator(f'button:has-text(\"{tab_name}\")').first
            if tab_btn.is_visible():
                tab_btn.click()
                page.wait_for_timeout(600)
                safe_slug = tab_name.lower().replace(' ', '_').replace('&', 'and')
                page.screenshot(path=str(proof_dir / f'tab_{idx+1}_{safe_slug}_light.png'))
                print(f'  [Tab {idx+1}] {tab_name} checked & screenshotted.')

        print('\n=== 4. AUDITING GENERATION FLOW IN LIGHT THEME ===')
        # Type custom prompt in light mode
        goal_input = page.locator('textarea, input[placeholder*=\"goal\"], input[placeholder*=\"Plain English\"]').first
        if goal_input.is_visible():
            goal_input.fill('track the price of the DGX Spark and inform when it is at lowest price via mail')
            page.wait_for_timeout(300)

            forge_btn = page.locator('button:has-text(\"Forge Unified MCP Server\")').first
            forge_btn.click()
            print('  Clicked Forge Unified MCP Server button...')
            page.wait_for_timeout(2000)
            page.screenshot(path=str(proof_dir / '03_after_forge_light.png'), full_page=True)

        print('\n=== 5. AUDITING DOWNLOAD BUTTONS IN HEADER ===')
        # Test download active MCP click
        download_active_btn = page.locator('button:has-text(\"Active MCP\"), button[title*=\"active individual\"]').first
        if download_active_btn.is_visible():
            download_active_btn.click()
            page.wait_for_timeout(1000)

        # Test download super-hub click
        download_hub_btn = page.locator('button:has-text(\"Super-Hub\"), button[title*=\"full Super-Hub\"]').first
        if download_hub_btn.is_visible():
            download_hub_btn.click()
            page.wait_for_timeout(1000)

        browser.close()

    print('\n======================================================================')
    print('  ERROR HUNTER AUDIT REPORT SUMMARY')
    print('======================================================================')
    print(f'Total Console Warnings/Errors: {len(console_errors)}')
    for err in console_errors:
        print('  Console:', err)
    print(f'\nTotal Failed Network Requests / 4xx / 5xx: {len(failed_requests)}')
    for freq in failed_requests:
        print('  Network Failure:', freq)
    print('======================================================================')

if __name__ == '__main__':
    hunt_all_errors()
