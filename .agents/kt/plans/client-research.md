---
status: open
size: medium
rounds_completed: 4
questions_asked: 13
---

# kt — Client Research plugin (rename + vendor-research + competitor-research)

## Status
open — 2026-07-22

## Original Intent
Person's ask, close to verbatim (from `/kt:idea`, graduated — credits `ideas/client-research.md`): "Vamos a modificar el nombre de nuestro plugin. Lo vamos a llamar Client Research y vamos a agregar otras herramientas, otras skills diseñadas específicamente para búsqueda de cosas con clientes. Que, además de buscar ahí, busque también sitios de proveedores de competencia. Estos recomiendan me diferentes opciones."

Restated as a checkable goal-state: rename the existing `rr-stack-research` plugin (repo `DyxBenjamin/R-R-Framework`, marketplace `rr-framework`) to `client-research` — a real technical rename of `plugin.json`'s `name`, the plugin folder, and the marketplace install slug, not just a display label — and add two new skills alongside the existing `stack-research`: `vendor-research` (discovers any type of provider the client currently works with — not limited to tech) and `competitor-research` (discovers bSide's own competitors/partners, then checks each one for public evidence of prior work with the target client). Both new skills reuse and extend stack-research's checklist/background-subagent/report persistence pattern, generalized off the old plugin name.

## Research Findings
No fresh `kt-scout` pass ran for this record — explicitly skipped per the person's continuation directive from `kt:idea` into `kt:project`, since every fact cited below (file paths, config shapes, mechanisms) was gathered first-hand while building `rr-stack-research` earlier in this same session, not re-derived secondhand from a disposable investigator.

Current state (as of this record):
- `plugins/rr-stack-research/` — `plugin.json` name `rr-stack-research`, version `0.1.0`, already tagged/released as GitHub Release `rr-stack-research-v0.1.0`, listed in root `.claude-plugin/marketplace.json`, installed by the person today as `rr-stack-research@rr-framework`.
- `skills/stack-research/SKILL.md` — given a client, searches 8 fixed job boards (`config/jobs.json`: LinkedIn Jobs, Indeed, Glassdoor, We Work Remotely, Computrabajo, Bumeran, GetOnBoard, OCC Mundial), one background sub-agent per board via the `Agent` tool (`run_in_background`), extracts tech-stack keywords from postings. Persists a per-client checklist at `.rr-stack-research/<client-slug>/checklist.json` (status `pending -> in_progress -> done|failed` per board, resumable across sessions) and writes `.rr-stack-research/<client-slug>/report.md` aggregating `stack_signals` ranked by cross-board corroboration.
- `scripts/generate-release-config.js` auto-syncs root `marketplace.json`, `release-please-config.json`, `.release-please-manifest.json` from every `plugins/<name>/.claude-plugin/plugin.json` on push (and can be run manually, as done earlier this session). It ADDS/UPDATES entries by matching `plugin.json`'s `name`, but never PRUNES a stale entry whose folder disappeared — a rename needs the old `rr-stack-research` marketplace.json entry removed by hand before re-running the script.
- A `kt-panelist` judgment panel already ran during the `kt:idea` phase (lenses: architecture, skeptic, scope, advocate) — see `ideas/client-research.md` for its full findings. Its agreements are folded into Original Intent above; its friction points became round-1 questions there (already answered, not re-asked here).

## Questions & Decisions
*(Round numbering continues from the `kt:idea` brainstorming round, which is recorded separately in `ideas/client-research.md` and does not count toward this record's floor — a graduated record starts a fresh count from here, per the `kt` skill's own rules.)*

**Round 1**
1. ¿Cuál va a ser el nuevo `name` técnico del plugin? → **`client-research`**.
2. ¿Cómo se va a llamar el nuevo skill de descubrimiento de competencia/proveedores? → *(Answer revealed a bigger scope than the question assumed — see below.)* "Separa uno para vendor y otro para competencia. De hecho tanto para el cliente como para nuestra competencia deberíamos tenerlos separados, analizaremos también proyectos que nuestros competidores o partners hayan hecho con ese cliente en cuestión." → Split into **two skills**: `vendor-research` (the client's own current providers) and `competitor-research` (bSide's own competitors/partners, and whether they've worked with this client before).
3. ¿Hasta dónde llega la búsqueda de descubrimiento antes de parar? → **Hasta que se agoten los resultados** (diminishing-returns stopping rule, no fixed cap).
4. ¿Los dos skills escriben un reporte separado cada uno, o un solo dossier? → **Reporte separado por skill**.

**Round 2** *(drafted after round 1's answer #2 opened the vendor/competitor split as a new unknown)*
1. Ahora que "competencia" es un skill aparte, ¿qué investiga `vendor-research` sobre el cliente? → **Proveedores actuales del cliente** (existing relationships, not market alternatives).
2. Para `competitor-research`, ¿cómo sabe el skill quiénes son "nuestros" competidores/partners? → **"Busca los competidores de bside.com.mx y crea una lista que después usarás para inspeccionar"** — i.e., a bootstrap discovery step anchored on bSide's own domain, cached for reuse across client runs (not a hand-typed list, and not re-discovered per client).
3. ¿Qué tipo de evidencia debe buscar para "proyectos que nuestros competidores/partners hicieron con ese cliente"? → **Las cuatro**: portfolio/case studies del competidor, prensa/comunicados, redes/LinkedIn, directorios de partners.
4. ¿Qué hacer con el release huérfano `rr-stack-research-v0.1.0`? → **Editar sus notas** (append a note that the plugin was renamed to `client-research`), leave the tag/release itself in place.

**Round 3**
1. `vendor-research`: ¿solo proveedores de tecnología/software, o cualquier tipo de proveedor? → **Cualquier proveedor, no solo tech** (agencies, consultancies, logistics, software — broad).
2. ¿La lista de competidores de bSide se puede curar a mano además de auto-descubrirse? → **Auto-descubre + edición manual** — a refresh only appends new suggestions, never overwrites or removes what the person curated by hand.
3. ¿`bside.com.mx` queda hardcodeado o es configurable? → **Configurable** — a small `config/company.json`, editable without touching `SKILL.md` prose.
4. `vendor-research`: ¿mismo criterio de "hasta agotar resultados" que `competitor-research`, o un tope distinto? → **Mismo criterio**.

**Round 4** *(one genuinely remaining unknown — vendor-research's evidence types were never defined, unlike competitor-research's)*
1. Para `vendor-research`, ¿qué tipo de evidencia pública debería buscar? → **Las cuatro**: sitio del cliente (partners/proveedores/"trusted by"), prensa/comunicados, LinkedIn/redes, directorios/procurement — the same four-category shape as `competitor-research`'s evidence types, adapted to vendor evidence.

## Resulting Plan

**Rename (`rr-stack-research` → `client-research`)**
1. `git mv plugins/rr-stack-research plugins/client-research` (preserves `CHANGELOG.md` history).
2. `plugins/client-research/.claude-plugin/plugin.json`: `name` → `client-research`, `version` → `0.1.0` (fresh lineage — `release-please` tracks by path/component, so the old component's history doesn't carry over automatically), `description`/`keywords` updated to cover all three capabilities (stack, vendor, competitor research).
3. Manually remove the stale `rr-stack-research` entry from root `.claude-plugin/marketplace.json`'s `plugins` array (the sync script only adds/updates, never prunes), then re-run `node scripts/generate-release-config.js` to add `client-research` fresh and regenerate `release-please-config.json` / `.release-please-manifest.json`.
4. Update root `README.md`: plugins table, install commands (`client-research@rr-framework`), layout tree.
5. `gh release edit rr-stack-research-v0.1.0` — append a note that the plugin was renamed to `client-research`. Leave the tag/release itself in place (harmless history).

**Shared persistence convention (all three skills)**
- Generalize the on-disk path off the old plugin name: `.client-research/<client-slug>/<skill-id>/checklist.json` and `.../report.md`, where `skill-id` ∈ `{stack-research, vendor-research, competitor-research}` — keeps each skill's report separate (per the person's explicit choice) while sharing one root namespace and one mechanism.
- Update `skills/stack-research/SKILL.md`'s path references only (its job-board logic is unchanged).
- Add `plugins/client-research/references/checklist-pattern.md` — the common `pending -> in_progress -> done|failed` checklist/report mechanism documented once, referenced from all three `SKILL.md` files instead of tripling the explanation.

**New config: `config/company.json`** — who "we" are, for `competitor-research`'s bootstrap step:
```json
{ "name": "bSide", "domain": "bside.com.mx" }
```

**New config: `config/competitors.json`** — cache of bSide's discovered competitors/partners, bootstrapped by `competitor-research`, hand-editable; a refresh appends new discoveries and never removes or overwrites an existing (including manually-added) entry:
```json
{
  "updated_at": "<ISO 8601>",
  "competitors": [
    { "name": "...", "domain": "...", "source": "...", "discovered_at": "<ISO 8601>", "manually_added": false }
  ]
}
```

**New skill: `skills/vendor-research/SKILL.md`**
- Given a client, discovers any type of current provider relationship (not limited to tech) via public evidence: the client's own site (partners/proveedores/"trusted by" pages), press/comunicados, LinkedIn/social posts, procurement/RFP/partner directories.
- No fixed source-site config (unlike `jobs.json`) — open-ended search/discovery, same "hasta agotar resultados" diminishing-returns stopping rule as `competitor-research`.
- Persists under `.client-research/<client-slug>/vendor-research/`.
- Output: a deduped, source-corroborated list of providers found (name, what they provide if evident, source links) — explicitly not an evaluative ranking or recommendation.

**New skill: `skills/competitor-research/SKILL.md`** — two phases:
- *Bootstrap* (business-level, not per-client): reads `config/company.json`, researches bSide's own positioning/market, discovers comparable/competing companies, merges new finds into `config/competitors.json` (append-only, never overwrites manual curation). Runs on demand ("actualizá la lista de competidores") or automatically the first time the skill runs against an empty/missing `competitors.json`.
- *Per-client*: for each entry in `config/competitors.json`, searches for evidence that competitor/partner worked with the target client, across the four confirmed evidence types (portfolio/case studies, press/comunicados, LinkedIn/social, partner directories), same "hasta agotar resultados" depth, one checklist item per competitor.
- Persists under `.client-research/<client-slug>/competitor-research/`.
- Output: a deduped list of competitors/partners with corroborated evidence of prior work with this client, source links per evidence type found.

**Resulting directory tree**
```
plugins/client-research/
├── .claude-plugin/plugin.json
├── README.md
├── CHANGELOG.md                    (moved from rr-stack-research, history preserved)
├── config/
│   ├── jobs.json                   (unchanged)
│   ├── company.json                (new)
│   └── competitors.json            (new, bootstrapped on first competitor-research run)
├── references/
│   └── checklist-pattern.md        (new, shared across all three skills)
└── skills/
    ├── stack-research/SKILL.md     (path references updated only)
    ├── vendor-research/SKILL.md    (new)
    └── competitor-research/SKILL.md (new)
```

**Explicitly out of scope for this pass**
- Any further "otras herramientas" client-research skills beyond these three — left as a stated future direction, not built now (matches the `scope` lens's conclusion and the original intent's own "starting with" wording, unchallenged by the panel).
- Migrating any already-existing `.rr-stack-research/*` runtime data on someone's machine — it's disposable, regenerable cache, not carried over by the rename.

## Open Items
- Sized `medium`, not `large` — the work is concentrated within one plugin/component (even though it grows from one skill to three), and the root `marketplace.json`/release-config touches are mechanical, already automated by the existing sync script exercised earlier this session, not independent design surface. Floor: 4 rounds. Reached exactly 4 rounds post-graduation (13 questions total across them) and stopped there because round 4's answer was a clean confirmation that opened no further fork — genuine unknowns ran dry, not an artificial ceiling.
- Exact search-query phrasing/strategy inside each new `SKILL.md` (how `competitor-research` composes its web searches, how `vendor-research` composes its own) is left to drafting/build time — an implementation-level detail, not a product ambiguity needing the person's input.
- No separate question was raised about warning or redirecting anyone who already has `rr-stack-research@rr-framework` installed — low-stakes given this is currently a solo/internal marketplace; handled by editing the old release's notes only (per the person's answer), no further migration tooling planned.
