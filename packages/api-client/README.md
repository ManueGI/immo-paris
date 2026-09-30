# @immo-paris/api-client

Typed client of the Immo Paris API, generated from [api/openapi.json](../../api/openapi.json)
with [openapi-typescript](https://openapi-ts.dev/). `src/schema.ts` is generated: never edit
it by hand.

```ts
import { createApiClient, type Sale } from "@immo-paris/api-client";

const api = createApiClient({ baseUrl: "https://api.example.com" });
const { data, error } = await api.GET("/api/v1/sales/nearby", {
  params: { query: { lat: 48.853, lng: 2.3499, radius_m: 300 } },
});
```

- Types only (`Sale`, `SalePage`, `CommuneStats`...): use them with any HTTP layer, such as
  Angular's `HttpClient`.
- `createApiClient()`: fetch-based client ([openapi-fetch](https://openapi-ts.dev/openapi-fetch/)),
  for React Native / Expo or any runtime with `fetch`. Paths, path parameters, request
  bodies and responses are type-checked; extra query parameters are not.

After an API change (`uv run immo-openapi` in `api/`), regenerate from the repository root
with `pnpm generate` and commit both files in the same pull request: CI fails otherwise.
