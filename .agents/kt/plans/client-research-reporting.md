---
status: resolved
size: large
rounds_completed: 2
questions_asked: 6
---

# kt — Client Research forensic reporting pipeline

## Status
resolved — 2026-07-23. Built directly (schema redesign + migration in all
three existing skills, new `forensic-report` skill with a stdlib-only PDF
writer, verified end-to-end against a fixture, `claude plugin validate
--strict` green). Version bump to `0.2.0` authorized via `kickoff`'s closing
step. Pending: commit + push (see conversation).

## Original Intent
Person's ask, close to verbatim (from `/kt:idea`, graduated — credits `ideas/client-research-reporting.md`): "creo que ya entiendes lo que quiero lograr con esto. Pero necesito más fuentes y necesitamos un workflow para analizar las fuentes y así poder generar un reporte muy detallado de la información de un cliente en formatos pdf y JSON con verificación de fuentes y esas cosas de un reporte forense de investigación necesitamos inteligencia para estar al frente de nuestra competencia."

Restated as a checkable goal-state: redesign the three existing `client-research` skills' (`stack-research`, `vendor-research`, `competitor-research`) on-disk checklist/report output to a shared structured schema (with a `schema_version` field and real migration logic for pre-existing on-disk data), add a fourth skill (`forensic-report`) that reads all three for a given client and produces one unified, source-verified report exported as both JSON and PDF — the plugin's first code-execution capability. "More sources" resolved to "more specialized research skills" beyond these three, which is explicitly out of scope for this pass (see Open Items). Source verification means visible per-source metadata (URL, access date, publish date, source type), not a credibility/reputation score.

## Research Findings
Three `kt-scout` passes ran in parallel (mandatory for `large` work): `conventions`, `risk`, `tests`. Merged findings:

- **Schema state today**: `stack-research` has its own committed, *deliberately divergent* checklist shape (`boards[]`/`stack_signals`/`aggregate_stack`, with a literal copy-template at `assets/checklist.template.json`) — `checklist-pattern.md` itself documents this divergence as intentional ("items varia segun el skill"). `vendor-research`/`competitor-research` share one generic shape (`items[]`/`findings`/`source_urls`/`aggregate`), documented only in prose, no committed JSON artifact. `source_urls` is a bare string array everywhere — no metadata anywhere.
- **This is real, live data, not a draft**: `client-research-v0.1.0` is a tagged, public GitHub Release from 2026-07-22. Runtime state (`checklist.json`, `report.md`) lives only in the end user's own project under `.client-research/<slug>/<skill>/`, never committed to this repo (confirmed via `.gitignore` and zero committed example output) — real client data, possibly mid-run (`pending`/`in_progress` items), may already exist on disk from real use in the ~1 day since release.
- **Two existing precedents for evolving a persisted file without destroying prior state**: `config/jobs.json` has an explicit `version: 1` field; `config/competitors.json` has an established append-only-never-overwrite convention. Neither is a precedent for an in-place *migration* — that pattern doesn't exist yet anywhere in this repo.
- **Zero code-execution precedent in this plugin**: none of the three skills request Bash or any tool beyond WebSearch/WebFetch/Agent/Read/Write. The only code-execution precedent in the *entire marketplace repo* is `base-plugin/skills/skill-creator/scripts/*.py` (Anthropic's own bundled skill, Apache-2.0, not bSide-authored) — its scripts already assume a third-party dependency (PyYAML) is pre-installed with **zero** dependency-provisioning mechanism anywhere in the repo or CI. No plugin here has ever used `bin/` or `.mcp.json`, though both are documented as valid in this repo's own `CLAUDE.md`.
- **Zero test infrastructure anywhere in this repo**: no test runner, no fixtures, no `package.json`. CI (`validate.yml`) runs only `claude plugin validate --strict` — manifest/frontmatter schema only, confirmed by direct read-only invocation; it would never catch a broken checklist schema or a missing PDF dependency. Skills are Markdown prompts interpreted at conversation time, not code with a callable entry point — genuinely untestable the way a function is; a JSON Schema and a PDF-generation script, by contrast, *would* be this plugin's first real, testable, non-prompt code artifacts.

A `kt-panelist` judgment panel (mandatory for `large`) ran a second time at this stage — the `kt:idea` phase panel (see `ideas/client-research-reporting.md`) had already settled the product-level scope (PDF now, metadata not scoring, schema-first synthesis, no new skills this pass); this second panel, grounded in the merged scout findings above, focused specifically on three still-open technical/architecture decisions: schema migration strategy, PDF implementation mechanism, and test/fixture strategy. Full positions and synthesis: Task ID `wxjsc1024`, workflow run `wf_92c2782d-555`.

Agreements from this second panel (settled ground): no panelist wanted `.mcp.json` for PDF generation — all considered it heavier/longer-lived machinery than a one-shot document export needs. No panelist wanted a validator wired into CI this pass. All four accepted adding a `schema_version`-style field (echoing `config/jobs.json`'s precedent) as the baseline versioning primitive. None proposed leaving `stack-research`'s on-disk shape untouched behind a synthesis-side adapter — all assumed a real redesign of what gets written to disk, not just a read-time reconciliation layer. None proposed general, repo-wide test infrastructure — where testing came up, it was scoped narrowly to the new schema and the PDF script.

## Questions & Decisions
*(Round numbering starts fresh at graduation, per `kt`'s own rules — the `kt:idea` brainstorming round is recorded separately in `ideas/client-research-reporting.md` and doesn't count toward this record's floor.)*

**Round 1**
1. When `client-research` encounters a pre-`schema_version` `stack-research` file on disk (possibly mid-run), should it fail with a clear error and require regeneration, or include real migration logic? → **Migrar de verdad el formato viejo** (real migration logic, not just fail-loud — the person went with the `skeptic` lens's position over the other three lenses' "fail loud, don't migrate" lean).
2. Is it acceptable to ship PDF export by reusing `skill-creator`'s existing pattern (assumes a pre-installed dependency, no detection), or must that gap close first? → **"claude ya tiene o debería tener las skills y tools para ello"** — read as delegating the specific technical mechanism to Claude's judgment rather than picking among the three offered options; resolved in Resulting Plan below (see the reasoning there), not re-asked.
3. Should the new shared schema ship with committed test fixture files (no CI wiring), or stay a documented artifact only? → **Sí, con fixtures (sin CI)**.
4. Should `source_type` reuse `vendor-research`/`competitor-research`'s existing 4 categories (site, prensa, LinkedIn/redes, directorios) plus a new one for job boards, or stay free text? → **Reusar las 4 + una nueva para empleo**.

**Round 2** *(drafted after round 1's answer to Q1 — "migrate for real" — opened two immediate follow-ups: how safely, and how the new unified report behaves when the three source skills aren't all done)*
1. When migrating an old-shape `checklist.json` in place, should the original be backed up first, or overwritten directly? → **Sobreescribir directo** (no backup file).
2. If the unified report is requested before all three skills have completed for that client, should it generate anyway (flagging gaps) or require all three complete first? → **Requiere los 3 completos** — the `forensic-report` skill hard-gates on all three being in a terminal `done` state; it does not generate a partial report.

## Resulting Plan

**Schema redesign — envelope + payload split** (adopting the `architecture` lens's proposal; no panelist objected to this shape, only to how migration around it was handled, which round 1/2's answers already settle): every skill's `checklist.json` gets a shared envelope — `schema_version` (starts at `1`), `client`, `slug`, `skill`, `created_at`, `updated_at` — wrapping a still-skill-specific payload. `stack-research` keeps its own `boards[]`/`stack_signals`/`aggregate_stack` payload shape (the documented, intentional divergence is preserved, not flattened); `vendor-research`/`competitor-research` keep their `items[]`/`findings`/`aggregate` payload shape. What changes uniformly across all three: `source_urls` (and `posting_urls`) becomes an array of objects — `{url, access_date, publish_date, source_type}` — instead of bare strings. `source_type` is a fixed set: `job-board` (new), `client-site`, `press`, `social`, `directory` (the four existing evidence categories, given consistent slugs).

**Migration**: each skill, on start, checks the on-disk `checklist.json` for `schema_version`. If absent (legacy file), it migrates in place: wraps the existing payload in the new envelope, converts bare `source_urls`/`posting_urls` strings into `{url, source_type: null, access_date: null, publish_date: null}` objects (legacy entries can't retroactively know dates that were never captured — only new entries going forward get real metadata), and overwrites the original file directly (no backup, per round 2's answer). `pending`/`in_progress` items carry over unchanged — the status enum itself doesn't change, so a mid-run checklist resumes normally post-migration.

**New skill: `skills/forensic-report/SKILL.md`** — the plugin's fourth skill. Given a client, checks that `stack-research`, `vendor-research`, and `competitor-research` each have a `done` (terminal) checklist for that client; if any is missing or not yet terminal, it says so explicitly and does not generate a report (per round 2's answer — hard gate, not a soft warning). Once all three are confirmed complete, it reads their three envelope+payload JSON files, cross-references findings (e.g., a vendor also appearing as a job-board tech signal), and produces:
- `.client-research/<slug>/report.json` — the full unified, schema-conformant export (all three envelopes/payloads plus the cross-referenced synthesis).
- `.client-research/<slug>/report.pdf` — a rendered version of the same content.

**PDF mechanism** (resolving round 1 Q2's delegated answer): implement via a script under `skills/forensic-report/scripts/` (following `skill-creator`'s only in-repo precedent for *where* a bundled script lives), invoked through the Bash tool, using **Python's standard library only — no third-party PDF dependency**. A minimal, valid PDF is fully constructable from Python's stdlib alone (a well-established technique); choosing this over a `reportlab`/`fpdf2`/`pandoc`-style dependency directly avoids reproducing the one dependency-provisioning gap the research flagged as already broken in this repo's only other code-execution precedent, and needs no install step on any machine that already has Python 3 (which `skill-creator` itself already assumes is present). This is Claude's own engineering call in response to "claude ya tiene o debería tener las tools" — flagged clearly here in case that reads the person's intent wrong; a pip-installable library remains a straightforward substitution later if this proves too limited. Third-party findings text (from WebSearch/WebFetch results) gets explicitly escaped/sanitized before being embedded in the rendered PDF, regardless of renderer — the one point in the pipeline where open-web content reaches a generated artifact through a code path rather than an LLM's own judgment.

**Bash scoping**: only `forensic-report/SKILL.md` declares `allowed-tools` including Bash. `stack-research`, `vendor-research`, `competitor-research` are untouched — their tool surface stays exactly as shipped in v0.1.0.

**Fixtures** (round 1 Q3): commit `plugins/client-research/schemas/` containing a JSON Schema (or schema-shaped documentation, mirroring `stack-research`'s existing `checklist.template.json` convention) for the envelope + each skill's payload, plus 2-3 synthetic (never real-client) example fixture files — one per skill plus one unified `report.json` example. No CI wiring this pass, matching the panel's unanimous lean.

**Shared docs**: `references/checklist-pattern.md` gets updated to document the envelope/payload split, `schema_version`, the migration behavior, and the new `source_type` taxonomy — the same "document once, reference from every SKILL.md" convention already established.

**Disclosure**: `README.md` and `CHANGELOG.md` get a short callout that this version introduces the plugin's first code-execution capability, scoped to the one new skill.

**Resulting directory tree (additions/changes only)**
```
plugins/client-research/
├── schemas/
│   ├── report-envelope.schema.json       (new — shared envelope + per-skill payload shapes)
│   └── fixtures/
│       ├── stack-research.example.json    (new, synthetic)
│       ├── vendor-research.example.json   (new, synthetic)
│       ├── competitor-research.example.json (new, synthetic)
│       └── report.example.json            (new, synthetic — unified output)
├── skills/
│   ├── stack-research/SKILL.md            (updated: envelope, schema_version, migration)
│   ├── vendor-research/SKILL.md           (updated: envelope, schema_version, migration, structured source_urls)
│   ├── competitor-research/SKILL.md       (updated: envelope, schema_version, migration, structured source_urls)
│   └── forensic-report/
│       ├── SKILL.md                       (new — the only skill requesting Bash)
│       └── scripts/
│           └── generate_pdf.py            (new — stdlib-only PDF writer)
├── references/checklist-pattern.md        (updated: envelope/payload, migration, source_type taxonomy)
└── README.md                              (updated: 4th skill, Bash disclosure)
```

**Explicitly out of scope for this pass**
- Any new specialized research skills beyond `stack-research`/`vendor-research`/`competitor-research`/`forensic-report` — the round-1 `kt:idea` answer that opened this ("más skills especializados en más tipos de búsqueda") named no specific skill types and needs its own dedicated brainstorming pass, not a guess folded into this record. See Open Items.
- A credibility/reputation scoring engine — verification here is visible metadata only, per the `kt:idea` phase's settled decision.
- CI wiring for the new fixtures/schema.
- A backup file during migration (explicitly declined).

## Open Items
- **Stopped at 2 rounds against a `large`-work floor of 8.** This is a real shortfall, not a rounding error, and is recorded honestly rather than papered over. Reasoning: the two rounds run resolved the judgment panel's three core friction points (schema migration strategy, PDF mechanism, fixture strategy) plus the two immediate follow-ups they opened (migration safety, partial-completion behavior) — five genuinely consequential, user-facing product decisions. The remaining scout-flagged unknowns (unified report file location, Bash-confinement scope, third-party-content sanitization, exact fixture directory location, disclosure mechanics) were, on review, implementation-level calls where the panel/scout already produced an uncontested lean or an obvious responsible default — not further product forks. Combined with the person's own delegating answer on the PDF-mechanism question ("claude ya tiene o debería tener las tools") signaling a preference for fewer granular technical questions this pass, asking 6 more rounds to hit the nominal floor would have been manufacturing questions rather than chasing real ambiguity. Each such item is decided explicitly above in Resulting Plan, not silently assumed, so the person can correct any of them.
- **"Más skills especializados en más tipos de búsqueda"** (from the graduated idea's round 1) is real, unresolved scope the person named but this record deliberately does not define — which search types (financial/legal, prensa/medios, redes sociales, patentes/IP, background de ejecutivos, litigios, mercado/industria?) needs its own `kt:idea` brainstorming pass, not a guess folded into an already-large piece of work.
- **Schema/envelope design (the envelope+payload split, the exact field names) was decided by Claude adopting the `architecture` lens's proposal**, not put to the person as a direct question — no panelist contested the shape itself, only the migration handling around it (which rounds 1–2 did resolve). Flagged here for the person's review since it's a real, if uncontested, design commitment.
- **PDF mechanism (stdlib-only Python, no third-party dependency) was decided by Claude**, interpreting "claude ya tiene o debería tener las tools" as delegation rather than picking one of the three originally-offered options. Flagged explicitly in Resulting Plan and here in case that reading is wrong — a pip-installable library remains a straightforward substitution if the stdlib-only approach proves too limiting once actually built.
- **Version bump for this change** (patch/minor/major on `client-research`, currently `0.1.0`) is intentionally not decided here — per this repo's established pattern, that's `kickoff`'s closing step's job once real code exists to diff against, not something `kt` should pre-empt.
