# references/contacts.md — Contacts (People API)

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> contacts <comando> [opciones]
```

> **Uso principal de verificación de identidad:** antes de cualquier acción destructiva o envío, ejecutar `contacts list --max 1` y confirmar que el email devuelto corresponde al perfil.

---

## `list`
Lista contactos de la cuenta.
```bash
contacts list [--max N]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--max` | int | 20 | Máximo de contactos |

Devuelve: lista de `{name, emails: [...], phones: [...]}`.

---

## `search`
Busca contactos por nombre o email. Más eficiente que `list` para agendas grandes.
```bash
contacts search <query>
```
| Argumento | Tipo | Descripción |
|---|---|---|
| `query` | str (posicional) | Nombre o email a buscar (parcial funciona) |

Devuelve: lista de `{name, emails: [...], phones: [...]}`.

> Preferir `search` sobre `list` cuando se busca a una persona específica.

---

## `list-groups`
Lista todos los grupos/labels de contactos de la cuenta.
```bash
contacts list-groups
```
Devuelve: lista de `{id, name, memberCount, type}`.

- `id` tiene forma `contactGroups/abc123`.
- `type: USER_CONTACT_GROUP` — grupos creados por el usuario.
- `type: SYSTEM_CONTACT_GROUP` — grupos del sistema (ej. "Starred", "All contacts").

---

## `list-group`
Devuelve los miembros de un grupo con sus emails.
```bash
contacts list-group <group_id>
```
| Argumento | Tipo | Descripción |
|---|---|---|
| `group_id` | str (posicional) | ID del grupo, ej. `contactGroups/abc123` |

Devuelve: lista de `{name, emails: [...]}`.

> **Flujo típico para invitar un grupo a Calendar:**
> ```bash
> # 1. Encontrar el ID del grupo
> contacts list-groups
> # 2. Obtener emails del grupo
> contacts list-group "contactGroups/abc123"
> # 3. Pasar los emails a calendar create
> calendar create --summary "Reunión" --start "..." --end "..." \
>   --attendees "juan@gmail.com,maria@gmail.com"
> ```
