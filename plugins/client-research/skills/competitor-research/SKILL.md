---
name: competitor-research
description: Investiga si nuestros propios competidores o partners (bSide) ya trabajaron antes con un cliente/prospecto dado, buscando evidencia publica de proyectos en comun. Mantiene una lista cacheada y curable de nuestros competidores (bootstrapeada buscando en base a quienes somos), y un checklist de progreso por cliente en disco que se puede retomar sin repetir trabajo. Usar siempre que el usuario pida saber si algun competidor o partner ya trabajo con un cliente, pida "competitor research", "inteligencia competitiva", quiera actualizar la lista de competidores de bSide, o pregunte por el estado de una investigacion ya iniciada.
---

# Competitor Research

Investiga, para un cliente/prospecto dado, si alguno de **nuestros propios**
competidores o partners (bSide) ya trabajo con el antes -- para saber con
quien estamos compitiendo por esa cuenta o quien ya tiene una relacion previa
con ese cliente.

**Esto no es investigar a la competencia del cliente** -- es investigar a la
competencia/partners de bSide. Si el pedido es sobre proveedores del propio
cliente (sin relacion con bSide), usar `vendor-research` en cambio.

Es uno de los tres skills de `client-research` (junto a `stack-research` y
`vendor-research`) que comparten el mismo mecanismo general de checklist
persistente en disco -- ver `../../references/checklist-pattern.md` para el
patron completo. Este documento cubre lo especifico de competitor-research:
sus dos fases (bootstrap de la lista de competidores, y busqueda por cliente).

## Cuando usar este skill

- "Algun competidor nuestro trabajo con Acme Corp?"
- "Inteligencia competitiva sobre Acme"
- "Actualiza la lista de competidores de bSide"
- "Como va la investigacion de competencia de Acme"

## Fase A -- Bootstrap de la lista de competidores (a nivel negocio, no por cliente)

La lista de "quienes son nuestros competidores/partners" es un dato del
negocio de bSide, no de un cliente puntual -- se descubre una sola vez y se
reutiliza en todas las corridas por cliente, no se rehace en cada una.

### Cuando correr esta fase

- La primera vez que se invoca `competitor-research` y
  `config/competitors.json` esta vacio (`competitors: []`).
- Cuando el usuario pide explicitamente "actualizar" o "refrescar" la lista
  de competidores.
- Nunca automaticamente en cada corrida por cliente si la lista ya tiene
  contenido -- eso desperdiciaria busquedas repetidas sobre algo que no
  cambia por cliente.

### Como descubrir

1. Leer `${CLAUDE_PLUGIN_ROOT}/config/company.json` (`name`, `domain` de
   bSide).
2. Visitar/entender que hace bSide (WebFetch a `domain`, o WebSearch sobre el
   `name`) para poder buscar comparables con criterio, no a ciegas.
3. Buscar (WebSearch) empresas/agencias que compitan con bSide en su mismo
   rubro/servicios -- variaciones de "alternativas a bSide", "competidores de
   <domain>", "agencias similares a bSide", segun lo que la busqueda del paso
   2 revele que hace bSide.
4. Seguir buscando hasta que dos rondas seguidas no revelen ningun competidor
   nuevo (mismo criterio de rendimientos decrecientes que `vendor-research`).

### Como guardar (append-only, nunca pisa curaduria manual)

Cargar `config/competitors.json`. Por cada competidor nuevo encontrado que no
este ya en la lista (comparar por `domain` o `name` normalizado), agregar una
entrada:

```json
{
  "name": "",
  "domain": "",
  "source": "",
  "discovered_at": "<ISO 8601>",
  "manually_added": false
}
```

**Nunca eliminar ni sobreescribir una entrada existente** -- incluidas las que
el usuario agrego a mano (`manually_added: true`) o cualquier entrada previa,
aunque una nueva busqueda no la vuelva a encontrar. Un refresh solo *agrega*.
Actualizar `updated_at` al terminar.

## Fase B -- Por cliente: buscar evidencia de trabajo en comun

Con `config/competitors.json` ya poblado (corriendo la Fase A antes si hace
falta), para el cliente pedido:

### 1. Preparar el checklist

Calcular `slug` del cliente y `checklist_path =
.client-research/<slug>/competitor-research/checklist.json`. Si existe,
revisar `schema_version`: si falta, migrar ahora (ver "Migracion desde
version sin `schema_version`" mas abajo) antes de seguir. Si existe (migrado
o no) y no se pidio refresh, cargarlo y continuar desde los items
`pending`/`in_progress`/`failed`. Si no existe, instanciar un item por cada
entrada de `config/competitors.json`, todos en `pending`, siguiendo
`assets/checklist.template.json` (`schema_version: 1`, `skill:
"competitor-research"`).

### Migracion desde version sin `schema_version`

Si el checklist en disco no tiene `schema_version`, migrar sobreescribiendo el
archivo original (sin backup): agregar `schema_version: 1` y `skill:
"competitor-research"` al nivel superior si faltan, y convertir cada string de
`source_urls` en un objeto `{url, source_type: null, access_date: null,
publish_date: null}`. A diferencia de `vendor-research`, aca un item cubre las
4 categorias de evidencia a la vez para un mismo competidor -- el dato viejo
no guarda que URL vino de que categoria, asi que `source_type` queda en
`null` para las entradas migradas (no se puede inferir de forma confiable,
solo las entradas nuevas lo llevan). Los items `pending`/`in_progress` se
preservan, la corrida a medias se retoma normal despues de migrar.

### 2. Buscar evidencia por competidor en background

Por cada competidor pendiente, despachar un sub-agente (Agent tool,
`run_in_background: true`) con el nombre del cliente y el nombre/dominio de
ese competidor, instruido para buscar evidencia publica de que trabajaron
juntos, cubriendo estas cuatro categorias:

1. **Portfolio/case studies** -- la seccion de casos de exito o portfolio en
   el sitio del competidor, buscando menciones del cliente.
2. **Prensa/comunicados** -- notas de prensa o comunicados sobre el
   competidor trabajando con ese cliente.
3. **LinkedIn/redes** -- posts anunciando el proyecto o la relacion.
4. **Directorios de partners** -- paginas tipo "nuestros clientes" o
   "partners" del competidor donde liste con quien trabajo.

Igual que en el resto del plugin: WebSearch primero, WebFetch solo sobre URLs
concretas ya encontradas, nunca login ni bypass de paywalls/CAPTCHAs. Mismo
criterio de "hasta agotar resultados" antes de dar por cerrado ese competidor.
El sub-agente devuelve: si encontro evidencia o no, y por cada URL fuente
(hasta 3), a que categoria pertenece -- `client-site` (portfolio/case
studies), `press`, `social` (LinkedIn/redes) o `directory` (directorios de
partners) -- para poder guardarla con su `source_type` correcto.

### 3. Actualizar el checklist a medida que vuelven los resultados

Marcar cada item `done` con sus `findings` (categorias con evidencia
encontrada) y `source_urls` como objetos `{url, source_type: <categoria de
esa URL>, access_date: <hoy>, publish_date: <si es visible, si no null>}`, o
`done` con `findings: []` y `source_urls: []` si no se encontro nada (no es
un error, es un resultado valido -- ese competidor probablemente no trabajo
con este cliente). Guardar el checklist despues de cada actualizacion.

### 4. Agregar y reportar

Escribir el agregado en `aggregate.competitors_with_evidence` (ver
`assets/checklist.template.json` y
`../../schemas/fixtures/competitor-research.example.json` para la forma
exacta: `name`, `mentions`, `source_types`, `source_urls`) y generar
`.client-research/<slug>/competitor-research/report.md`: nombre del cliente y
fecha, y la lista de competidores/partners con evidencia encontrada (cuales
categorias, con fuentes) -- omitir o listar aparte a los que no dieron ningun
resultado. **Es una lista con evidencia, no una recomendacion** -- reportar
que se encontro y donde, sin opinar sobre que hacer con esa informacion.

## Reglas de acceso

Ver `../../references/checklist-pattern.md` -- solo informacion publica, sin
login, sin bypass de paywalls/CAPTCHAs, research puntual, nunca scraping
masivo.
