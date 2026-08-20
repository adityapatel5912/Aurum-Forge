import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_fixed_injector():
    out_dir = Path('dist/playwright_proof')
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto('http://localhost:5173', wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Open IDE Injector
        page.locator('button:has-text(\"IDE Injector\")').first.click()
        page.wait_for_timeout(800)

        # Click 1-Click Inject into ALL IDEs
        inject_btn = page.locator('button:has-text(\"1-Click Inject into ALL IDEs\")').first
        inject_btn.click()
        page.wait_for_timeout(1200)

        page.screenshot(path=str(out_dir / 'injector_fixed_proof.png'))
        print('Captured screenshot: dist/playwright_proof/injector_fixed_proof.png')

        browser.close()

if __name__ == '__main__':
    test_fixed_injector()
