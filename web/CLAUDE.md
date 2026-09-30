# web/CLAUDE.md

Angular 22 web app, server-side rendered (SSR) for search engines. It reads the API
through the types of `@immo-paris/api-client`. Repository-wide rules are in the root
[CLAUDE.md](../CLAUDE.md).

## Commands

Run from the repository root (pnpm workspace), with the API running on port 8000
(`uv run python -m immo_paris` in `api/`):

```bash
pnpm --filter @immo-paris/web start      # dev server with SSR: http://localhost:4200
pnpm --filter @immo-paris/web test       # unit tests (Vitest)
pnpm --filter @immo-paris/web build      # production build in web/dist/web
pnpm --filter @immo-paris/web serve:ssr  # serve the production build: http://localhost:4000
```

**Definition of done** (from the root): `pnpm format:check && pnpm typecheck && pnpm test && pnpm build`.

## Structure

```
src/app/
├── app.ts, app.html        root component: layout shared by every page (<router-outlet>)
├── app.config.ts           application-wide providers (router, HTTP, hydration, locale)
├── app.routes.ts           URL → page component (lazy loaded)
├── app.routes.server.ts    how each route is rendered on the server
├── core/                   services and helpers without UI (API access, arrondissements)
├── shared/                 reusable UI: components and pipes used by several pages
├── pages/                  one folder per route: <name>-page.ts/.html/.scss/.spec.ts
└── testing/                test helpers (typed API response builders)
```

## Conventions

- Standalone components only (no NgModules); each component lists what its template uses in
  `imports`. File names follow the 2025 style guide: `home-page.ts` exports `HomePage`.
- State is held in signals: `signal()` for local state, `computed()` for derived values,
  `input()` for component inputs, `linkedSignal()` for state reset by another signal.
  Load data with `rxResource()` from a service; never subscribe in a template.
- A resource's `value()` throws in an error state: read it only after `hasValue()`, and
  render `isLoading()` and `error()` states.
- Templates use the built-in control flow (`@if`, `@for` with `track`, `@let`), never
  `*ngIf` / `*ngFor`.
- API access goes through the services in `core/api/` (HttpClient + generated types); the
  base URL comes from the `API_BASE_URL` token.
- SSR: code runs on the server first, so never touch `window`, `document` or
  `localStorage` directly. Set the title and meta description of every page (SEO), and
  return a real 404 status for unknown pages (`RESPONSE_INIT`).
- User-facing text is French (the audience is French); code and comments stay English.
- Tests: `TestBed` with `provideHttpClientTesting()`. Start the component with
  `TestBed.tick()`, answer its requests with `HttpTestingController`, and only then
  `await fixture.whenStable()`: awaiting it before answering would never resolve.
