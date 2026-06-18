# references/calendar.md — Google Calendar

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> calendar <comando> [opciones]
```

---

## `list`
Lista eventos próximos de un calendario.
```bash
calendar list [--start ISO8601] [--end ISO8601] [--calendar-id ID] [--max N]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--start` | ISO8601 | ahora | Inicio del rango |
| `--end` | ISO8601 | — | Fin del rango (opcional) |
| `--calendar-id` | str | `primary` | ID del calendario |
| `--max` | int | 50 | Máximo de resultados |

Devuelve: lista de `{id, summary, start, end, location, description, htmlLink, attendees}`.

---

## `list-calendars`
Lista todos los calendarios de la cuenta.
```bash
calendar list-calendars
```
Devuelve: lista de `{id, summary, primary}`.

---

## `create`
Crea un evento nuevo, opcionalmente con sala de Meet.
```bash
calendar create --summary <str> --start <ISO8601> --end <ISO8601> \
                [--location <str>] [--description <str>] \
                [--attendees email1,email2] [--calendar-id ID] [--create-meet]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--summary` | str | requerido | Título del evento |
| `--start` | ISO8601 | requerido | Inicio (ej. `2026-06-16T10:00:00Z`) |
| `--end` | ISO8601 | requerido | Fin |
| `--location` | str | — | Ubicación |
| `--description` | str | — | Descripción |
| `--attendees` | str | — | Emails separados por coma |
| `--calendar-id` | str | `primary` | ID del calendario |
| `--create-meet` | flag | false | Genera sala de Google Meet en el evento |

Devuelve: `{status: "created", id, summary, htmlLink, conferenceData, space_id?}`.

> **Nota:** `space_id` (formato `spaces/XYZ`) se devuelve únicamente cuando `--create-meet` es verdadero. Es el identificador necesario para modificar la configuración de la sala usando la sub-skill de Meet (ej. cambiar acceso a `OPEN`).

---

## `update`
Edita un evento existente. Solo se modifican los campos que se pasen — el resto se preserva.
```bash
calendar update <event_id> [--summary <str>] [--start <ISO8601>] [--end <ISO8601>] \
                            [--location <str>] [--description <str>] \
                            [--attendees email1,email2] [--calendar-id ID]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `event_id` | str (posicional) | requerido | ID del evento |
| `--summary` | str | — | Nuevo título |
| `--start` | ISO8601 | — | Nueva hora de inicio |
| `--end` | ISO8601 | — | Nueva hora de fin |
| `--location` | str | — | Nueva ubicación (pasar `""` para borrar) |
| `--description` | str | — | Nueva descripción (pasar `""` para borrar) |
| `--attendees` | str | — | Lista completa de asistentes (reemplaza la existente) |
| `--calendar-id` | str | `primary` | ID del calendario |

Devuelve: `{status: "updated", id, summary, start, end, htmlLink}`.

> `sendUpdates: "none"` está hardcodeado — nunca se notifica a los asistentes.

---

## `delete`
Elimina un evento.
```bash
calendar delete <event_id> [--calendar-id ID]
```
Devuelve: `{status: "deleted", eventId}`.
