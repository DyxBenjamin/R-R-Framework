---
name: vendor-research
description: Descubre los proveedores actuales de un cliente/prospecto (de cualquier tipo -- agencias, consultoras, software, logistica, no solo tecnologia) buscando evidencia publica de relaciones vigentes con ese cliente. Mantiene un checklist de progreso por cliente en disco, despacha cada busqueda en background, y se puede retomar sin repetir trabajo ya hecho. Usar siempre que el usuario pida investigar los proveedores, partners o agencias con las que trabaja un cliente/empresa, pida un "research de proveedores", "vendor research", "con quien trabaja <empresa>", o pregunte por el estado de una investigacion de proveedores ya iniciada.
---

# Vendor Research

Investiga con que proveedores trabaja actualmente una empresa cliente/prospecto
-- cualquier tipo de proveedor externo (agencias, consultoras, plataformas de
software, logistica, staffing, lo que sea), no solo tecnologia -- y arma un
reporte de proveedores detectados con nivel de confianza segun cuantas fuentes
independientes lo corroboran.

Es uno de los tres skills de `client-research` (junto a `stack-research` y
`competitor-research`) que comparten el mismo mecanismo general de checklist
persistente en disco -- ver `../../references/checklist-pattern.md` para el
patron completo (forma del checklist, ciclo `pending -> in_progress ->
done|failed`, como despachar sub-agentes en background). Este documento cubre
solo lo especifico de vendor-research: que buscar y donde.

## Cuando usar este skill

- "Que proveedores tiene Acme Corp"
- "Con que agencias/partners trabaja <empresa>"
- "Investiga los proveedores de Acme" / "vendor research de Acme"
- "Como va la investigacion de proveedores de Acme"

## Diferencia con `stack-research`

`stack-research` infiere tecnologia a partir de lo que un cliente busca
*contratar* (ofertas de empleo). `vendor-research` busca relaciones *ya
existentes* del cliente con terceros que lo proveen de algo (tecnologia o no)
-- fuentes distintas, pregunta distinta. Un mismo nombre (ej. "Salesforce")
puede aparecer en ambos reportes por razones distintas; eso es esperable, no
una duplicacion a evitar.

## Entradas necesarias

1. **Cliente**: nombre de la empresa a investigar (obligatorio).
2. **Refresh**: si el usuario pide "actualizar" la investigacion, reintentar
   tambien los items en estado `done` (por defecto se saltan).

## Sin lista fija de fuentes

A diferencia de `stack-research` (que tiene una lista fija de portales en
`config/jobs.json`), no existe un config con "sitios de proveedores" porque
quien es proveedor de un cliente es informacion abierta, no una lista
enumerable de antemano. El descubrimiento es dinamico: cada corrida busca
desde cero para ese cliente especifico.

## Estado en disco

```text
.client-research/<slug-del-cliente>/vendor-research/checklist.json
.client-research/<slug-del-cliente>/vendor-research/report.md
```

El checklist sigue la forma generica de `../../references/checklist-pattern.md`:
un `item` por cada ronda de busqueda/fuente explorada (no por un catalogo fijo,
ya que no hay uno), con `findings` acumulando los proveedores detectados y sus
`source_urls`.

## Flujo

### 1. Preparar el checklist

Calcular `slug` del cliente y `checklist_path =
.client-research/<slug>/vendor-research/checklist.json`. Si existe y no se
pidio refresh, cargarlo y continuar desde los items `pending`/`in_progress`/
`failed`. Si no existe, crearlo vacio (sin items todavia -- se van agregando a
medida que el descubrimiento avanza, ver paso 2).

### 2. Descubrir y buscar evidencia en background

Buscar evidencia publica de proveedores actuales del cliente, cubriendo estas
cuatro categorias (cada una es al menos un item del checklist, despachado
como sub-agente en background vía Agent tool con `run_in_background: true`):

1. **Sitio del cliente** -- paginas tipo "partners", "proveedores",
   "trusted by", "quienes confian en nosotros" en el dominio del cliente.
2. **Prensa/comunicados** -- notas de prensa o comunicados de un proveedor
   mencionando que trabaja con ese cliente.
3. **LinkedIn/redes** -- posts del proveedor o del cliente anunciando la
   relacion comercial.
4. **Directorios/procurement** -- portales de proveedores, adjudicaciones de
   RFP, o directorios de partners donde aparezca el cliente.

Cada sub-agente recibe el nombre del cliente y su categoria de evidencia
asignada, busca con WebSearch, hace WebFetch solo sobre URLs concretas que ya
aparecieron en resultados, nunca intenta iniciar sesion ni sortear paywalls, y
devuelve: proveedores detectados (nombre, que provee si es evidente), y hasta
3 URLs fuente por proveedor.

**Cuando parar**: seguir buscando (nuevas queries dentro de cada categoria)
hasta que dos rondas seguidas no revelen ningun proveedor nuevo -- rendimientos
decrecientes, sin tope fijo de cantidad.

### 3. Actualizar el checklist a medida que vuelven los resultados

Marcar cada item `done` con sus `findings`/`source_urls`/`checked_at`, o
`failed` con `error` si una categoria no encontro nada accesible. Guardar el
checklist despues de cada actualizacion. Si el usuario pregunta el estado
mientras tanto, leer el checklist actual sin esperar a que termine todo.

### 4. Agregar y reportar

Unificar los proveedores encontrados en todas las categorias, deduplicando
(case-insensitive) y contando en cuantas categorias/fuentes distintas aparece
cada uno (señal de confianza). Escribir el agregado en el checklist y generar
`.client-research/<slug>/vendor-research/report.md`: nombre del cliente y
fecha, proveedores detectados ordenados por confianza, con fuente(s) por cada
uno. **Es una lista con fuentes, no una recomendacion evaluativa** -- no
rankear "mejor opcion", solo reportar lo que se encontro y donde.

## Reglas de acceso

Ver `../../references/checklist-pattern.md` -- solo informacion publica, sin
login, sin bypass de paywalls/CAPTCHAs, research puntual por cliente.
