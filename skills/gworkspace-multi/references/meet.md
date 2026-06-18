# references/meet.md — Google Meet

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> meet <command> [options]
```

> For rooms associated with a Calendar event, use `calendar create --create-meet` instead.

---

## `create-space`
Creates a persistent Meet room (independent of Calendar).
```bash
meet create-space
```
Returns: `{status: "created", name, meetingUri, meetingCode}`.

The `name` has the format `spaces/XYZ` — save it for subsequent commands.

---

## `get-space`
Retrieves information about a room.
```bash
meet get-space <space_name>
```
`space_name` in `spaces/XYZ` format.

---

## `patch-space`
Modifies the access configuration of a room.
```bash
meet patch-space <space_name> [--access-type OPEN|TRUSTED]
```
- **`space_name`**: Space ID in `spaces/XYZ` format. This can be obtained automatically when creating a Calendar event with `--create-meet`.
- **`--access-type`**: `OPEN` (anyone with the link can enter) or `TRUSTED` (only invited users/organization).

Returns: `{status: "patched", name, config}`.

---

## `end-conference`
Ends the active conference in a room (disconnects all participants).
```bash
meet end-conference <space_name>
```

---

## 💡 Recipe: Open Meeting with Calendar

To create a calendar event where anyone can join without needing to be admitted:

1. **Create space**: `meet create-space` $\rightarrow$ save the `name` (`spaces/XYZ`) and the `meetingUri`.
2. **Open access**: `meet patch-space <name> --access-type OPEN`.
3. **Link to Calendar**: `calendar create --summary "..." --start "..." --end "..." --description "Open link: <meetingUri>"`.
