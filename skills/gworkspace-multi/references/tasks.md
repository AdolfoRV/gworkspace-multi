# references/tasks.md — Google Tasks

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> tasks <command> [options]
```

---

## `list-lists`
Lists available task lists in the account.
```bash
tasks list-lists
```
Returns: list of `{id, title, updated}`. Use these IDs in other commands.

---

## `list`
Lists tasks from a specific list.
```bash
tasks list [--tasklist ID] [--show-completed] [--max N]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--tasklist` | str | `@default` | List ID (obtain with `list-lists`) |
| `--show-completed` | flag | false | Include completed tasks |
| `--max` | int | 50 | Maximum results |

> ⚠️ Always use `--tasklist <id>` as a flag, never as a positional argument.

---

## `create`
Creates a new task.
```bash
tasks create --title <str> [--notes <str>] [--due <ISO8601>] [--tasklist ID]
```
The `--due` date must be RFC 3339, e.g. `2026-06-20T00:00:00Z`.

Returns: `{status: "created", id, title, due, task_status}`.

---

## `complete`
Marks a task as completed.
```bash
tasks complete <task_id> [--tasklist ID]
```
Returns: `{status: "completed", id, title}`.

---

## `delete`
Permanently deletes a task.
```bash
tasks delete <task_id> [--tasklist ID]
```
Returns: `{status: "deleted", taskId}`.
