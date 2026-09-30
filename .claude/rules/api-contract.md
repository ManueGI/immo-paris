---
paths:
  - "api/src/immo_paris/api/**"
  - "api/src/immo_paris/schemas/**"
  - "api/openapi.json"
---

# API contract

The API serves an Angular web app and a React Native mobile app at the same time;
`schemas/` is their contract (TypeScript types will be generated from `/openapi.json`).

- Routers only handle HTTP: no pandas, SQL or file access in `api/`. Data access goes
  through an injected dependency (`Depends`), so tests can override it.
- Every endpoint declares a `response_model` from `schemas/`, and its error responses
  (`responses={404: {"model": ErrorResponse}}`) so generated clients know them.
- `api/openapi.json` is the committed contract: after any API change, run `uv run immo-openapi`
  and commit it with the change (a test fails otherwise), then regenerate the TypeScript
  client (`pnpm generate` at the root). Review both diffs like code.
- CI (`contract.yml`) fails a pull request that breaks the contract. The
  `breaking-change` label skips that check: use it only for a deliberate break, such as
  removing a version that clients no longer use.
- Keep payloads light and typed for mobile: flat objects, numbers as numbers (a `Decimal`
  is serialized as a string: convert it), `null` for missing values (never `NaN`), enums
  for closed sets of values.
- Breaking changes to a response (renaming or removing a field, changing a type) require a
  new API version (`/api/v2`): installed mobile apps cannot be updated instantly. Adding an
  optional field is not breaking.
- Paginate lists with a cursor on (`sale_date`, `id`), not `OFFSET`: offsets get slower
  with depth and skip or repeat rows when data changes during infinite scroll.
- Declare fixed routes before parameterized ones (`/nearby` before `/{sale_id}`).
- Error responses use the right status (`404` missing resource, `422` invalid input,
  `503` data not loaded yet) and a `detail` telling the caller how to fix the problem.
