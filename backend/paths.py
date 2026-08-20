"""FORGE Dynamic Path Resolution & Normalization Module.

Provides portable, environment-aware path resolution for deployment on
Linux (e.g. Render, Docker, AWS), macOS, and Windows without hardcoded user directories.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, Union

# Root directory detection: respects FORGE_ROOT environment variable if set,
# otherwise falls back to detecting repository root from this file's position.
_ENV_ROOT = os.getenv("FORGE_ROOT")
if _ENV_ROOT and Path(_ENV_ROOT).is_dir():
    PROJECT_ROOT = Path(_ENV_ROOT).resolve()
else:
    # backend/paths.py -> parents[1] is the repo root
    PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_project_root() -> Path:
    """Return the resolved project root directory."""
    return PROJECT_ROOT


def get_user_home() -> Path:
    """Return the user home directory dynamically, respecting FORGE_HOME/HOME/USERPROFILE."""
    env_home = os.getenv("FORGE_HOME") or os.getenv("HOME") or os.getenv("USERPROFILE")
    if env_home and Path(env_home).is_dir():
        return Path(env_home).resolve()
    return Path.home().resolve()


def normalize_path(path: Union[str, Path]) -> str:
    """Convert any path to a forward-slash normalized string with no trailing slash (unless root)."""
    if path is None:
        return ""
    p_str = str(path).replace("\\", "/")
    # Collapse double slashes while preserving leading protocol or slash
    if p_str.startswith("//"):
        return "//" + "/".join(part for part in p_str[2:].split("/") if part)
    elif p_str.startswith("/"):
        return "/" + "/".join(part for part in p_str.split("/") if part)
    else:
        return "/".join(part for part in p_str.split("/") if part)


def resolve_path(rel_or_abs: Union[str, Path], base: Optional[Path] = None) -> Path:
    """Resolve a path relative to project root or provided base, returning a resolved Path."""
    p = Path(rel_or_abs)
    if p.is_absolute():
        return p.resolve()
    base_dir = base or PROJECT_ROOT
    return (base_dir / p).resolve()


def to_posix_str(path: Union[str, Path]) -> str:
    """Return path as clean POSIX string with '/' separators."""
    if isinstance(path, Path):
        return path.resolve().as_posix()
    return normalize_path(str(path))


def get_temp_dir() -> Path:
    """Return platform-independent temp directory for Forge runtime caches."""
    env_temp = os.getenv("FORGE_TEMP_DIR")
    if env_temp:
        p = Path(env_temp).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p
    default_temp = PROJECT_ROOT / "mcp_registry" / "temp"
    default_temp.mkdir(parents=True, exist_ok=True)
    return default_temp
