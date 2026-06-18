import json
import os
from pathlib import Path

from .output import _err

HERMES_DIR = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CONFIG_PATH = HERMES_DIR / "gworkspace-multi.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        _err(f"Config not found at {CONFIG_PATH}. Run setup.py first.")
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        _err(f"Corrupted config file at {CONFIG_PATH}: {e}. Backup and re-run setup.")


def get_profile_token(profile: str) -> dict:
    cfg = load_config()
    token = cfg.get("profiles", {}).get(profile)
    if not token:
        _err(f"No token found for profile '{profile}'. Run setup.py --auth-url --profile {profile}")
    return token
