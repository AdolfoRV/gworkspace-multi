# references/setup.md — Autorización OAuth y gestión de perfiles

Script: `python3 ${HERMES_SKILL_DIR}/scripts/setup.py`

---

## Flujo completo de autorización

### 1. Instalar dependencias (una sola vez)
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --install-deps
```

### 2. Registrar client secret del proyecto GCP
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --client-secret /ruta/google_client_secret.json
```
El archivo debe contener la clave `installed` o `web` en la raíz.
Se guarda en `~/.hermes/gworkspace-multi.json` bajo `client_secret`.

> 💡 Para no dejar el archivo en disco, créalo en `/tmp/` y pásalo desde ahí.

> ⚠️ **Múltiples proyectos GCP:** el sistema almacena un único client secret global. Si usas distintos Client IDs para distintos perfiles, completa el flujo completo de un perfil (`--auth-url` → `--auth-code`) antes de cambiar el secret para el siguiente.

### 3. Generar URL de autorización
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --auth-url --profile <perfil> [--services all|email,calendar,...]
```
Devuelve `{"auth_url": "https://accounts.google.com/o/oauth2/..."}`.

**Servicios disponibles:** `email`, `calendar`, `drive`, `docs`, `sheets`, `tasks`, `meet`, `scripts`, `contacts` (o `all`).

### 4. Autorizar en el navegador
- Abrir en **ventana de incógnito**.
- Añadir `&login_hint=correo@ejemplo.com` al final de la URL para forzar la cuenta correcta.
- Completar el flujo hasta la pantalla de error de redirección — es esperado.
- Copiar la **URL completa** de la barra de direcciones.

> **Nota:** El `redirect_uri` usado es `http://localhost:1`, lo que provoca un error de conexión en el navegador. Esto es intencional: el `code` aparece en la URL de la barra de direcciones y se extrae automáticamente al pasarlo a `--auth-code`.

### 5. Intercambiar el código
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --auth-code "URL_COMPLETA_O_SOLO_EL_CODE" --profile <perfil>
```
El token se guarda en `profiles.<perfil>` dentro de `~/.hermes/gworkspace-multi.json`.

### 6. Verificar
```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --check --profile <perfil>
# Confirmar con una llamada real:
python3 ${HERMES_SKILL_DIR}/scripts/google_api.py --profile <perfil> contacts list --max 1
```

---

## Comandos de gestión

```bash
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --list-profiles                    # listar perfiles autorizados
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --check [--profile <p>]            # verificar estado del token
python3 ${HERMES_SKILL_DIR}/scripts/setup.py --revoke --profile <p>             # revocar y eliminar token
```

---

## 🚩 Pitfalls comunes

| Error | Causa | Solución |
|---|---|---|
| `Invalid Code Verifier` | Reutilizar pestaña o código viejo | Cerrar todo, incógnito nueva, generar URL fresca |
| `Token expirado` | Token vencido sin refresh | Re-autorizar con `--auth-url` |
| `No token found for profile` | Perfil no autorizado o nombre incorrecto | `--list-profiles` para ver perfiles existentes |
| Acción aplicada a cuenta incorrecta | Ghosting de perfil | Verificar siempre con `contacts list --max 1` antes |
| `Corrupted config file` | `gworkspace-multi.json` está dañado | Hacer backup, borrar, y reconfigurar desde `--client-secret` |

---

## 🔍 Reporte de diagnóstico

Para fallos persistentes:
1. **Contexto:** qué se intentaba hacer y con qué perfil.
2. **Inventario:** contenido de `~/.hermes/gworkspace-multi.json` (redactar tokens y client_secret).
3. **Traza:** comandos ejecutados en orden y error exacto de cada uno.
