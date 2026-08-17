"""FORGE planner — turns goal + tool manifest into a DAG (JSON) via gpt-oss-120b.

Output shape (per spec):
  {"t1": {"tool": "search_siteA", "source": "Custom A Forged", "parallel": True},
   "t2": {"tool": "search_siteB", "source": "Custom B Forged", "parallel": True},
   "t3": {"tool": "create_entry", "source": "Official C", "deps": ["t1", "t2"]}}
"""
from backend.planner.planner import build_dag

__all__ = ["build_dag"]
