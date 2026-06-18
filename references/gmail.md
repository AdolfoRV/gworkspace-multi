# references/gmail.md — Gmail

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> gmail <comando> [opciones]
```

---

## `search`
Busca mensajes. Acepta cualquier query de Gmail (`is:unread`, `from:`, `subject:`, etc.).
```bash
gmail search <query> [--max N]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `query` | str (posicional) | requerido | Query de Gmail |
| `--max` | int | 10 | Máximo de resultados |

Devuelve: lista de `{id, threadId, from, to, subject, date, snippet, labels}`.

---

## `get`
Obtiene el contenido completo de un mensaje (cuerpo incluido).
```bash
gmail get <message_id>
```
Devuelve: `{id, threadId, from, to, subject, date, labels, body}`.

---

## `send`
Envía un email nuevo.
```bash
gmail send --to <addr> --subject <str> --body <str> [--from <addr>] [--html] [--reply-to <msg_id>]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--to` | str | requerido | Destinatario |
| `--subject` | str | requerido | Asunto |
| `--body` | str | requerido | Cuerpo del mensaje |
| `--from` | str | — | Remitente explícito (alias de cuenta) |
| `--html` | flag | false | Enviar como HTML (multipart/alternative con fallback plain) |
| `--reply-to` | str | — | Message-ID al que se responde (añade headers In-Reply-To/References) |

Devuelve: `{status: "sent", id, threadId}`.

---

## `reply`
Responde a un mensaje existente, manteniendo el hilo.
```bash
gmail reply <message_id> --body <str> [--from <addr>]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `message_id` | str (posicional) | requerido | ID del mensaje original |
| `--body` | str | requerido | Cuerpo de la respuesta |
| `--from` | str | — | Remitente explícito |

Devuelve: `{status: "sent", id, threadId}`.

---

## `labels`
Lista todos los labels de la cuenta.
```bash
gmail labels
```
Devuelve: lista de `{id, name, type}`.

---

## `modify`
Añade o quita labels a un mensaje.
```bash
gmail modify <message_id> [--add-labels L1 L2] [--remove-labels L1 L2]
```
| Argumento | Tipo | Descripción |
|---|---|---|
| `message_id` | str (posicional) | ID del mensaje |
| `--add-labels` | str… | IDs de labels a añadir |
| `--remove-labels` | str… | IDs de labels a quitar |

**Alias útiles:**
- Archivar: `--remove-labels INBOX`
- Marcar leído: `--remove-labels UNREAD`
- Destacar: `--add-labels STARRED`
- Mover a spam: `--add-labels SPAM --remove-labels INBOX`

---

## `get-attachments`
Descarga todos los adjuntos de un mensaje a disco.
```bash
gmail get-attachments <message_id> [--output <dir>]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `message_id` | str (posicional) | requerido | ID del mensaje |
| `--output` | str | `~/Downloads` | Directorio de destino |

Devuelve: `{status: "saved", messageId, attachments: [{filename, path, size}]}`.
Si el mensaje no tiene adjuntos: `{status: "no_attachments", messageId}`.

---

## `draft-create`
Crea un borrador sin enviarlo.
```bash
gmail draft-create --to <addr> --subject <str> --body <str> [--from <addr>] [--html] [--reply-to-id <msg_id>]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--to` | str | requerido | Destinatario |
| `--subject` | str | requerido | Asunto |
| `--body` | str | requerido | Cuerpo |
| `--from` | str | — | Remitente explícito |
| `--html` | flag | false | Cuerpo en HTML |
| `--reply-to-id` | str | — | ID del mensaje original para reply draft |

Devuelve: `{status: "draft_created", draftId, messageId}`.

## `draft-send`
Envía un borrador existente.
```bash
gmail draft-send <draft_id>
```
Devuelve: `{status: "sent", id, threadId}`.

> **Flujo draft para revisión humana:**
> ```bash
> gmail draft-create --to "foo@bar.com" --subject "Propuesta" --body "..."
> # → {draftId: "r123..."}
> # humano revisa en Gmail, luego:
> gmail draft-send "r123..."
> ```

---

## `schedule`
Programa la creación de un borrador para ser enviado en una fecha futura. 
**Nota:** La API de Gmail no soporta envío programado nativo; esta función crea el borrador y genera un comando para el sistema `at`.

```bash
gmail schedule --to <addr> --subject <str> --body <str> --send-at <ISO8601> [--from <addr>] [--html]
```
| Argumento | Tipo | Default | Descripción |
|---|---|---|---|
| `--to` | str | requerido | Destinatario |
| `--subject` | str | requerido | Asunto |
| `--body` | str | requerido | Cuerpo |
| `--send-at` | ISO8601 | requerido | Fecha/hora de envío (debe incluir TZ, ej. `2026-06-20T15:00:00Z`) |
| `--from` | str | — | Remitente explícito |
| `--html` | flag | false | Enviar como HTML |

Devuelve: `{status: "draft_created", draftId, messageId, send_at, send_at_unix, note, at_command}`.

> **Flujo de envío programado:**
> 1. Ejecutar `gmail schedule ...` $\rightarrow$ obtener `at_command`.
> 2. Ejecutar el `at_command` en la terminal para que el sistema operativo dispare el envío mediante `gmail draft-send` en la fecha indicada.
