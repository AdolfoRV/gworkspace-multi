# references/tasks.md — Google Tasks

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> tasks <comando> [opciones]
```

---

## `list-lists`
Lista las listas de tareas disponibles en la cuenta.
```bash
tasks list-lists
```
Devuelve: lista de `{id, title, updated}`. Usar los IDs en los demás comandos.

---

## `list`
Lista tareas de una lista.
```bash
tasks list [--tasklist ID] [--show-completed] [--max N]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--tasklist` | str | `@default` | ID de la lista (obtener con `list-lists`) |
| `--show-completed` | flag | false | Incluir tareas completadas |
| `--max` | int | 50 | Máximo de resultados |

> ⚠️ Usar siempre `--tasklist <id>` como flag, nunca como argumento posicional.

---

## `create`
Crea una tarea nueva.
```bash
tasks create --title <str> [--notes <str>] [--due <ISO8601>] [--tasklist ID]
```
La fecha `--due` debe ser RFC 3339, ej. `2026-06-20T00:00:00Z`.

Devuelve: `{status: "created", id, title, due, task_status}`.

---

## `complete`
Marca una tarea como completada.
```bash
tasks complete <task_id> [--tasklist ID]
```
Devuelve: `{status: "completed", id, title}`.

---

## `delete`
Elimina una tarea permanentemente.
```bash
tasks delete <task_id> [--tasklist ID]
```
Devuelve: `{status: "deleted", taskId}`.
