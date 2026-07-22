# rr-stack-research

Investiga el stack tecnologico de un cliente/prospecto rastreando sus ofertas
de empleo publicas en varios portales de trabajo, globales y LATAM.

```text
rr-stack-research/
├── .claude-plugin/
│   └── plugin.json
├── config/
│   └── jobs.json             # portales a buscar + palabras clave de stack
└── skills/
    └── stack-research/
        ├── SKILL.md           # logica del research y del checklist
        └── assets/
            └── checklist.template.json
```

## Que hace

- **`stack-research`** (skill) - dado el nombre de una empresa, busca sus
  vacantes publicadas en los portales listados en `config/jobs.json`
  (LinkedIn Jobs, Indeed, Glassdoor, We Work Remotely, Computrabajo, Bumeran,
  GetOnBoard, OCC Mundial), despacha esa busqueda por portal en background con
  sub-agentes, y extrae las tecnologias mencionadas en cada publicacion.
- **Checklist persistente** - el progreso por cliente se guarda en
  `.rr-stack-research/<cliente>/checklist.json` dentro del proyecto donde se
  invoca el skill (no dentro del plugin). Cada portal pasa por
  `pending -> in_progress -> done|failed`, asi que una investigacion se puede
  cortar y retomar despues sin repetir portales ya resueltos.
- **Reporte** - al terminar, genera
  `.rr-stack-research/<cliente>/report.md` con el stack agregado, ordenado por
  cuantos portales distintos corroboran cada tecnologia, y las fuentes.

## Uso

```text
Investiga el stack de Acme Corp
Como va la investigacion de stack de Acme
Actualiza el research de stack de Acme (refresco completo)
```

El skill se auto-invoca por descripcion; tambien podes llamarlo explicito con
`/rr-stack-research:stack-research`.

## Configurar los portales

Editar `config/jobs.json`. Cada entrada de `boards` necesita `id`, `name`,
`region` (`global`/`latam`), `base_url`, `search_query_template` (con
`{client}` como placeholder) y notas de `access` (si requiere login, si
renderiza con JS). Poner `enabled: false` para desactivar un portal sin
borrarlo.

`stack_signal_keywords` es una lista de arranque de tecnologias conocidas por
categoria; el skill no se limita a ella, registra cualquier tecnologia
mencionada explicitamente en una publicacion.

## Reglas de acceso

Solo se usa informacion publicamente accesible (resultados de busqueda y
paginas de vacante sin login). El skill nunca intenta iniciar sesion ni
sortear paywalls/CAPTCHAs -- ver la seccion "Reglas de acceso" en
`skills/stack-research/SKILL.md`.
