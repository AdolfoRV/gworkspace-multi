# references/scripts.md — Google Apps Script

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> scripts <comando> [opciones]
```

> Para encontrar scripts disponibles en Drive:
> ```bash
> $SCRIPT --profile <perfil> drive search "mimeType='application/vnd.google-apps.script'" --raw-query
> ```

---

## `run`
Ejecuta una función de un Apps Script desplegado como API ejecutable.
```bash
scripts run <script_id> --function <nombre> [--params '<JSON_array>']
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `script_id` | str (posicional) | requerido | ID del script |
| `--function` | str | requerido | Nombre de la función a ejecutar |
| `--params` | JSON array | — | Parámetros, ej. `'["arg1", 42]'` |

Devuelve: `{status: "ok", response}` o `{status: "script_error", error}`.

---

## `get-project`
Obtiene metadatos de un proyecto de Apps Script.
```bash
scripts get-project <script_id>
```

---

## `get-content`
Obtiene el código fuente de un proyecto de Apps Script.
```bash
scripts get-content <script_id>
```
