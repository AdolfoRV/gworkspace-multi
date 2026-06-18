# references/meet.md — Google Meet

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> meet <comando> [opciones]
```

> Para salas asociadas a un evento de Calendar, usar `calendar create --create-meet` en su lugar.

---

## `create-space`
Crea una sala de Meet persistente (independiente de Calendar).
```bash
meet create-space
```
Devuelve: `{status: "created", name, meetingUri, meetingCode}`.

El `name` tiene forma `spaces/XYZ` — guardarlo para comandos posteriores.

---

## `get-space`
Obtiene información de una sala.
```bash
meet get-space <space_name>
```
`space_name` en formato `spaces/XYZ`.

---

## `patch-space`
Modifica la configuración de acceso de una sala.
```bash
meet patch-space <space_name> [--access-type OPEN|TRUSTED]
```
- **`space_name`**: ID del espacio en formato `spaces/XYZ`. Se puede obtener automáticamente al crear un evento en Calendar con `--create-meet`.
- **`--access-type`**: `OPEN` (cualquiera con el link entra) o `TRUSTED` (solo invitados/org).

Devuelve: `{status: "patched", name, config}`.

---

## `end-conference`
Finaliza la conferencia activa en una sala (desconecta a todos los participantes).
```bash
meet end-conference <space_name>
```


---

## 💡 Receta: Reunión Abierta con Calendar

Para crear un evento de calendario donde cualquier persona pueda entrar sin ser admitida:

1. **Crear espacio**: `meet create-space` $\rightarrow$ guarda el `name` (`spaces/XYZ`) y la `meetingUri`.
2. **Abrir acceso**: `meet patch-space <name> --access-type OPEN`.
3. **Vincular a Calendar**: `calendar create --summary "..." --start "..." --end "..." --description "Link abierto: <meetingUri>"`.
