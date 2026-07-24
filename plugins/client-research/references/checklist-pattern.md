# Patron de checklist persistente

Mecanismo compartido por los tres skills de este plugin (`stack-research`,
`vendor-research`, `competitor-research`). Cada `SKILL.md` referencia este
documento en vez de repetir la explicacion.

## Donde vive el estado

Todo el progreso vive en el proyecto del usuario, no en el plugin:

```text
.client-research/<slug-del-cliente>/<skill-id>/checklist.json
.client-research/<slug-del-cliente>/<skill-id>/report.md
```

- `slug-del-cliente`: nombre del cliente en kebab-case (minusculas, sin
  acentos, espacios -> guiones).
- `skill-id`: uno de `stack-research`, `vendor-research`, `competitor-research`.
  Cada skill tiene su propio checklist y su propio `report.md` — nunca se
  comparte o se mezcla el estado entre skills.

Este archivo es la fuente de verdad del progreso. Escribilo despues de
**cada** cambio de estado (no solo al final) para que una interrupcion a
mitad de camino no pierda el trabajo ya hecho.

## Forma del checklist

Un objeto por cliente+skill con una lista de items (uno por portal, fuente,
o entidad a investigar segun el skill) mas un agregado final. El esquema
completo (formal, machine-checkable) vive en `../schemas/envelope.schema.json`
-- esto es un resumen, no la fuente de verdad:

```json
{
  "schema_version": 1,
  "skill": "",
  "client": "",
  "slug": "",
  "created_at": "",
  "updated_at": "",
  "items": [
    {
      "id": "",
      "label": "",
      "status": "pending",
      "findings": [],
      "source_urls": [],
      "checked_at": null,
      "error": null
    }
  ],
  "aggregate": {}
}
```

`items` varia segun el skill: en `stack-research` es un portal de empleo de
`config/jobs.json` (con su propia forma `boards`/`stack_signals`/
`aggregate_stack`, ver `skills/stack-research/assets/checklist.template.json`
-- esa divergencia es intencional, no se unifico con el resto); en
`vendor-research` es una fuente/tipo de evidencia encontrada durante el
descubrimiento; en `competitor-research` es un competidor/partner de
`config/competitors.json`. Los tres comparten el sobre (`schema_version`,
`skill`, `client`, `slug`, `created_at`, `updated_at`) y la forma de
`source_urls`/`posting_urls` (ver abajo).

## `schema_version` y migracion

`schema_version` (hoy `1`) es lo que distingue un checklist ya migrado de uno
viejo. Cada skill, al arrancar, revisa el checklist en disco: si no tiene
`schema_version`, es un archivo legacy (de antes de este esquema) y hay que
**migrarlo en el momento, sobreescribiendo el archivo original** (sin backup
-- decision explicita, ver `.agents/kt/plans/client-research-reporting.md`)
antes de seguir. Migrar significa: envolver el contenido existente con el
sobre nuevo (`schema_version: 1`, agregar `skill` si falta), y convertir
cualquier `source_urls`/`posting_urls` de string suelto a la forma de objeto
de abajo -- las entradas migradas quedan con `source_type`/`access_date`/
`publish_date` en `null` porque ese dato nunca se capturo antes y no se puede
reconstruir; solo las entradas nuevas que se escriban de aca en adelante
llevan metadata real. Los items en `pending`/`in_progress` de un archivo
migrado siguen igual (el enum de `status` no cambia), asi que una corrida a
medias se retoma normal despues de migrar.

## `source_urls` / `posting_urls`: forma y `source_type`

Cada entrada de fuente es un objeto, no un string suelto:

```json
{
  "url": "",
  "source_type": "client-site",
  "access_date": "2026-07-23",
  "publish_date": null
}
```

`source_type` es un set fijo, compartido por los cuatro skills del plugin
(ver `../schemas/envelope.schema.json`):

| Valor | Skill que lo usa |
| --- | --- |
| `job-board` | `stack-research` (portales de empleo) |
| `client-site` | `vendor-research`, `competitor-research` (sitio del cliente/competidor) |
| `press` | `vendor-research`, `competitor-research` (prensa/comunicados) |
| `social` | `vendor-research`, `competitor-research` (LinkedIn/redes) |
| `directory` | `vendor-research`, `competitor-research` (directorios/procurement) |

## Fixtures

`../schemas/fixtures/` tiene un ejemplo poblado (datos sinteticos, nunca de
un cliente real) por cada skill mas uno del reporte unificado de
`forensic-report` -- sirven como referencia de la forma completa y como
fixtures si en el futuro se agrega un validador (hoy no hay ninguno
conectado a CI).

## Flujo

### 1. Preparar el checklist

Calcular `slug` del cliente y `checklist_path =
.client-research/<slug>/<skill-id>/checklist.json`. Si ya existe y no se pidio
refresh, cargarlo — los items en `done` se saltan; los que estan en `pending`,
`in_progress` (una corrida anterior quedo a medias) o `failed` se reintentan.
Si no existe, instanciar los items iniciales segun la logica de ese skill y
escribir el checklist inicial.

### 2. Despachar cada item en background

Por cada item pendiente: marcarlo `in_progress` y guardar el checklist
inmediatamente, despues lanzar un sub-agente (Agent tool, `run_in_background:
true`) con un prompt autocontenido — el sub-agente no ve la conversacion, asi
que hay que darle todo el contexto necesario (cliente, que buscar, donde
buscar, que evidencia cuenta). Se pueden lanzar varios items en paralelo sin
esperar a que termine uno para lanzar el siguiente.

### 3. Actualizar el checklist a medida que vuelven los resultados

Cuando cada sub-agente en background termina: si devolvio resultados, marcar
`done` y completar `findings`/`source_urls`/`checked_at`. Si fallo o no
encontro nada accesible, marcar `failed` (o `done` con `findings: []` si
genuinamente no hay nada que encontrar) y anotar `error`. Guardar el
checklist despues de cada actualizacion. Si el usuario pregunta el estado
mientras tanto, leer el checklist actual y responder sin esperar a que
termine todo.

### 4. Agregar y reportar

Cuando todos los items quedan en un estado terminal (`done`, `failed` o
`skipped`): unificar `findings` deduplicando (case-insensitive) y contando en
cuantas fuentes/items distintos aparece cada hallazgo (esa es la señal de
confianza). Escribir el resultado en `aggregate`, generar
`.client-research/<slug>/<skill-id>/report.md` con el detalle por item (con
links fuente) y el resumen agregado ordenado por confianza, y responder al
usuario en el chat con el resumen y la ruta del reporte.

## Reglas de acceso (aplica a los tres skills)

- Solo usar informacion publicamente accesible: resultados de busqueda y
  paginas que cargan sin login.
- Nunca intentar iniciar sesion, sortear paywalls/CAPTCHAs, ni scrapear a
  volumen — esto es research puntual por cliente, no recoleccion masiva.
- Si una fuente exige login para ver el detalle, quedarse con lo que exponga
  la busqueda (snippets, cache del buscador) y marcarla igual como fuente,
  sin forzar el acceso.
