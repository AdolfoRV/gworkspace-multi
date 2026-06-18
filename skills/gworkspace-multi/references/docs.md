# references/docs.md — Google Docs

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <profile> docs <command> [options]
```

---

## `get`
Retrieves the plain text of a Google Doc.
```bash
docs get <doc_id>
```
Returns: `{documentId, title, text, revisionId}`.

---

## `create`
Creates a new Google Doc, optionally with initial content.
```bash
docs create --title <str> [--body <text>]
```
Returns: `{status: "created", documentId, title, url}`.

---

## `append`
Adds text to the end of an existing document.
```bash
docs append <doc_id> --text <text>
```
Returns: `{status: "appended", documentId, inserted_at, characters}`.
