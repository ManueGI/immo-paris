---
paths:
  - "packages/api-client/**"
  - "api/openapi.json"
---

# Generated API client

- `packages/api-client/src/schema.ts` is generated from `api/openapi.json`: never edit it.
  After any API change: `uv run immo-openapi` in `api/`, then `pnpm generate` at the root,
  and commit `openapi.json`, `schema.ts` and the code using them in the same pull request.
  CI fails when the generated code is out of date.
- Re-export the schemas apps need as named types in `src/index.ts` (`Sale`, `SalePage`...),
  so that apps never reach into `components["schemas"]` themselves.
- One TypeScript version for the whole workspace, aligned with the version Angular
  supports.
