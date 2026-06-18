# references/docs.md — Google Docs

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> docs <comando> [opciones]
```

---

## `get`
Obtiene el texto plano de un Google Doc.
```bash
docs get <doc_id>
```
Devuelve: `{documentId, title, text, revisionId}`.

---

## `create`
Crea un Google Doc nuevo, opcionalmente con contenido inicial.
```bash
docs create --title <str> [--body <texto>]
```
Devuelve: `{status: "created", documentId, title, url}`.

---

## `append`
Agrega texto al final de un documento existente.
```bash
docs append <doc_id> --text <texto>
```
Devuelve: `{status: "appended", documentId, inserted_at, characters}`.
