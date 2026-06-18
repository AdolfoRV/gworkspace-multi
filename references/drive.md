# references/drive.md — Google Drive

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> drive <comando> [opciones]
```

---

## `search`
Busca archivos. Por defecto usa búsqueda de texto completo.
```bash
drive search <query> [--max N] [--raw-query]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `query` | str (posicional) | requerido | Texto a buscar |
| `--max` | int | 10 | Máximo de resultados |
| `--raw-query` | flag | false | Usar `query` como query Drive API cruda (ej. `mimeType='application/pdf'`) |

Devuelve: lista de `{id, name, mimeType, modifiedTime, webViewLink, size}`.

> Para encontrar Apps Scripts: `drive search "mimeType='application/vnd.google-apps.script'" --raw-query`

---

## `get`
Obtiene metadatos de un archivo.
```bash
drive get <file_id>
```
Devuelve: `{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`.

---

## `upload`
Sube un archivo local a Drive.
```bash
drive upload <local_path> [--name <nombre>] [--parent <folder_id>]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `local_path` | str (posicional) | requerido | Ruta local del archivo |
| `--name` | str | nombre original | Nombre en Drive |
| `--parent` | str | — | ID de carpeta destino |

Devuelve: `{status: "uploaded", id, name, mimeType, webViewLink}`.

---

## `download`
Descarga un archivo. Los Google Docs/Sheets/Slides se exportan automáticamente.
```bash
drive download <file_id> [--output <ruta>] [--export-mime <mime>]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `file_id` | str (posicional) | requerido | ID del archivo |
| `--output` | str | `~/Downloads/<nombre>` | Ruta de salida |
| `--export-mime` | str | — | MIME de exportación (sobreescribe el default) |

**Exportaciones por defecto:**
- Google Doc → PDF
- Google Sheet → CSV
- Google Slides → PDF
- Google Drawing → PNG

Devuelve: `{status: "downloaded", id, name, path, mimeType}`.

---

## `create-folder`
Crea una carpeta en Drive.
```bash
drive create-folder <name> [--parent <folder_id>]
```
Devuelve: `{status: "created", id, name, webViewLink}`.

---

## `share`
Comparte un archivo con un usuario, grupo o dominio.
```bash
drive share <file_id> [--email <addr>] [--role reader|writer|commenter|owner] \
                      [--type user|group|domain|anyone] [--domain <dominio>] [--notify]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `file_id` | str (posicional) | requerido | ID del archivo |
| `--email` | str | — | Email del destinatario (para type=user/group) |
| `--role` | str | `reader` | Nivel de acceso |
| `--type` | str | `user` | Tipo de permiso |
| `--domain` | str | — | Dominio (para type=domain) |
| `--notify` | flag | false | Enviar email de notificación |

Devuelve: `{status: "shared", permissionId, fileId, role, type}`.

---

## `delete`
Mueve a papelera (default) o elimina permanentemente.
```bash
drive delete <file_id> [--permanent]
```
Devuelve: `{status: "trashed"|"deleted", fileId, permanent}`.

---

## `activity`
Consulta la actividad reciente sobre un archivo o carpeta (Drive Activity API).
```bash
drive activity [--item-name items/<file_id>] [--ancestor-name items/<folder_id>] [--max N]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--item-name` | str | — | Actividad sobre un archivo: `items/<file_id>` |
| `--ancestor-name` | str | — | Actividad dentro de una carpeta: `items/<folder_id>` |
| `--max` | int | 10 | Máximo de resultados |
