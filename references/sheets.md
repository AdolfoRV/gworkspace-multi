# references/sheets.md — Google Sheets

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> sheets <command> [options]
```

---

## `create`
Creates a new spreadsheet.
```bash
sheets create --title <str> [--sheet-name <sheet_name>]
```
Returns: `{status: "created", spreadsheetId, title, spreadsheetUrl}`.

---

## `get`
Reads values from a range.
```bash
sheets get <sheet_id> <range>
```
| Argument | Description |
|---|---|
| `sheet_id` | Spreadsheet ID |
| `range` | Range in A1 notation, e.g. `Sheet1!A1:C10` or `A:Z` |

Returns: list of lists with the range values.

---

## `update`
Writes values to a range (overwrites).
```bash
sheets update <sheet_id> <range> --values '<JSON>'
```
`--values` is a JSON list of lists, e.g. `'[["a","b"],["c","d"]]'`.

Returns: `{status: "updated", updatedRange, updatedRows, updatedCells}`.

---

## `append`
Adds rows to the end of the specified range (inserts below existing data).
```bash
sheets append <sheet_id> <range> --values '<JSON>'
```
Same format as `update`.

Returns: `{status: "appended", updatedRange, updatedRows}`.
