# references/gmail.md — Gmail

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> gmail <command> [options]
```

---

## `search`
Searches for messages. Accepts any Gmail query (`is:unread`, `from:`, `subject:`, etc.).
```bash
gmail search <query> [--max N]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `query` | str (positional) | required | Gmail query |
| `--max` | int | 10 | Maximum results |

Returns: list of `{id, threadId, from, to, subject, date, snippet, labels}`.

---

## `get`
Retrieves the full content of a message (including body).
```bash
gmail get <message_id>
```
Returns: `{id, threadId, from, to, subject, date, labels, body}`.

---

## `send`
Sends a new email.
```bash
gmail send --to <addr> --subject <str> --body <str> [--from <addr>] [--html] [--reply-to <msg_id>]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--to` | str | required | Recipient |
| `--subject` | str | required | Subject |
| `--body` | str | required | Message body |
| `--from` | str | — | Explicit sender (account alias) |
| `--html` | flag | false | Send as HTML (multipart/alternative with plain fallback) |
| `--reply-to` | str | — | Message-ID being replied to (adds In-Reply-To/References headers) |

Returns: `{status: "sent", id, threadId}`.

---

## `reply`
Replies to an existing message, maintaining the thread.
```bash
gmail reply <message_id> --body <str> [--from <addr>]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `message_id` | str (positional) | required | Original message ID |
| `--body` | str | required | Reply body |
| `--from` | str | — | Explicit sender |

Returns: `{status: "sent", id, threadId}`.

---

## `labels`
Lists all labels for the account.
```bash
gmail labels
```
Returns: list of `{id, name, type}`.

---

## `modify`
Adds or removes labels from a message.
```bash
gmail modify <message_id> [--add-labels L1 L2] [--remove-labels L1 L2]
```
| Argument | Type | Description |
|---|---|---|
| `message_id` | str (positional) | Message ID |
| `--add-labels` | str... | Label IDs to add |
| `--remove-labels` | str... | Label IDs to remove |

**Useful aliases:**
- Archive: `--remove-labels INBOX`
- Mark as read: `--remove-labels UNREAD`
- Star: `--add-labels STARRED`
- Move to spam: `--add-labels SPAM --remove-labels INBOX`

---

## `get-attachments`
Downloads all attachments from a message to disk.
```bash
gmail get-attachments <message_id> [--output <dir>]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `message_id` | str (positional) | required | Message ID |
| `--output` | str | `~/Downloads` | Destination directory |

Returns: `{status: "saved", messageId, attachments: [{filename, path, size}]}`.
If no attachments: `{status: "no_attachments", messageId}`.

---

## `draft-create`
Creates a draft without sending it.
```bash
gmail draft-create --to <addr> --subject <str> --body <str> [--from <addr>] [--html] [--reply-to-id <msg_id>]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--to` | str | required | Recipient |
| `--subject` | str | required | Subject |
| `--body` | str | required | Body |
| `--from` | str | — | Explicit sender |
| `--html` | flag | false | HTML body |
| `--reply-to-id` | str | — | Original message ID for reply draft |

Returns: `{status: "draft_created", draftId, messageId}`.

## `draft-send`
Sends an existing draft.
```bash
gmail draft-send <draft_id>
```
Returns: `{status: "sent", id, threadId}`.

> **Draft workflow for human review:**
> ```bash
> gmail draft-create --to "foo@bar.com" --subject "Proposal" --body "..."
> # → {draftId: "r123..."}
> # human reviews in Gmail, then:
> gmail draft-send "r123..."
> ```

---

## `schedule`
Schedules the creation of a draft to be sent at a future date.
**Note:** The Gmail API does not support native scheduled sending; this function creates the draft and generates a command for the `at` system.

```bash
gmail schedule --to <addr> --subject <str> --body <str> --send-at <ISO8601> [--from <addr>] [--html]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--to` | str | required | Recipient |
| `--subject` | str | required | Subject |
| `--body` | str | required | Body |
| `--send-at` | ISO8601 | required | Send date/time (must include TZ, e.g. `2026-06-20T15:00:00Z`) |
| `--from` | str | — | Explicit sender |
| `--html` | flag | false | Send as HTML |

Returns: `{status: "draft_created", draftId, messageId, send_at, send_at_unix, note, at_command}`.

> **Scheduled sending workflow:**
> 1. Run `gmail schedule ...` $\rightarrow$ obtain `at_command`.
> 2. Run the `at_command` in the terminal so the operating system triggers the send via `gmail draft-send` at the indicated date.
