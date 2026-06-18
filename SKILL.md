---
name: gworkspace-multi
description: Gmail, Calendar, Drive, Docs, Sheets, Tasks, Meet, Apps Script, Contacts — multi-account Google Workspace management with native profile support.
version: 1.0.0
author: AdolfoRV
required_environment_variables:
  - name: HERMES_HOME
    prompt: "Hermes configuration directory"
    help: "Base path where Hermes stores configs and skills. Default: ~/.hermes"
    required_for: "location of the gworkspace-multi.json file"
required_credential_files:
  - path: gworkspace-multi.json
    description: "Unified skill config: client_secret, profiles, pending OAuth sessions (Permissions 0600)"
  - path: client_secret.json
    description: "Google OAuth2 client credentials (Permissions 0600)"
metadata:
  hermes:
    tags: [productivity, google, workspace, gmail, calendar, drive, docs, sheets, oauth, multi-account]
    related_skills: []
    requires_toolsets: []
    requires_tools: []
    fallback_for_toolsets: []
    fallback_for_tools: []
    config:
      - key: gworkspace-multi.default_profile
        description: "Default Google profile used when --profile is not specified"
        default: ""
        prompt: "Default Google profile name (e.g. personal, work, university)"
---

# GWorkspace Multi-Account

Skill for operating multiple Google accounts in an isolated and secure manner.

## 🛠️ Components

| File | Role |
|---|---|
| `scripts/google_api.py` | Main client — dispatcher to all services |
| `scripts/setup.py` | OAuth setup per profile, revocation, status verification |
| `~/.hermes/gworkspace-multi.json` | Unified config: `client_secret`, `profiles`, `pending` |
| `~/.hermes/client_secret.json` | Global Google Cloud project credentials (Hermes standard) |

## 🚀 General Syntax

```bash
SCRIPT="python3 ${HERMES_SKILL_DIR}/scripts/google_api.py"
$SCRIPT --profile <profile> <service> <command> [options]
```

> **Note on `${HERMES_SKILL_DIR}`:** This token is automatically replaced by the absolute path of this skill's directory upon loading. No manual configuration required.

All commands return **JSON via stdout**. Errors follow the format `{"status": "error", "error": "..."}`.

---

## 📦 Sub-skills — Load as needed

Before using a service or configuring a profile, load the corresponding reference with `skill_view`.

| Sub-skill | When to load |
|---|---|
| `references/setup.md` | Authorize a new profile, revoke tokens, install dependencies, verify OAuth status |
| `references/gmail.md` | Search, read, send, reply, label, drafts, schedule emails |
| `references/calendar.md` | List, create, edit or delete events; list calendars |
| `references/drive.md` | Search, upload, download, share, delete files; query activity |
| `references/docs.md` | Read, create or add content to Google Docs |
| `references/sheets.md` | Read, write or add rows in Google Sheets |
| `references/tasks.md` | Manage lists and tasks (create, complete, delete) |
| `references/meet.md` | Create and manage independent Google Meet spaces |
| `references/scripts.md` | Execute or inspect Apps Script projects |
| `references/contacts.md` | List contacts, search by name/email, manage groups — includes identity verification |

---

## ⚠️ Pitfalls & Solutions

1. **Meet Identifiers**: When creating meetings via Calendar (`--create-meet`), the API returns a `conferenceId` (the public link code). To modify the room (e.g., open access or enable moderation) via the Meet API, the `space_id` (format `spaces/XYZ`) is required. The skill resolves this automatically and returns `space_id` in the `calendar create` result.
2. **Moderation**: To enable "Host Management", use `meet patch-space <space_id> --moderation ON`.
3. **Profile Synchronization**: Always verify the active account with `contacts list --max 1` before destructive actions to avoid profile errors.
4. **Scheduled Sending**: The Gmail API does not support native scheduled sending. The correct flow is: `gmail schedule` $\rightarrow$ Create draft $\rightarrow$ Execute the generated `at` command to trigger `gmail draft-send`.
5. **Git Cleanup**: When publishing the skill, avoid uploading temporary editor files (e.g., `*.swp`). These must be included in `.gitignore`.

---

## 🔐 Security & Credentials

- The `gworkspace-multi.json` file stores refreshable OAuth2 tokens. It is created with `0o600` permissions.
- Tokens refresh automatically upon expiration.
- `client_secret.json` is stored once via `--client-secret` and reused for all profiles.
- **Default Profile**: A `default_profile` can be defined in `gworkspace-multi.json` to avoid passing `--profile` in every command.
- To revoke a profile's access: `python3 /home/ubuntu/.hermes/skills/productivity/gworkspace-multi/scripts/setup.py --revoke --profile <name>`

- **File Permissions**: Both `gworkspace-multi.json` and `client_secret.json` MUST have `0600` permissions (`chmod 600`) to prevent credential leaks.

## ⚠️ Critical Rules & Pitfalls

1. **Profile Verification**: Before any destructive action or sending, verify the account:
   `$SCRIPT --profile <profile> contacts list --max 1`
2. **Meet Management**: To modify permissions of a room created via Calendar, the `space_id` (format `spaces/XYZ`) is required. The `calendar create` function now returns it automatically. Do not attempt to use the public URL code directly in `meet patch-space`.
3. **Scheduled Sending**: Gmail API does not support native `scheduled send`. The correct flow is: `gmail schedule` $\rightarrow$ Create draft $\rightarrow$ Execute the generated `at` command to trigger `gmail draft-send`.
- **Gmail Scheduled Sending**: The Gmail API does not support native scheduled sending. The skill implements a **Draft $\rightarrow$ `at` Command** flow. The `at_command` returned by `gmail schedule` must be executed in the terminal to schedule the actual delivery.
- **Moderation Management**: To enable Host Management in a room, use `meet patch-space <space_id> --moderation ON`.
