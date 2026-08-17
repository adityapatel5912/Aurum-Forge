"""FORGE scout — headful stealth explorer that captures TWO locators per element."""
from backend.scout.explorer import scout_site
from backend.scout.stealth import launch_stealth_browser, new_stealth_page

__all__ = ["scout_site", "launch_stealth_browser", "new_stealth_page"]
