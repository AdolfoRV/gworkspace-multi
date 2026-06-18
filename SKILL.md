---
name: gworkspace-multi
description: Gmail, Calendar, Drive, Docs, Sheets, Tasks, Meet, Apps Script, Contacts — gestión de múltiples cuentas Google con soporte nativo de perfiles.
version: 1.0.0
author: AdolfoRV
required_environment_variables:
  - name: HERMES_HOME
    prompt: "Directorio de configuración de Hermes"
    help: "Ruta base donde Hermes almacena configs y skills. Por defecto: ~/.hermes"
    required_for: "ubicación del archivo gworkspace-multi.json"
required_credential_files:
  - path: gworkspace-multi.json
    description: "Config unificada de la skill: client_secret, profiles, pending OAuth sessions (Permisos 0600)"
  - path: client_secret.json
    description: "Google OAuth2 client credentials (Permisos 0600)"
metadata:
  hermes:
    tags: [productivity, google, workspace, gmail, calendar, drive, docs, sheets, oauth, multi-account]
    related_skills: []
    requires_toolsets: []
    requires_tools: []
    fallback_for_toolsets: []
    fallback_for_tools: []
    config:
      - key: gworkspace-multi.default_profile
        description: "Perfil de Google por defecto cuando no se especifica --profile"
        default: ""
        prompt: "Nombre del perfil Google por defecto (ej. personal, work, universidad)"
---

# GWorkspace Multi-Account

Skill para operar múltiples cuentas de Google de forma aislada y segura.

## 🛠️ Componentes

| Archivo | Rol |
|---|---|
| `scripts/google_api.py` | Cliente principal — dispatcher a todos los servicios |
| `scripts/setup.py` | Setup OAuth por perfil, revocación, verificación de estado |
| `~/.hermes/gworkspace-multi.json` | Config unificada: `client_secret`, `profiles`, `pending` |
| `~/.hermes/client_secret.json` | Credenciales globales del proyecto Google Cloud (estándar Hermes) |

## 🚀 Sintaxis general

```bash
SCRIPT="python3 ${HERMES_SKILL_DIR}/scripts/google_api.py"
$SCRIPT --profile <perfil> <servicio> <comando> [opciones]
```

> **Nota sobre `${HERMES_SKILL_DIR}`:** Este token se sustituye automáticamente por la ruta absoluta del directorio de esta skill al cargarse. No requiere configuración manual.

Todos los comandos devuelven **JSON por stdout**. Los errores tienen forma `{"status": "error", "error": "..."}`.

---

## 📦 Sub-skills — cargar según necesidad

Antes de usar un servicio o configurar un perfil, carga la referencia correspondiente con `skill_view`.

| Sub-skill | Cuándo cargarla |
|---|---|
| `references/setup.md` | Autorizar un perfil nuevo, revocar token, instalar dependencias, verificar estado OAuth |
| `references/gmail.md` | Buscar, leer, enviar, responder, etiquetar, borradores, programar correos |
| `references/calendar.md` | Listar, crear, editar o eliminar eventos; listar calendarios |
| `references/drive.md` | Buscar, subir, descargar, compartir, eliminar archivos; consultar actividad |
| `references/docs.md` | Leer, crear o añadir contenido a Google Docs |
| `references/sheets.md` | Leer, escribir o añadir filas en Google Sheets |
| `references/tasks.md` | Gestionar listas y tareas (crear, completar, eliminar) |
| `references/meet.md` | Crear y gestionar salas de Google Meet independientes |
| `references/scripts.md` | Ejecutar o inspeccionar proyectos de Apps Script |
| `references/contacts.md` | Listar contactos, buscar por nombre/email, gestionar grupos — incluye verificación de identidad |

---

## ⚠️ Pitfalls y Soluciones

1. **Identificadores de Meet**: Al crear reuniones vía Calendar (`--create-meet`), la API devuelve un `conferenceId` (el código público del link). Para modificar la sala (ej. abrir acceso o activar moderación) vía la API de Meet, se requiere el `space_id` (formato `spaces/XYZ`). La skill ya resuelve esto automáticamente y retorna `space_id` en el resultado de `calendar create`.
2. **Moderación**: Para activar el "Host Management", utiliza `meet patch-space <space_id> --moderation ON`.
3. **Sincronización de Perfiles**: Siempre verifica la cuenta activa con `contacts list --max 1` antes de acciones destructivas para evitar errores de perfil.

---

## 🔐 Seguridad y credenciales

- El archivo `gworkspace-multi.json` almacena tokens OAuth2 refrescables. Se crea con permisos `0o600` (solo lectura/escritura para el owner).
- Los tokens se refrescan automáticamente cuando expiran.

## ⚠️ Pitfalls y Seguridad

- **Permisos de Archivos**: Los archivos `gworkspace-multi.json` y `client_secret.json` DEBEN tener permisos `0600` (`chmod 600`) para evitar fugas de credenciales.
- **Sincronización de Identidad**: No asumir que el perfil es correcto sin verificar: `python3 ... google_api.py --profile <perfil> contacts list --max 1`.
- **Meet ID vs Code**: No utilizar el código público de la reunión (ej. `abc-defg-hij`) para modificar permisos mediante la API de Meet. Se debe utilizar el `space_id` (formato `spaces/XYZ`) que la función `calendar create` devuelve ahora automáticamente.
- **Envío Programado de Gmail**: La API de Gmail no soporta el envío programado nativo. La skill implementa un flujo de **Borrador $\rightarrow$ Comando `at`**. El comando `at_command` devuelto por `gmail schedule` debe ejecutarse en la terminal para programar la entrega real.
- **Gestión de Moderación**: Para activar el Host Management en una sala, usar `meet patch-space <space_id> --moderation ON`.
