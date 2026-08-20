import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def verify_injector_layout():
    out_dir = Path('dist/playwright_proof')
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto('http://localhost:5173', wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Open IDE Injector
        inj_btn = page.locator('button:has-text(\"IDE Injector\")').first
        assert inj_btn.is_visible()
        inj_btn.click()
        page.wait_for_timeout(800)

        # Dark mode screenshot
        page.screenshot(path=str(out_dir / 'injector_dark_clean.png'))
        print('Captured dark mode injector: dist/playwright_proof/injector_dark_clean.png')

        # Toggle to Light mode
        theme_btn = page.locator('button[title*=\"Theme\"], button:has-text(\"Toggle Theme\"), button:has(svg.lucide-sun), button:has(svg.lucide-moon)').first
        if theme_btn.is_visible():
            theme_btn.click()
            page.wait_for_timeout(800)
            page.screenshot(path=str(out_dir / 'injector_light_clean.png'))
            print('Captured light mode injector: dist/playwright_proof/injector_light_clean.png')

        browser.close()

if __name__ == '__main__':
    verify_injector_layout()
