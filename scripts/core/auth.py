import json

from .config import CONFIG_PATH, load_config, get_profile_token
from .output import _err


def get_credentials(profile: str):
    """Load and auto-refresh OAuth2 credentials for the given profile."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    token_data = get_profile_token(profile)
    creds = Credentials.from_authorized_user_info(token_data)

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds, profile)
        except Exception as e:
            _err(f"Token refresh failed for profile '{profile}': {e}")

    if not creds.valid:
        _err(f"Invalid credentials for profile '{profile}'. Token may be expired or revoked. Re-run setup.")

    return creds


def _save_token(creds, profile: str) -> None:
    cfg = load_config()
    cfg.setdefault("profiles", {})[profile] = json.loads(creds.to_json())
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    tmp.chmod(0o600)
    tmp.replace(CONFIG_PATH)


def build_service(name: str, version: str, profile: str):
    """Build and return an authenticated Google API service client."""
    from googleapiclient.discovery import build
    return build(name, version, credentials=get_credentials(profile))
