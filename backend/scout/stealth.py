"""Stealth Playwright primitives shared by Scout and the forged servers.

Headful by default, AutomationControlled disabled, real-world UA at
1920x1080 — the browser looks like a human's Chrome, not a bot.
"""
from __future__ import annotations

STEALTH_LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-infobars",
    "--window-size=1920,1080",
]

REAL_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

STEALTH_INIT_JS = (
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    "window.chrome = window.chrome || {runtime: {}};"
    "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});"
    "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});"
)


def launch_stealth_browser(p, headful: bool = True):
    """Launch Chromium with anti-fingerprint args. headful=True per FORGE spec."""
    return p.chromium.launch(headless=not headful, args=STEALTH_LAUNCH_ARGS)


def new_stealth_page(browser):
    """Fresh 1920x1080 context with a real UA + webdriver masking."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=REAL_UA,
        locale="en-US",
    )
    context.add_init_script(STEALTH_INIT_JS)
    return context.new_page()
