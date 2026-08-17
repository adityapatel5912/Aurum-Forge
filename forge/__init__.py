"""FORGE shared package — zip builder, exporter, skills, and registry history.

Regular package (not namespace) so `from forge.zip_builder import ...` always
resolves here when the project ROOT is on sys.path, even though `backend/forge/`
also exists and would otherwise shadow it under `python backend/main.py`.
"""
