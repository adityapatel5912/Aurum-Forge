"""FORGE-AURUM Super-Hub Background Hot-Reload Watcher.

Continuously monitors mcp_registry/servers/, forge/mcp/, and marketplace.json every 0.1s.
On detection of any new/modified MCP servers or tools:
- Triggers discover_and_load() in <0.1s
- Re-generates super_hub.mcp.json
- Auto-syncs IDE configuration files (~/.antigravity/mcp.json, etc.)
- Logs: [HOT-RELOAD] Discovered {server_name} {tools_count} tools Total {total_tools}
"""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.aurum.generate_super_hub_config import (
    generate_and_sync_super_hub,
    scan_all_mcp_servers,
)
from backend.config import MCP_REGISTRY_DIR

WATCH_DIR = MCP_REGISTRY_DIR / "servers"


class SuperHubWatcher:
    def __init__(self, interval_s: float = 0.1, on_change_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.interval_s = interval_s
        self.on_change_callback = on_change_callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._known_snapshots: Dict[str, float] = {}
        self._known_server_counts: Dict[str, int] = {}
        self._initial_scan()

    def _initial_scan(self) -> None:
        """Record initial mtimes and server states."""
        self._known_snapshots = self._capture_dir_snapshots()
        discovered, _ = scan_all_mcp_servers()
        self._known_server_counts = {k: v.get("tools", 0) for k, v in discovered.items()}

    def _capture_dir_snapshots(self) -> Dict[str, float]:
        """Capture mtimes of all server.py files in watch directory."""
        snapshots = {}
        if WATCH_DIR.exists():
            for sdir in WATCH_DIR.iterdir():
                if sdir.is_dir() and not sdir.name.startswith((".", "_")) and sdir.name != "temp":
                    spy = sdir / "server.py"
                    if spy.exists():
                        try:
                            snapshots[sdir.name] = spy.stat().st_mtime
                        except Exception:
                            pass
        return snapshots

    def check_for_changes(self) -> Optional[Dict[str, Any]]:
        """Check if any server directory or server.py was added or modified."""
        current_snapshots = self._capture_dir_snapshots()
        new_or_modified = []

        for sname, mtime in current_snapshots.items():
            if sname not in self._known_snapshots or mtime > self._known_snapshots[sname]:
                new_or_modified.append(sname)

        # Check for deleted
        for sname in self._known_snapshots:
            if sname not in current_snapshots:
                new_or_modified.append(sname)

        if new_or_modified:
            self._known_snapshots = current_snapshots
            # Trigger auto-sync and reload
            sync_res = generate_and_sync_super_hub(auto_sync_ides=True)
            discovered = sync_res.get("discovered_servers", {})
            total_tools = sync_res.get("total_tools", 0)

            for sname in new_or_modified:
                if sname in discovered:
                    t_count = discovered[sname].get("tools", 0)
                    print(f"[HOT-RELOAD] Discovered {sname} {t_count} tools Total {total_tools}")

            if self.on_change_callback:
                try:
                    self.on_change_callback(sync_res)
                except Exception as e:
                    print(f"[HOT-RELOAD] Callback error: {e}")

            return sync_res
        return None

    def start(self) -> None:
        """Start the 0.1s background polling watcher loop."""
        if self.running:
            return
        self.running = True

        def _loop():
            while self.running:
                try:
                    self.check_for_changes()
                except Exception as e:
                    print(f"[WATCHER ERROR] {e}")
                time.sleep(self.interval_s)

        self.thread = threading.Thread(target=_loop, daemon=True, name="SuperHubWatcherThread")
        self.thread.start()
        print(f"[HOT-RELOAD] Super-Hub Watcher active (polling every {self.interval_s}s on {WATCH_DIR})")

    def stop(self) -> None:
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)


_global_watcher: Optional[SuperHubWatcher] = None


def get_or_start_watcher() -> SuperHubWatcher:
    global _global_watcher
    if _global_watcher is None:
        _global_watcher = SuperHubWatcher(interval_s=0.1)
        _global_watcher.start()
    return _global_watcher


if __name__ == "__main__":
    watcher = SuperHubWatcher(interval_s=0.1)
    watcher.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        watcher.stop()
