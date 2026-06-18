```markdown
# gworkspace-multi

Hermes skill to manage multiple Google Workspace accounts (Gmail, Calendar, Drive, Docs, Sheets, Tasks, Meet, Apps Script, Contacts) from a single entry point, with native support for isolated profiles.

## Prerequisites

* Python 3.10+
* A project in Google Cloud Console with the APIs you plan to use enabled
* OAuth 2.0 credentials of type "Desktop Application" downloaded as `client_secret.json`

### APIs you need to enable in GCP (depending on the services you use)

| Service | API to enable |
| :--- | :--- |
| Gmail | Gmail API |
| Calendar | Google Calendar API |
| Drive | Google Drive API + Drive Activity API |
| Docs | Google Docs API |
| Sheets | Google Sheets API |
| Tasks | Google Tasks API |
| Meet | Google Meet API |
| Apps Script | Apps Script API |
| Contacts | People API |

## Installation

### 1. Install Python dependencies
```bash
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py --install-deps

```

Installs: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.

### 2. Register the client secret

```bash
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py \
  --client-secret /path/to/client_secret.json

```

The file is saved inside `~/.hermes/gworkspace-multi.json`. You can delete the original afterwards if you want.

⚠️ Only one client secret at a time. If you need different GCP projects for different profiles, complete the authorization flow of one profile before changing the secret.

## Authorizing a profile (Google account)

Each account you want to use needs to go through this flow only once.

### Step 1 — Generate the authorization URL

```bash
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py \
  --auth-url --profile <name> [--services all|email,calendar,drive,...]

```

Returns a Google URL. You can use `--services all` to authorize everything at once, or only the services you need (e.g., `email,calendar`).

### Step 2 — Authorize in the browser

1. Open the URL in an incognito window.
2. If you want to force a specific account, add `&login_hint=your@email.com` to the end of the URL.
3. Complete the permissions flow until the browser shows a connection error — this is expected. The `redirect_uri` is `http://localhost:1`, which does not exist: Google still generates the code.
4. Copy the complete URL from the address bar.

### Step 3 — Exchange the code

```bash
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py \
  --auth-code "COPIED_COMPLETE_URL" --profile <name>

```

The token remains saved in `~/.hermes/gworkspace-multi.json` under `profiles.<name>`.

### Step 4 — Verify

```bash
# Verify token status
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py \
  --check --profile <name>

# Verify with a real call
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py \
  --profile <name> gmail search "in:inbox" --max 1

```

## File structure

```text
~/.hermes/
├── gworkspace-multi.json     # Unified config: tokens, client_secret, pending sessions
└── skills/productivity/gworkspace-multi/
    ├── SKILL.md
    └── scripts/
        ├── google_api.py     # Main entry point
        ├── setup.py          # OAuth management
        └── core/
            ├── __init__.py
            ├── auth.py
            ├── config.py
            └── output.py
        └── services/
            ├── gmail.py
            ├── calendar.py
            ├── drive.py
            └── ...           # one file per service

```

The `gworkspace-multi.json` file has `0600` permissions (read/write only for your user). Tokens refresh automatically when they expire.

## Usage from terminal

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT [--profile <name>] <service> <command> [options]

> **Note:** The `--profile` flag is optional if a `default_profile` is defined in `gworkspace-multi.json`.

```

All commands return JSON through stdout. Errors have the format `{"status": "error", "error": "..."}`.

### Quick examples

```bash
# Search unread emails
$SCRIPT --profile personal gmail search "is:unread" --max 5

# Send an email
$SCRIPT --profile work gmail send \
  --to recipient@example.com \
  --subject "Subject" \
  --body "Message body"

# Create a draft for human review before sending
$SCRIPT --profile personal gmail draft-create \
  --to someone@example.com \
  --subject "Proposal" \
  --body "Content..."
# → {"draftId": "r123...", ...}
# Review in Gmail, then:
$SCRIPT --profile personal gmail draft-send "r123..."

# Schedule an email for a future date
$SCRIPT gmail schedule \
  --to boss@example.com \
  --subject "Weekly Report" \
  --body "Attached is the report" \
  --send-at "2026-06-24T09:00:00Z"

```

## Profile management

```bash
# List authorized profiles
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py --list-profiles

# Verify status of a profile
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py --check --profile <name>

# Revoke a profile (removes the local token and revokes it on Google)
python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py --revoke --profile <name>

```

## Troubleshooting

| Error | Probable cause | Solution |
| --- | --- | --- |
| Invalid Code Verifier | Old code or reused tab | Close everything, new incognito window, generate new URL |
| No token found for profile 'X' | Profile not authorized or incorrect name | `--list-profiles` to see available ones |
| Token refresh failed | Token revoked or expired | Re-authorize with `--auth-url` + `--auth-code` |
| No client_secret stored | Missing initial step | Run `--client-secret /path/to/file.json` |
| Corrupted config file | Damaged `gworkspace-multi.json` | Make a backup, delete the file, and reconfigure from scratch |
| Action applied to the wrong account | Incorrect profile name | Always verify with `gmail search "in:inbox" --max 1` before destructive actions |

## Security

* OAuth tokens are stored only on your machine in `~/.hermes/gworkspace-multi.json` with `0600` permissions.
* Hermes never exposes tokens to the language model.
* To revoke access permanently, use `--revoke` or revoke access directly from `myaccount.google.com/permissions`.
* The original `client_secret.json` can be removed from disk once registered — the skill stores only what is necessary internally.

```

```
