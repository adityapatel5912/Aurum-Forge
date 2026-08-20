import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def inspect_light_theme():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto('http://localhost:5173', wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Look for theme toggle button
        theme_toggle = page.locator('button:has-text(\"Toggle Theme\"), button[title*=\"Theme\"], button:has(svg.lucide-sun), button:has(svg.lucide-moon)').first
        print('Theme toggle button visible:', theme_toggle.is_visible())
        if theme_toggle.is_visible():
            theme_toggle.click()
            page.wait_for_timeout(1000)
            print('Toggled theme!')

        out_dir = Path('dist/playwright_proof')
        out_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out_dir / 'light_mode_full.png'), full_page=True)
        print('Saved screenshot: dist/playwright_proof/light_mode_full.png')

        # Check all drawer tabs in light mode
        tabs = ['Live Benchmark', 'IDE Injector', 'Self-Heal Diff', 'Marketplace & Graph', 'Aurum Wrapper', 'Skill Bridge', 'Time-Travel', 'Security Vault']
        for tab_name in tabs:
            btn = page.locator(f'button:has-text(\"{tab_name}\")').first
            if btn.is_visible():
                btn.click()
                page.wait_for_timeout(500)
                slug = tab_name.lower().replace(' ', '_').replace('&', 'and')
                page.screenshot(path=str(out_dir / f'light_{slug}.png'))
                print(f'Captured {tab_name} in light mode')

        browser.close()

if __name__ == '__main__':
    inspect_light_theme()
