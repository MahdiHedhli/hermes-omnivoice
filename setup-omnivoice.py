#!/usr/bin/env python3
"""OmniVoice-for-Hermes setup wizard.

Detects your environment and configures the plugin's backend. OmniVoice's model
runtime is a real dependency; this makes choosing/wiring it explicit:

  1. Use a detected local setup  — a speech server is already running, or the
     OmniVoice SDK is installed in your Hermes environment (in-process).
  2. Install a local server      — create a venv, install the model deps, and
     run server/serve.py on loopback; wire backend: studio.
  3. Use a remote server         — point at a model node over the LAN/tailnet
     (backend: service, http or ssh-loopback), with run instructions.

It writes only the `tts.omnivoice` block of ~/.hermes/config.yaml (surgically,
preserving the rest of the file). Run:  python setup-omnivoice.py
Non-interactive: --detect (report only), or --mode {use,install,remote} + flags.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
CONFIG = HERMES_HOME / "config.yaml"
REPO = Path(__file__).resolve().parent
DEFAULT_LOOPBACK = "http://127.0.0.1:8880"


# --------------------------------------------------------------------------- detect

def find_hermes_python() -> str:
    base = HERMES_HOME / "hermes-agent" / "venv" / "bin"
    for name in ("python3.11", "python3", "python"):
        if (base / name).exists():
            return str(base / name)
    return sys.executable


def _probe(python_exe: str, code: str) -> str:
    try:
        r = subprocess.run([python_exe, "-c", code], cwd="/tmp",
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def check_sdk(python_exe: str) -> dict:
    out = _probe(python_exe, "import importlib.util as u,json;"
                 "print(json.dumps({k:bool(u.find_spec(k)) for k in "
                 "('omnivoice','torch','soundfile')}))")
    try:
        return json.loads(out or "{}")
    except Exception:
        return {}


def check_device(python_exe: str) -> str:
    return _probe(python_exe, "import torch;print('cuda' if torch.cuda.is_available() "
                 "else ('mps' if torch.backends.mps.is_available() else 'cpu'))") or "?"


def check_server(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/health", timeout=3) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def current_config() -> dict:
    try:
        import yaml
        d = yaml.safe_load(CONFIG.read_text()) if CONFIG.exists() else {}
        tts = (d or {}).get("tts") or {}
        ov = tts.get("omnivoice") or {}
        return {"provider": tts.get("provider"), "backend": ov.get("backend"),
                "studio_url": (ov.get("studio") or {}).get("url"),
                "service_url": (ov.get("service") or {}).get("url")}
    except Exception:
        return {}


def detect() -> dict:
    hpy = find_hermes_python()
    sdk = check_sdk(hpy)
    cfg = current_config()
    urls = [u for u in {cfg.get("studio_url"), DEFAULT_LOOPBACK} if u]
    server = None
    server_url = None
    for u in urls:
        info = check_server(u)
        if info:
            server, server_url = info, u
            break
    return {
        "hermes_python": hpy,
        "sdk": sdk,
        "device": check_device(hpy) if sdk.get("torch") else "n/a (torch not installed)",
        "server": server, "server_url": server_url,
        "ffmpeg": bool(_which("ffmpeg")),
        "config": cfg,
    }


def _which(name: str) -> str | None:
    from shutil import which
    return which(name)


def report(d: dict) -> None:
    print("\n=== OmniVoice environment ===")
    print(f"  Hermes Python:   {d['hermes_python']}")
    s = d["sdk"]
    print(f"  Local SDK:       omnivoice={s.get('omnivoice')} torch={s.get('torch')} "
          f"soundfile={s.get('soundfile')}   (device: {d['device']})")
    if d["server"]:
        print(f"  Speech server:   RUNNING at {d['server_url']} "
              f"(model={d['server'].get('model')}, voices={d['server'].get('voices')})")
    else:
        print("  Speech server:   none reachable")
    print(f"  ffmpeg:          {'yes' if d['ffmpeg'] else 'no (optional; WAV works)'}")
    c = d["config"]
    print(f"  Current config:  tts.provider={c.get('provider')} "
          f"omnivoice.backend={c.get('backend')} studio.url={c.get('studio_url')}")
    print()


# --------------------------------------------------------------------------- config write

def write_block(block: list[str]) -> None:
    """Replace/insert the `  omnivoice:` block under `tts:`, preserving the rest."""
    if not CONFIG.exists():
        CONFIG.write_text("tts:\n" + "\n".join(block) + "\n")
        return
    lines = CONFIG.read_text().split("\n")
    tts_i = next((i for i, l in enumerate(lines) if l.rstrip() == "tts:"), None)
    if tts_i is None:
        lines = ["tts:"] + block + lines
        CONFIG.write_text("\n".join(lines))
        return
    start = None
    for i in range(tts_i + 1, len(lines)):
        l = lines[i]
        if not l.strip():
            continue
        indent = len(l) - len(l.lstrip())
        if indent == 0:
            break
        if indent == 2 and l.strip().startswith("omnivoice:"):
            start = i
            break
    if start is not None:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            l = lines[j]
            if not l.strip():
                continue
            if (len(l) - len(l.lstrip())) <= 2:
                end = j
                break
        lines = lines[:start] + block + lines[end:]
    else:
        lines = lines[:tts_i + 1] + block + lines[tts_i + 1:]
    CONFIG.write_text("\n".join(lines))


def block_studio(url: str) -> list[str]:
    return ["  omnivoice:", "    backend: studio", "    studio:", f"      url: {url}"]


def block_local(device: str) -> list[str]:
    return ["  omnivoice:", "    backend: local", "    local:", f"      device: {device}"]


def block_service(url: str, transport: str, ssh_host: str) -> list[str]:
    b = ["  omnivoice:", "    backend: service", "    service:", f"      url: {url}",
         "      auth_token_env: HERMES_OMNIVOICE_SERVICE_TOKEN", f"      transport: {transport}"]
    if transport == "ssh-loopback":
        b.append(f"      ssh_host: {ssh_host}")
    return b


# --------------------------------------------------------------------------- flows

def _apply(block: list[str], note: str) -> None:
    write_block(block)
    print(f"\n✓ Wrote tts.omnivoice to {CONFIG}:")
    print("\n".join("    " + b for b in block))
    print(f"\n{note}")
    print("  (Set tts.provider: omnivoice when you want OmniVoice to be the active voice.)")


def flow_use(d: dict) -> None:
    if d["server"]:
        _apply(block_studio(d["server_url"]),
               f"Using the running server at {d['server_url']} (backend: studio).")
    elif d["sdk"].get("omnivoice") and d["sdk"].get("torch"):
        _apply(block_local(d["device"] if d["device"].startswith(("mps", "cuda", "cpu")) else "auto"),
               "Using the in-process SDK (backend: local). Note: a very long clone "
               "reference can exhaust GPU memory — keep references ~10-30s.")
    else:
        print("Nothing to use: no server running and the OmniVoice SDK isn't installed "
              "in your Hermes Python. Choose 'install' or 'remote'.")


def flow_install(server_venv: str, run_now: bool) -> None:
    venv = Path(server_venv).expanduser()
    print(f"\nInstalling a local speech server into: {venv}")
    reqs = REPO / "server" / "requirements.txt"
    print("Steps:")
    print(f"  python3 -m venv {venv}")
    print(f"  {venv}/bin/pip install -r {reqs}")
    print(f"  {venv}/bin/python {REPO}/server/serve.py --host 127.0.0.1 --port 8880")
    if run_now:
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        subprocess.run([str(venv / "bin" / "pip"), "install", "-r", str(reqs)], check=True)
        print("\n✓ Deps installed. Start the server with the last command above "
              "(or add it to launchd/systemd to run on boot).")
    _apply(block_studio(DEFAULT_LOOPBACK),
           "Configured backend: studio → the loopback server. Start the server, then it's live.")


def flow_remote(url: str, transport: str, ssh_host: str) -> None:
    _apply(block_service(url, transport, ssh_host),
           "Configured backend: service.\n"
           "  Run the model server on the remote node:\n"
           f"    python server/serve.py --host 0.0.0.0 --port 8880 --require-auth\n"
           "  Set the bearer token on BOTH sides via HERMES_OMNIVOICE_SERVICE_TOKEN.\n"
           "  Keep it on a VPN/tailnet. For ssh-loopback, the server binds 127.0.0.1 on the node.")


# --------------------------------------------------------------------------- main

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="OmniVoice for Hermes — setup wizard")
    p.add_argument("--detect", action="store_true", help="print detection and exit")
    p.add_argument("--json", action="store_true", help="detection as JSON")
    p.add_argument("--mode", choices=["use", "install", "remote"], help="non-interactive mode")
    p.add_argument("--url", default="")
    p.add_argument("--transport", choices=["http", "ssh-loopback"], default="http")
    p.add_argument("--ssh-host", default="")
    p.add_argument("--server-venv", default=str(HERMES_HOME / "omnivoice-server-venv"))
    p.add_argument("--install-deps", action="store_true", help="actually create venv + pip install")
    args = p.parse_args(argv)

    d = detect()
    if args.json:
        print(json.dumps(d, indent=2))
        return 0
    report(d)
    if args.detect:
        return 0

    if args.mode == "use":
        flow_use(d); return 0
    if args.mode == "install":
        flow_install(args.server_venv, args.install_deps); return 0
    if args.mode == "remote":
        flow_remote(args.url or "http://model-node.local:8880", args.transport, args.ssh_host); return 0

    # interactive
    print("How do you want OmniVoice to synthesize?")
    print("  1) Use a detected local setup" + (
        f"  [server at {d['server_url']}]" if d["server"] else
        ("  [in-process SDK]" if d["sdk"].get("torch") else "  [nothing detected]")))
    print("  2) Install a local server here")
    print("  3) Use a remote server")
    choice = input("Choice [1/2/3]: ").strip()
    if choice == "1":
        flow_use(d)
    elif choice == "2":
        yn = input(f"Install deps into {args.server_venv} now? [y/N]: ").strip().lower()
        flow_install(args.server_venv, yn == "y")
    elif choice == "3":
        url = input("Remote server URL (e.g. http://mac-studio.local:8880 or http://127.0.0.1:8880 for ssh-loopback): ").strip()
        tr = input("Transport [http/ssh-loopback] (default http): ").strip() or "http"
        sh = input("SSH host (only for ssh-loopback, e.g. user@100.x.x.x): ").strip() if tr == "ssh-loopback" else ""
        flow_remote(url, tr, sh)
    else:
        print("No change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
