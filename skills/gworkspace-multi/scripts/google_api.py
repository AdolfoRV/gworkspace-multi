#!/usr/bin/env python3
"""
google_api.py — Multi-account Google Workspace API client for gworkspace-multi skill.
All commands output JSON. Use --profile to target a specific account.
"""

import argparse
import sys
import json
from pathlib import Path

# Allow imports from this directory (core/, services/)
sys.path.insert(0, str(Path(__file__).parent))

from core.output import _err

_SERVICES = {
    "gmail":    "services.gmail",
    "calendar": "services.calendar",
    "drive":    "services.drive",
    "docs":     "services.docs",
    "sheets":   "services.sheets",
    "tasks":    "services.tasks",
    "meet":     "services.meet",
    "scripts":  "services.scripts",
    "contacts": "services.contacts",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="gworkspace-multi API client")
    parser.add_argument("--profile", 
                        help="Account profile name (e.g. personal, uni, tripleta). Falls back to default_profile in config.")
    parser.add_argument("service",
                        help=f"Service: {' | '.join(_SERVICES)}")
    parser.add_argument("command",
                        help="Command (varies by service — see references/<service>.md)")
    parser.add_argument("args", nargs=argparse.REMAINDER)

    ns, remaining = parser.parse_known_args()
    args = ns.args + remaining

    # Handle profile fallback
    profile = ns.profile
    if not profile:
        try:
            config_path = Path(sys.prefix).parent / ".hermes" / "gworkspace-multi.json" 
            # Fallback to common home path if sys.prefix is not helpful
            if not config_path.exists():
                config_path = Path.home() / ".hermes" / "gworkspace-multi.json"
            
            if config_path.exists():
                with open(config_path) as f:
                    cfg = json.load(f)
                    profile = cfg.get("default_profile")
        except Exception:
            pass
            
    if not profile:
        _err("No profile specified via --profile and no 'default_profile' found in gworkspace-multi.json")
        sys.exit(1)

    module_path = _SERVICES.get(ns.service)
    if not module_path:
        _err(f"Unknown service '{ns.service}'. Available: {', '.join(_SERVICES)}")

    try:
        import importlib
        module = importlib.import_module(module_path)
        module.dispatch(profile, ns.command, args)
    except ModuleNotFoundError as e:
        _err(f"Missing dependency or module: {e}. Run setup.py --install-deps first.")
    except Exception as e:
        _err(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
