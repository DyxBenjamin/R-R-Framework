---
status: captured
---

# Idea — Client Research plugin rebrand + competitor/vendor research

## The Idea
Vamos a modificar el nombre de nuestro plugin. Lo vamos a llamar Client Research y vamos a agregar otras herramientas, otras skills diseñadas específicamente para búsqueda de cosas con clientes. Que, además de buscar ahí, busque también sitios de proveedores de competencia. Estos recomiendan me diferentes opciones.

## Panel Findings
Judgment panel ran (lenses: architecture, skeptic, scope, advocate) against the idea as originally stated — rename `rr-stack-research` → "Client Research", add one new skill that searches competitor/vendor sites. Full positions and synthesis in the workflow run (Task ID `w5ta0txct`, run `wf_21fade64-91b`).

Agreements (settled ground): the checklist.json + background-subagent + report.md persistence mechanism proven in stack-research is sound, reusable infrastructure for any new skill's mechanics. `plugin.json`'s `name` field is load-bearing, not cosmetic — the plugin was already tagged/released as `rr-stack-research-v0.1.0` and listed in `marketplace.json`, so changing `name` breaks the existing install slug and release lineage. Build exactly one new skill now, not a speculative suite. "Recommend different options" was genuinely ambiguous (a plain corroborated list vs. an evaluative recommendation with rationale) rather than a wording nuance to smooth over.

Sharp friction points (became the round-1 questions below): whether "rename" meant the technical identifier/install slug or just branding (`displayName`); whether the fixed-list config pattern (`jobs.json`) transfers to competitor/vendor sites, or whether "who counts as a competitor/vendor" needs an open-ended discovery step first; whether the new skill's output should be a plain corroborated list or an evaluative recommendation; whether to generalize the checklist's on-disk path off the old plugin name now (architecture) or defer it as premature for a two-skill plugin (scope).

## Quick Questions & Answers
1. **¿Qué debe producir el nuevo skill de competencia/proveedores?** → Lista con fuentes (dedupe + corroboración entre fuentes, no una recomendación evaluativa con criterio).
2. **¿Cómo identifica el skill qué sitios de competencia/proveedores mirar por cliente?** → El skill descubre — sin lista fija, a diferencia del patrón estático de `jobs.json`.
3. **¿"Renombrar el plugin" es literal o de branding?** → Rename técnico real — cambia `name`/slug de instalación, acepta romper `rr-stack-research@rr-framework` ya instalado.

## Open Items
Graduó de inmediato tras esta ronda — ver `plans/client-research.md` para todo lo que surgió después. En particular, "un skill nuevo" resultó ser dos (`vendor-research` y `competitor-research`), con arquitecturas materialmente distintas — eso solo se descubrió al empezar a formalizar el plan, no durante esta fase de idea.

---
Graduated to `plans/client-research.md` — 2026-07-22
