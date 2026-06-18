# references/setup.md — OAuth Authorization and Profile Management

Script: `python3 ${HERMES_SKILL_DIR}/scripts/setup.py`

---

## Full Authorization Flow

### 1. Install Dependencies (once)
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --install-deps
```

### 2. Register GCP Project Client Secret
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --client-secret /path/google_client_secret.json
```
The file must contain the `installed` or `web` key at the root.
It is saved in `~/.hermes/gworkspace-multi.json` under `client_secret`.

> 💡 To avoid leaving the file on disk, create it in `/tmp/` and pass it from there.

> ⚠️ **Multiple GCP Projects:** The system stores a single global client secret. If you use different Client IDs for different profiles, complete the full flow for one profile (`--auth-url` $\rightarrow$ `--auth-code`) before changing the secret for the next one.

### 3. Generate Authorization URL
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --auth-url --profile <profile> [--services all|email,calendar,...]
```
Returns `{"auth_url": "https://accounts.google.com/o/oauth2/..."}`.

**Available services:** `email`, `calendar`, `drive`, `docs`, `sheets`, `tasks`, `meet`, `scripts`, `contacts` (or `all`).

### 4. Authorize in Browser
- Open in an **incognito window**.
- Add `&login_hint=email@example.com` to the end of the URL to force the correct account.
- Complete the flow until the redirection error screen — this is expected.
- Copy the **complete URL** from the address bar.

> **Note:** The `redirect_uri` used is `http://localhost:1`, which causes a connection error in the browser. This is intentional: the `code` appears in the URL of the address bar and is automatically extracted when passed to `--auth-code`.

### 5. Exchange the Code
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --auth-code "COMPLETE_URL_OR_JUST_THE_CODE" --profile <profile>
```
The token is saved in `profiles.<profile>` inside `~/.hermes/gworkspace-multi.json`.

### 6. Verify
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --check --profile <profile>
# Confirm with a real call:
python3 ${HERMES_SKILL_DIR}/scripts/google_api.py --profile <profile> contacts list --max 1
```

---

## Management Commands

```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --list-profiles                    # list authorized profiles
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --check [--profile <p>]            # verify token status
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --revoke --profile <p>             # revoke and remove token
```

---

## 🚩 Common Pitfalls

| Error | Cause | Solution |
|---|---|---|
| `Invalid Code Verifier` | Reusing tab or old code | Close everything, new incognito window, generate fresh URL |
| `Token expired` | Expired token without refresh | Re-authorize with `--auth-url` |
| `No token found for profile` | Profile not authorized or incorrect name | `--list-profiles` to see existing profiles |
| Action applied to wrong account | Profile ghosting | Always verify with `contacts list --max 1` before |
| `Corrupted config file` | `gworkspace-multi.json` is damaged | Make backup, delete, and reconfigure from `--client-secret` |

---

## 🔍 Diagnostic Report

For persistent failures:
1. **Context:** what was being attempted and with which profile.
2. **Inventory:** content of `~/.hermes/gworkspace-multi.json` (redact tokens and client_secret).
3. **Trace:** commands executed in order and the exact error for each one.
