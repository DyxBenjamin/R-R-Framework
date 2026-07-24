---
status: captured
---

# Idea — Client Research forensic reporting pipeline

## The Idea
"creo que ya entiendes lo que quiero lograr con esto. Pero necesito más
fuentes y necesitamos un workflow para analizar las fuentes y así poder
generar un reporte muy detallado de la información de un cliente en formatos
pdf y JSON con verificación de fuentes y esas cosas de un reporte forense de
investigación necesitamos inteligencia para estar al frente de nuestra
competencia."

## Panel Findings
Judgment panel ran (lenses: architecture, skeptic, scope, advocate) against
the idea as stated, grounded in the current `client-research` plugin
(`stack-research`, `vendor-research`, `competitor-research`, shipped as
`client-research-v0.1.0`). Full positions and synthesis: Task ID `wqe7e927c`,
workflow run `wf_ba5d05ca-1f1`.

Agreements (settled ground): the ask bundles several unequally-costly
problems (more sources, cross-skill synthesis, JSON export, PDF export,
source verification) that need separate scoping, not one uniform "add
reporting" feature. JSON export is nearly free (the plugin's existing
per-item/aggregate schema is already structured data). PDF export is
categorically different — the plugin's first-ever code-execution capability
(today all three skills are pure prompt/tool-use, no bundled script, binary,
or MCP server). The existing "confidence" signal is a corroboration count
(how many independent sources agree), not an assessment of any single
source's own credibility/freshness — genuinely different from "source
verification." "More sources" isn't uniform across skills: stack-research has
a bounded config list, vendor/competitor-research are already open-ended by
design. A real unified per-client report needs genuine synthesis work, since
today's three skills are deliberately siloed (own checklist, own report.md,
"nunca se comparte o se mezcla el estado entre skills").

Sharp friction points (became the round-1 questions below): whether PDF ships
now (minimal) vs. gets split into its own separate decision vs. gets deferred
until implementation-route feasibility is assessed; what "source
verification" concretely means (metadata tagging vs. a genuine credibility
judgment); whether cross-skill synthesis can parse the three skills' existing
markdown as-is or needs a shared structured schema first; which skill(s)
actually need more sources.

## Quick Questions & Answers
1. **¿Necesitás PDF en esta misma tanda?** → Sí, PDF mínimo viable ahora (primer script/ejecución de código del plugin).
2. **¿Qué significa "verificación de fuentes"?** → Metadata visible por fuente (URL, fecha de acceso, fecha de publicación, tipo de fuente) — no un puntaje de credibilidad.
3. **¿Síntesis lee los markdown existentes tal cual, o primero un esquema compartido?** → Primero un esquema compartido — redisña el formato de salida de los 3 skills existentes antes de construir síntesis/JSON/PDF encima.
4. **¿Qué skill(s) necesitan más fuentes?** → *(Reveló un alcance más grande de lo que la pregunta asumía — ver Open Items.)* "Más skills especializados en más tipos de búsqueda" — no es ampliar las fuentes de los 3 skills existentes, es agregar skills de investigación nuevos y distintos.

## Open Items
La respuesta 4 abrió una incógnita real que el cap de una sola ronda de `kt:idea` no permite perseguir ahora: qué skills nuevos de investigación especializada se necesitan (tipos de búsqueda: ¿financiero/legal, prensa/medios, redes sociales, patentes/IP, background de ejecutivos, litigios, mercado/industria?). Eso queda fuera del alcance de esta graduación — es un tema para un `kt:idea` propio más adelante, no algo que se pueda resolver adivinando ahora. El plan que gradúa cubre solo lo que las otras 3 respuestas ya dejaron concreto: esquema compartido + síntesis + JSON + PDF mínimo + metadata de verificación por fuente.

---
Graduated to `plans/client-research-reporting.md` — 2026-07-23
