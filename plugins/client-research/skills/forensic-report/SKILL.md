---
name: forensic-report
description: Genera el reporte forense unificado de un cliente combinando lo que ya encontraron stack-research, vendor-research y competitor-research -- exportado a JSON y PDF, con metadata de verificacion por fuente (URL, fecha de acceso, fecha de publicacion, tipo de fuente). Requiere que los tres skills ya hayan terminado su investigacion para ese cliente. Usar siempre que el usuario pida el "reporte forense", el "reporte completo" o "unificado" de un cliente, pida exportar a PDF o JSON, o pregunte si ya se puede generar el reporte final.
allowed-tools: Read, Write, Bash
---

# Forensic Report

Combina lo que `stack-research`, `vendor-research` y `competitor-research` ya
investigaron para un cliente en un solo reporte forense: `report.json`
(datos completos, machine-readable) y `report.pdf` (version legible).

Es el cuarto skill de `client-research` y el **unico** que declara `Bash` --
los otros tres (`stack-research`, `vendor-research`, `competitor-research`)
no necesitan ni piden ejecucion de codigo, y este cambio no les agrega
ninguna capacidad nueva. Ver `../../schemas/report.schema.json` para el
esquema formal de `report.json`.

## Cuando usar este skill

- "Dame el reporte forense de Acme Corp"
- "Genera el PDF/JSON de la investigacion de Acme"
- "Ya podemos armar el reporte completo de Acme?"

## Precondicion: los tres skills deben estar completos

Este skill **no** despacha busquedas nuevas -- solo lee lo que los otros tres
ya dejaron en disco. Antes de generar nada:

1. Calcular `slug` del cliente.
2. Leer `.client-research/<slug>/stack-research/checklist.json`,
   `.../vendor-research/checklist.json` y `.../competitor-research/checklist.json`.
3. Si falta alguno de los tres archivos, o alguno tiene items en `pending`/
   `in_progress` (no todos en estado terminal), **no generar el reporte**:
   decirle al usuario explicitamente cuales skills todavia faltan o estan a
   medio terminar para ese cliente, y sugerir correrlos primero. Esto es una
   condicion dura, no una advertencia — decision explicita registrada en
   `.agents/kt/plans/client-research-reporting.md`.
4. Si alguno de los tres archivos no tiene `schema_version`, es un checklist
   legacy — no lo migres desde aca; decile al usuario que corra ese skill de
   nuevo primero (correrlo dispara su propia migracion, ver
   `../../references/checklist-pattern.md`).

## Flujo

### 1. Armar `report.json`

Con los tres checklists confirmados completos, construir el objeto segun
`../../schemas/report.schema.json`:

- `schema_version: 1`, `client`, `slug`, `generated_at` (timestamp actual).
- `sources.stack_research` / `sources.vendor_research` /
  `sources.competitor_research`: el contenido completo de cada checklist.json,
  tal cual (no reescribir ni resumir).
- `cross_references`: recorrer los `aggregate`/`aggregate_stack` de los tres
  y detectar nombres que aparecen en mas de uno (ej. una herramienta que sale
  como `stack_signal` en stack-research Y como proveedor en vendor-research).
  Cada coincidencia es un objeto `{name, appears_in: [...], detail}`
  explicando la coincidencia en una frase.
- `verification_summary`: contar el total de `source_urls`/`posting_urls` de
  los tres checklists juntos (`total_sources`), y cuantos hay de cada
  `source_type` (`source_types_breakdown`).

Escribir esto en `.client-research/<slug>/report.json`.

### 2. Generar el PDF

Invocar el script bundleado con el Bash tool:

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/forensic-report/scripts/generate_pdf.py" \
  .client-research/<slug>/report.json \
  .client-research/<slug>/report.pdf
```

El script usa solo la libreria estandar de Python (nada que instalar) y
escapa internamente cualquier texto de terceros (findings, nombres, URLs)
antes de incrustarlo en el PDF -- esa sanitizacion no es opcional ni algo que
este skill deba repetir, ya esta resuelta en `generate_pdf.py`. Si el
comando falla (ej. Python no disponible), reportarlo claro al usuario en vez
de dar el reporte por generado.

### 3. Confirmar al usuario

Responder con la ruta de ambos archivos generados
(`.client-research/<slug>/report.json`, `.client-research/<slug>/report.pdf`)
y un resumen breve: cuantas fuentes se verificaron en total, y si hubo
referencias cruzadas entre los tres skills.

## Reglas de acceso

Este skill no hace busquedas nuevas -- solo lee estado ya generado por los
otros tres y ejecuta el script de PDF localmente. Las reglas de acceso de
`../../references/checklist-pattern.md` (sin login, sin bypass de
paywalls/CAPTCHAs) siguen aplicando a como stack-research/vendor-research/
competitor-research obtuvieron esos datos, no a este skill.
