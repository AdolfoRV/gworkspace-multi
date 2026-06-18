# references/drive.md — Google Drive

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> drive <command> [options]
```

---

## `search`
Searches for files. Uses full-text search by default.
```bash
drive search <query> [--max N] [--raw-query]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `query` | str (positional) | required | Search text |
| `--max` | int | 10 | Maximum results |
| `--raw-query` | flag | false | Use `query` as a raw Drive API query (e.g. `mimeType='application/pdf'`) |

Returns: list of `{id, name, mimeType, modifiedTime, webViewLink, size}`.

> To find Apps Scripts: `drive search "mimeType='application/vnd.google-apps.script'" --raw-query`

---

## `get`
Retrieves metadata for a file.
```bash
drive get <file_id>
```
Returns: `{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`.

---

## `upload`
Uploads a local file to Drive.
```bash
drive upload <local_path> [--name <name>] [--parent <folder_id>]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `local_path` | str (positional) | required | Local file path |
| `--name` | str | original name | Name in Drive |
| `--parent` | str | — | Destination folder ID |

Returns: `{status: "uploaded", id, name, mimeType, webViewLink}`.

---

## `download`
Downloads a file. Google Docs/Sheets/Slides are exported automatically.
```bash
drive download <file_id> [--output <path>] [--export-mime <mime>]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `file_id` | str (positional) | required | File ID |
| `--output` | str | `~/Downloads/<name>` | Output path |
| `--export-mime` | str | — | Export MIME type (overrides default) |

**Default exports:**
- Google Doc $\rightarrow$ PDF
- Google Sheet $\rightarrow$ CSV
- Google Slides $\rightarrow$ PDF
- Google Drawing $\rightarrow$ PNG

Returns: `{status: "downloaded", id, name, path, mimeType}`.

---

## `create-folder`
Creates a folder in Drive.
```bash
drive create-folder <name> [--parent <folder_id>]
```
Returns: `{status: "created", id, name, webViewLink}`.

---

## `share`
Shares a file with a user, group, or domain.
```bash
drive share <file_id> [--email <addr>] [--role reader|writer|commenter|owner] \
                      [--type user|group|domain|anyone] [--domain <domain>] [--notify]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `file_id` | str (positional) | required | File ID |
| `--email` | str | — | Recipient email (for type=user/group) |
| `--role` | str | `reader` | Access level |
| `--type` | str | `user` | Permission type |
| `--domain` | str | — | Domain (for type=domain) |
| `--notify` | flag | false | Send notification email |

Returns: `{status: "shared", permissionId, fileId, role, type}`.

---

## `delete`
Moves to trash (default) or deletes permanently.
```bash
drive delete <file_id> [--permanent]
```
Returns: `{status: "trashed"|"deleted", fileId, permanent}`.

---

## `activity`
Queries recent activity on a file or folder (Drive Activity API).
```bash
drive activity [--item-name items/<file_id>] [--ancestor-name items/<folder_id>] [--max N]
```
| Argument | Type | Default | Description |
|---|---|---|---|
| `--item-name` | str | — | Activity on a file: `items/<file_id>` |
| `--ancestor-name` | str | — | Activity within a folder: `items/<folder_id>` |
| `--max` | int | 10 | Maximum results |
