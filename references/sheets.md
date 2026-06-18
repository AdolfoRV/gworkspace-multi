# references/sheets.md — Google Sheets

```bash
SCRIPT="python3 ~/.hermes/skills/productivity/gworkspace-multi/scripts/google_api.py"
$SCRIPT --profile <perfil> sheets <comando> [opciones]
```

---

## `create`
Crea una hoja de cálculo nueva.
```bash
sheets create --title <str> [--sheet-name <nombre_hoja>]
```
Devuelve: `{status: "created", spreadsheetId, title, spreadsheetUrl}`.

---

## `get`
Lee valores de un rango.
```bash
sheets get <sheet_id> <range>
```
| Argumento | Descripción |
|---|---|
| `sheet_id` | ID del spreadsheet |
| `range` | Rango en notación A1, ej. `Hoja1!A1:C10` o `A:Z` |

Devuelve: lista de listas con los valores del rango.

---

## `update`
Escribe valores en un rango (sobreescribe).
```bash
sheets update <sheet_id> <range> --values '<JSON>'
```
`--values` es un JSON de lista de listas, ej. `'[["a","b"],["c","d"]]'`.

Devuelve: `{status: "updated", updatedRange, updatedRows, updatedCells}`.

---

## `append`
Agrega filas al final del rango especificado (inserta debajo de los datos existentes).
```bash
sheets append <sheet_id> <range> --values '<JSON>'
```
Mismo formato que `update`.

Devuelve: `{status: "appended", updatedRange, updatedRows}`.
