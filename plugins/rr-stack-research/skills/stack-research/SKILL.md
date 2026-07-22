---
name: stack-research
description: Investiga el stack tecnologico de un cliente, prospecto o empresa rastreando sus ofertas de empleo publicadas en portales de trabajo globales y LATAM (LinkedIn Jobs, Indeed, Glassdoor, We Work Remotely, Computrabajo, Bumeran, GetOnBoard, OCC Mundial). Mantiene un checklist de progreso por cliente en disco, despacha la busqueda de cada portal en background con sub-agentes, y se puede retomar en cualquier momento sin repetir trabajo ya hecho. Usar siempre que el usuario pida investigar el stack tecnologico, las tecnologias, herramientas o vacantes de un cliente/empresa, pida un "research de stack", "tech stack research", "que tecnologias usa <empresa>", o pregunte por el estado de una investigacion de stack ya iniciada.
---

# R&R Stack Research

Investiga que tecnologias usa una empresa cliente/prospecto analizando sus
ofertas de empleo publicas en varios portales de trabajo, y arma un reporte de
stack tecnologico con nivel de confianza segun cuantas fuentes independientes
lo corroboran.

El trabajo se organiza como un **checklist persistente por cliente**: cada
portal es un item que pasa por `pending -> in_progress -> done|failed`. El
checklist vive en un archivo JSON dentro del proyecto (no en la conversacion),
asi que una investigacion se puede interrumpir, retomar en otra sesion, o
correr en paralelo en background sin perder progreso.

## Cuando usar este skill

- "Investiga el stack de Acme Corp"
- "Que tecnologias usa <empresa> segun sus vacantes"
- "Segui con el research de stack de Acme" / "como va la investigacion de Acme"
- Cualquier pedido de inteligencia de prospeccion sobre el stack tecnico de un
  cliente a partir de ofertas de empleo publicas

## Entradas necesarias

Antes de arrancar, confirma (o infiere del mensaje del usuario):

1. **Cliente**: nombre de la empresa a investigar (obligatorio).
2. **Foco** (opcional): roles/areas especificas (ej. "backend", "data",
   "devops") para afinar la busqueda dentro de cada portal.
3. **Paises** (opcional): relevante sobre todo para portales LATAM que tienen
   un dominio por pais (Computrabajo, Bumeran). Si no se especifica, usar el
   dominio regional generico o el que aparezca en los resultados de busqueda.
4. **Refresh**: si el usuario pide "actualizar" o "repetir" la investigacion,
   reintentar tambien los portales en estado `done` (por defecto se saltan).

## Archivos del skill

- `${CLAUDE_PLUGIN_ROOT}/config/jobs.json` - lista de portales habilitados,
  con la plantilla de busqueda y notas de acceso de cada uno, mas una lista de
  arranque de palabras clave de stack (`stack_signal_keywords`).
- `assets/checklist.template.json` - forma del checklist que se instancia por
  cliente (no editar el template; copiarlo).

## Estado en disco (el "background" del checklist)

Todo el progreso vive en el proyecto del usuario, no en el plugin:

```text
.rr-stack-research/<slug-del-cliente>/checklist.json
.rr-stack-research/<slug-del-cliente>/report.md
```

`slug-del-cliente` es el nombre del cliente en kebab-case (minusculas, sin
acentos, espacios -> guiones). El checklist sigue la forma de
`assets/checklist.template.json`: un objeto por cliente con un array `boards`
(uno por portal de `jobs.json`) y un `aggregate_stack` final.

Este archivo es la fuente de verdad del progreso. Escribilo despues de **cada**
cambio de estado (no solo al final) para que una interrupcion a mitad de
camino no pierda el trabajo ya hecho.

## Flujo

### 1. Preparar el checklist

- Calcular `slug` del cliente y `checklist_path =
  .rr-stack-research/<slug>/checklist.json`.
- Si el archivo ya existe y no se pidio refresh: cargarlo. Los portales en
  `done` se saltan; los que estan en `pending`, `in_progress` (una corrida
  anterior quedo a medias) o `failed` se vuelven a intentar.
- Si no existe: leer `jobs.json`, instanciar un item de `boards` por cada
  portal con `enabled: true`, todos en `pending`, y escribir el checklist
  inicial (con `client`, `slug`, `created_at`, `focus`).

### 2. Despachar la busqueda de cada portal en background

Por cada portal pendiente:

1. Marcar ese item como `in_progress` y guardar el checklist inmediatamente.
2. Lanzar un sub-agente (Agent tool, `run_in_background: true`) con un prompt
   autocontenido -- el sub-agente no ve esta conversacion, asi que dale todo
   el contexto necesario: nombre del cliente, foco/roles si aplica, el
   `search_query_template` y `base_url` de ese portal, y las
   `stack_signal_keywords` de referencia. Instruirlo para que:
   - Use WebSearch primero con el query armado a partir de
     `search_query_template` (reemplazando `{client}`).
   - Haga WebFetch solo sobre URLs concretas que ya aparecieron en los
     resultados (paginas de detalle de la vacante), nunca intente iniciar
     sesion ni sortear paywalls/CAPTCHAs.
   - Extraiga tecnologias mencionadas explicitamente en la publicacion
     (secciones tipo "Requisitos", "Stack", "Nice to have", "Responsibilities")
     -- no limitarse a `stack_signal_keywords`, registrar cualquier
     lenguaje/framework/nube/herramienta nombrada.
   - Devuelva un resumen breve y estructurado: cantidad de publicaciones
     encontradas, lista de tecnologias detectadas, hasta 3 URLs fuente.
3. Podes lanzar varios portales en paralelo (varios `agent()`/Agent calls
   seguidos); no hace falta esperar a que termine uno para lanzar el
   siguiente.

### 3. Actualizar el checklist a medida que vuelven los resultados

Cuando cada sub-agente en background termina y llega su notificacion:

- Si devolvio resultados: marcar `done`, completar `postings_found`,
  `stack_signals`, `posting_urls`, `checked_at` (timestamp actual).
- Si fallo o no encontro nada accesible (login wall, sin resultados): marcar
  `failed` (o `done` con `postings_found: 0` si genuinamente no hay vacantes
  publicadas) y anotar `error` con una razon breve.
- Guardar el checklist despues de cada actualizacion.

Si el usuario pregunta por el estado mientras tanto ("como va"), leer el
checklist actual y responder con una tabla portal -> estado, sin esperar a que
termine todo.

### 4. Agregar y reportar

Cuando todos los portales quedan en un estado terminal (`done`, `failed` o
`skipped`):

1. Unificar `stack_signals` de todos los portales `done`, deduplicando
   (case-insensitive) y contando en cuantos portales distintos aparece cada
   tecnologia -- eso es la señal de confianza (una tecnologia que aparece en 3
   portales distintos es mas confiable que una que aparece en 1 solo posting).
2. Escribir el resultado en `aggregate_stack` del checklist, agrupado como en
   el template (`languages`, `frameworks`, `cloud_infra`, `data`, `other`).
3. Generar `.rr-stack-research/<slug>/report.md` con: nombre del cliente y
   fecha, tabla de hallazgos por portal (con links fuente), y el resumen de
   stack agregado ordenado por confianza (# de portales que lo corroboran).
4. Responder al usuario en el chat con el resumen y la ruta del reporte
   guardado.

## Reglas de acceso (importante)

- Solo usar informacion publicamente accesible: resultados de busqueda y
  paginas de detalle de vacantes que cargan sin login.
- Nunca intentar iniciar sesion, sortear paywalls/CAPTCHAs, ni scrapear a
  volumen -- esto es research puntual por cliente, no recoleccion masiva.
- Si un portal exige login para ver el detalle (ver `access.requires_login`
  en `jobs.json`), quedarse con lo que exponga la busqueda (snippets,
  cache del buscador) y marcarlo igual como fuente, sin forzar el acceso.

## Mantenimiento de `jobs.json`

Agregar o desactivar portales editando `config/jobs.json` (campo `enabled`).
Cada entrada nueva necesita `id`, `name`, `region`, `base_url`,
`search_query_template` (con `{client}`) y notas de `access`. No hace falta
tocar este SKILL.md al agregar portales.
