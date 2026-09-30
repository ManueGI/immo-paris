# CLAUDE.md

Conventions for anyone (human or AI) changing this repository. Setup and usage are in
[README.md](README.md).

Immo Paris is a Paris real-estate analytics platform built on DVF open data (property
sales published by the DGFiP). This monorepo holds every part of it:

| Directory | Content | Stack | Details |
|---|---|---|---|
| `api/` | API, DVF ingestion, database schema | Python, FastAPI, PostgreSQL + PostGIS | [api/CLAUDE.md](api/CLAUDE.md) |
| `web/` (planned) | Dashboard and back-office | Angular | |
| `mobile/` (planned) | Field app with geolocation | React Native / Expo | |
| `packages/` | Code shared by the web and mobile apps: `api-client`, generated from `api/openapi.json` | TypeScript, pnpm | [packages/api-client/README.md](packages/api-client/README.md) |

The API serves the web and mobile apps **at the same time**, and installed mobile apps
lag behind: the API contract must stay backward compatible (see
`.claude/rules/api-contract.md`).

## Language

Everything in the repository is in **English**: identifiers, comments, docstrings, JSON
fields, error and log messages, tests, commit messages, docs. Only DVF domain values keep
their official French spelling.

## Repository layout rules

- Each part is self-contained: its own dependencies, commands and `CLAUDE.md`. Run a
  part's commands from its directory (`cd api`, or `uv run --directory api ...`).
- Shared local infrastructure lives at the root: `compose.yaml` and the `.env` it reads
  (see `.env.example`). Never commit `.env`.
- The TypeScript parts form one pnpm workspace (`pnpm-workspace.yaml`, Node version in
  `.node-version`, pnpm version in `package.json`). From the root: `pnpm install`,
  `pnpm generate`, `pnpm typecheck`, `pnpm build`; all must pass before committing.
- CI workflows in `.github/workflows/` are required checks on `main`. Do not add a
  workflow-level `paths` filter to a required workflow: a skipped workflow never reports
  its checks and blocks unrelated pull requests. Skip work inside the jobs instead.

## Commits and pull requests

- `main` is protected: no direct push. Work on a branch (`feat/...`, `fix/...`,
  `docs/...`, `chore/...`), open a pull request, and merge once CI is green.
- Pull requests are squash-merged: the PR title becomes the commit subject on `main`, so
  write it like a commit (English, imperative: `Add ...`, `Fix ...`) and explain **why**
  in the description.
- Keep a pull request to one logical change; each part's definition of done passes on
  every commit.

## Where the other rules live

- `<part>/CLAUDE.md`: commands, architecture and definition of done of that part.
- `.claude/rules/`: rules loaded when working on matching files (API contract, DVF data,
  database, tests).
- `.claude/skills/`: step-by-step procedures (`new-migration`).
- `.claude/settings.json`: a hook formats every edited Python file with ruff and reports
  lint errors.
