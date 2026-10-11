#!/usr/bin/env python3
"""Fail-closed source/network/CLI preflight; no wallet access or deployment."""
import ast
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/contextfold.py"
RPC = "https://studio.genlayer.com/api"
CHAIN = 61999


def main() -> int:
    errors = []
    src = CONTRACT.read_text(encoding="utf-8")
    ast.parse(src, filename=str(CONTRACT))
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    if pkg.get("dependencies", {}).get("genlayer") != "0.39.1":
        errors.append("package.json must pin genlayer exactly 0.39.1")
    config = (ROOT / "gltest.config.yaml").read_text(encoding="utf-8")
    if f"url: {RPC}" not in config:
        errors.append("gltest must point at real StudioNet")
    if "run_nondet_unsafe" not in src or "evaluate_groups" not in src:
        errors.append("substantive validator path absent")
    if "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" not in src:
        errors.append("GenVM py-genlayer dependency pin missing")
    if "0.40.0rc" in pkg.get("dependencies", {}).get("genlayer", ""):
        errors.append("release candidate forbidden")
    for rel in ("package.json", "gltest.config.yaml", "scripts/gl.mjs", "scripts/deploy_studionet.py"):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for forbidden in ("studio-dev.genlayer.com", "studio-next.genlayer.com", "61997", "0.40.0rc2"):
            if forbidden in txt:
                errors.append(f"{rel} contains forbidden network/tooling: {forbidden}")
    if any((ROOT / name).exists() for name in ("frontend", "web", "app")):
        errors.append("unexpected frontend")
    try:
        installed = json.loads((ROOT / "node_modules/genlayer/package.json").read_text(encoding="utf-8"))
        if installed.get("version") != "0.39.1":
            errors.append("installed CLI is not 0.39.1")
    except FileNotFoundError:
        print("NOTE: npm dependencies not installed here; run npm install before deployment")
    print(f"Target: StudioNet chain {CHAIN}; RPC {RPC}; repo-local CLI genlayer@0.39.1")
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
