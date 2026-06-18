#!/usr/bin/env python3
"""
setup.py — OAuth2 setup for gworkspace-multi skill.
Supports multiple Google accounts (profiles) in a single JSON file.

Usage:
  python setup.py --check [--profile NAME]
  python setup.py --client-secret /path/to/client_secret.json
  python setup.py --auth-url --profile NAME [--services all|email,calendar,...]
  python setup.py --auth-code "URL_OR_CODE" --profile NAME
  python setup.py --list-profiles
  python setup.py --revoke --profile NAME
  python setup.py --install-deps
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode

HERMES_DIR = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CONFIG_PATH = HERMES_DIR / "gworkspace-multi.json"


SCOPES = {
    "email": [
        "https://mail.google.com/",
    ],
    "calendar": [
        "https://www.googleapis.com/auth/calendar",
    ],
    "drive": [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.activity",
        "https://www.googleapis.com/auth/drive.activity.readonly",
    ],
    "docs": [
        "https://www.googleapis.com/auth/documents",
    ],
    "sheets": [
        "https://www.googleapis.com/auth/spreadsheets",
    ],
    "tasks": [
        "https://www.googleapis.com/auth/tasks",
    ],
    "meet": [
        "https://www.googleapis.com/auth/meetings.space.created",
        "https://www.googleapis.com/auth/meetings.space.readonly",
        "https://www.googleapis.com/auth/meetings.space.settings",
    ],
    "scripts": [
        "https://www.googleapis.com/auth/script.projects",
        "https://www.googleapis.com/auth/script.deployments",
        "https://www.googleapis.com/auth/script.processes",
        "https://www.googleapis.com/auth/script.metrics",
        "https://www.googleapis.com/auth/script.scriptapp",
    ],
    "contacts": [
        "https://www.googleapis.com/auth/contacts",
    ],
}

ALL_SCOPES = [s for group in SCOPES.values() for s in group]

SERVICE_APIS = {
    "email": "Gmail API",
    "calendar": "Google Calendar API",
    "drive": "Google Drive API + Drive Activity API",
    "docs": "Google Docs API",
    "sheets": "Google Sheets API",
    "tasks": "Google Tasks API",
    "meet": "Google Meet API",
    "scripts": "Apps Script API",
    "contacts": "People API",
}


def load_config() -> dict:
    """Load the unified config file. Create if missing."""
    if not CONFIG_PATH.exists():
        return {"profiles": {}, "client_secret": None}
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "error": f"Corrupted config file at {CONFIG_PATH}: {e}"}))
        sys.exit(1)


def save_config(cfg: dict):
    """Save the unified config file atomically."""
    HERMES_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    tmp.chmod(0o600)
    tmp.replace(CONFIG_PATH)


def get_profile_token(cfg: dict, profile: str) -> dict | None:
    """Get token data for a profile, or None."""
    return cfg.get("profiles", {}).get(profile)


def set_profile_token(cfg: dict, profile: str, token: dict):
    """Set token data for a profile."""
    if "profiles" not in cfg:
        cfg["profiles"] = {}
    cfg["profiles"][profile] = token


def resolve_scopes(services_arg: str) -> list[str]:
    if services_arg == "all":
        return ALL_SCOPES
    result = []
    for svc in services_arg.split(","):
        svc = svc.strip()
        if svc not in SCOPES:
            print(f"Warning: unknown service '{svc}', skipping.", file=sys.stderr)
            continue
        result.extend(SCOPES[svc])
    return list(dict.fromkeys(result))


def install_deps():
    import subprocess
    pkgs = ["google-auth", "google-auth-oauthlib", "google-auth-httplib2", "google-api-python-client"]
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + pkgs)
    print("Dependencies installed.")


def load_client_secret() -> dict:
    cfg = load_config()
    cs = cfg.get("client_secret")
    if not cs:
        print(json.dumps({"status": "error", "error": f"No client_secret stored in {CONFIG_PATH}. Run --client-secret first."}))
        sys.exit(1)
    return cs


def cmd_check(profile: str):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    cfg = load_config()
    token = get_profile_token(cfg, profile)
    if not token:
        print(json.dumps({"status": "NOT_AUTHENTICATED", "profile": profile, "config_path": str(CONFIG_PATH)}))
        return

    try:
        creds = Credentials.from_authorized_user_info(token)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            set_profile_token(cfg, profile, json.loads(creds.to_json()))
            save_config(cfg)
        if creds.valid:
            scopes = getattr(creds, "scopes", None) or []
            expiry = getattr(creds, "expiry", None)
            expiry_iso = expiry.isoformat() if expiry else None
            print(json.dumps({"status": "AUTHENTICATED", "profile": profile, "scopes": list(scopes), "expires_at": expiry_iso}))
        else:
            print(json.dumps({"status": "NOT_AUTHENTICATED", "profile": profile}))
    except Exception as e:
        print(json.dumps({"status": "REFRESH_FAILED", "profile": profile, "error": str(e)}))


def cmd_list_profiles():
    cfg = load_config()
    profiles = sorted(cfg.get("profiles", {}).keys())
    print(json.dumps({"profiles": profiles, "config_path": str(CONFIG_PATH)}))


def cmd_set_client_secret(path: str):
    src = Path(path).expanduser()
    if not src.exists():
        print(json.dumps({"status": "error", "error": f"File not found: {src}"}))
        sys.exit(1)
    try:
        with open(src) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "error": f"Invalid JSON in client secret file: {e}"}))
        sys.exit(1)

    key = "installed" if "installed" in data else "web" if "web" in data else None
    if key is None:
        print(json.dumps({"status": "error", "error": "Invalid client secret JSON (missing 'installed' or 'web' key)"}))
        sys.exit(1)

    inner = data[key]
    for required in ("client_id", "client_secret"):
        if required not in inner:
            print(json.dumps({"status": "error", "error": f"Invalid client secret JSON: missing '{required}' inside '{key}'"}))
            sys.exit(1)

    cfg = load_config()
    cfg["client_secret"] = data
    save_config(cfg)
    print(json.dumps({"status": "ok", "saved_to": str(CONFIG_PATH)}))


def cmd_auth_url(profile: str, services: str, fmt: str):
    try:
        from google_auth_oauthlib.flow import Flow
    except ImportError:
        print(json.dumps({"status": "error", "error": "Missing deps. Run --install-deps first."}))
        sys.exit(1)

    scopes = resolve_scopes(services)
    if not scopes:
        print(json.dumps({"status": "error", "error": "No valid services specified."}))
        sys.exit(1)

    secret = load_client_secret()
    flow = Flow.from_client_config(
        secret,
        scopes=scopes,
        redirect_uri="http://localhost:1",
    )
    flow.code_verifier = _generate_code_verifier()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="false",
        prompt="consent",
        code_challenge=_generate_code_challenge(flow.code_verifier),
        code_challenge_method="S256",
    )

    cfg = load_config()
    if "pending" not in cfg:
        cfg["pending"] = {}
    cfg["pending"][profile] = {
        "services": services,
        "scopes": scopes,
        "state": state,
        "code_verifier": flow.code_verifier,
        "redirect_uri": "http://localhost:1",
    }
    save_config(cfg)

    print(json.dumps({"status": "ok", "auth_url": auth_url, "profile": profile, "services": services, "scopes": scopes}))


def cmd_auth_code(profile: str, code_or_url: str, fmt: str):
    try:
        from google_auth_oauthlib.flow import Flow
    except ImportError:
        print(json.dumps({"status": "error", "error": "Missing deps. Run --install-deps first."}))
        sys.exit(1)

    cfg = load_config()
    pending = cfg.get("pending", {}).get(profile)
    if not pending:
        print(json.dumps({"status": "error", "error": f"No pending OAuth session for profile '{profile}'. Run --auth-url first."}))
        sys.exit(1)

    secret = load_client_secret()
    flow = Flow.from_client_config(
        secret,
        scopes=pending["scopes"],
        redirect_uri=pending["redirect_uri"],
        state=pending["state"],
    )
    flow.code_verifier = pending["code_verifier"]

    code = code_or_url.strip()
    if code.startswith("http"):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(code)
        qs = parse_qs(parsed.query)
        if "code" not in qs:
            print(json.dumps({"status": "error", "error": "Could not extract 'code' from URL."}))
            sys.exit(1)
        code = qs["code"][0]

    try:
        flow.fetch_token(code=code)
    except Exception as e:
        err_str = str(e)
        print(json.dumps({
            "status": "error",
            "error": f"Token exchange failed: {err_str}",
            "hint": "Code may be expired or state mismatch. Run --auth-url again and retry."
        }))
        sys.exit(1)

    creds = flow.credentials
    token_data = json.loads(creds.to_json())
    set_profile_token(cfg, profile, token_data)
    # Clean pending
    if "pending" in cfg and profile in cfg["pending"]:
        del cfg["pending"][profile]
    save_config(cfg)

    print(json.dumps({
        "status": "AUTHENTICATED",
        "profile": profile,
        "scopes": list(creds.scopes or []),
    }))


def cmd_revoke(profile: str):
    cfg = load_config()
    token = get_profile_token(cfg, profile)
    if not token:
        print(json.dumps({"status": "error", "error": f"No token found for profile '{profile}'."}))
        sys.exit(1)
    try:
        tok = token.get("token") or token.get("access_token")
        if tok:
            data = urlencode({"token": tok}).encode()
            req = Request("https://oauth2.googleapis.com/revoke", data=data, method="POST")
            urlopen(req)
    except Exception:
        pass
    del cfg["profiles"][profile]
    save_config(cfg)
    print(json.dumps({"status": "revoked", "profile": profile}))


def _generate_code_verifier() -> str:
    import secrets, base64
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()


def _generate_code_challenge(verifier: str) -> str:
    import hashlib, base64
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def main():
    parser = argparse.ArgumentParser(description="gworkspace-multi OAuth setup")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list-profiles", action="store_true")
    parser.add_argument("--client-secret", metavar="PATH")
    parser.add_argument("--auth-url", action="store_true")
    parser.add_argument("--auth-code", metavar="CODE_OR_URL")
    parser.add_argument("--revoke", action="store_true")
    parser.add_argument("--install-deps", action="store_true")
    parser.add_argument("--profile", default="default", help="Account profile name")
    parser.add_argument("--services", default="all", help="Comma-separated services or 'all'")
    parser.add_argument("--format", default="json", choices=["json", "text"])

    args = parser.parse_args()

    if args.install_deps:
        install_deps()
    elif args.list_profiles:
        cmd_list_profiles()
    elif args.check:
        cmd_check(args.profile)
    elif args.client_secret:
        cmd_set_client_secret(args.client_secret)
    elif args.auth_url:
        cmd_auth_url(args.profile, args.services, args.format)
    elif args.auth_code:
        cmd_auth_code(args.profile, args.auth_code, args.format)
    elif args.revoke:
        cmd_revoke(args.profile)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
