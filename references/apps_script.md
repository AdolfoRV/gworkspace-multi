# references/scripts.md — Google Apps Script

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> scripts <command> [options]
```

> To find available scripts in Drive:
> ```bash
> $SCRIPT --profile <profile> drive search "mimeType='application/vnd.google-apps.script'" --raw-query
> ```

---

## `run`
Executes a function from an Apps Script deployed as an executable API.
```bash
scripts run <script_id> --function <name> [--params '<JSON_array>']
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `script_id` | str (positional) | required | Script ID |
| `--function` | str | required | Name of the function to execute |
| `--params` | JSON array | — | Parameters, e.g. `'["arg1", 42]'` |

Returns: `{status: "ok", response}` or `{status: "script_error", error}`.

---

## `get-project`
Retrieves metadata for an Apps Script project.
```bash
scripts get-project <script_id>
```

---

## `get-content`
Retrieves the source code of an Apps Script project.
```bash
scripts get-content <script_id>
```
