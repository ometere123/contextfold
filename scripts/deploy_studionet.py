#!/usr/bin/env python3
"""Deploy only to verified StudioNet chain 61999 using repository-local CLI.

Requires a pre-existing unlocked CLI account. No private keys are read or created.
Never switches global network configuration.
"""
import json
import pathlib
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RPC = "https://studio.genlayer.com/api"
CHAIN_ID = 61999
GL = ROOT / "scripts/gl.mjs"
CONTRACT = ROOT / "contracts/contextfold.py"


def check_chain_id() -> None:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}).encode()
    # StudioNet's Cloudflare edge rejects urllib's default ``Python-urllib``
    # user agent even though the JSON-RPC endpoint is otherwise available.
    # Keep the check fail-closed while identifying this as a normal client.
    req = urllib.request.Request(
        RPC,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "contextfold-deployer/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        value = json.load(response)
    if "error" in value:
        raise RuntimeError(f"chain ID RPC unavailable: {value['error']}")
    number = int(str(value.get("result", "")), 16)
    if number != CHAIN_ID:
        raise RuntimeError(f"WRONG NETWORK: expected 61999, received {number}")
    print(f"Verified RPC chain ID: {number}")


def local_cli(*args: str) -> None:
    process = subprocess.run(["node", str(GL), *args], cwd=ROOT, check=False)
    if process.returncode:
        raise RuntimeError(f"local genlayer command failed: {args}")


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts/preflight.py")], check=True, cwd=ROOT)
    installed = json.loads((ROOT / "node_modules/genlayer/package.json").read_text(encoding="utf-8"))
    if installed["version"] != "0.39.1":
        raise RuntimeError("local genlayer CLI must be 0.39.1")
    check_chain_id()  # fail closed; never deploy if RPC cannot identify the chain
    local_cli("--version")
    local_cli("account", "show", "--rpc", RPC)
    print("Deploying only to StudioNet (61999)...")
    local_cli("deploy", "--contract", str(CONTRACT), "--rpc", RPC)
    print("Record transaction hash, FINALIZED receipt, contract address, and source parity in docs/DEPLOYMENT.md")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Deployment blocked: {exc}", file=sys.stderr)
        raise SystemExit(2)
