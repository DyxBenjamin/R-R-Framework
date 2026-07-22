# client-research

Investiga clientes/prospectos desde tres angulos: su stack tecnologico, sus
proveedores actuales, y si nuestros propios competidores o partners (bSide)
ya trabajaron con ellos antes.

```text
client-research/
├── .claude-plugin/
│   └── plugin.json
├── config/
│   ├── jobs.json              # portales de empleo (stack-research)
│   ├── company.json           # quienes somos (ancla de competitor-research)
│   └── competitors.json       # cache curable de competidores/partners de bSide
├── references/
│   └── checklist-pattern.md   # mecanismo de checklist/reporte, compartido por los 3 skills
└── skills/
    ├── stack-research/        # stack tecnologico del cliente via ofertas de empleo
    ├── vendor-research/       # proveedores actuales del cliente
    └── competitor-research/   # historial de nuestros competidores/partners con el cliente
```

> Este plugin se llamaba `rr-stack-research` (solo `stack-research`) hasta
> esta version. Fue renombrado a `client-research` al sumarle `vendor-research`
> y `competitor-research` — es un rename tecnico real, `rr-stack-research@rr-framework`
> ya no es instalable.

## Que hace cada skill

- **`stack-research`** — dado un cliente, busca sus vacantes publicadas en los
  portales de `config/jobs.json` (LinkedIn Jobs, Indeed, Glassdoor, We Work
  Remotely, Computrabajo, Bumeran, GetOnBoard, OCC Mundial), despacha esa
  busqueda por portal en background, y extrae las tecnologias mencionadas.
- **`vendor-research`** — dado un cliente, descubre sus proveedores actuales
  (de cualquier tipo: agencias, consultoras, software, no solo tech) buscando
  evidencia publica: el sitio del cliente (paginas de partners/proveedores/
  "trusted by"), prensa/comunicados, LinkedIn/redes, y directorios/procurement.
  Sin lista fija de sitios — busca hasta que se agotan los resultados nuevos.
- **`competitor-research`** — mantiene en `config/competitors.json` una lista
  de los competidores/partners de bSide (bootstrapeada buscando en base a
  `config/company.json`, curable a mano). Para un cliente dado, busca en cada
  competidor/partner evidencia de que ya trabajo con ese cliente: portfolio/
  case studies, prensa/comunicados, LinkedIn/redes, directorios de partners.

## Checklist persistente (compartido por los 3 skills)

El progreso de cada corrida se guarda en el proyecto donde se invoca el
skill (no dentro del plugin), separado por cliente y por skill:

```text
.client-research/<cliente>/stack-research/{checklist.json,report.md}
.client-research/<cliente>/vendor-research/{checklist.json,report.md}
.client-research/<cliente>/competitor-research/{checklist.json,report.md}
```

Cada item pasa por `pending -> in_progress -> done|failed`, asi que una
investigacion se puede cortar y retomar despues sin repetir trabajo ya hecho.
Cada skill escribe su propio `report.md` — no se combinan en un solo dossier.
El mecanismo completo esta documentado una sola vez en
`references/checklist-pattern.md` y cada `SKILL.md` lo referencia en vez de
repetirlo.

## Uso

```text
Investiga el stack de Acme Corp
Que proveedores tiene Acme Corp
Algun competidor nuestro trabajo con Acme Corp?
Actualiza la lista de competidores de bSide
```

Los skills se auto-invocan por descripcion; tambien se pueden llamar
explicito con `/client-research:stack-research`, `:vendor-research` o
`:competitor-research`.

## Configuracion

- **`config/jobs.json`** — portales de empleo para `stack-research`. Cada
  entrada de `boards` necesita `id`, `name`, `region` (`global`/`latam`),
  `base_url`, `search_query_template` (con `{client}`) y notas de `access`.
  `enabled: false` desactiva un portal sin borrarlo.
- **`config/company.json`** — quienes somos (`name`, `domain`), usado por
  `competitor-research` para descubrir nuestros propios competidores. Editar
  si cambia el dominio o el nombre de la empresa.
- **`config/competitors.json`** — cache de competidores/partners descubiertos.
  Editable a mano; un refresco solo agrega sugerencias nuevas, nunca borra o
  pisa una entrada existente (incluidas las agregadas a mano).

## Reglas de acceso

Solo se usa informacion publicamente accesible (resultados de busqueda y
paginas sin login). Ningun skill de este plugin intenta iniciar sesion ni
sortear paywalls/CAPTCHAs — ver la seccion "Reglas de acceso" en cada
`SKILL.md`.
