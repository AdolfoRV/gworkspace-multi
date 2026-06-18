# references/contacts.md — Contacts (People API)

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> contacts <command> [options]
```

> **Primary use for identity verification:** before any destructive action or sending, run `contacts list --max 1` and confirm that the returned email matches the intended profile.

---

## `list`
Lists contacts from the account.
```bash
contacts list [--max N]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--max` | int | 20 | Maximum number of contacts |

Returns: list of `{name, emails: [...], phones: [...]}`.

---

## `search`
Searches for contacts by name or email. More efficient than `list` for large directories.
```bash
contacts search <query>
```
| Argument | Type | Description |
|---|---|---|
| `query` | str (positional) | Name or email to search for (partial matches work) |

Returns: list of `{name, emails: [...], phones: [...]}`.

> Prefer `search` over `list` when looking for a specific person.

---

## `list-groups`
Lists all contact groups/labels for the account.
```bash
contacts list-groups
```
Returns: list of `{id, name, memberCount, type}`.

- `id` has the format `contactGroups/abc123`.
- `type: USER_CONTACT_GROUP` — groups created by the user.
- `type: SYSTEM_CONTACT_GROUP` — system groups (e.g., "Starred", "All contacts").

---

## `list-group`
Returns the members of a group along with their emails.
```bash
contacts list-group <group_id>
```
| Argument | Type | Description |
|---|---|---|
| `group_id` | str (positional) | Group ID, e.g., `contactGroups/abc123` |

Returns: list of `{name, emails: [...]}`.

> **Typical workflow for inviting a group to Calendar:**
> ```bash
> # 1. Find the group ID
> contacts list-groups
> # 2. Get group emails
> contacts list-group "contactGroups/abc123"
> # 3. Pass the emails to calendar create
> calendar create --summary "Meeting" --start "..." --end "..." \
>   --attendees "juan@gmail.com,maria@gmail.com"
> ```
