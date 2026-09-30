# Immo Paris web app

Angular 22 web app, server-side rendered so that search engines index real content:

- `/`: median price per m² of apartments in the 20 arrondissements
- `/arrondissements/paris-<n>`: statistics and most recent sales of one arrondissement,
  paginated ("Voir plus de ventes")

Data comes from the Immo Paris API, typed with
[@immo-paris/api-client](../packages/api-client/).

## Development

Requirements: Node.js 22.22+ and pnpm (`corepack enable`), and the API running on
http://127.0.0.1:8000 (see [api/README.md](../api/README.md)).

From the repository root:

```bash
pnpm install
pnpm --filter @immo-paris/web start   # http://localhost:4200, with server-side rendering
pnpm --filter @immo-paris/web test    # unit tests (Vitest)
```

Production build and server:

```bash
pnpm --filter @immo-paris/web build
pnpm --filter @immo-paris/web serve:ssr   # http://localhost:4000
```

Conventions are in [CLAUDE.md](CLAUDE.md).
