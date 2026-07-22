# R&R Framework — Claude Marketplace

Marketplace de plugins de Claude Code para **Research & Report (R&R)**:
investigacion de clientes/prospectos e inteligencia comercial automatizada.
Nace de este [GitHub template](https://github.com/DyxBenjamin/R-R-Framework)
y trae una CI que versiona y publica cada plugin a partir de los mensajes de
commit.

## Plugins en este marketplace

| Plugin | Que hace |
| --- | --- |
| [`base-plugin`](plugins/base-plugin) | Plugin de ejemplo: el skill `skill-creator` y un hook de muestra. |
| [`rr-stack-research`](plugins/rr-stack-research) | Investiga el stack tecnologico de un cliente rastreando sus ofertas de empleo en portales globales y LATAM, con checklist de progreso persistente. |

## Install (para quien instale este marketplace)

```sh
/plugin marketplace add DyxBenjamin/R-R-Framework
/plugin install rr-stack-research@rr-framework
/plugin install base-plugin@rr-framework
```

`rr-stack-research@rr-framework` es `<plugin-name>@<marketplace-name>`. El
nombre del marketplace es el campo `name` en `.claude-plugin/marketplace.json`.

## Setup (si se vuelve a usar como template)

1. Crear un repositorio a partir de este template.
2. Reemplazar los placeholders `CHANGE_ME` restantes (buscar en el repo). Viven
   en:

   | File | Field |
   | --- | --- |
   | `.claude-plugin/marketplace.json` | `name`, `owner.name`, `owner.email` |
   | `plugins/<plugin>/.claude-plugin/plugin.json` | `author.name`, `author.email` |
   | `CLAUDE.md` | `plugin.json` template author |
   | `README.md` | install commands |

Si renombras un directorio en `plugins/`, tambien renombra su entrada en
`marketplace.json` y `.release-please-manifest.json`. CI los mantiene
sincronizados despues del primer push, pero corregirlo antes evita una entrada
huerfana.

## Test locally

Load a plugin from disk without installing it:

```sh
claude --plugin-dir ./plugins/rr-stack-research
claude --plugin-dir ./plugins/base-plugin
```

Run `/rr-stack-research:stack-research` (or `/base-plugin:skill-creator`) to
confirm the skill loads, and `/reload-plugins` to pick up edits without
restarting. Validate the manifests:

```sh
claude plugin validate .                            # marketplace.json
claude plugin validate ./plugins/rr-stack-research   # plugin.json + skills
claude plugin validate ./plugins/base-plugin         # plugin.json + skills/agents/hooks
```

`claude plugin validate` is a local schema check; no account or network needed.
CI runs it on every push and pull request (`.github/workflows/validate.yml`).

## Enable releases

The release workflow needs write access to push the sync commit and open release
PRs. It uses the built-in `GITHUB_TOKEN`. Under **Settings → Actions → General**:

1. **Actions permissions**: "Allow all actions and reusable workflows".
2. **Workflow permissions**: "Read and write permissions".
3. Tick "Allow GitHub Actions to create and approve pull requests", then **Save**.

Skip step 2 or 3 and the run fails with a `403`.

Keep `main` without strict protection rules. The pipeline pushes to `main`
itself, so rules that require a PR, restrict updates, or enforce signed commits
or linear history block the bot's sync push.

## Releasing

Commits reaching `main` drive versioning via
[Release Please](https://github.com/googleapis/release-please) and
[Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Bump | Example |
| --- | --- | --- |
| `fix:` | patch (0.1.0 → 0.1.1) | `fix: correct regex in guard` |
| `feat:` | minor (0.1.0 → 0.2.0) | `feat: add new hook` |
| `feat!:` or `BREAKING CHANGE:` | major (0.1.0 → 1.0.0) | `feat!: redesign hook API` |

On a commit to `main`, CI syncs `marketplace.json` and opens a release PR.
Merging that PR publishes a tagged GitHub Release, bumps the version, and writes
the changelog. Each plugin versions independently.

A small CI script (`scripts/generate-release-config.js`) discovers plugins under
`plugins/` and keeps `marketplace.json` and the Release Please config in sync
from each `plugin.json` on every push.

These files are updated automatically:

- `plugins/<name>/.claude-plugin/plugin.json` — plugin version
- `.claude-plugin/marketplace.json` — marketplace plugin entry version
- `plugins/<name>/CHANGELOG.md` — changelog

Two caveats when merging:

- With **squash-merge**, the PR title is what Release Please reads. Keep the
  conventional prefix or no version bump happens.
- Release Please tracks its release PR by the `autorelease: pending` label, not
  the title. If the next release PR never opens, a stale `autorelease: pending`
  label on an old PR is the usual cause — remove it and re-run.

## Adding a plugin

Create only `plugins/<name>/.claude-plugin/plugin.json`. CI discovers it and
syncs `marketplace.json` and the Release Please config; version bumps are handled
by Release Please.

A plugin can contain more than the example skill and hook here — subagents
(`agents/`), MCP servers (`.mcp.json`), LSP servers (`.lsp.json`), background
monitors, output styles, and more. See [`CLAUDE.md`](CLAUDE.md) for the full
component map, or the
[Plugins reference](https://code.claude.com/docs/en/plugins-reference).

## Layout

```text
.
├── .claude-plugin/
│   └── marketplace.json
├── .github/
│   └── workflows/
│       ├── release.yml         # sync config + Release Please
│       └── validate.yml        # claude plugin validate on push/PR
├── plugins/
│   ├── base-plugin/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── hooks/
│   │   │   ├── hooks.json      # sample hook — replace or delete
│   │   │   └── example-guard.sh
│   │   ├── skills/
│   │   │   └── skill-creator/  # Anthropic's skill, Apache-2.0
│   │   └── README.md
│   └── rr-stack-research/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── config/
│       │   └── jobs.json       # job boards + stack keyword list
│       ├── skills/
│       │   └── stack-research/ # research + persistent checklist logic
│       └── README.md
├── scripts/
│   └── generate-release-config.js
├── release-please-config.json
├── .release-please-manifest.json
├── CLAUDE.md
└── README.md
```

## License

The Unlicense (public domain). See `LICENSE`.

Exception: `plugins/base-plugin/skills/skill-creator/` is Anthropic's skill,
under the Apache License 2.0 (terms in that folder's `LICENSE.txt`). Only that
skill is Apache-2.0; everything else, including skills you add, is covered by The
Unlicense.

