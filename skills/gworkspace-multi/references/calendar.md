# references/calendar.md — Google Calendar

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> calendar <command> [options]
```

---

## `list`
Lists upcoming events from a calendar.
```bash
calendar list [--start ISO8601] [--end ISO8601] [--calendar-id ID] [--max N]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--start` | ISO8601 | now | Range start |
| `--end` | ISO8601 | — | Range end (optional) |
| `--calendar-id` | str | `primary` | Calendar ID |
| `--max` | int | 50 | Maximum results |

Returns: list of `{id, summary, start, end, location, description, htmlLink, attendees}`.

---

## `list-calendars`
Lists all calendars in the account.
```bash
calendar list-calendars
```
Returns: list of `{id, summary, primary}`.

---

## `create`
Creates a new event, optionally with a Meet room.
```bash
calendar create --summary <str> --start <ISO8601> --end <ISO8601> \
                [--location <str>] [--description <str>] \
                [--attendees email1,email2] [--calendar-id ID] [--create-meet]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--summary` | str | required | Event title |
| `--start` | ISO8601 | required | Start (e.g. `2026-06-16T10:00:00Z`) |
| `--end` | ISO8601 | required | End |
| `--location` | str | — | Location |
| `--description` | str | — | Description |
| `--attendees` | str | — | Comma-separated emails |
| `--calendar-id` | str | `primary` | Calendar ID |
| `--create-meet` | flag | false | Generates a Google Meet room for the event |

Returns: `{status: "created", id, summary, htmlLink, conferenceData, space_id?}`.

> **Note:** `space_id` (format `spaces/XYZ`) is returned only when `--create-meet` is true. This is the identifier required to modify the room configuration using the Meet sub-skill (e.g., changing access to `OPEN`).

---

## `update`
Edits an existing event. Only passed fields are modified — others are preserved.
```bash
calendar update <event_id> [--summary <str>] [--start <ISO8601>] [--end <ISO8601>] \
                            [--location <str>] [--description <str>] \
                            [--attendees email1,email2] [--calendar-id ID]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `event_id` | str (positional) | required | Event ID |
| `--summary` | str | — | New title |
| `--start` | ISO8601 | — | New start time |
| `--end` | ISO8601 | — | New end time |
| `--location` | str | — | New location (pass `""` to clear) |
| `--description` | str | — | New description (pass `""` to clear) |
| `--attendees` | str | — | Full attendee list (replaces existing) |
| `--calendar-id` | str | `primary` | Calendar ID |

Returns: `{status: "updated", id, summary, start, end, htmlLink}`.

> `sendUpdates: "none"` is hardcoded — attendees are never notified.

---

## `delete`
Deletes an event.
```bash
calendar delete <event_id> [--calendar-id ID]
```
Returns: `{status: "deleted", eventId}`.
